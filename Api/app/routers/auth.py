"""Authentication endpoints: dev login + current-user echo."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from ..core.auth import current_user, mint_token
from ..schemas import LoginBody
from ..services.seed import seed_skills_for

router = APIRouter()


@router.post("/auth/dev-login")
async def dev_login(body: LoginBody) -> dict:
    # Dev-only: trust the username and mint a token. Replace with real auth.
    user_id = body.username.strip()
    if not user_id:
        raise HTTPException(400, "username required")
    await seed_skills_for(user_id)  # first login: give them the starter skills
    return {"token": mint_token(user_id), "user_id": user_id}


@router.get("/me")
def me(user_id: str = Depends(current_user)) -> dict:
    return {"user_id": user_id}
