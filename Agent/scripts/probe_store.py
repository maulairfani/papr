"""Throwaway probe: reveal how deepagents StoreBackend lays out files in the Store.

The FastAPI file browser will read the Store directly, so it needs to know the
namespace tuples and key format deepagents uses. Run from Agent/:
    .venv\\Scripts\\python.exe scripts\\probe_store.py
"""
from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from langgraph.store.memory import InMemoryStore  # noqa: E402

from papr.agent import build_agent  # noqa: E402

store = InMemoryStore()
agent = build_agent(store=store)

agent.invoke(
    {"messages": [{"role": "user", "content": "Create a note at /notes/intro.md with content: Hello from probe."}]},
    context={"user_id": "alice"},
)

print("=== namespaces ===")
for ns in store.list_namespaces():
    print(ns)

print("\n=== items ===")
for ns in store.list_namespaces():
    for item in store.search(ns):
        print(ns, "| key:", item.key, "| value:", repr(item.value)[:300])
