// Energy Research Warehouse (ERW) site, session 2200 (chain 086): the words of where a figure came from, read from its
// check key, for the hover tip every figure of a signature explorer carries (components/Num.tsx, `source`). A key names
// the table, the entity, the variable and the period (series|<table>|<entity>|<variable>|<ts>); this file adds the
// source report the method note names for that table and the method note's own name, so the tip reads, for one figure:
//
//   ercot_peak_premium_annual: HB_HUBAVG, peak_iqr, 2025. Source: ERCOT real-time settlement point prices (NP6-785-ER,
//   NP6-905-CD), every 15-minute interval, computed by the ERW. Method: ERCOT peak premium.
//
// Nothing is typed per figure: the page passes the key it already draws (and, where it has better words for the entity
// than the key's, those). This file imports nothing, so a test may import it with node alone, and no number is read or
// computed here.

export type TableSource = {
  /** the source report, as the method note names it; `<iso>` is replaced by the entity's grid where the key has one */
  report: string;
  /** the method note's title, as the page's method link names it */
  method: string;
  /** how a period is written: a year (P1Y) or a month (P1M) */
  interval: "P1Y" | "P1M";
};

/** The tables the signature explorers draw, each with its source report and its method note (docs/methods/). */
export const SOURCES: Record<string, TableSource> = {
  ercot_peak_premium_annual: {
    report: "ERCOT real-time settlement point prices (NP6-785-ER, NP6-905-CD), every 15-minute interval, computed by the ERW",
    method: "ERCOT peak premium", interval: "P1Y",
  },
  ercot_peak_premium_monthly: {
    report: "ERCOT real-time settlement point prices (NP6-785-ER, NP6-905-CD), every 15-minute interval, computed by the ERW",
    method: "ERCOT peak premium", interval: "P1M",
  },
  eia930_demand_growth: {
    report: "EIA Form EIA-930 (Hourly Electric Grid Monitor), hourly demand, computed by the ERW",
    method: "Demand growth since 2019", interval: "P1Y",
  },
  iso_queue_statistics: {
    report: "the ISO's own interconnection queue as the ERW last pulled it (<iso>_interconnection_queue), computed by the ERW",
    method: "Energy projects, Queue statistics", interval: "P1Y",
  },
};

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

/** The period a key's timestamp labels, by the table's interval: "2025", or "August 2025". */
export function periodWords(ts: string, interval: "P1Y" | "P1M"): string {
  const d = new Date(ts);
  if (Number.isNaN(d.getTime())) return ts;
  return interval === "P1M" ? `${MONTHS[d.getUTCMonth()]} ${d.getUTCFullYear()}` : String(d.getUTCFullYear());
}

/** The entity's words from the key alone: the part after the grid's colon; a queue's "<iso>:queue_<year>" reads as
 *  "<ISO>'s queue, entry year <year>". A page with better words passes them to sourceOf instead. */
export function entityWords(entity: string): string {
  const m = entity.match(/^([a-z0-9-]+):queue_(\d{4})$/);
  if (m) return `${m[1].toUpperCase()}'s queue, entry year ${m[2]}`;
  const i = entity.indexOf(":");
  return i < 0 ? entity : entity.slice(i + 1);
}

/** The words of where a figure came from, for a series key of one of the explorers' tables; undefined for any other
 *  key (the figure then carries no tip, and the page says so in its report). */
export function sourceOf(key: string, entity?: string): string | undefined {
  const p = key.split("|");
  if (p.length < 5 || p[0] !== "series") return undefined;
  const [, table, ent, variable, ts] = p;
  const s = SOURCES[table];
  if (!s) return undefined;
  const grid = ent.includes(":") ? ent.slice(0, ent.indexOf(":")) : "";
  const report = s.report.replace("<iso>", grid || "iso");
  return `${table}: ${entity ?? entityWords(ent)}, ${variable}, ${periodWords(ts, s.interval)}. Source: ${report}. Method: ${s.method}.`;
}
