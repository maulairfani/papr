import { Markdown } from "../Markdown";

/** Renders a parsed Markdown file (read view) in the editor pane. */
export function MarkdownView({ source }: { source: string }) {
  return (
    <div className="h-full overflow-auto px-8 py-6">
      <Markdown source={source} className="max-w-3xl" />
    </div>
  );
}
