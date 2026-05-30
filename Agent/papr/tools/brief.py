"""Tools for the daily brief.

`current_date` gives papr a reliable clock (LLMs don't know "today"), so it can
name a brief file `/briefs/YYYY-MM-DD.md`.
"""
from __future__ import annotations

from datetime import datetime, timezone

from langchain_core.tools import tool


@tool
def current_date() -> str:
    """Return today's date and time in UTC (ISO 8601).

    Use the date part (YYYY-MM-DD) to name the daily brief file
    `/briefs/YYYY-MM-DD.md`.
    """
    return datetime.now(timezone.utc).isoformat()
