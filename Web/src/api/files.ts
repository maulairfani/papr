// File endpoints (the one generic CRUD surface over the store).
import { API_BASE, authed, getToken } from "./client";
import type { FsNode } from "./types";

export async function fetchTree(): Promise<FsNode[]> {
  const res = await authed("/files");
  if (!res.ok) throw new Error("failed to load files");
  return ((await res.json()) as { tree: FsNode[] }).tree;
}

export type FileContent = { path: string; content: string; encoding: string };

export async function readFile(path: string): Promise<FileContent> {
  const res = await authed(`/files/content?path=${encodeURIComponent(path)}`);
  if (!res.ok) throw new Error(`failed to read ${path}`);
  return await res.json();
}

/** Direct URL for binary content (PDF). Token rides the query so an <iframe> works. */
export function rawUrl(path: string): string {
  return `${API_BASE}/files/raw?path=${encodeURIComponent(path)}&token=${encodeURIComponent(getToken())}`;
}

export async function writeFile(path: string, content: string, encoding = "utf-8"): Promise<void> {
  const res = await authed("/files/content", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ path, content, encoding }),
  });
  if (!res.ok) throw new Error(`failed to write ${path}`);
}
