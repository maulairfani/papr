import type { MouseEvent } from "react";
import { useWorkspace } from "../../workspace/WorkspaceContext";

function basename(path: string): string {
  return path.split("/").pop() || path;
}

/** VS Code-style tab bar of open files. */
export function EditorTabs() {
  const ws = useWorkspace();
  if (ws.openPaths.length === 0) return null;

  return (
    <div className="flex items-stretch overflow-x-auto border-b border-border bg-surface">
      {ws.openPaths.map((path) => {
        const isActive = path === ws.activePath;
        return (
          <div
            key={path}
            onClick={() => ws.setActive(path)}
            title={path}
            className={[
              "group flex cursor-pointer items-center gap-2 whitespace-nowrap border-t-2 border-r border-border px-3 py-1.5 text-xs",
              isActive
                ? "border-t-brand bg-canvas text-ink"
                : "border-t-transparent bg-surface text-muted hover:bg-white/5",
            ].join(" ")}
          >
            <span>{basename(path)}</span>
            <button
              type="button"
              onClick={(e: MouseEvent) => {
                e.stopPropagation();
                ws.close(path);
              }}
              aria-label={`Close ${basename(path)}`}
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
  );
}
