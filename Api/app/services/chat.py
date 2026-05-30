"""Chat service: stream papr's reply as a sequence of typed events.

Yields plain dicts ({"type": "thread"|"token"|"error"|"done", ...}); the router
formats them as SSE frames. `user_id` is injected into the run context here so
the agent isolates to the right store.
"""
from __future__ import annotations

from typing import Any, AsyncIterator

from .. import config
from ..core.agent_client import client


def _text(content: Any) -> str:
    """Normalize message content (str or list of content blocks) to text."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        return "".join(
            b.get("text", "")
            for b in content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


async def stream_reply(
    user_id: str, message: str, thread_id: str | None
) -> AsyncIterator[dict]:
    try:
        if not thread_id:
            thread = await client.threads.create()
            thread_id = thread["thread_id"]
        # Tell the client the thread up front so it can continue the conversation.
        yield {"type": "thread", "thread_id": thread_id}

        async for chunk in client.runs.stream(
            thread_id,
            config.ASSISTANT_ID,
            input={"messages": [{"role": "user", "content": message}]},
            context={"user_id": user_id},  # server-side identity, never client-chosen
            stream_mode="messages-tuple",
        ):
            if chunk.event == "error":
                yield {"type": "error", "error": str(chunk.data)}
                continue
            if chunk.event != "messages":
                continue
            data = chunk.data
            msg = data[0] if isinstance(data, (list, tuple)) and data else None
            if not isinstance(msg, dict):
                continue
            # Only forward assistant text (skip human echo / tool messages).
            if msg.get("type") not in (None, "ai", "AIMessageChunk"):
                continue
            text = _text(msg.get("content"))
            if text:
                yield {"type": "token", "text": text}
    except Exception as e:  # surface failures instead of ending with a silent done
        yield {"type": "error", "error": str(e)}
    yield {"type": "done"}
