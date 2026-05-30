import { useEffect, useState } from "react";
import {
  listTopics,
  addTopic,
  deleteTopic,
  getSubscription,
  subscribeBrief,
  unsubscribeBrief,
  runBriefNow,
  listBriefs,
  getFileContent,
  type Topic,
  type Subscription,
  type BriefEntry,
} from "../api";

const pad = (n: number) => String(n).padStart(2, "0");

// Topics the user follows + the daily-brief schedule, plus the briefs papr writes.
export default function Topics() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [name, setName] = useState("");
  const [query, setQuery] = useState("");

  const [sub, setSub] = useState<Subscription>({ subscribed: false });
  const [hour, setHour] = useState(6);
  const [minute, setMinute] = useState(0);

  const [briefs, setBriefs] = useState<BriefEntry[]>([]);
  const [openBrief, setOpenBrief] = useState<string | null>(null);
  const [briefContent, setBriefContent] = useState("");
  const [status, setStatus] = useState("");
  const [busy, setBusy] = useState(false);

  const refreshTopics = () => listTopics().then(setTopics).catch(() => setTopics([]));
  const refreshBriefs = () => listBriefs().then(setBriefs).catch(() => setBriefs([]));
  const refreshSub = () =>
    getSubscription()
      .then((s) => {
        setSub(s);
        if (s.hour != null) setHour(s.hour);
        if (s.minute != null) setMinute(s.minute);
      })
      .catch(() => {});

  useEffect(() => {
    refreshTopics();
    refreshSub();
    refreshBriefs();
  }, []);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim()) return;
    setBusy(true);
    try {
      await addTopic(name.trim(), query.trim() || undefined);
      setName("");
      setQuery("");
      await refreshTopics();
    } finally {
      setBusy(false);
    }
  }

  async function remove(slug: string) {
    await deleteTopic(slug);
    refreshTopics();
  }

  async function toggleSub() {
    setBusy(true);
    try {
      if (sub.subscribed) await unsubscribeBrief();
      else await subscribeBrief(hour, minute);
      await refreshSub();
    } finally {
      setBusy(false);
    }
  }

  async function openOne(b: BriefEntry) {
    setOpenBrief(b.path);
    try {
      setBriefContent(await getFileContent(b.path));
    } catch {
      setBriefContent("(could not load brief)");
    }
  }

  async function generateNow() {
    if (!topics.length) {
      setStatus("Add a topic first — the brief follows your topics.");
      return;
    }
    setStatus("Generating… this can take ~30–60s.");
    // Baseline so we can tell when a brief is new OR an existing day was rewritten.
    const baseline = new Map(briefs.map((b) => [b.path, b.modified_at]));
    await runBriefNow();
    let tries = 0;
    const timer = setInterval(async () => {
      tries += 1;
      const latest = await listBriefs();
      const changed = latest.some((b) => baseline.get(b.path) !== b.modified_at);
      if (changed || tries > 40) {
        clearInterval(timer);
        setBriefs(latest);
        if (changed) {
          setStatus("Brief ready ✓");
          if (latest[0]) void openOne(latest[0]);
        } else {
          setStatus("Still working — refresh in a moment.");
        }
      }
    }, 3000);
  }

  return (
    <div className="topics-page">
      <aside className="topics-side">
        <div className="files-head">
          <h2>Topics</h2>
        </div>
        <form className="topic-add" onSubmit={add}>
          <input
            placeholder="Topic name (e.g. Diffusion models)"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />
          <input
            placeholder="arXiv search (optional — defaults to name)"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <button disabled={busy || !name.trim()}>Follow topic</button>
        </form>

        <ul className="file-list">
          {topics.map((t) => (
            <li key={t.slug} className="topic-row">
              <div className="topic-meta">
                <span className="topic-name">{t.name}</span>
                <span className="muted topic-query">{t.query}</span>
              </div>
              <button className="upload" onClick={() => void remove(t.slug)}>
                Remove
              </button>
            </li>
          ))}
          {!topics.length && <li className="muted">No topics yet. Follow one above.</li>}
        </ul>

        <div className="brief-sub">
          <h2>Daily brief</h2>
          <div className="muted">
            {sub.subscribed
              ? `On — daily at ${pad(sub.hour ?? hour)}:${pad(sub.minute ?? minute)} UTC`
              : "Off — papr won't schedule a brief."}
          </div>
          <div className="time-row">
            <label>
              UTC&nbsp;
              <input
                type="number"
                min={0}
                max={23}
                value={hour}
                onChange={(e) => setHour(Number(e.target.value))}
              />
            </label>
            <span>:</span>
            <input
              type="number"
              min={0}
              max={59}
              value={minute}
              onChange={(e) => setMinute(Number(e.target.value))}
            />
          </div>
          <div className="skills-actions">
            <button onClick={() => void toggleSub()} disabled={busy}>
              {sub.subscribed ? "Unsubscribe" : "Subscribe"}
            </button>
            <button className="ghost" onClick={() => void generateNow()} disabled={busy}>
              Generate now
            </button>
          </div>
          <span className="muted">{status}</span>
        </div>
      </aside>

      <section className="briefs-pane">
        <div className="files-head">
          <h2>Briefs</h2>
        </div>
        <ul className="file-list briefs-list">
          {briefs.map((b) => (
            <li key={b.path}>
              <button
                className={openBrief === b.path ? "file active" : "file"}
                onClick={() => void openOne(b)}
              >
                {b.date}
              </button>
            </li>
          ))}
          {!briefs.length && <li className="muted">No briefs yet. Try “Generate now”.</li>}
        </ul>
        {openBrief && (
          <div className="viewer">
            <div className="viewer-path">{openBrief}</div>
            <pre>{briefContent}</pre>
          </div>
        )}
      </section>
    </div>
  );
}
