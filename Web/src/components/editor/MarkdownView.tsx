import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/** Renders a parsed Markdown file (read view), styled with Tailwind Typography. */
export function MarkdownView({ source }: { source: string }) {
  return (
    <div className="h-full overflow-auto">
      <div className="prose prose-invert max-w-3xl px-8 py-6">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{source}</ReactMarkdown>
      </div>
    </div>
  );
}
