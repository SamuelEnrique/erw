import { SiteLink as Link } from "@/components/SiteLink";

// Session 73: one plain sentence near any figure that uses EIA-930's generation for California after the series changed
// on 16 December 2025 (docs/methods/eia930_caiso_break.md). A label, not a correction: no value on the page changes.
export function CaisoBreakNote({ className = "mb-4" }: { className?: string }) {
  return (
    <p className={`${className} max-w-3xl border-l-2 border-accent bg-paper px-3 py-1.5 text-xs`} data-caiso-break="1">
      EIA&apos;s generation series for California changed on 16 December 2025, and California figures after that date are under review:{" "}
      <Link href="/data/methods/eia930_caiso_break">the method note</Link>.
    </p>
  );
}
