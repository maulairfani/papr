// Chat endpoint: POST /chat returns an SSE stream; we yield parsed events.
import { API_BASE, ensureToken } from "./client";
import type { ChatEvent } from "./types";

export async function* chatStream(
  message: string,
  threadId?: string,
): AsyncGenerator<ChatEvent> {
  const t = await ensureToken();
  const res = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${t}` },
    body: JSON.stringify({ message, thread_id: threadId }),
  });
  if (!res.body) throw new Error("no chat stream");

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buf = "";
  for (;;) {
    const { done, value } = await reader.read();
    if (done) break;
    buf += decoder.decode(value, { stream: true });
    const frames = buf.split("\n\n");
    buf = frames.pop() ?? "";
    for (const frame of frames) {
      const line = frame.trim();
      if (line.startsWith("data:")) {
        const json = line.slice(5).trim();
        if (json) yield JSON.parse(json) as ChatEvent;
      }
    }
  }
}
