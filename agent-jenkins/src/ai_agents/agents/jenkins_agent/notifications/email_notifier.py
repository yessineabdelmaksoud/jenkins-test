"""SMTP email notifier using MIME multipart.

Provides:
- send_email(...) low-level function
- notify_email(config, content) high-level helper that composes subject/body and sends email

Config keys expected by notify_email:
- smtp_host, smtp_port, username, password, to (list or comma-separated string)

If password is not provided in config, falls back to environment variable EMAIL_PASSWORD.
"""

import os
import smtplib
from typing import Dict, Iterable
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_email(smtp_host: str, smtp_port: int, username: str, password: str, to: Iterable[str], subject: str, body: str, html: str = None) -> None:
    """Send an email using SMTP with STARTTLS. Raises on failure.

    Args:
        smtp_host: SMTP server host
        smtp_port: SMTP server port
        username: SMTP username (From)
        password: SMTP password or app password
        to: iterable of recipient addresses
        subject: email subject
        body: plain text body
        html: optional HTML body
    """
    if isinstance(to, str):
        to_list = [a.strip() for a in to.split(",") if a.strip()]
    else:
        to_list = list(to)

    msg = MIMEMultipart()
    msg["From"] = username
    msg["To"] = ", ".join(to_list)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))
    if html:
        msg.attach(MIMEText(html, "html"))

    server = None
    try:
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
        server.ehlo()
        server.starttls()
        server.ehlo()
        if password:
            server.login(username, password)
        server.sendmail(username, to_list, msg.as_string())
    finally:
        if server is not None:
            try:
                server.quit()
            except Exception:
                pass


def notify_email(config: Dict, content: Dict) -> None:
    """High-level helper to notify via email using a config dict and a content dict.

    config example:
      {
        'smtp_host': 'smtp.gmail.com',
        'smtp_port': 587,
        'username': 'me@example.com',
        'password': 'app-password',
        'to': ['recipient@example.com']
      }

    content example (from agent):
      { 'job': 'my-job', 'build': 123, 'status': 'FAILURE', 'summary': 'Short summary' }
    """
    smtp_host = config.get("smtp_host") or os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(config.get("smtp_port", os.getenv("SMTP_PORT", 587)))
    username = config.get("username") or os.getenv("EMAIL_SENDER")
    password = config.get("password") or os.getenv("EMAIL_PASSWORD")
    to = config.get("to") or os.getenv("EMAIL_TO") or []

    # normalize recipients
    if isinstance(to, str):
        to_list = [a.strip() for a in to.split(",") if a.strip()]
    elif isinstance(to, (list, tuple)):
        to_list = list(to)
    else:
        to_list = []

    subject = config.get("subject") or f"Jenkins job {content.get('job')} build {content.get('build')} status {content.get('status')}"
    
    # Format the body per status and summary structure
    status_upper = str(content.get('status') or '').upper()
    action_taken = content.get('action') or '-'
    summary = content.get("summary", "No details provided.")

    if isinstance(summary, dict):
        if status_upper == 'SUCCESS' or ('improvements' in summary and 'summary' in summary):
            # SUCCESS analysis email with improvements list
            improvements = summary.get('improvements') or []
            if not isinstance(improvements, list):
                improvements = [str(improvements)]
            confidence = summary.get('confidence', 0.0)
            sum_text = summary.get('summary', '')
            body = f"""Jenkins Job Success Report

Job: {content.get('job')}
Build: {content.get('build')}
Status: {content.get('status')}
Action Taken: {action_taken}

LLM Summary:
{sum_text}

Suggested Improvements:
{chr(10).join(f"- {str(item)}" for item in improvements)}

Confidence: {confidence:.1%}
"""
        else:
            # FAILURE-style analysis with cause/suggested actions
            cause = summary.get("cause", "Unknown cause")
            actions = summary.get("suggested_actions", [])
            if not isinstance(actions, list):
                actions = [str(actions)]
            confidence = summary.get("confidence", 0.0)
            body = f"""Jenkins Job Failure Report
        
Job: {content.get('job')}
Build: {content.get('build')}
Status: {content.get('status')}
Action Taken: {action_taken}

Analysis:
Cause: {cause}
Confidence: {confidence:.1%}

Suggested Actions:
{chr(10).join(f"- {action}" for action in actions)}
"""
    else:
        # Plain text summary
        body = config.get("body") or str(summary)

    if not username:
        raise ValueError("Email sender (username) not configured")
    if not to_list:
        raise ValueError("No email recipients configured")

    send_email(smtp_host, smtp_port, username, password, to_list, subject, body)
