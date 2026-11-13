// Energy Research Warehouse (ERW) site, session 2207 (Samuel's ruling of 23 October 2026 on item 7 of
// docs/reviews/deals-rulings-2026-10-23.md): a stored Digest issue is a record and keeps the figure it printed. When
// the warehouse later holds another value for the same row (EIA restated WTI at Cushing for 14 October 2026 from
// 101.91 to 96.34 after the issues of 20 and 21 October were written), the page says so in one line under the numbers,
// with the value the warehouse holds now, and leaves the stored issue as it is. This reads the live set for each
// figure of the issue's fuel closes (EIA's series, the ones EIA restates) and returns the rows whose value differs.
// A read that fails returns nothing for that figure: the page then shows no note, never a guess.
import { digestFigures, type Revision } from "@/lib/digest";
import { HOURLY, attempt, rest } from "@/lib/supabase";

type Row = { value: number; retrieved_at: string | null };

/** The figures of an issue the live set holds at another value than the issue printed, by check key. */
export async function digestRevisions(md: string, date: string, now: Date = new Date()): Promise<Record<string, Revision>> {
  const out: Record<string, Revision> = {};
  // session 3891 (chain 227): the US48 demand line too. EIA restates EIA-930's hours: the issue of 12 November 2026 printed
  // 488,034 MW for 11 November 23:00 UTC, and the run of 13 November loaded EIA's 488,341. It is read as printed, whole MW.
  const figs = digestFigures(md, date, null, now).filter((f) => (f.part === "fuel" || f.part === "demand") && !f.held);
  for (const f of figs) {
    const demand = f.part === "demand";
    const [, table, entity, a, b] = f.key.split("|");   // fuel: day; demand: variable and hour
    const r = await attempt(() => rest<Row>("series", demand
      ? { select: "value,retrieved_at", table_name: `eq.${table}`, entity: `eq.${entity}`, variable: `eq.${a}`, ts_utc: `eq.${b}` }
      : { select: "value,retrieved_at", table_name: `eq.${table}`, entity: `eq.${entity}`, ts_utc: `eq.${a}T00:00:00Z`, order: "variable" },
    HOURLY, 1));
    if (!r.ok || !r.data.length) continue;
    const v = Number(r.data[0].value);
    if (!Number.isFinite(v)) continue;
    if (demand ? Math.round(v) === Number(f.raw) : v.toFixed(2) === Number(f.raw).toFixed(2)) continue;
    out[f.key] = { key: f.key, value: v, retrieved: r.data[0].retrieved_at ?? null };
  }
  return out;
}
