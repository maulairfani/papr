"""File routes — one generic CRUD surface over the per-user store.

Covers papers, skills, briefs and memory: they are all just files. Thin adapters
over services/files.py.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, File, Query, UploadFile
from fastapi.responses import Response
from pydantic import BaseModel

from ..core.auth import current_user, user_from_token
from ..services import files as files_service

router = APIRouter(tags=["files"])


@router.get("/files")
async def list_tree(user_id: str = Depends(current_user)) -> dict:
    return {"tree": await files_service.tree(user_id)}


@router.get("/files/content")
async def read_content(path: str = Query(...), user_id: str = Depends(current_user)) -> dict:
    return await files_service.read(user_id, path)


class WriteBody(BaseModel):
    path: str
    content: str
    encoding: str = "utf-8"


@router.put("/files/content")
async def write_content(body: WriteBody, user_id: str = Depends(current_user)) -> dict:
    return await files_service.write(user_id, body.path, body.content, body.encoding)


@router.get("/files/raw")
async def read_raw(path: str = Query(...), token: str = Query(...)) -> Response:
    # Auth via query token: an <iframe> PDF src can't send an Authorization header.
    user_id = user_from_token(token)
    data, media = await files_service.raw_bytes(user_id, path)
    return Response(content=data, media_type=media)


@router.post("/files/upload")
async def upload(file: UploadFile = File(...), user_id: str = Depends(current_user)) -> dict:
    data = await file.read()
    return await files_service.upload(user_id, file.filename or "upload", data)


@router.delete("/files")
async def delete(path: str = Query(...), user_id: str = Depends(current_user)) -> dict:
    await files_service.delete(user_id, path)
    return {"deleted": path}
