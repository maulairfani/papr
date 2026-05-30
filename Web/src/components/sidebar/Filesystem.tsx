import { useTree } from "../../hooks/useTree";
import { FileTree } from "./FileTree";

/** Explorer pane: loads the per-user file tree from the BFF and renders it. */
export function Filesystem() {
  const { tree, loading, error } = useTree();

  return (
    <div className="flex-1 overflow-auto py-1.5">
      <div className="px-3 py-1 text-[11px] font-semibold uppercase tracking-wider text-muted">
        Explorer
      </div>
      {loading && <div className="px-3 py-2 text-xs text-muted">Loading…</div>}
      {error && <div className="px-3 py-2 text-xs text-red-400">{error}</div>}
      {!loading && !error && <FileTree nodes={tree} />}
    </div>
  );
}
