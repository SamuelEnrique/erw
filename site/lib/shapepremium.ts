// Session 48: the shape premium report's period statistics, from cost_of_power_monthly rows (docs/methods/
// cost_of_power.md). Shared by /reports/draft/shape-premium and scripts/check-values.mjs (key shape|<entity>|<market>|
// <stat>|<start>|<end>), so every statistic on the page is recomputed from Supabase by the same rule. No imports.
//
// A month counts only when it is complete for the market: <market>_hours equals hours_in_month. The shape premium is
// the load-weighted mean price less the simple mean: what a load shaped like the grid's pays per MWh beyond a flat one.

export type Row = { entity: string; variable: string; ts_utc: string; value: number };
export type Month = { ts: string; lw: number; simple: number; premium: number; hours: number; complete: boolean };

export function monthsOf(rows: Row[], entity: string, market: "rt" | "da"): Month[] {
  const by = new Map<string, Record<string, number>>();
  for (const r of rows) {
    if (r.entity !== entity) continue;
    const k = r.ts_utc.slice(0, 10);
    const m = by.get(k) ?? {};
    m[r.variable] = Number(r.value);
    by.set(k, m);
  }
  return [...by.entries()].sort((a, b) => (a[0] < b[0] ? -1 : 1))
    .filter(([, m]) => m[`${market}_shape_premium`] !== undefined)
    .map(([ts, m]) => ({ ts, lw: m[`${market}_load_weighted`], simple: m[`${market}_simple_mean`], premium: m[`${market}_shape_premium`],
      hours: m[`${market}_hours`], complete: m[`${market}_hours`] === m.hours_in_month }));
}

export type Stats = { n: number; npos: number; mean: number; usdmw: number; first: string; last: string };

/** Over the complete months in [start, end) (YYYY-MM-DD): their count, how many had a positive premium, the mean
 * premium (USD/MWh), and usdmw, the sum of premium times hours: the USD one megawatt shaped like the grid's load paid
 * beyond one flat megawatt over those months. */
export function stats(rows: Row[], entity: string, market: "rt" | "da", start: string, end: string): Stats {
  const ms = monthsOf(rows, entity, market).filter((m) => m.complete && m.ts >= start && m.ts < end);
  return {
    n: ms.length, npos: ms.filter((m) => m.premium > 0).length, mean: ms.reduce((a, m) => a + m.premium, 0) / ms.length,
    usdmw: ms.reduce((a, m) => a + m.premium * m.hours, 0), first: ms[0]?.ts ?? "", last: ms.at(-1)?.ts ?? "",
  };
}
