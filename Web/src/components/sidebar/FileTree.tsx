import { useState } from "react";
import type { FsNode } from "../../api/types";
import { useWorkspace } from "../../workspace/WorkspaceContext";

function Triangle({ open }: { open: boolean }) {
  return (
    <svg
      viewBox="0 0 24 24"
      aria-hidden
      className={`h-3.5 w-3.5 shrink-0 text-muted transition-transform ${open ? "rotate-90" : ""}`}
      fill="currentColor"
    >
      <path d="M9 6l6 6-6 6z" />
    </svg>
  );
}

function FolderIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden className="h-4 w-4 shrink-0 text-muted" fill="currentColor">
      <path d="M10 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2h-8l-2-2z" />
    </svg>
  );
}

function FileIcon() {
  return (
    <svg viewBox="0 0 24 24" aria-hidden className="h-4 w-4 shrink-0 text-muted" fill="currentColor">
      <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V8l-6-6zm4 18H6V4h7v5h5v11z" />
    </svg>
  );
}

function TreeItem({ node, depth }: { node: FsNode; depth: number }) {
  const ws = useWorkspace();
  const isFolder = node.type === "folder";
  const [open, setOpen] = useState(depth === 0); // top-level folders open
  const isActive = ws.activePath === node.path;

  return (
    <li>
      <div
        onClick={() => (isFolder ? setOpen((o) => !o) : ws.open(node.path))}
        style={{ paddingLeft: `${depth * 14 + 8}px` }}
        className={[
          "flex cursor-pointer select-none items-center gap-1.5 py-1 pr-2 text-sm",
          isActive ? "bg-brand/25 text-ink" : "text-ink/80 hover:bg-white/5",
        ].join(" ")}
      >
        {isFolder ? <Triangle open={open} /> : <span className="w-3.5 shrink-0" />}
        {isFolder ? <FolderIcon /> : <FileIcon />}
        <span className="truncate">{node.name}</span>
      </div>

      {isFolder && open && node.children && (
        <ul>
          {node.children.map((child) => (
            <TreeItem key={child.path} node={child} depth={depth + 1} />
          ))}
        </ul>
      )}
    </li>
  );
}

/** Recursive file tree, VS Code-explorer style. Clicking a file opens it. */
export function FileTree({ nodes }: { nodes: FsNode[] }) {
  return (
    <ul>
      {nodes.map((node) => (
        <TreeItem key={node.path} node={node} depth={0} />
      ))}
    </ul>
  );
}
