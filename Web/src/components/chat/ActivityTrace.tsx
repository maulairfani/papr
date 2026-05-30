import type { Activity } from "./types";

function CheckIcon() {
  return (
    <svg
      viewBox="0 0 16 16"
      aria-hidden
      className="mt-0.5 h-3.5 w-3.5 shrink-0 text-emerald-400"
      fill="currentColor"
    >
      <path d="M6.5 11.5 3 8l1-1 2.5 2.5L12 4l1 1z" />
    </svg>
  );
}

/** The "what papr is doing" trace shown above an assistant reply. */
export function ActivityTrace({ items }: { items: Activity[] }) {
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
                <div className="truncate font-mono text-[11px] text-muted">
                  {JSON.stringify(a.args)}
                </div>
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
              <pre className="mt-1 ml-5 whitespace-pre-wrap break-words font-mono text-[11px] text-muted">
                {a.result}
              </pre>
            </details>
          );
        }
        return (
          <div key={i} className="space-y-1">
            {a.items.map((t, j) => (
              <div key={j} className="flex items-start gap-2">
                <span className={`mt-0.5 ${t.done ? "text-emerald-400" : "text-muted"}`}>
                  {t.done ? "✓" : "○"}
                </span>
                <span className={t.done ? "text-muted line-through" : "text-ink"}>{t.text}</span>
              </div>
            ))}
          </div>
        );
      })}
    </div>
  );
}
