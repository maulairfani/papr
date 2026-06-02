/**
 * Dev-only living style guide. Renders every design token so we can eyeball the
 * foundations in one place. Primitives (Button, Input, …) get added here as they
 * land in later PRs. Reachable at /design.
 */

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mb-12">
      <h2 className="mb-4 text-sm font-semibold uppercase tracking-wider text-muted">{title}</h2>
      {children}
    </section>
  );
}

function Swatch({ name, varName }: { name: string; varName: string }) {
  return (
    <div className="flex flex-col gap-1.5">
      <div
        className="h-16 w-full rounded-md border border-border"
        style={{ background: `var(${varName})` }}
      />
      <div className="text-xs text-ink">{name}</div>
      <code className="text-[11px] text-muted">{varName}</code>
    </div>
  );
}

const SURFACES = [
  ["canvas", "--color-canvas"],
  ["surface", "--color-surface"],
  ["raised", "--color-raised"],
  ["hover", "--color-hover"],
  ["active", "--color-active"],
];
const TEXT = [
  ["ink", "--color-ink"],
  ["muted", "--color-muted"],
  ["faint", "--color-faint"],
];
const BRAND_STATE = [
  ["brand", "--color-brand"],
  ["brand-hover", "--color-brand-hover"],
  ["danger", "--color-danger"],
  ["success", "--color-success"],
  ["warning", "--color-warning"],
];
const LINES = [
  ["border", "--color-border"],
  ["border-strong", "--color-border-strong"],
];

const TYPE_SCALE: [string, string][] = [
  ["text-xs", "The quick brown fox"],
  ["text-sm", "The quick brown fox"],
  ["text-base", "The quick brown fox"],
  ["text-lg", "The quick brown fox"],
  ["text-xl", "The quick brown fox"],
  ["text-2xl", "The quick brown fox"],
];

const RADII = ["sm", "md", "lg", "xl"];
const SHADOWS = ["sm", "md", "lg"];

export function Design() {
  return (
    <div className="min-h-full overflow-y-auto bg-canvas px-10 py-10 text-ink">
      <header className="mb-10">
        <h1 className="text-2xl font-semibold">papr design system</h1>
        <p className="mt-1 text-sm text-muted">
          Living reference for tokens and primitives. Tokens live in{" "}
          <code className="text-ink">src/index.css</code>.
        </p>
      </header>

      <Section title="Surfaces">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-5">
          {SURFACES.map(([n, v]) => (
            <Swatch key={v} name={n} varName={v} />
          ))}
        </div>
      </Section>

      <Section title="Text">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          {TEXT.map(([n, v]) => (
            <Swatch key={v} name={n} varName={v} />
          ))}
        </div>
      </Section>

      <Section title="Brand & state">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 md:grid-cols-5">
          {BRAND_STATE.map(([n, v]) => (
            <Swatch key={v} name={n} varName={v} />
          ))}
        </div>
      </Section>

      <Section title="Lines">
        <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
          {LINES.map(([n, v]) => (
            <Swatch key={v} name={n} varName={v} />
          ))}
        </div>
      </Section>

      <Section title="Typography">
        <div className="flex flex-col gap-3 rounded-lg border border-border bg-surface p-6">
          {TYPE_SCALE.map(([cls, text]) => (
            <div key={cls} className="flex items-baseline gap-4">
              <code className="w-20 shrink-0 text-xs text-muted">{cls}</code>
              <span className={cls}>{text}</span>
            </div>
          ))}
          <div className="mt-2 flex items-baseline gap-4 border-t border-border pt-3">
            <code className="w-20 shrink-0 text-xs text-muted">mono</code>
            <span className="font-mono text-sm">const papr = "ai";</span>
          </div>
        </div>
      </Section>

      <Section title="Radius">
        <div className="flex flex-wrap gap-6">
          {RADII.map((r) => (
            <div key={r} className="flex flex-col items-center gap-2">
              <div
                className="h-16 w-16 border border-border-strong bg-raised"
                style={{ borderRadius: `var(--radius-${r})` }}
              />
              <code className="text-xs text-muted">{r}</code>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Elevation">
        <div className="flex flex-wrap gap-8">
          {SHADOWS.map((s) => (
            <div key={s} className="flex flex-col items-center gap-2">
              <div
                className="flex h-20 w-28 items-center justify-center rounded-lg bg-raised text-xs text-muted"
                style={{ boxShadow: `var(--shadow-${s})` }}
              >
                shadow-{s}
              </div>
            </div>
          ))}
        </div>
      </Section>

      <Section title="Primitives">
        <p className="text-sm text-faint">
          Buttons, inputs, tabs, tooltips, dialogs… land here in upcoming PRs.
        </p>
      </Section>
    </div>
  );
}
