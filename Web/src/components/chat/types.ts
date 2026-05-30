// Conversation shapes the ChatInterface renders. Built up from the BFF's
// ChatEvent stream (api/types.ts).

export type Activity =
  | { kind: "tool_call"; tool: string; args: Record<string, unknown> }
  | { kind: "tool_result"; tool: string; result: string }
  | { kind: "todos"; items: { text: string; done: boolean }[] };

export type Turn =
  | { role: "user"; text: string }
  | { role: "assistant"; activity: Activity[]; text: string };
