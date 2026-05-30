import { useState } from "react";

type FsNode = {
  name: string;
  children?: FsNode[];
};

// Static mock of the per-user store. Wiring to the BFF comes later; selecting a
// file will eventually drive the Editor.
const TREE: FsNode[] = [
  {
    name: "papers",
    children: [
      {
        name: "attention-is-all-you-need",
        children: [{ name: "1706.03762.pdf" }, { name: "notes.md" }],
      },
      { name: "diffusion-survey", children: [{ name: "2209.00796.pdf" }] },
    ],
  },
  {
    name: "skills",
    children: [
      { name: "daily-brief", children: [{ name: "SKILL.md" }] },
      { name: "new-brief", children: [{ name: "SKILL.md" }] },
      { name: "eli5", children: [{ name: "SKILL.md" }] },
    ],
  },
  {
    name: "briefs",
    children: [
      { name: "specs", children: [{ name: "ai-safety.md" }, { name: "diffusion-models.md" }] },
      { name: "ai-safety", children: [{ name: "2026-05-30.md" }] },
      { name: "diffusion-models", children: [{ name: "2026-05-30.md" }] },
    ],
  },
  { name: "memories", children: [{ name: "AGENTS.md" }] },
];

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

function TreeItem({
  node,
  depth,
  path,
  selected,
  onSelect,
}: {
  node: FsNode;
  depth: number;
  path: string;
  selected: string | null;
  onSelect: (path: string) => void;
}) {
  const isFolder = !!node.children;
  const [open, setOpen] = useState(depth === 0); // top-level folders open
  const isSelected = selected === path;

  return (
    <li>
      <div
        onClick={() => (isFolder ? setOpen((o) => !o) : onSelect(path))}
        style={{ paddingLeft: `${depth * 14 + 8}px` }}
        className={[
          "flex cursor-pointer select-none items-center gap-1.5 py-1 pr-2 text-sm",
          isSelected ? "bg-brand/25 text-ink" : "text-ink/80 hover:bg-white/5",
        ].join(" ")}
      >
        {isFolder ? <Triangle open={open} /> : <span className="w-3.5 shrink-0" />}
        {isFolder ? <FolderIcon /> : <FileIcon />}
        <span className="truncate">{node.name}</span>
      </div>

      {node.children && open && (
        <ul>
          {node.children.map((child) => (
            <TreeItem
              key={child.name}
              node={child}
              depth={depth + 1}
              path={`${path}/${child.name}`}
              selected={selected}
              onSelect={onSelect}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

/** File tree for the per-user store (papers / skills / briefs / memories),
 * VS Code-explorer style. Mock data for now. */
export function Filesystem() {
  const [selected, setSelected] = useState<string | null>(null);

  return (
    <div className="flex-1 overflow-auto py-1.5">
      <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-muted">
        Explorer
      </div>
      <ul>
        {TREE.map((node) => (
          <TreeItem
            key={node.name}
            node={node}
            depth={0}
            path={`/${node.name}`}
            selected={selected}
            onSelect={setSelected}
          />
        ))}
      </ul>
    </div>
  );
}
