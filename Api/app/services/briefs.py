"""Daily-brief service: cron lifecycle + immediate trigger.

The brief is a native LangGraph cron carrying `user_id` in run context, so the
scheduled run isolates to the right store. Subscription state (the cron id +
schedule) lives in an internal `_briefmeta` namespace, not a user-visible folder.
"""
from __future__ import annotations

from .. import config
from ..core.agent_client import client
from . import store
from .errors import Invalid

_META = "_briefmeta"  # internal namespace; never listed as a user folder
_SUB_KEY = "/subscription.json"


def _brief_input() -> dict:
    return {"messages": [{"role": "user", "content": config.BRIEF_TRIGGER}]}


async def _read_sub(user_id: str) -> dict | None:
    item = await store.get(user_id, _META, _SUB_KEY)
    return (item or {}).get("value") if item else None


async def _delete_cron(cron_id: str) -> None:
    try:
        await client.crons.delete(cron_id)
    except Exception:  # noqa: BLE001 - already gone / server hiccup; treat as removed
        pass


async def subscription_status(user_id: str) -> dict:
    sub = await _read_sub(user_id)
    if not sub or not sub.get("cron_id"):
        return {"subscribed": False}
    return {
        "subscribed": True,
        "hour": sub.get("hour"),
        "minute": sub.get("minute"),
        "cron_id": sub.get("cron_id"),
    }


async def subscribe(user_id: str, hour: int, minute: int) -> dict:
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise Invalid("hour 0-23 and minute 0-59 (UTC)")

    # Replace any existing subscription so re-subscribing never leaves orphans.
    existing = await _read_sub(user_id)
    if existing and existing.get("cron_id"):
        await _delete_cron(existing["cron_id"])

    schedule = f"{minute} {hour} * * *"  # daily at HH:MM UTC
    cron = await client.crons.create(
        config.ASSISTANT_ID,
        schedule=schedule,
        input=_brief_input(),
        context={"user_id": user_id},  # carries identity into the scheduled run
        metadata={"papr_user": user_id, "papr_kind": "daily_brief"},
    )
    sub = {
        "cron_id": cron["cron_id"],
        "schedule": schedule,
        "hour": hour,
        "minute": minute,
        "created_at": store.now_iso(),
    }
    await store.put(user_id, _META, _SUB_KEY, sub)
    return {"subscribed": True, "hour": hour, "minute": minute, "cron_id": cron["cron_id"]}


async def unsubscribe(user_id: str) -> dict:
    sub = await _read_sub(user_id)
    if sub and sub.get("cron_id"):
        await _delete_cron(sub["cron_id"])
    await store.delete(user_id, _META, _SUB_KEY)
    return {"subscribed": False}


async def run_now(user_id: str) -> dict:
    # Fire the same trigger as the cron, immediately, as a background run. The
    # brief file appears in /briefs/ when the run finishes (poll the file list).
    run = await client.runs.create(
        None, config.ASSISTANT_ID, input=_brief_input(), context={"user_id": user_id}
    )
    return {"run_id": run.get("run_id"), "thread_id": run.get("thread_id")}
