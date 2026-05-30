import { Brand } from "./Brand";
import { Filesystem } from "./Filesystem";

/** Left rail: brand on top, then the filesystem (and later: actions). */
export function Sidebar() {
  return (
    <aside className="flex w-96 shrink-0 flex-col border-r border-border bg-surface">
      <Brand />
      <Filesystem />
    </aside>
  );
}
