// Shared workspace state: which files are open and which is active. Lets the
// Filesystem (opens files) and the Editor (shows them) talk without prop drilling.
import { createContext, useContext, useState, type ReactNode } from "react";

export type Workspace = {
  openPaths: string[];
  activePath: string | null;
  open: (path: string) => void;
  close: (path: string) => void;
  setActive: (path: string) => void;
};

const WorkspaceCtx = createContext<Workspace | null>(null);

export function WorkspaceProvider({ children }: { children: ReactNode }) {
  const [openPaths, setOpenPaths] = useState<string[]>([]);
  const [activePath, setActivePath] = useState<string | null>(null);

  function open(path: string) {
    setOpenPaths((p) => (p.includes(path) ? p : [...p, path]));
    setActivePath(path);
  }

  function close(path: string) {
    setOpenPaths((prev) => prev.filter((x) => x !== path));
    setActivePath((a) => {
      if (a !== path) return a;
      const remaining = openPaths.filter((x) => x !== path);
      return remaining[remaining.length - 1] ?? null;
    });
  }

  return (
    <WorkspaceCtx.Provider value={{ openPaths, activePath, open, close, setActive: setActivePath }}>
      {children}
    </WorkspaceCtx.Provider>
  );
}

export function useWorkspace(): Workspace {
  const ctx = useContext(WorkspaceCtx);
  if (!ctx) throw new Error("useWorkspace must be used within <WorkspaceProvider>");
  return ctx;
}
