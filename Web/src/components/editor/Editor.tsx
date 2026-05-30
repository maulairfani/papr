import { useState, type MouseEvent } from "react";
import { MarkdownView } from "./MarkdownView";
import { PdfViewer } from "./PdfViewer";
import { RichTextEditor } from "./RichTextEditor";

type View = "pdf" | "markdown" | "richtext";
type OpenFile = { path: string; name: string; view: View };

// Mock open files — one per editor capability. Later these are opened from the
// Filesystem, with the view chosen by extension (.pdf -> pdf, .md -> markdown/edit).
const FILES: OpenFile[] = [
  { path: "/papers/attention-is-all-you-need/notes.md", name: "notes.md", view: "richtext" },
  { path: "/briefs/ai-safety/2026-05-30.md", name: "2026-05-30.md", view: "markdown" },
  { path: "/papers/attention-is-all-you-need/1706.03762.pdf", name: "1706.03762.pdf", view: "pdf" },
];

const MOCK_MD = `# AI Safety — 2026-05-30

New work on alignment, interpretability, and oversight. One line per paper.

- **Keeping an Eye on AI** (arXiv:2605.16278) — a framework for effective human oversight.
- **SafeInfer** (arXiv:2406.12274) — decoding-time, context-adaptive safety alignment.

> A brief is a morning read, not an exhaustive dump.

| Paper | Why it matters |
| --- | --- |
| WildGuard | open moderation tooling |
`;

export function Editor() {
  const [openPaths, setOpenPaths] = useState(FILES.map((f) => f.path));
  const [activePath, setActivePath] = useState(FILES[0]!.path);

  const tabs = FILES.filter((f) => openPaths.includes(f.path));
  const active = FILES.find((f) => f.path === activePath) ?? null;

  function close(path: string, e: MouseEvent) {
    e.stopPropagation();
    const remaining = openPaths.filter((p) => p !== path);
    setOpenPaths(remaining);
    if (path === activePath) setActivePath(remaining[remaining.length - 1] ?? "");
  }

  return (
    <div className="flex flex-1 flex-col bg-canvas">
      {/* Editor tabs (open files), VS Code-style. */}
      <div className="flex items-stretch overflow-x-auto border-b border-border bg-surface">
        {tabs.map((f) => {
          const isActive = f.path === activePath;
          return (
            <div
              key={f.path}
              onClick={() => setActivePath(f.path)}
              className={[
                "group flex cursor-pointer items-center gap-2 whitespace-nowrap border-t-2 border-r border-border px-3 py-1.5 text-xs",
                isActive
                  ? "border-t-brand bg-canvas text-ink"
                  : "border-t-transparent bg-surface text-muted hover:bg-white/5",
              ].join(" ")}
            >
              <span>{f.name}</span>
              <button
                type="button"
                onClick={(e) => close(f.path, e)}
                aria-label={`Close ${f.name}`}
                className="rounded p-0.5 text-muted opacity-0 hover:bg-white/10 hover:text-ink group-hover:opacity-100"
              >
                <svg viewBox="0 0 16 16" className="h-3 w-3" fill="currentColor">
                  <path d="M8 6.6 12.3 2.3l1.4 1.4L9.4 8l4.3 4.3-1.4 1.4L8 9.4l-4.3 4.3-1.4-1.4L6.6 8 2.3 3.7l1.4-1.4z" />
                </svg>
              </button>
            </div>
          );
        })}
      </div>

      {/* Content — dispatched by the active file's view. */}
      <div className="min-h-0 flex-1">
        {!active && (
          <div className="grid h-full place-items-center text-sm text-muted">No file open</div>
        )}
        {active?.view === "pdf" && <PdfViewer src="/sample.pdf" />}
        {active?.view === "markdown" && <MarkdownView source={MOCK_MD} />}
        {active?.view === "richtext" && <RichTextEditor />}
      </div>
    </div>
  );
}
