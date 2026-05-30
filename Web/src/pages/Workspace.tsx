import { Sidebar } from "../components/sidebar/Sidebar";
import { Editor } from "../components/editor/Editor";
import { ChatInterface } from "../components/chat/ChatInterface";
import { WorkspaceProvider } from "../workspace/WorkspaceContext";

/** The single page: a three-pane workspace, sharing open-file state via context.
 * Sidebar (filesystem) · Editor (paper/markdown) · Chat. */
export function Workspace() {
  return (
    <WorkspaceProvider>
      <div className="flex h-full">
        <Sidebar />
        <Editor />
        <ChatInterface />
      </div>
    </WorkspaceProvider>
  );
}
