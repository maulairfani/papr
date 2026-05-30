import { rawUrl } from "../../api/files";
import { useFileContent } from "../../hooks/useFileContent";
import { MarkdownView } from "./MarkdownView";
import { PdfViewer } from "./PdfViewer";

/** Renders a file by type: PDF in the native viewer, everything else as Markdown.
 * (Editing via the rich-text editor comes next.) */
export function FileView({ path }: { path: string }) {
  if (path.toLowerCase().endsWith(".pdf")) {
    return <PdfViewer src={rawUrl(path)} />;
  }
  return <MarkdownFile path={path} />;
}

function MarkdownFile({ path }: { path: string }) {
  const { content, loading, error } = useFileContent(path);

  if (loading) {
    return <div className="grid h-full place-items-center text-sm text-muted">Loading…</div>;
  }
  if (error) {
    return <div className="grid h-full place-items-center text-sm text-red-400">{error}</div>;
  }
  return <MarkdownView source={content ?? ""} />;
}
