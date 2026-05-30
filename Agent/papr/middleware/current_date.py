"""Inject today's date into the system prompt on every model call.

papr needs to know "today" (e.g. to date a brief file `/briefs/<slug>/<date>.md`)
without spending a tool call on it. We inject it per-request rather than baking it
into the static prompt, so the date is always current instead of frozen at
agent-build time. As a user middleware it runs outermost — before memory/skills
append — so reading `request.system_prompt` here sees the base prompt and we just
append to it.
"""
from __future__ import annotations

from datetime import datetime, timezone

from langchain.agents.middleware import ModelRequest, dynamic_prompt


@dynamic_prompt
def inject_current_date(request: ModelRequest) -> str:
    """Append today's UTC date to whatever system prompt is in effect."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    base = request.system_prompt or ""
    return f"{base}\n\nToday's date is {today} (UTC)."
