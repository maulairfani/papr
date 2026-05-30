import { useWorkspace } from "../../workspace/WorkspaceContext";
import { EditorTabs } from "./EditorTabs";
import { FileView } from "./FileView";

/** Center pane: open-file tabs over the active file's content. */
export function Editor() {
  const ws = useWorkspace();

  return (
    <div className="flex min-w-0 flex-1 flex-col bg-canvas">
      <EditorTabs />
      <div className="min-h-0 flex-1">
        {ws.activePath ? (
          <FileView path={ws.activePath} />
        ) : (
          <div className="grid h-full place-items-center text-sm text-muted">
            Select a file from the explorer
          </div>
        )}
      </div>
    </div>
  );
}
