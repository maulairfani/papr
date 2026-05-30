"""Topics + daily-brief endpoints (logic in services.topics / services.briefs)."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..core.auth import current_user
from ..schemas import SubscribeBody, TopicBody
from ..services import briefs as briefs_service
from ..services import topics as topics_service

router = APIRouter()


# --- topics ----------------------------------------------------------------

@router.get("/topics")
async def list_topics(user_id: str = Depends(current_user)) -> dict:
    return {"topics": await topics_service.list_topics(user_id)}


@router.post("/topics")
async def add_topic(body: TopicBody, user_id: str = Depends(current_user)) -> dict:
    return await topics_service.add_topic(user_id, body.name, body.query)


@router.delete("/topics/{slug}")
async def delete_topic(slug: str, user_id: str = Depends(current_user)) -> dict:
    return {"deleted": await topics_service.delete_topic(user_id, slug)}


# --- daily brief -----------------------------------------------------------

@router.get("/brief/subscription")
async def get_subscription(user_id: str = Depends(current_user)) -> dict:
    return await briefs_service.subscription_status(user_id)


@router.post("/brief/subscribe")
async def subscribe(body: SubscribeBody, user_id: str = Depends(current_user)) -> dict:
    return await briefs_service.subscribe(user_id, body.hour, body.minute)


@router.post("/brief/unsubscribe")
async def unsubscribe(user_id: str = Depends(current_user)) -> dict:
    return await briefs_service.unsubscribe(user_id)


@router.post("/brief/run-now")
async def run_now(user_id: str = Depends(current_user)) -> dict:
    return await briefs_service.run_now(user_id)
