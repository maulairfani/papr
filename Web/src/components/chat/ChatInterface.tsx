import { useState } from "react";

// Shapes mirror the agent's stream so wiring later is a 1:1 map:
//   updates(model).tool_calls -> tool_call ; updates(tools) -> tool_result ;
//   updates(TodoListMiddleware).todos -> todos ; messages -> assistant text.
type Activity =
  | { kind: "tool_call"; tool: string; args: Record<string, unknown> }
  | { kind: "tool_result"; tool: string; result: string }
  | { kind: "todos"; items: { text: string; done: boolean }[] };

type Turn =
  | { role: "user"; text: string }
  | { role: "assistant"; activity: Activity[]; text: string };

const THREAD: Turn[] = [
  { role: "user", text: "Find the Transformer paper on arXiv." },
  {
    role: "assistant",
    activity: [
      {
        kind: "tool_call",
        tool: "search_arxiv",
        args: { query: "attention is all you need", max_results: 5 },
      },
      {
        kind: "tool_result",
        tool: "search_arxiv",
        result:
          "5 results.\nTop: Attention Is All You Need — arXiv:1706.03762\nAuthors: Vaswani et al.\nThe paper that introduced the Transformer.",
      },
    ],
    text: "The paper is Attention Is All You Need (arXiv:1706.03762). Want me to download it to /papers/?",
  },
];

function CheckIcon() {
  return (
    <svg viewBox="0 0 16 16" aria-hidden className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-400" fill="currentColor">
      <path d="M6.5 11.5 3 8l1-1 2.5 2.5L12 4l1 1z" />
    </svg>
  );
}

function ActivityTrace({ items }: { items: Activity[] }) {
  return (
    <div className="mb-2 space-y-1.5 rounded-lg border border-border bg-surface/60 p-2.5 text-xs">
      {items.map((a, i) => {
        if (a.kind === "tool_call") {
          return (
            <div key={i} className="flex items-start gap-2">
              <span className="mt-1.5 h-1.5 w-1.5 shrink-0 rounded-full bg-amber-400" />
              <div className="min-w-0">
                <span className="text-muted">Calling </span>
                <code className="text-ink">{a.tool}</code>
                <div className="truncate font-mono text-[11px] text-muted">{JSON.stringify(a.args)}</div>
              </div>
            </div>
          );
        }
        if (a.kind === "tool_result") {
          return (
            <details key={i} className="group">
              <summary className="flex cursor-pointer list-none items-start gap-2">
                <CheckIcon />
                <span className="text-muted">
                  <code className="text-ink">{a.tool}</code> finished
                </span>
              </summary>
              <pre className="mt-1 ml-5 whitespace-pre-wrap font-mono text-[11px] text-muted">{a.result}</pre>
            </details>
          );
        }
        return (
          <div key={i} className="space-y-1">
            {a.items.map((t, j) => (
              <div key={j} className="flex items-start gap-2">
                <span className={`mt-0.5 ${t.done ? "text-emerald-400" : "text-muted"}`}>{t.done ? "✓" : "○"}</span>
                <span className={t.done ? "text-muted line-through" : "text-ink"}>{t.text}</span>
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
}

export function ChatInterface() {
  const [draft, setDraft] = useState("");

  return (
    <section className="flex flex-1 flex-col border-l border-border bg-surface">
      <header className="border-b border-border px-4 py-3 text-sm font-semibold text-ink">Chat</header>

      <div className="min-h-0 flex-1 space-y-4 overflow-auto px-4 py-4">
        {THREAD.map((turn, i) =>
          turn.role === "user" ? (
            <div key={i} className="flex justify-end">
              <div className="max-w-[85%] rounded-2xl bg-brand px-3.5 py-2 text-sm text-brand-fg">{turn.text}</div>
            </div>
          ) : (
            <div key={i} className="max-w-[92%]">
              {turn.activity.length > 0 && <ActivityTrace items={turn.activity} />}
              <div className="rounded-2xl border border-border bg-canvas px-3.5 py-2 text-sm leading-relaxed text-ink">
                {turn.text}
              </div>
            </div>
          ),
        )}
      </div>

      <form className="border-t border-border p-3" onSubmit={(e) => e.preventDefault()}>
        <div className="flex items-end gap-2 rounded-xl border border-border bg-canvas p-2">
          <textarea
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            rows={1}
            placeholder="Message papr…"
            className="max-h-40 flex-1 resize-none bg-transparent px-2 py-1 text-sm text-ink outline-none placeholder:text-muted"
          />
          <button
            type="submit"
            className="rounded-lg bg-brand px-3 py-1.5 text-sm font-medium text-brand-fg disabled:opacity-50"
            disabled={!draft.trim()}
          >
            Send
          </button>
        </div>
      </form>
    </section>
  );
}
