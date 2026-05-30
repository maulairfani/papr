// Base client + dev auth. Auto-logs-in as "local-dev" once and caches the token;
// swap `login()` for a real flow later. Other api modules build on `authed()`.

export const API_BASE =
  (import.meta.env.VITE_API_URL as string | undefined) ?? "http://localhost:8000";

let token = "";
let tokenPromise: Promise<string> | null = null;

async function login(): Promise<string> {
  const res = await fetch(`${API_BASE}/auth/dev-login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ user_id: "local-dev" }),
  });
  if (!res.ok) throw new Error("dev-login failed");
  token = ((await res.json()) as { token: string }).token;
  return token;
}

/** Resolve once to the cached bearer token, logging in on first use. */
export function ensureToken(): Promise<string> {
  if (!tokenPromise) tokenPromise = login();
  return tokenPromise;
}

/** Sync access to the cached token (for query-string auth, e.g. an <iframe> src).
 * Empty until `ensureToken()` has resolved at least once. */
export function getToken(): string {
  return token;
}

export async function authed(
  path: string,
  opts: { method?: string; headers?: Record<string, string>; body?: BodyInit } = {},
): Promise<Response> {
  const t = await ensureToken();
  return fetch(`${API_BASE}${path}`, {
    method: opts.method,
    headers: { ...(opts.headers ?? {}), Authorization: `Bearer ${t}` },
    body: opts.body,
  });
}
