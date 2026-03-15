# Workflow Assistant MVP

A lightweight MVP for a workflow assistant that turns messy text (meeting notes, emails, task dumps, or webhook payloads) into:
- a concise summary
- actionable next steps
- a simple status

It includes:
- FastAPI backend
- SQLite database
- small HTML UI
- OpenAI-powered analysis
- inbound webhook endpoint for Zapier or other tools
- outbound Zapier webhook button for pushing analyzed items into another automation

## Why this MVP
Instead of trying to integrate with Gmail, Slack, Notion, HubSpot, Salesforce, and everything else at once, this MVP proves the core value first:
1. intake information
2. analyze it
3. convert it into structured work
4. optionally pass it into another automation

## Local setup

### 1) Create a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2) Install dependencies
```bash
pip install -r requirements.txt
```

### 3) Configure environment variables
```bash
cp .env.example .env
```
Then edit `.env`.

Minimum useful settings:
```env
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4.1-mini
DATABASE_URL=sqlite:///./workflow_assistant.db
```

Optional Zapier setting:
```env
ZAPIER_OUTBOUND_WEBHOOK_URL=https://hooks.zapier.com/hooks/catch/...
```

### 4) Run the app
```bash
python run.py
```
Then open:
```text
http://127.0.0.1:8000
```

## How to test

### Test 1: Manual workflow item
1. Open the app in the browser.
2. Paste messy notes like:
   ```text
   Spoke with Megan from Saville Dodgen. She wants pricing details and implementation timeline. Need to send a comparison sheet by Friday. Also wants another meeting with payroll manager next week.
   ```
3. Click **Save item**.
4. You should see a summary and action items.

### Test 2: API endpoint directly
```bash
curl -X POST http://127.0.0.1:8000/api/items \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Client follow-up",
    "raw_text": "Client wants revised proposal, legal review, and a meeting next Tuesday.",
    "source": "api",
    "run_ai": true
  }'
```

### Test 3: Inbound webhook endpoint
This is the easiest place to use Zapier.

```bash
curl -X POST http://127.0.0.1:8000/api/webhooks/inbound \
  -H "Content-Type: application/json" \
  -d '{
    "title": "New lead email",
    "body": "Potential client asked for pricing, onboarding steps, and whether you support Dallas-based payroll teams.",
    "source": "zapier"
  }'
```

That will create a workflow item, run AI analysis, and return the structured result.

## Recommended first integration path

### Option A: Zapier inbound only
Use Zapier as the integration layer instead of building many direct integrations.

Example Zap:
1. Trigger: New Gmail email, new Google Calendar event, or new Slack message
2. Filter: only messages with a specific label, sender, or keyword
3. Action: Webhooks by Zapier → POST to your app's `/api/webhooks/inbound`

Body example:
```json
{
  "title": "{{subject}}",
  "body": "{{body_plain}}",
  "source": "gmail"
}
```

This gives you instant connectivity to many apps while keeping your product code small.

### Option B: Zapier outbound
Set `ZAPIER_OUTBOUND_WEBHOOK_URL` and click **Send to Zapier** in the UI.
Then build downstream automations like:
- create a Notion page
- append a Google Sheet row
- send a Slack message
- create a task in ClickUp or Asana

## Best MVP positioning
Do not sell this as “AI for everybody.”
Sell it as:
- AI assistant for sales reps
- AI assistant for consultants
- AI assistant for founders
- AI assistant for recruiters

That way the workflows stay narrow and valuable.

## Suggested next steps after MVP
1. Add authentication
2. Add user accounts
3. Add daily digest email
4. Add direct Gmail/Google Calendar OAuth
5. Add rule templates by profession
6. Add approval flows before pushing to Zapier
7. Add embeddings/search over past workflow items

## Project structure
```text
workflow_assistant_mvp/
├── app/
│   ├── ai.py
│   ├── database.py
│   ├── integrations.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── static/
│   │   └── style.css
│   └── templates/
│       └── index.html
├── .env.example
├── README.md
├── requirements.txt
└── run.py
```
