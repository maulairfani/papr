"""Single LangGraph SDK client to the Agent Server (runs, store, crons)."""
from __future__ import annotations

from functools import lru_cache

from langgraph_sdk import get_client
from langgraph_sdk.client import LangGraphClient

from ..config import settings


@lru_cache(maxsize=1)
def agent_client() -> LangGraphClient:
    """The async LangGraph client, reused across requests."""
    return get_client(url=settings.agent_url)
