// A number on the page, carrying where it came from: `check` names the Supabase
// table and key it was read from, and `raw` the value as read. scripts/check-values.mjs
// reads these attributes from the rendered pages and compares each one with a direct
// Supabase query. The text shown is the value rounded for display.
export function Num({ check, raw, children, className }: { check: string; raw: number | string; children: React.ReactNode; className?: string }) {
  return (
    <span data-check={check} data-raw={String(raw)} className={className}>
      {children}
    </span>
  );
}
