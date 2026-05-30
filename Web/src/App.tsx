import { useState } from "react";
import { getToken, clearToken } from "./api";
import Login from "./components/Login";
import Chat from "./components/Chat";
import FilePane from "./components/FilePane";
import SkillsEditor from "./components/SkillsEditor";
import Topics from "./components/Topics";

type View = "chat" | "topics" | "skills";

export default function App() {
  const [token, setTokenState] = useState<string | null>(getToken());
  // Bumped whenever papr might have written files, to refresh the file pane.
  const [filesVersion, setFilesVersion] = useState(0);
  const [view, setView] = useState<View>("chat");

  if (!token) {
    return <Login onLogin={() => setTokenState(getToken())} />;
  }

  return (
    <div className="app">
      <header className="topbar">
        <span className="brand">papr</span>
        <nav className="nav">
          <button className={view === "chat" ? "tab active" : "tab"} onClick={() => setView("chat")}>
            Chat
          </button>
          <button className={view === "topics" ? "tab active" : "tab"} onClick={() => setView("topics")}>
            Topics
          </button>
          <button className={view === "skills" ? "tab active" : "tab"} onClick={() => setView("skills")}>
            Skills
          </button>
        </nav>
        <button
          className="ghost"
          onClick={() => {
            clearToken();
            setTokenState(null);
          }}
        >
          Sign out
        </button>
      </header>
      {view === "chat" ? (
        <main className="layout">
          <Chat onFilesMaybeChanged={() => setFilesVersion((v) => v + 1)} />
          <FilePane filesVersion={filesVersion} />
        </main>
      ) : view === "topics" ? (
        <main className="layout-full">
          <Topics />
        </main>
      ) : (
        <main className="layout-full">
          <SkillsEditor />
        </main>
      )}
    </div>
  );
}
