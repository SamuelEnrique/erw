// Session 369: the UTC day a figure of hourly tables is asked of, chosen once and shared by the page and its check.
//
// /learn/problems/know-your-grid (lib/problems.ts, set A, questions 1 and 2) asked of the newest UTC day the demand table
// held in full for ERCOT and CAISO, then summed eia930_all_generation on that day. The generation table ends a day
// earlier than the demand table, so from 19 October 2026 the page wrote 0 MWh and 0 percent from gas. The rule now: the
// newest UTC day that every table named holds in full, a day "in full" as the page always meant it (every one of its 24
// hours, for each grid and each variable asked). scripts/check-values.mjs imports this file and checks the page's day
// with the same function: a day the page names is held in full in every table, or the check fails.
//
// Pure: no request, no import. The rows are read by the caller.

export type HourRow = { entity: string; variable: string; ts_utc: string };
export type Held = { table: string; variables: string[]; rows: HourRow[] };

/** The tables, variables and grids set A's questions 1 and 2 read; the check reads the same. */
export const KNOW_YOUR_GRID = {
  entities: ["eia930:ERCO", "eia930:CISO"],
  tables: [
    { table: "eia930_all_demand", variables: ["demand_mw"] },
    { table: "eia930_all_generation", variables: ["net_generation_mw", "net_generation_natural_gas_mw"] },
  ],
} as const;

const dayOf = (ts: string) => ts.slice(0, 10);

/** The UTC days on which every entity holds all 24 hours of every variable in these rows. */
export function fullDays(rows: HourRow[], entities: readonly string[], variables: readonly string[]): Set<string> {
  const hours = new Map<string, Set<number>>();
  for (const r of rows) {
    const k = `${r.entity}|${r.variable}|${dayOf(r.ts_utc)}`;
    if (!hours.has(k)) hours.set(k, new Set());
    hours.get(k)!.add(Date.parse(r.ts_utc));   // parsed: "+00:00" and "Z" are the same hour
  }
  const days = new Set(rows.map((r) => dayOf(r.ts_utc)));
  return new Set([...days].filter((d) => entities.every((e) => variables.every((v) => hours.get(`${e}|${v}|${d}`)?.size === 24))));
}

/** The newest UTC day held in full in every table, for every entity; with `until`, no day after it. */
export function newestCommonFullDay(held: Held[], entities: readonly string[], until?: string): string | undefined {
  if (!held.length) return undefined;
  const sets = held.map((h) => fullDays(h.rows, entities, h.variables));
  return [...sets[0]].filter((d) => sets.every((s) => s.has(d)) && (!until || d <= until)).sort().at(-1);
}

/** The check key the page writes beside the day: fullday|<set>|<day>. */
export const dayKey = (set: string, d: string) => `fullday|${set}|${d}`;
