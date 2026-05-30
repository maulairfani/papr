"""Paper upload (logic in services.papers)."""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, UploadFile

from ..core.auth import current_user
from ..services import papers as papers_service

router = APIRouter()


@router.post("/papers/upload")
async def upload_paper(
    file: UploadFile = File(...), user_id: str = Depends(current_user)
) -> dict:
    raw = await file.read()
    return await papers_service.save_upload(user_id, file.filename, raw)
