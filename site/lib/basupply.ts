// Session 68: who supplies a grid, over the last twelve months, from ba_supply_monthly (warehouse/derived/ba_supply.py).
// /network's panel and its folded table compute every figure here, and scripts/check-values.mjs recomputes them from its
// own read (key bsup|<BA>|<stat>). No imports: Node runs this file as it is. docs/methods/grid_network.md, "Who supplies
// a grid". Positive always means the neighbour supplied the grid (a net import).

export type SupplyRow = { entity: string; variable: string; ts_utc: string; value: number };
export const TABLE = "ba_supply_monthly";
export const MEASURES = {
  pairs: "the sum of its reported ties",
  total_interchange: "EIA's total interchange",
  balance: "demand less net generation",
} as const;
export type Measure = keyof typeof MEASURES;
/** Session 68's headline rule: the pair sum, which is complete on every held day, equals EIA's total interchange on the
 * same days for five of the seven ISOs, and is the measure the neighbours' shares add up to. */
export const HEADLINE: Measure = "pairs";
/** When the three measures spread wider than this (points of demand), the panel shows the range and says so. */
export const SPREAD = 1;

const monthLen = (m: string) => new Date(Date.UTC(Number(m.slice(0, 4)), Number(m.slice(5, 7)), 0)).getUTCDate();

/** The twelve months: the newest month the table holds whole (its days_in_month is the calendar month's) and the eleven
 * before it. */
export function twelveMonths(rows: SupplyRow[], ba: string): string[] {
  const full = rows.filter((r) => r.entity === `eia930:${ba}` && r.variable === "days_in_month" && r.value === monthLen(r.ts_utc.slice(0, 7)))
    .map((r) => r.ts_utc.slice(0, 7)).sort();
  const last = full.at(-1);
  if (!last) return [];
  const out: string[] = [];
  for (let k = 11; k >= 0; k--) out.push(new Date(Date.UTC(Number(last.slice(0, 4)), Number(last.slice(5, 7)) - 1 - k, 1)).toISOString().slice(0, 7));
  return out;
}

export type Supply = {
  ba: string; months: string[]; daysHeld: number; daysLeftOut: number; thin: number; shareDays: number;
  share: Partial<Record<Measure, number>>;        // percent of demand over the months that hold the measure's share
  mwh: Partial<Record<Measure, number>>;          // MWh over held days
  neighbours: { id: string; mwh: number; share: number | null }[];   // largest supplier first
  hasDemand: boolean;
  spread: number | null;                          // max minus min of the three shares, points
};

/** The twelve months of one balancing authority. */
export function supplyOf(rows: SupplyRow[], ba: string): Supply | null {
  const months = twelveMonths(rows, ba);
  if (!months.length) return null;
  const inM = (r: SupplyRow) => months.includes(r.ts_utc.slice(0, 7));
  const me = rows.filter((r) => r.entity === `eia930:${ba}` && inM(r));
  const v = (variable: string, m: string) => me.find((r) => r.variable === variable && r.ts_utc.startsWith(m))?.value;
  const sum = (variable: string) => me.filter((r) => r.variable === variable).reduce((a, r) => a + r.value, 0);
  const share: Partial<Record<Measure, number>> = {}, mwh: Partial<Record<Measure, number>> = {};
  for (const k of Object.keys(MEASURES) as Measure[]) {
    let num = 0, den = 0;
    for (const m of months) {
      const s = v(`net_import_${k}_share_pct`, m), d = v("demand_mwh", m);
      if (s !== undefined && d !== undefined) { num += (s * d) / 100; den += d; }
    }
    if (den > 0) share[k] = (num / den) * 100;
    const t = me.filter((r) => r.variable === `net_import_${k}_mwh`);
    if (t.length) mwh[k] = t.reduce((a, r) => a + r.value, 0);
  }
  // the neighbours: each pair's MWh, and its share over the same months as the headline's
  const prefix = `eia930:${ba}-`;
  const pairs = rows.filter((r) => r.entity.startsWith(prefix) && inM(r));
  const ids = [...new Set(pairs.map((r) => r.entity.slice(prefix.length)))];
  const dem = (m: string) => v("demand_mwh", m);
  const neighbours = ids.map((id) => {
    const p = pairs.filter((r) => r.entity === prefix + id);
    const mw = p.filter((r) => r.variable === "net_import_mwh").reduce((a, r) => a + r.value, 0);
    let num = 0, den = 0;
    for (const m of months) {
      const s = p.find((r) => r.variable === "net_import_share_pct" && r.ts_utc.startsWith(m))?.value, d = dem(m);
      const headline = v(`net_import_${HEADLINE}_share_pct`, m);
      if (headline !== undefined && d !== undefined) { num += ((s ?? 0) * d) / 100; den += d; }  // a month the tie did not report adds no flow
    }
    return { id, mwh: mw, share: den > 0 ? (num / den) * 100 : null };
  }).sort((a, b) => (b.share ?? b.mwh) - (a.share ?? a.mwh) || b.mwh - a.mwh || a.id.localeCompare(b.id));
  const vals = Object.values(share);
  return {
    ba, months, daysHeld: sum("days_held"), daysLeftOut: sum("days_left_out"), thin: sum("thin_month"), shareDays: sum("share_days"),
    share, mwh, neighbours, hasDemand: share[HEADLINE] !== undefined, spread: vals.length === 3 ? Math.max(...vals) - Math.min(...vals) : null,
  };
}

/** One number for a check key (bsup|<BA>|<stat>): share:<measure>, mwh:<measure>, top_share, top (the supplier's rank
 * is not a number: top_share only), neighbour:<ID>, neighbour_mwh:<ID>, days_held, days_left_out. */
export function supplyStat(rows: SupplyRow[], ba: string, what: string): number | null {
  const s = supplyOf(rows, ba);
  if (!s) return null;
  const [a, b] = what.split(":");
  switch (a) {
    case "share": return s.share[b as Measure] ?? null;
    case "mwh": { const x = s.mwh[b as Measure]; return x === undefined ? null : Math.round(x); }  // whole MWh
    case "top_share": return s.neighbours[0]?.share ?? null;
    case "neighbour": return s.neighbours.find((n) => n.id === b)?.share ?? null;
    case "neighbour_mwh": { const x = s.neighbours.find((n) => n.id === b)?.mwh; return x === undefined ? null : Math.round(x); }
    case "days_held": return s.daysHeld;
    case "days_left_out": return s.daysLeftOut;
    case "spread": return s.spread;
    default: return null;
  }
}
