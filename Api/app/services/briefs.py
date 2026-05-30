"""Daily-brief scheduling — the one brief piece that isn't file CRUD.

Brief *content* (specs + outputs) is plain files under /briefs/ (handled by the
files service). This module only manages the native LangGraph cron that fires the
brief trigger on a schedule, plus a "run now". The cron carries `user_id` in its
run context so scheduled runs isolate to the right store. We keep the per-user
cron id in a private `_briefmeta` store namespace (BFF bookkeeping, not a file).
"""
from __future__ import annotations

from ..config import settings
from ..core.agent_client import agent_client
from .errors import Invalid

_META_FOLDER = "_briefmeta"
_META_KEY = "/cron.json"

# Static trigger — tells papr to load its daily-brief skill. The "what's new"
# logic lives in the skill, which reads /briefs/specs/ and writes the outputs.
BRIEF_TRIGGER = (
    "Time to generate today's research briefs. Open your `daily-brief` skill and "
    "follow it exactly: read every spec in /briefs/specs/ and write today's brief for "
    "each, overwriting today's file if it already exists. This is an automated run "
    "with no one to ask — work only from the specs, and write only under /briefs/."
)


def _brief_input() -> dict:
    return {"messages": [{"role": "user", "content": BRIEF_TRIGGER}]}


async def _meta(user_id: str) -> dict:
    try:
        item = await agent_client().store.get_item([user_id, "papr", _META_FOLDER], key=_META_KEY)
    except Exception:  # noqa: BLE001 - absent meta
        return {}
    return (item or {}).get("value") or {}


async def status(user_id: str) -> dict:
    m = await _meta(user_id)
    return {
        "subscribed": bool(m.get("cron_id")),
        "hour": m.get("hour"),
        "minute": m.get("minute"),
        "cron_id": m.get("cron_id"),
    }


async def schedule(user_id: str, hour: int, minute: int) -> dict:
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise Invalid("hour must be 0-23 and minute 0-59 (UTC)")
    await unschedule(user_id)  # idempotent: replace any existing cron
    client = agent_client()
    cron = await client.crons.create(
        settings.assistant_id,
        schedule=f"{minute} {hour} * * *",  # UTC, daily
        input=_brief_input(),
        context={"user_id": user_id},
        metadata={"user_id": user_id, "kind": "daily-brief"},
    )
    cron_id = cron.get("cron_id") or cron.get("id")
    await client.store.put_item(
        [user_id, "papr", _META_FOLDER],
        key=_META_KEY,
        value={"cron_id": cron_id, "hour": hour, "minute": minute},
    )
    return await status(user_id)


async def unschedule(user_id: str) -> dict:
    client = agent_client()
    m = await _meta(user_id)
    if m.get("cron_id"):
        try:
            await client.crons.delete(m["cron_id"])
        except Exception:  # noqa: BLE001 - cron already gone
            pass
    try:
        await client.store.delete_item([user_id, "papr", _META_FOLDER], key=_META_KEY)
    except Exception:  # noqa: BLE001
        pass
    return {"subscribed": False}


async def run_now(user_id: str) -> dict:
    """Fire the brief trigger immediately as a one-off background run."""
    client = agent_client()
    thread = await client.threads.create()
    run = await client.runs.create(
        thread["thread_id"],
        settings.assistant_id,
        input=_brief_input(),
        context={"user_id": user_id},
    )
    return {"thread_id": thread["thread_id"], "run_id": run.get("run_id") or run.get("id")}
