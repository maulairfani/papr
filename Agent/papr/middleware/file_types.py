"""Keep the /papers/ workspace to Markdown and PDF files only.

papr's filesystem write tools (`write_file`, `edit_file`) flow through every
middleware's `wrap_tool_call`. This one inspects writes targeting the /papers/
workspace and rejects any whose path isn't `.md` or `.pdf`, returning a tool
error so the model self-corrects. Everything else is untouched: the other routes
(/topics/ /skills/ /briefs/, all Markdown) and papr's ephemeral scratch (which
lives in the StateBackend, not /papers/) are never policed.
"""
from __future__ import annotations

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import ToolMessage

_WRITE_TOOLS = ("write_file", "edit_file")
_ALLOWED_EXT = (".md", ".pdf")
_WORKSPACE = "/papers/"


def offending_path(tool_name: str, args: dict | None) -> str | None:
    """Return the file_path to reject, or None if the write is allowed.

    A write is rejected only when it targets the /papers/ workspace with a path
    that is neither `.md` nor `.pdf`.
    """
    if tool_name not in _WRITE_TOOLS:
        return None
    file_path = ((args or {}).get("file_path") or "").strip()
    if not file_path.startswith(_WORKSPACE):
        return None
    if file_path.lower().endswith(_ALLOWED_EXT):
        return None
    return file_path


def _rejection(file_path: str, tool_call_id: str) -> ToolMessage:
    return ToolMessage(
        content=(
            f"Rejected write to '{file_path}'. The /papers/ workspace allows only "
            ".md and .pdf files — save notes as Markdown (.md). Organize freely with "
            "subfolders, but keep file types to .md or .pdf."
        ),
        tool_call_id=tool_call_id,
        status="error",
    )


class PapersFileTypeMiddleware(AgentMiddleware):
    """Reject non-.md/.pdf writes into the /papers/ workspace."""

    name = "PapersFileTypeMiddleware"

    def wrap_tool_call(self, request, handler):
        bad = offending_path(request.tool_call.get("name", ""), request.tool_call.get("args"))
        if bad is not None:
            return _rejection(bad, request.tool_call.get("id", ""))
        return handler(request)

    async def awrap_tool_call(self, request, handler):
        bad = offending_path(request.tool_call.get("name", ""), request.tool_call.get("args"))
        if bad is not None:
            return _rejection(bad, request.tool_call.get("id", ""))
        return await handler(request)
