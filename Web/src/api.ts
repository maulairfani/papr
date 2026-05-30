// Thin client for the papr BFF. The token (carrying user_id) lives in
// localStorage and is sent as a Bearer header on every authenticated call.
const BASE: string = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

const TOKEN_KEY = "papr_token";

export const getToken = (): string | null => localStorage.getItem(TOKEN_KEY);
export const setToken = (t: string): void => localStorage.setItem(TOKEN_KEY, t);
export const clearToken = (): void => localStorage.removeItem(TOKEN_KEY);

function authHeaders(): Record<string, string> {
  const t = getToken();
  return t ? { Authorization: `Bearer ${t}` } : {};
}

export async function devLogin(username: string): Promise<{ token: string; user_id: string }> {
  const r = await fetch(`${BASE}/auth/dev-login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username }),
  });
  if (!r.ok) throw new Error(`login failed (${r.status})`);
  return r.json();
}

export interface FileEntry {
  path: string;
  modified_at: string | null;
}

export async function listFiles(): Promise<FileEntry[]> {
  const r = await fetch(`${BASE}/files`, { headers: authHeaders() });
  if (!r.ok) throw new Error(`files failed (${r.status})`);
  return (await r.json()).files as FileEntry[];
}

export async function getFileContent(path: string): Promise<string> {
  const r = await fetch(`${BASE}/files/content?path=${encodeURIComponent(path)}`, {
    headers: authHeaders(),
  });
  if (!r.ok) throw new Error(`content failed (${r.status})`);
  return (await r.json()).content as string;
}

export async function uploadPaper(file: File): Promise<{ path: string }> {
  const form = new FormData();
  form.append("file", file);
  // Don't set Content-Type — the browser adds the multipart boundary.
  const r = await fetch(`${BASE}/papers/upload`, {
    method: "POST",
    headers: authHeaders(),
    body: form,
  });
  if (!r.ok) throw new Error(`upload failed (${r.status})`);
  return r.json();
}

export interface SkillEntry {
  name: string;
  path: string;
}

// Skills are files at /skills/<name>/SKILL.md; derive the list from /files.
export async function listSkills(): Promise<SkillEntry[]> {
  const files = await listFiles();
  return files
    .filter((f) => f.path.startsWith("/skills/") && f.path.endsWith("/SKILL.md"))
    .map((f) => ({ name: f.path.split("/")[2], path: f.path }));
}

export async function saveSkill(name: string, content: string): Promise<void> {
  const r = await fetch(`${BASE}/skills/save`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ name, content }),
  });
  if (!r.ok) throw new Error(`save skill failed (${r.status})`);
}

// --- topics & daily brief --------------------------------------------------

export interface Topic {
  slug: string;
  name: string;
  query: string;
  modified_at: string | null;
}

export async function listTopics(): Promise<Topic[]> {
  const r = await fetch(`${BASE}/topics`, { headers: authHeaders() });
  if (!r.ok) throw new Error(`topics failed (${r.status})`);
  return (await r.json()).topics as Topic[];
}

export async function addTopic(name: string, query?: string): Promise<void> {
  const r = await fetch(`${BASE}/topics`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ name, query: query || null }),
  });
  if (!r.ok) throw new Error(`add topic failed (${r.status})`);
}

export async function deleteTopic(slug: string): Promise<void> {
  const r = await fetch(`${BASE}/topics/${encodeURIComponent(slug)}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!r.ok) throw new Error(`delete topic failed (${r.status})`);
}

export interface Subscription {
  subscribed: boolean;
  hour?: number;
  minute?: number;
  cron_id?: string;
}

export async function getSubscription(): Promise<Subscription> {
  const r = await fetch(`${BASE}/brief/subscription`, { headers: authHeaders() });
  if (!r.ok) throw new Error(`subscription failed (${r.status})`);
  return r.json();
}

export async function subscribeBrief(hour: number, minute: number): Promise<Subscription> {
  const r = await fetch(`${BASE}/brief/subscribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ hour, minute }),
  });
  if (!r.ok) throw new Error(`subscribe failed (${r.status})`);
  return r.json();
}

export async function unsubscribeBrief(): Promise<void> {
  const r = await fetch(`${BASE}/brief/unsubscribe`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!r.ok) throw new Error(`unsubscribe failed (${r.status})`);
}

export async function runBriefNow(): Promise<{ run_id: string; thread_id: string }> {
  const r = await fetch(`${BASE}/brief/run-now`, {
    method: "POST",
    headers: authHeaders(),
  });
  if (!r.ok) throw new Error(`run-now failed (${r.status})`);
  return r.json();
}

export interface BriefEntry {
  path: string;
  date: string;
  modified_at: string | null;
}

// Briefs are files at /briefs/<date>.md; derive the list from /files.
export async function listBriefs(): Promise<BriefEntry[]> {
  const files = await listFiles();
  return files
    .filter((f) => f.path.startsWith("/briefs/") && f.path.endsWith(".md"))
    .map((f) => ({
      path: f.path,
      date: f.path.replace("/briefs/", "").replace(/\.md$/, ""),
      modified_at: f.modified_at,
    }))
    .sort((a, b) => b.date.localeCompare(a.date));
}

interface StreamCallbacks {
  onToken: (text: string) => void;
  onError: (error: string) => void;
}

// Stream a chat turn, parsing the BFF's SSE frames. Returns the (possibly new)
// thread id so the caller can continue the conversation.
export async function streamChat(
  message: string,
  threadId: string | null,
  { onToken, onError }: StreamCallbacks,
): Promise<string | null> {
  const r = await fetch(`${BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ message, thread_id: threadId }),
  });
  if (!r.ok || !r.body) {
    onError(`chat failed (${r.status})`);
    return threadId;
  }

  const reader = r.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let thread = threadId;

  // SSE frames are separated by a blank line; each has a `data:` payload.
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    let sep: number;
    while ((sep = buffer.indexOf("\n\n")) >= 0) {
      const frame = buffer.slice(0, sep);
      buffer = buffer.slice(sep + 2);
      const dataLine = frame.split("\n").find((l) => l.startsWith("data:"));
      if (!dataLine) continue;
      const payload = JSON.parse(dataLine.slice(5).trim());
      if (payload.type === "thread") thread = payload.thread_id;
      else if (payload.type === "token") onToken(payload.text);
      else if (payload.type === "error") onError(payload.error);
    }
  }
  return thread;
}
