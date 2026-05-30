import { useCallback, useEffect, useRef, useState } from "react";
import { listFiles, getFileContent, uploadPaper, type FileEntry } from "../api";

// Browses the user's store-backed files, uploads papers, and shows content.
export default function FilePane({ filesVersion }: { filesVersion: number }) {
  const [files, setFiles] = useState<FileEntry[]>([]);
  const [selected, setSelected] = useState<string | null>(null);
  const [content, setContent] = useState("");
  const [uploading, setUploading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const refresh = useCallback(() => {
    listFiles()
      .then(setFiles)
      .catch(() => setFiles([]));
  }, []);

  // Refresh when papr may have written files, and on mount.
  useEffect(() => refresh(), [filesVersion, refresh]);

  async function open(path: string) {
    setSelected(path);
    try {
      setContent(await getFileContent(path));
    } catch {
      setContent("(could not load file)");
    }
  }

  async function onUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setUploading(true);
    try {
      await uploadPaper(file);
      refresh();
    } finally {
      setUploading(false);
      if (inputRef.current) inputRef.current.value = "";
    }
  }

  return (
    <aside className="files">
      <div className="files-head">
        <h2>Files</h2>
        <label className="upload">
          {uploading ? "Uploading…" : "Upload"}
          <input ref={inputRef} type="file" hidden onChange={onUpload} disabled={uploading} />
        </label>
      </div>
      {files.length === 0 && <p className="muted">No files yet.</p>}
      <ul className="file-list">
        {files.map((f) => (
          <li key={f.path}>
            <button
              className={selected === f.path ? "file active" : "file"}
              onClick={() => void open(f.path)}
            >
              {f.path}
            </button>
          </li>
        ))}
      </ul>
      {selected && (
        <div className="viewer">
          <div className="viewer-path">{selected}</div>
          <pre>{content}</pre>
        </div>
      )}
    </aside>
  );
}
