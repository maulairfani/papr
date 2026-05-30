import { useState, type KeyboardEvent } from "react";
import { chatStream } from "../../api/chat";
import type { ChatEvent } from "../../api/types";
import { Markdown } from "../Markdown";
import { ActivityTrace } from "./ActivityTrace";
import type { Activity, Turn } from "./types";

type AssistantTurn = Extract<Turn, { role: "assistant" }>;

export function ChatInterface() {
  const [turns, setTurns] = useState<Turn[]>([]);
  const [threadId, setThreadId] = useState<string | undefined>();
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);

  function updateLastAssistant(fn: (t: AssistantTurn) => AssistantTurn) {
    setTurns((prev) => {
      const copy = [...prev];
      const last = copy[copy.length - 1];
      if (last && last.role === "assistant") copy[copy.length - 1] = fn(last);
      return copy;
    });
  }

  function applyEvent(ev: ChatEvent) {
    if (ev.type === "thread") {
      setThreadId(ev.thread_id);
    } else if (ev.type === "token") {
      updateLastAssistant((t) => ({ ...t, text: t.text + ev.text }));
    } else if (ev.type === "activity") {
      const a: Activity =
        ev.kind === "tool_call"
          ? { kind: "tool_call", tool: ev.tool, args: ev.args }
          : ev.kind === "tool_result"
            ? { kind: "tool_result", tool: ev.tool, result: ev.result }
            : { kind: "todos", items: ev.items };
      updateLastAssistant((t) => ({ ...t, activity: [...t.activity, a] }));
    } else if (ev.type === "error") {
      updateLastAssistant((t) => ({ ...t, text: t.text || `⚠ ${ev.detail}` }));
    }
  }

  async function send() {
    const message = draft.trim();
    if (!message || busy) return;
    setDraft("");
    setTurns((t) => [
      ...t,
      { role: "user", text: message },
      { role: "assistant", activity: [], text: "" },
    ]);
    setBusy(true);
    try {
      for await (const ev of chatStream(message, threadId)) applyEvent(ev);
    } catch (e: unknown) {
      updateLastAssistant((t) => ({ ...t, text: t.text || `⚠ ${String(e)}` }));
    } finally {
      setBusy(false);
    }
  }

  function onKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      void send();
    }
  }

  return (
    <section className="flex min-w-0 flex-1 flex-col border-l border-border bg-surface">
      <header className="border-b border-border px-4 py-3 text-sm font-semibold text-ink">Chat</header>

      <div className="min-h-0 flex-1 space-y-4 overflow-auto px-4 py-4">
        {turns.length === 0 && (
          <div className="grid h-full place-items-center text-sm text-muted">
            Ask papr about a paper
          </div>
        )}
        {turns.map((turn, i) =>
          turn.role === "user" ? (
            <div key={i} className="flex justify-end">
              <div className="max-w-[85%] rounded-2xl bg-brand px-3.5 py-2 text-sm text-brand-fg">
                {turn.text}
              </div>
            </div>
          ) : (
            <div key={i} className="max-w-[92%]">
              {turn.activity.length > 0 && <ActivityTrace items={turn.activity} />}
              {turn.text && (
                <div className="rounded-2xl border border-border bg-canvas px-3.5 py-2 text-ink">
                  <Markdown source={turn.text} className="prose-sm max-w-none" />
                </div>
              )}
            </div>
          ),
        )}
      </div>

      <form
        className="border-t border-border p-3"
        onSubmit={(e) => {
          e.preventDefault();
          void send();
        }}
      >
        <div className="flex items-end gap-2 rounded-xl border border-border bg-canvas p-2">
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={onKeyDown}
            rows={1}
            placeholder="Message papr…"
            className="max-h-40 flex-1 resize-none bg-transparent px-2 py-1 text-sm text-ink outline-none placeholder:text-muted"
          />
          <button
            type="submit"
            disabled={!draft.trim() || busy}
            className="rounded-lg bg-brand px-3 py-1.5 text-sm font-medium text-brand-fg disabled:opacity-50"
          >
            {busy ? "…" : "Send"}
          </button>
        </div>
      </form>
    </section>
  );
}
