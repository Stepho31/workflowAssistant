import os
import requests


def send_to_zapier(payload: dict) -> tuple[bool, str]:
    webhook_url = os.getenv("ZAPIER_OUTBOUND_WEBHOOK_URL", "").strip()
    if not webhook_url:
        return False, "ZAPIER_OUTBOUND_WEBHOOK_URL is not configured"

    try:
        response = requests.post(webhook_url, json=payload, timeout=10)
        response.raise_for_status()
        return True, f"Sent to Zapier ({response.status_code})"
    except Exception as exc:
        return False, f"Zapier send failed: {exc}"
