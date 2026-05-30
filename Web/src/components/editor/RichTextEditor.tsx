import { EditorContent, useEditor } from "@tiptap/react";
import StarterKit from "@tiptap/starter-kit";

const INITIAL = `
<h1>Notes</h1>
<p>A <strong>rich-text</strong> editor (TipTap). Try <em>formatting</em>, headings, and lists — markdown shortcuts work too (type <code>## </code> or <code>- </code>).</p>
<ul><li>self-attention</li><li>positional encodings</li></ul>
`;

function ToolbarButton({ label, onClick }: { label: string; onClick: () => void }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="rounded px-2 py-1 text-xs font-medium text-ink/70 hover:bg-white/5 hover:text-ink"
    >
      {label}
    </button>
  );
}

/** A WYSIWYG rich-text editor for notes (TipTap). */
export function RichTextEditor() {
  const editor = useEditor({
    extensions: [StarterKit],
    content: INITIAL,
    immediatelyRender: false,
    editorProps: {
      attributes: { class: "prose prose-invert max-w-3xl px-8 py-6 focus:outline-none" },
    },
  });

  return (
    <div className="flex h-full flex-col">
      <div className="flex gap-1 border-b border-border px-3 py-1.5">
        <ToolbarButton label="Bold" onClick={() => editor?.chain().focus().toggleBold().run()} />
        <ToolbarButton label="Italic" onClick={() => editor?.chain().focus().toggleItalic().run()} />
        <ToolbarButton
          label="H2"
          onClick={() => editor?.chain().focus().toggleHeading({ level: 2 }).run()}
        />
        <ToolbarButton
          label="List"
          onClick={() => editor?.chain().focus().toggleBulletList().run()}
        />
      </div>
      <div className="min-h-0 flex-1 overflow-auto">
        <EditorContent editor={editor} />
      </div>
    </div>
  );
}
