"""Per-run context passed at invocation time (not persisted, not in the prompt).

`user_id` is the key the backend's namespace factory uses to isolate each user's
files. It is set server-side — by the API for interactive runs, by the
assistant/cron config for scheduled runs — never chosen by the client.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PaprContext:
    # Optional so local `langgraph dev` runs (no context) fall back to a dev user.
    user_id: str | None = None
