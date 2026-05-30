"""Shared async client for the LangGraph Agent Server."""
from __future__ import annotations

from langgraph_sdk import get_client

from .. import config

# Reused across requests; constructs its httpx client lazily.
client = get_client(url=config.AGENT_URL)
