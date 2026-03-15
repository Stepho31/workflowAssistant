import json
import os
from openai import OpenAI

PROMPT = """
You are a workflow assistant for busy professionals.
Given the input, produce JSON with these exact keys:
- summary: a short executive summary in 2-4 bullet points as a single string
- action_items: 3-7 actionable next steps as a single string with one bullet per line
- status: one of new, waiting, done
If the text is unclear, make the best grounded attempt.
""".strip()


def analyze_text(title: str, raw_text: str) -> dict:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {
            "summary": "- AI disabled because OPENAI_API_KEY is not set.\n- Add your key in .env to enable summaries.",
            "action_items": "- Set OPENAI_API_KEY in .env\n- Re-run analysis",
            "status": "new",
        }

    client = OpenAI(api_key=api_key)
    model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": PROMPT},
            {
                "role": "user",
                "content": f"Title: {title}\n\nContent:\n{raw_text}",
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "workflow_analysis",
                "schema": {
                    "type": "object",
                    "properties": {
                        "summary": {"type": "string"},
                        "action_items": {"type": "string"},
                        "status": {
                            "type": "string",
                            "enum": ["new", "waiting", "done"],
                        },
                    },
                    "required": ["summary", "action_items", "status"],
                    "additionalProperties": False,
                },
            }
        },
    )

    parsed = json.loads(response.output_text)
    return parsed
