import { useState } from "react";
import { streamChat } from "../api";

interface Message {
  role: "user" | "assistant";
  text: string;
}

export default function Chat({ onFilesMaybeChanged }: { onFilesMaybeChanged: () => void }) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [threadId, setThreadId] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // Append text to the last (assistant) message as tokens stream in.
  const appendToLast = (text: string) =>
    setMessages((prev) => {
      const next = [...prev];
      next[next.length - 1] = { role: "assistant", text: next[next.length - 1].text + text };
      return next;
    });

  async function send() {
    const text = input.trim();
    if (!text || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text }, { role: "assistant", text: "" }]);
    setBusy(true);
    const tid = await streamChat(text, threadId, {
      onToken: appendToLast,
      onError: (err) => appendToLast(`\n⚠️ ${err}`),
    });
    setThreadId(tid);
    setBusy(false);
    onFilesMaybeChanged(); // papr may have written notes/briefs
  }

  return (
    <section className="chat">
      <div className="messages">
        {messages.length === 0 && (
          <p className="muted center">Ask papr about a paper, or tell it to take a note.</p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`msg ${m.role}`}>
            <span className="role">{m.role === "user" ? "you" : "papr"}</span>
            <div className="bubble">{m.text || (busy && i === messages.length - 1 ? "…" : "")}</div>
          </div>
        ))}
      </div>
      <form
        className="composer"
        onSubmit={(e) => {
          e.preventDefault();
          void send();
        }}
      >
        <input
          placeholder="Message papr…"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          disabled={busy}
        />
        <button type="submit" disabled={busy || !input.trim()}>
          Send
        </button>
      </form>
    </section>
  );
}
