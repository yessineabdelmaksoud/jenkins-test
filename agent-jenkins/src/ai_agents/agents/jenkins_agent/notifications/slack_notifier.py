"""Slack notifier using webhook URL."""

import requests
from typing import Dict


def notify_slack(webhook_url: str, content: Dict):
    """Post a formatted message to Slack via Incoming Webhook.

    Expects `content` like the email notifier:
      {
        'job': str,
        'build': int,
        'status': 'SUCCESS'|'FAILURE'|..., 
        'action': 'retriggered'|'notified'|..., 
        'summary': str | {
            # SUCCESS style
            'summary': str,
            'improvements': list[str],
            'confidence': float
          } | {
            # FAILURE style
            'cause': str,
            'suggested_actions': list[str],
            'confidence': float
          }
      }
    """
    job = content.get('job')
    build = content.get('build')
    status = content.get('status')
    action = content.get('action') or '-'
    summary = content.get('summary')

    status_upper = str(status or '').upper()

    # Build a readable Slack message
    lines = []
    header = f"Jenkins Job {status_upper}: {job} (build {build})"
    lines.append(header)
    lines.append(f"Action: {action}")

    if isinstance(summary, dict):
        if status_upper == 'SUCCESS' or ('improvements' in summary and 'summary' in summary):
            # SUCCESS formatting
            sum_text = summary.get('summary', '')
            improvements = summary.get('improvements') or []
            if not isinstance(improvements, list):
                improvements = [str(improvements)]
            confidence = summary.get('confidence', 0.0)
            if sum_text:
                lines.append(f"Summary: {sum_text}")
            if improvements:
                lines.append("Improvements:")
                lines.extend([f"• {str(item)}" for item in improvements])
            lines.append(f"Confidence: {confidence:.1%}")
        else:
            # FAILURE formatting
            cause = summary.get('cause', 'Unknown cause')
            actions = summary.get('suggested_actions') or []
            if not isinstance(actions, list):
                actions = [str(actions)]
            confidence = summary.get('confidence', 0.0)
            lines.append(f"Cause: {cause}")
            if actions:
                lines.append("Suggested actions:")
                lines.extend([f"• {str(a)}" for a in actions])
            lines.append(f"Confidence: {confidence:.1%}")
    else:
        # Plain text
        if summary:
            lines.append(f"Summary: {summary}")

    text = "\n".join(lines)

    resp = requests.post(webhook_url, json={"text": text}, timeout=15)
    try:
        resp.raise_for_status()
    except Exception:
        # Include response text in exception for easier debugging
        raise RuntimeError(f"Slack webhook error {resp.status_code}: {resp.text}")
