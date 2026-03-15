import json
import os
from pathlib import Path
from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from .ai import analyze_text
from .database import Base, engine, get_db
from .integrations import send_to_zapier
from .models import WorkflowItem
from .schemas import WorkflowCreate

load_dotenv()
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Workflow Assistant MVP")
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/health")
def health_check():
    return {"ok": True}


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db: Session = Depends(get_db)):
    items = db.query(WorkflowItem).order_by(WorkflowItem.id.desc()).all()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "items": items,
            "openai_enabled": bool(os.getenv("OPENAI_API_KEY")),
            "zapier_enabled": bool(os.getenv("ZAPIER_OUTBOUND_WEBHOOK_URL")),
        },
    )


@app.post("/items")
def create_item(
    title: str = Form(...),
    raw_text: str = Form(...),
    source: str = Form("manual"),
    run_ai: str = Form("true"),
    db: Session = Depends(get_db),
):
    item = WorkflowItem(title=title, raw_text=raw_text, source=source, status="new")
    db.add(item)
    db.commit()
    db.refresh(item)

    if run_ai.lower() == "true":
        result = analyze_text(title=title, raw_text=raw_text)
        item.summary = result["summary"]
        item.action_items = result["action_items"]
        item.status = result["status"]
        db.commit()

    return RedirectResponse(url="/", status_code=303)


@app.post("/api/items")
def create_item_api(payload: WorkflowCreate, db: Session = Depends(get_db)):
    item = WorkflowItem(title=payload.title, raw_text=payload.raw_text, source=payload.source, status="new")
    db.add(item)
    db.commit()
    db.refresh(item)

    if payload.run_ai:
        result = analyze_text(title=payload.title, raw_text=payload.raw_text)
        item.summary = result["summary"]
        item.action_items = result["action_items"]
        item.status = result["status"]
        db.commit()
        db.refresh(item)

    return {
        "id": item.id,
        "title": item.title,
        "source": item.source,
        "raw_text": item.raw_text,
        "summary": item.summary,
        "action_items": item.action_items,
        "status": item.status,
    }


@app.post("/api/webhooks/inbound")
async def inbound_webhook(request: Request, db: Session = Depends(get_db)):
    try:
        payload = await request.json()
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON body: {exc}")
    source = payload.get("source", "webhook")

    title = (
        payload.get("title")
        or payload.get("subject")
        or payload.get("meeting_title")
        or payload.get("event_name")
        or "Untitled item"
    )

    raw_text = (
        payload.get("raw_text")
        or payload.get("body")
        or payload.get("text")
        or payload.get("message")
        or payload.get("transcript")
        or json.dumps(payload, indent=2)
    )

    item = WorkflowItem(title=title, raw_text=raw_text, source=source, status="new")
    db.add(item)
    db.commit()
    db.refresh(item)

    result = analyze_text(title=title, raw_text=raw_text)
    item.summary = result["summary"]
    item.action_items = result["action_items"]
    item.status = result["status"]
    db.commit()
    db.refresh(item)

    return {
        "ok": True,
        "item_id": item.id,
        "summary": item.summary,
        "action_items": item.action_items,
        "status": item.status,
    }


@app.post("/items/{item_id}/send-to-zapier")
def push_item_to_zapier(item_id: int, db: Session = Depends(get_db)):
    item = db.query(WorkflowItem).filter(WorkflowItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    payload = {
        "event": "workflow_item_created",
        "item": {
            "id": item.id,
            "title": item.title,
            "source": item.source,
            "raw_text": item.raw_text,
            "summary": item.summary,
            "action_items": item.action_items,
            "status": item.status,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }
    }

    success, message = send_to_zapier(payload)
    if not success:
        raise HTTPException(status_code=400, detail=message)
    return {"ok": True, "message": message}
