import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

/** Shared GitHub-flavored Markdown renderer, styled with Tailwind Typography.
 * Callers set width/size via `className` (e.g. "max-w-3xl", "prose-sm"). */
export function Markdown({ source, className = "" }: { source: string; className?: string }) {
  return (
    <div className={`prose prose-invert ${className}`}>
      <ReactMarkdown remarkPlugins={[remarkGfm]}>{source}</ReactMarkdown>
    </div>
  );
}
