"""Runtime configuration, sourced from environment variables."""
from __future__ import annotations

import os

# Model in `provider:model` format. Defaults to an OpenAI model; override via PAPR_MODEL.
PAPR_MODEL = os.environ.get("PAPR_MODEL", "openai:gpt-5.4-nano")
