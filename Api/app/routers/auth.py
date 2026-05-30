"""Auth routes (dev login + whoami)."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from ..core.auth import current_user, mint_token
from ..services.seed import seed_user

router = APIRouter(tags=["auth"])


class DevLogin(BaseModel):
    user_id: str


@router.post("/auth/dev-login")
async def dev_login(body: DevLogin) -> dict:
    """Dev-only: trade a chosen user_id for a bearer token; seed starter content."""
    seeded = await seed_user(body.user_id)
    return {"token": mint_token(body.user_id), "user_id": body.user_id, "seeded": seeded}


@router.get("/me")
def me(user_id: str = Depends(current_user)) -> dict:
    return {"user_id": user_id}
