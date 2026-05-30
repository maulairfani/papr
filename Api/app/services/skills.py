"""Skill service: validate a skill name and store its SKILL.md."""
from __future__ import annotations

import re

from . import store
from .errors import Invalid

_SKILL_NAME = re.compile(r"^[a-z0-9-]{1,64}$")


def _validate(name: str) -> None:
    # Agent Skills spec: dir name is lowercase alphanumeric + single hyphens.
    if not _SKILL_NAME.match(name) or name.startswith("-") or name.endswith("-") or "--" in name:
        raise Invalid("skill name must be lowercase letters/digits/hyphens")


async def save_skill(user_id: str, name: str, content: str) -> dict:
    name = name.strip()
    _validate(name)
    await store.put(user_id, "skills", f"/{name}/SKILL.md", store.file_value(content))
    return {"path": f"/skills/{name}/SKILL.md"}
