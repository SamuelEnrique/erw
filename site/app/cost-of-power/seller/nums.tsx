// Session 195: the small pieces /cost-of-power/seller writes its figures with, moved out of page.tsx so that the
// figures that follow scenario A in the browser (SellerScenarios.tsx: the headline's coverage, the months below a
// month of debt payments, the section "Debt coverage", each month's coverage) are written as the server's are, check
// key included (mr|<inputs>|<stat>).
import type { ReactNode } from "react";
import { Num } from "@/components/Num";
import { usdShort } from "@/lib/batterystack";
import { shown } from "@/lib/format";

/** A short placeholder with its reason on hover. */
export function Missing({ why, words = "not held yet" }: { why: string; words?: string }) {
  return <span className="cursor-help border-b border-dotted border-muted italic text-muted" title={why} data-missing="1">{words}</span>;
}
/** A label with its definition on hover. */
export function Hint({ children, why }: { children: ReactNode; why: string }) {
  return <span className="cursor-help border-b border-dotted border-muted" title={why}>{children}</span>;
}
/** A number with its check key (mr|<inputs>|<stat>); a count, a ratio or USD as the page shows it. */
export function V({ pre, stat, v, d }: { pre: string; stat: string; v: number | null; d?: (v: number) => string }) {
  return v === null ? <span className="text-muted">not held</span> : <Num check={`mr|${pre}|${stat}`} raw={v}>{d ? d(v) : shown(v)}</Num>;
}
export function U({ pre, stat, v }: { pre: string; stat: string; v: number | null }) {
  return v === null ? <span className="text-muted">not held</span> : <span data-format="usd"><Num check={`mr|${pre}|${stat}`} raw={v}>{usdShort(v)}</Num></span>;
}
export const count = (v: number) => String(v);
export const longMonth = (m: string) => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });
