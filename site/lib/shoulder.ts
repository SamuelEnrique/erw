// Energy Research Warehouse (ERW) site, session 75: the shoulder hours (/shoulder). The page's model: it picks rows of
// shoulder_hours_monthly (warehouse/derived/shoulder_hours.py; docs/methods/shoulder_hours.md) and does no arithmetic.
// Every number on the page is a row, carried with its check key (series|shoulder_hours_monthly|<entity>|<variable>|<ts>),
// which scripts/check-values.mjs reads like any series value. No imports from the app: Node runs this file as it is.

export const TABLE = "shoulder_hours_monthly";
export type Row = { entity: string; variable: string; ts_utc: string; value: number };

export const GRIDS = [
  { slug: "ercot", name: "ERCOT", short: "ERCOT", by: "", entity: "iso:ercot", note: "EIA-930 hourly demand, solar, wind and battery output, from January 2019." },
  { slug: "caiso", name: "CAISO", short: "CAISO", by: "by EIA-930, ", entity: "iso:caiso", note: "EIA-930 hourly demand, solar and wind, January 2019 to November 2025: EIA's generation series for California changed on 16 December 2025, and this page does not mix the changed series in. Battery output is CAISO's own (Today's Outlook), from August 2025." },
  // session 80: California on CAISO's own supply by fuel, a separate entity, never mixed with the EIA-930 one above
  { slug: "caiso-own", name: "CAISO, its own data", short: "CAISO", by: "by CAISO's own data, ", entity: "iso:caiso_own", note: "CAISO's own supply by fuel (Today's Outlook), from June 2025: solar, wind and battery output are CAISO's, and demand is the sum of its sources, imports and batteries included. A separate series from the EIA-930 one, never mixed with it." },
] as const;
export type Grid = (typeof GRIDS)[number];

export const tsOf = (month: string) => `${month}-01T00:00:00Z`;
export const yearTs = (year: string) => `${year}-01-01T00:00:00Z`;
export const monthOf = (ts: string) => ts.slice(0, 7);

/** A number as the site writes it: whole numbers with separators, others to two decimals (as check-values reads). */
export function shown(v: number): string {
  return Number.isInteger(v) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}
/** The check key of a row: a month's rows and a year's (dated its first day) are both at <YYYY-MM>-01T00:00:00Z. */
export const checkKey = (r: Row) => `series|${TABLE}|${r.entity}|${r.variable}|${tsOf(monthOf(r.ts_utc))}`;
export const monthName = (m: string) => new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });
export const hourName = (h: number) => (h >= 24 ? "midnight" : `${String(h).padStart(2, "0")}:00`);
/** Session 80: a worst day's rows are dated the day itself, so their check key carries the day. */
export const dayOf = (ts: string) => ts.slice(0, 10);
export const dayKey = (r: Row) => `series|${TABLE}|${r.entity}|${r.variable}|${dayOf(r.ts_utc)}T00:00:00Z`;
export const dayName = (d: string) => new Date(`${d}T12:00:00Z`).toLocaleString("en-US", { day: "numeric", month: "long", year: "numeric", timeZone: "UTC" });
const DAILY = (v: string) => v === "worst_rank" || v.startsWith("day_");

/** An index of the rows: (entity, variable, month or year start) to the row. */
export function index(rows: Row[]): Map<string, Row> {
  return new Map(rows.filter((r) => !DAILY(r.variable)).map((r) => [`${r.entity}|${r.variable}|${monthOf(r.ts_utc)}`, { ...r, ts_utc: `${monthOf(r.ts_utc)}-01T00:00:00Z` }]));
}

/** Session 90: the figures of a month the page states in its summary sentence and headline numbers. The newest month
 * usually lacks the fleet (EIA's inventory is published a month or two behind) and with it the hours covered and
 * needed, so the page opened on a sentence with "not held" in it. Curtailment and battery output are not in the list:
 * they are held for some grids only, and the page says so in words. */
export const REQUIRED = [
  "days_held", "shoulder_hours", "shoulder_start_hour", "shoulder_end_hour", "shoulder_mwh_above_mean", "fleet_mw", "fleet_mwh", "fleet_hours",
  "shoulder_hours_covered", "shoulder_hours_needed", "midday_surplus_mwh", "midday_surplus_hours", "midday_low_hour",
  "shoulder2_hours", "shoulder2_start_hour", "shoulder2_end_hour", "shoulder2_mwh_above_midpoint", "shoulder2_hours_needed", "evening_peak_mw", "evening_peak_hour",
] as const;

/** The months of a grid that hold every figure in REQUIRED, oldest first. */
export function completeMonths(rows: Row[], grid: Grid): string[] {
  const need = new Set<string>(REQUIRED);
  const n = new Map<string, number>();
  for (const r of rows) if (r.entity === grid.entity && need.has(r.variable)) n.set(monthOf(r.ts_utc), (n.get(monthOf(r.ts_utc)) ?? 0) + 1);
  return [...n.entries()].filter(([, k]) => k === REQUIRED.length).map(([m]) => m).sort();
}

/** The month a grid opens on: the latest that holds every figure; the newest held when none does. */
export function opening(held: string[], complete: string[]): string | null {
  return complete.at(-1) ?? held.at(-1) ?? null;
}

/** The grid and the month from a query; with no month named (or one not held) the page opens on the latest month that
 * holds every figure (session 90; until then the newest month held). A later month is still in the panel. */
export function choices(q: Record<string, string | undefined>, months: Record<string, string[]>, complete: Record<string, string[]> = {}) {
  const grid = GRIDS.find((g) => g.slug === q.grid) ?? GRIDS[0];
  const held = months[grid.slug] ?? [];
  const month = q.month && held.includes(q.month) ? q.month : opening(held, complete[grid.slug] ?? []);
  return { grid, month };
}

/** Session 7512 (the page read as its reader): California is two grids of the panel, one place from two sources. */
export const OTHER_SOURCE: Record<string, string> = { caiso: "caiso-own", "caiso-own": "caiso" };
/** How a grid is named with its source, in a sentence. */
export const sourceName = (g: Grid) => (g.slug === "caiso" ? "CAISO by EIA-930" : g.slug === "caiso-own" ? "CAISO by its own data" : g.name);

/** Session 7512: what the address asked for and the page does not hold, one line each, never replaced in silence (the
 * rule of /cost-of-power/battery since session 263). Until then a month not held, or a grid not held, opened the
 * grid's latest month, or ERCOT, with no word. `other` names California's other source when it holds the month asked. */
export function notShown(q: Record<string, string | undefined>, months: Record<string, string[]>, grid: Grid, month: string | null): { key: string; words: string; other?: { grid: Grid; month: string } }[] {
  const out: { key: string; words: string; other?: { grid: Grid; month: string } }[] = [];
  if (q.grid !== undefined && !GRIDS.some((g) => g.slug === q.grid)) {
    out.push({ key: "grid", words: `Grid: "${q.grid.slice(0, 24)}" is not held here (${GRIDS.map((g) => g.name).join("; ")} are), so ${grid.name} is shown.` });
  }
  const held = months[grid.slug] ?? [];
  if (q.month !== undefined && month && !held.includes(q.month)) {
    if (!/^\d{4}-(0[1-9]|1[0-2])$/.test(q.month)) {
      out.push({ key: "month", words: `Month: "${q.month.slice(0, 24)}" is not a month as the address writes one (YYYY-MM), so ${monthName(month)} is shown.` });
    } else {
      const o = GRIDS.find((g) => g.slug === OTHER_SOURCE[grid.slug]);
      const there = o && (months[o.slug] ?? []).includes(q.month) ? { grid: o, month: q.month } : undefined;
      out.push({ key: "month", other: there,
        words: `${monthName(q.month)} is not held for ${sourceName(grid)}, which holds ${held.length} months from ${monthName(held[0])} to ${monthName(held[held.length - 1])}, so ${monthName(month)} is shown.` });
    }
  }
  return out;
}

/** Session 7512: the months two grids both hold, oldest first (California by EIA-930 and by CAISO's own data: six
 * months of 2025). The page sets the two sources side by side over them; each figure is a row of the table. */
export function bothHold(rows: Row[], a: Grid, b: Grid): string[] {
  const of = (g: Grid) => new Set(rows.filter((r) => r.entity === g.entity && r.variable === "days_held").map((r) => monthOf(r.ts_utc)));
  const inB = of(b);
  return [...of(a)].filter((m) => inB.has(m)).sort();
}

/** Ruling alternative 5 of /shoulder (session 7703, branch wip/alt-shoulder-5; not a default on main): where the table's
 * month carries fleet_from_monitor, its fleet is a market monitor's year-end count (warehouse/derived/shoulder_hours.py
 * MONITOR_FLEET), and the page names the document. */
export const MONITOR_DOCS: Record<string, string> = {
  "iso:ercot": "Potomac Economics, 2025 State of the Market Report for the ERCOT Electricity Markets, June 2026, page ii: \"more than 17,000 MW\" and 31,500 MWh, read as 17,000 MW",
  "iso:caiso": "CAISO Department of Market Monitoring, 2025 Annual Report on Market Issues and Performance, June 2026, page 23: \"over 17 GW\", read as 17,000 MW; no MWh is given",
  "iso:caiso_own": "CAISO Department of Market Monitoring, 2025 Annual Report on Market Issues and Performance, June 2026, page 23: \"over 17 GW\", read as 17,000 MW; no MWh is given",
};

export type Series = "demand" | "solar" | "wind" | "net_load" | "battery";
export type View = {
  grid: Grid; month: string; months: string[];
  hour: (s: Series, h: number) => Row | undefined;
  get: (v: string) => Row | undefined;
  hasBattery: boolean;
  monthly: { month: string; shoulder?: Row; covered?: Row; needed?: Row; fleetHours?: Row }[];
  years: { year: string; get: (v: string) => Row | undefined }[];
  /** session 80: the ten worst days of the selected month's year, in rank order; empty when the table holds none */
  worst: { day: string; get: (v: string) => Row | undefined }[];
  /** the selected month's year: its yearly rows */
  year: { year: string; get: (v: string) => Row | undefined };
};

export function view(rows: Row[], grid: Grid, month: string): View {
  const ix = index(rows);
  const at = (v: string, m: string) => ix.get(`${grid.entity}|${v}|${m}`);
  const months = [...new Set(rows.filter((r) => r.entity === grid.entity && r.variable === "days_held").map((r) => monthOf(r.ts_utc)))].sort();
  const years = [...new Set(rows.filter((r) => r.entity === grid.entity && r.variable === "year_months_held").map((r) => monthOf(r.ts_utc)))].sort();
  return {
    grid, month, months,
    hour: (s, h) => at(`avg_${s}_mw_h${String(h).padStart(2, "0")}`, month),
    get: (v) => at(v, month),
    hasBattery: !!at("avg_battery_mw_h00", month),
    monthly: months.map((m) => ({ month: m, shoulder: at("shoulder_hours", m), covered: at("shoulder_hours_covered", m), needed: at("shoulder_hours_needed", m), fleetHours: at("fleet_hours", m) })),
    years: years.map((y) => ({ year: y.slice(0, 4), get: (v: string) => at(v, y) })),
    worst: worstDays(rows, grid, month.slice(0, 4)),
    year: { year: month.slice(0, 4), get: (v: string) => at(v, `${month.slice(0, 4)}-01`) },
  };
}

/** Session 80: a grid's ranked days of one local year, from the table's daily rows (worst_rank and day_*). */
export function worstDays(rows: Row[], grid: Grid, year: string) {
  const byDay = new Map<string, Map<string, Row>>();
  for (const r of rows) {
    if (r.entity !== grid.entity || !DAILY(r.variable) || !r.ts_utc.startsWith(year)) continue;
    const d = dayOf(r.ts_utc);
    if (!byDay.has(d)) byDay.set(d, new Map());
    byDay.get(d)!.set(r.variable, { ...r, ts_utc: `${d}T00:00:00Z` });
  }
  return [...byDay.entries()].filter(([, m]) => m.has("worst_rank"))
    .sort((a, b) => a[1].get("worst_rank")!.value - b[1].get("worst_rank")!.value)
    .map(([day, m]) => ({ day, get: (v: string) => m.get(v) }));
}
