import { Sidebar } from "../components/sidebar/Sidebar";
import { Editor } from "../components/editor/Editor";
import { ChatInterface } from "../components/chat/ChatInterface";

/** The single page: a three-pane workspace.
 * Sidebar (with the filesystem) · Editor (paper/markdown/rich text) · Chat. */
export function Workspace() {
  return (
    <div className="flex h-full">
      <Sidebar />
      <Editor />
      <ChatInterface />
    </div>
  );
}
