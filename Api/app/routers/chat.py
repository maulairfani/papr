"""Chat route — streams the agent's run to the client as SSE."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ..core.auth import current_user
from ..services import chat as chat_service

router = APIRouter(tags=["chat"])


class ChatBody(BaseModel):
    message: str
    thread_id: str | None = None


@router.post("/chat")
async def chat(body: ChatBody, user_id: str = Depends(current_user)) -> StreamingResponse:
    return StreamingResponse(
        chat_service.stream_reply(user_id, body.message, body.thread_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
