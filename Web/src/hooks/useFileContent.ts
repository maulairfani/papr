import { useEffect, useState } from "react";
import { readFile } from "../api/files";

/** Loads a text file's content for the given path (null = nothing to load). */
export function useFileContent(path: string | null) {
  const [content, setContent] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!path) {
      setContent(null);
      return;
    }
    let cancelled = false;
    setLoading(true);
    setError(null);
    readFile(path)
      .then((r) => {
        if (!cancelled) setContent(r.content);
      })
      .catch((e: unknown) => {
        if (!cancelled) setError(String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [path]);

  return { content, loading, error };
}
