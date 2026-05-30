"""Brief routes — only the cron lifecycle (specs/outputs are files via /files)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..core.auth import current_user
from ..services import briefs as briefs_service

router = APIRouter(tags=["briefs"])


@router.get("/brief/schedule")
async def get_schedule(user_id: str = Depends(current_user)) -> dict:
    return await briefs_service.status(user_id)


class ScheduleBody(BaseModel):
    hour: int = Field(ge=0, le=23)
    minute: int = Field(ge=0, le=59)


@router.post("/brief/schedule")
async def set_schedule(body: ScheduleBody, user_id: str = Depends(current_user)) -> dict:
    return await briefs_service.schedule(user_id, body.hour, body.minute)


@router.delete("/brief/schedule")
async def delete_schedule(user_id: str = Depends(current_user)) -> dict:
    return await briefs_service.unschedule(user_id)


@router.post("/brief/run-now")
async def run_now(user_id: str = Depends(current_user)) -> dict:
    return await briefs_service.run_now(user_id)
