// Session 195: the two ways /cost-of-power/battery writes a number with its check key (bs|<inputs>|<stat>), moved out
// of page.tsx so that the headline, which is computed in the browser from scenario A (Scenarios.tsx), writes them as
// the server's sections do. `keyed` is false for a figure that is not the table's own: scenario A at another
// round-trip efficiency or cycle limit than the model's, whose months come from the file of steps.
import { Num } from "@/components/Num";
import { usdShort } from "@/lib/batterystack";

/** A US dollar amount with its check key. */
export function U({ pre, s, v, keyed = true }: { pre: string; s: string; v: number | null; keyed?: boolean }) {
  if (v === null) return <span className="text-muted">not held</span>;
  return keyed ? <span data-format="usd"><Num check={`bs|${pre}|${s}`} raw={v}>{usdShort(v)}</Num></span> : <span>{usdShort(v)}</span>;
}
/** A ratio, a count, a percent or USD per kW with its check key (a whole number, else two decimals). */
export function V({ pre, s, v, keyed = true }: { pre: string; s: string; v: number | null; keyed?: boolean }) {
  if (v === null) return <span className="text-muted">not held</span>;
  const text = Number.isInteger(v) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  return keyed ? <Num check={`bs|${pre}|${s}`} raw={v}>{text}</Num> : <span>{text}</span>;
}
