import { useCallback, useEffect, useState } from "react";
import { fetchTree } from "../api/files";
import type { FsNode } from "../api/types";

/** Loads the file tree from the BFF; `reload()` refetches (e.g. after a write). */
export function useTree() {
  const [tree, setTree] = useState<FsNode[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(() => {
    setLoading(true);
    fetchTree()
      .then((t) => {
        setTree(t);
        setError(null);
      })
      .catch((e: unknown) => setError(String(e)))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => reload(), [reload]);

  return { tree, loading, error, reload };
}
