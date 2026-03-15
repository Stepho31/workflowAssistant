from pydantic import BaseModel, Field
from typing import Optional


class AnalyzeRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    raw_text: str = Field(..., min_length=1)
    source: str = Field(default="manual", max_length=50)


class WorkflowCreate(BaseModel):
    title: str
    raw_text: str
    source: str = "manual"
    run_ai: bool = True


class WorkflowResponse(BaseModel):
    id: int
    title: str
    source: str
    raw_text: str
    summary: Optional[str] = None
    action_items: Optional[str] = None
    status: str

    class Config:
        from_attributes = True
