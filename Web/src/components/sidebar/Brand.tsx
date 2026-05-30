/** papr brand: logo mark (public/papr.svg) + wordmark. Sits atop the sidebar. */
export function Brand() {
  return (
    <div className="flex items-center gap-2.5 border-b border-border px-4 py-3.5">
      <img src="/papr.svg" alt="" className="h-6 w-6 shrink-0" />
      <span className="text-base font-semibold tracking-tight text-ink">papr</span>
    </div>
  );
}
