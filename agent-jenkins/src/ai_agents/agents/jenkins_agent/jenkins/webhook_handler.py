"""Adapter for existing webhook handling code. Place your webhook parsing logic here."""


def parse_webhook(payload: dict) -> dict:
    """Normalize a webhook payload to the state fields used by the agent."""
    # TODO: implement logic from your existing webhook.py
    # Minimal placeholder mapping
    return {
        "job_name": payload.get("job_name") or payload.get("name"),
        "build_number": payload.get("build_number") or payload.get("build", {}).get("number"),
        "build_status": payload.get("status") or payload.get("build", {}).get("status"),
        "raw": payload,
    }
