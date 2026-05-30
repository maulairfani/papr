"""File browser: list and read the user's files (logic in services.files)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from ..core.auth import current_user
from ..services import files as files_service

router = APIRouter()


@router.get("/files")
async def list_files(user_id: str = Depends(current_user)) -> dict:
    return {"files": await files_service.list_files(user_id)}


@router.get("/files/content")
async def file_content(path: str = Query(...), user_id: str = Depends(current_user)) -> dict:
    return {"path": path, "content": await files_service.read_file(user_id, path)}
