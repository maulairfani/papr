"""Chat: proxy a run to the agent and normalize its stream for the frontend.

The agent streams two modes (see the identification run): `updates` (per-node
state deltas = what papr is doing) and `messages` (assistant text tokens). We map
them to a small SSE event model the ChatInterface consumes directly:

    {type: thread, thread_id}
    {type: activity, kind: tool_call|tool_result|todos, ...}
    {type: token, text}
    {type: done} | {type: error, detail}

`user_id` is injected into the run context server-side (same mechanism the cron
uses), so the agent isolates to this user's store. Clients never set it.
"""
from __future__ import annotations

import json
from collections.abc import AsyncIterator

from ..config import settings
from ..core.agent_client import agent_client

_TOOL_RESULT_CAP = 4000  # keep SSE frames sane; the FE collapses long results


def _sse(obj: dict) -> str:
    return f"data: {json.dumps(obj, default=str)}\n\n"


def _text_of(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            parts.append(block.get("text", "") if isinstance(block, dict) else str(block))
        return "".join(parts)
    return ""


def _frames(event: str, data) -> list[str]:
    out: list[str] = []
    if event == "updates":
        for _node, update in (data or {}).items():
            if not isinstance(update, dict):
                continue
            todos = update.get("todos")
            if todos:
                items = [
                    {
                        "text": t.get("content") or t.get("text") or "",
                        "done": t.get("status") == "completed",
                    }
                    for t in todos
                    if isinstance(t, dict)
                ]
                out.append(_sse({"type": "activity", "kind": "todos", "items": items}))
            for m in update.get("messages", []):
                if not isinstance(m, dict):
                    continue
                if m.get("type") == "ai":
                    for tc in m.get("tool_calls") or []:
                        out.append(
                            _sse(
                                {
                                    "type": "activity",
                                    "kind": "tool_call",
                                    "tool": tc.get("name"),
                                    "args": tc.get("args"),
                                }
                            )
                        )
                elif m.get("type") == "tool":
                    out.append(
                        _sse(
                            {
                                "type": "activity",
                                "kind": "tool_result",
                                "tool": m.get("name"),
                                "result": _text_of(m.get("content"))[:_TOOL_RESULT_CAP],
                            }
                        )
                    )
    elif event == "messages":
        msg = data[0] if isinstance(data, list) and data else None
        if isinstance(msg, dict) and msg.get("type") == "AIMessageChunk":
            text = _text_of(msg.get("content"))
            if text:
                out.append(_sse({"type": "token", "text": text}))
    return out


async def stream_reply(
    user_id: str, message: str, thread_id: str | None = None
) -> AsyncIterator[str]:
    client = agent_client()
    if not thread_id:
        thread = await client.threads.create()
        thread_id = thread["thread_id"]
    yield _sse({"type": "thread", "thread_id": thread_id})
    try:
        async for chunk in client.runs.stream(
            thread_id,
            settings.assistant_id,
            input={"messages": [{"role": "user", "content": message}]},
            context={"user_id": user_id},
            stream_mode=["updates", "messages-tuple"],
        ):
            for frame in _frames(chunk.event, chunk.data):
                yield frame
    except Exception as exc:  # noqa: BLE001 - surface stream errors to the client
        yield _sse({"type": "error", "detail": str(exc)})
    yield _sse({"type": "done"})
