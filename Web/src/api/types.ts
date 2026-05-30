// Shared API types.

export type FsNode = {
  name: string;
  path: string;
  type: "file" | "folder";
  children?: FsNode[];
};

// Normalized chat stream events from the BFF (mirrors the agent's updates/messages).
export type ChatEvent =
  | { type: "thread"; thread_id: string }
  | { type: "token"; text: string }
  | { type: "activity"; kind: "tool_call"; tool: string; args: Record<string, unknown> }
  | { type: "activity"; kind: "tool_result"; tool: string; result: string }
  | { type: "activity"; kind: "todos"; items: { text: string; done: boolean }[] }
  | { type: "done" }
  | { type: "error"; detail: string };
