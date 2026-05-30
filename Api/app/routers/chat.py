"""Chat: stream papr's reply to the browser as Server-Sent Events.

Thin transport adapter — the run logic lives in services.chat; this just frames
each event dict as an SSE `data:` line.
"""
from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from ..core.auth import current_user
from ..schemas import ChatBody
from ..services import chat as chat_service

router = APIRouter()


def _sse(obj: dict) -> str:
    return f"data: {json.dumps(obj)}\n\n"


@router.post("/chat")
async def chat(body: ChatBody, user_id: str = Depends(current_user)) -> StreamingResponse:
    async def gen():
        async for event in chat_service.stream_reply(user_id, body.message, body.thread_id):
            yield _sse(event)

    return StreamingResponse(gen(), media_type="text/event-stream")
