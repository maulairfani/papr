"""Liveness + agent-connectivity check."""
from __future__ import annotations

from fastapi import APIRouter

from ..core.agent_client import agent_client

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """Report whether the BFF can reach the Agent Server."""
    agent_ok, detail = True, None
    try:
        await agent_client().assistants.search(limit=1)
    except Exception as exc:  # noqa: BLE001 - surface any connectivity error
        agent_ok, detail = False, str(exc)
    return {"status": "ok", "agent": agent_ok, "detail": detail}
