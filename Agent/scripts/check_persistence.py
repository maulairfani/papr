"""Step 1 verification: per-user file persistence + isolation.

Builds a papr agent backed by an in-memory store and checks that:
  1. a note written by one user persists and is readable in a later conversation, and
  2. another user cannot see it (namespace isolation).

Run from the Agent/ directory (needs OPENAI_API_KEY, loaded from Agent/.env):
    .venv\\Scripts\\python.exe scripts\\check_persistence.py
"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

# Load Agent/.env so OPENAI_API_KEY is set before the model is constructed.
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from langgraph.store.memory import InMemoryStore  # noqa: E402

from papr.agent import build_agent  # noqa: E402

MARKER = "Alice was here"


def ask(agent, user_id: str, text: str) -> str:
    """Run one single-turn conversation as `user_id`; return the final reply."""
    result = agent.invoke(
        {"messages": [{"role": "user", "content": text}]},
        context={"user_id": user_id},
    )
    return str(result["messages"][-1].content)


def main() -> int:
    # One shared store = the per-user backing store; separate invokes simulate
    # separate conversations (threads).
    agent = build_agent(store=InMemoryStore())

    # 1. Alice writes a note.
    ask(agent, "alice", f"Create a note at /notes/intro.md whose content is: {MARKER}. Then say done.")

    # 2. Alice, in a new conversation, reads it back.
    alice_view = ask(agent, "alice", "Read /notes/intro.md and show its contents verbatim.")

    # 3. Bob lists his notes — must not see Alice's.
    bob_view = ask(agent, "bob", "List everything under /notes/ with contents. If there are none, reply exactly: NO NOTES.")

    persisted = MARKER in alice_view
    isolated = MARKER not in bob_view

    print("--- Alice (second conversation) ---")
    print(alice_view, "\n")
    print("--- Bob ---")
    print(bob_view, "\n")
    print(f"persistence across conversations: {'PASS' if persisted else 'FAIL'}")
    print(f"per-user isolation:               {'PASS' if isolated else 'FAIL'}")
    return 0 if (persisted and isolated) else 1


if __name__ == "__main__":
    raise SystemExit(main())
