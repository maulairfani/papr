"""Skills: create/edit the SKILL.md files (logic in services.skills)."""
from __future__ import annotations

from fastapi import APIRouter, Depends

from ..core.auth import current_user
from ..schemas import SkillBody
from ..services import skills as skills_service

router = APIRouter()


@router.post("/skills/save")
async def save_skill(body: SkillBody, user_id: str = Depends(current_user)) -> dict:
    return await skills_service.save_skill(user_id, body.name, body.content)
