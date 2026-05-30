"""Paper service: encode an uploaded file and store it under /papers/."""
from __future__ import annotations

import base64
import os

from . import store

TEXT_EXTENSIONS = {".md", ".markdown", ".txt", ".rst", ".csv", ".json"}


async def save_upload(user_id: str, filename: str | None, raw: bytes) -> dict:
    # Keep only the basename; the store key is the path within /papers/.
    name = (filename or "upload").replace("\\", "/").split("/")[-1]
    ext = os.path.splitext(name)[1].lower()

    # utf-8 for text, base64 for binary (PDFs etc.) so the agent's read_file can
    # decode it as a multimodal file.
    if ext in TEXT_EXTENSIONS:
        try:
            content, encoding = raw.decode("utf-8"), "utf-8"
        except UnicodeDecodeError:
            content, encoding = base64.b64encode(raw).decode("ascii"), "base64"
    else:
        content, encoding = base64.b64encode(raw).decode("ascii"), "base64"

    await store.put(user_id, "papers", f"/{name}", store.file_value(content, encoding))
    return {"path": f"/papers/{name}", "encoding": encoding, "bytes": len(raw)}
