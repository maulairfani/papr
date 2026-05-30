import { useState } from "react";
import { devLogin, setToken } from "../api";

// Dev login: any username mints a token. Real auth replaces this later.
export default function Login({ onLogin }: { onLogin: () => void }) {
  const [username, setUsername] = useState("");
  const [error, setError] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    try {
      const { token } = await devLogin(username.trim());
      setToken(token);
      onLogin();
    } catch {
      setError("Login failed — is the API running?");
    }
  }

  return (
    <div className="login">
      <form className="login-card" onSubmit={submit}>
        <h1 className="brand">papr</h1>
        <p className="muted">Understand papers, with an agent that takes notes.</p>
        <input
          autoFocus
          placeholder="username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <button type="submit" disabled={!username.trim()}>
          Continue
        </button>
        {error && <p className="error">{error}</p>}
      </form>
    </div>
  );
}
