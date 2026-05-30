"""Tools for the daily brief.

`current_date` gives papr a reliable clock (LLMs don't know "today"), so it can
name a brief file `/briefs/YYYY-MM-DD.md`. `send_email` is the brief's delivery
channel — best-effort SMTP: it sends when SMTP_* is configured and otherwise
returns a clear "not configured" message, so an unconfigured dev box still
produces the brief file (the primary artifact) without the run failing.
"""
from __future__ import annotations

import os
import smtplib
from datetime import datetime, timezone
from email.message import EmailMessage

from langchain_core.tools import tool


@tool
def current_date() -> str:
    """Return today's date and time in UTC (ISO 8601).

    Use the date part (YYYY-MM-DD) to name the daily brief file
    `/briefs/YYYY-MM-DD.md`.
    """
    return datetime.now(timezone.utc).isoformat()


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Email a recipient (used to deliver the daily brief).

    Delivery is best-effort: if the server's SMTP_* environment is configured the
    message is sent, otherwise this reports that email is not configured. Either
    way, always write the brief to /briefs/ first — that file is the source of
    truth; the email is just a notification.
    """
    host = os.environ.get("SMTP_HOST")
    if not host:
        return (
            "Email not sent: SMTP is not configured on this server "
            "(set SMTP_HOST/SMTP_PORT/SMTP_USER/SMTP_PASSWORD/SMTP_FROM). "
            "The brief file in /briefs/ is still the delivered artifact."
        )

    msg = EmailMessage()
    msg["From"] = os.environ.get("SMTP_FROM", os.environ.get("SMTP_USER", "papr@localhost"))
    msg["To"] = to
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        port = int(os.environ.get("SMTP_PORT", "587"))
        with smtplib.SMTP(host, port, timeout=20) as server:
            server.starttls()
            user, password = os.environ.get("SMTP_USER"), os.environ.get("SMTP_PASSWORD")
            if user and password:
                server.login(user, password)
            server.send_message(msg)
    except Exception as e:  # noqa: BLE001 - delivery failure shouldn't crash the run
        return f"Email delivery to {to} failed: {e}. The brief was still saved to /briefs/."
    return f"Brief emailed to {to}."
