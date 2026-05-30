import { useEffect, useState } from "react";
import { listSkills, getFileContent, saveSkill, type SkillEntry } from "../api";

const template = (name: string) =>
  `---\nname: ${name}\ndescription: <one line: what it does and when to use it>\n---\n\n# ${name}\n\n<how papr should behave when this skill applies>\n`;

// Lets users create/edit the SKILL.md files that shape how papr explains.
export default function SkillsEditor() {
  const [skills, setSkills] = useState<SkillEntry[]>([]);
  const [name, setName] = useState<string | null>(null);
  const [content, setContent] = useState("");
  const [status, setStatus] = useState("");

  const refresh = () => {
    listSkills().then(setSkills).catch(() => setSkills([]));
  };
  useEffect(() => refresh(), []);

  async function open(s: SkillEntry) {
    setName(s.name);
    setStatus("");
    try {
      setContent(await getFileContent(s.path));
    } catch {
      setContent("(could not load skill)");
    }
  }

  function newSkill() {
    const n = window.prompt("New skill name (lowercase letters, digits, hyphens):")?.trim();
    if (!n) return;
    setName(n);
    setContent(template(n));
    setStatus("");
  }

  async function save() {
    if (!name) return;
    setStatus("Saving…");
    try {
      await saveSkill(name, content);
      setStatus("Saved ✓ — applies on papr's next conversation");
      refresh();
    } catch (e) {
      setStatus(`Error: ${(e as Error).message}`);
    }
  }

  return (
    <div className="skills-editor">
      <aside className="skills-list">
        <div className="files-head">
          <h2>Skills</h2>
          <button className="upload" onClick={newSkill}>
            New
          </button>
        </div>
        <ul className="file-list">
          {skills.map((s) => (
            <li key={s.name}>
              <button
                className={name === s.name ? "file active" : "file"}
                onClick={() => void open(s)}
              >
                {s.name}
              </button>
            </li>
          ))}
        </ul>
      </aside>
      <section className="skills-edit">
        {name ? (
          <>
            <div className="viewer-path">/skills/{name}/SKILL.md</div>
            <textarea
              value={content}
              onChange={(e) => setContent(e.target.value)}
              spellCheck={false}
            />
            <div className="skills-actions">
              <button onClick={() => void save()}>Save</button>
              <span className="muted">{status}</span>
            </div>
          </>
        ) : (
          <p className="muted center">
            Select a skill to edit, or create one. Skills shape how papr explains.
          </p>
        )}
      </section>
    </div>
  );
}
