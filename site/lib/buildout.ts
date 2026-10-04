// Energy Research Warehouse (ERW) site, session 69: the storage build-out page's model (/storage/buildout).
//
// Pure functions over rows of storage_buildout_monthly (warehouse/derived/storage_buildout.py,
// docs/methods/storage_buildout.md): which months the page reads, and the values it shows for one grid. Nothing here
// reads Supabase or a file, and nothing computes a number: every value on the page is a row of the table, so
// scripts/check-values.mjs can check each one by its key. The page's reader is app/storage/buildout/read.ts; the
// tests feed the same functions from a fixture (scripts/test-buildout.mjs).

export const TABLE = "storage_buildout_monthly";
export const FIRST_YEAR = 2015;

export type Row = { entity: string; variable: string; ts_utc: string; value: number };
export type Measure = "mw" | "mwh";

export const GRIDS = [
  { slug: "us", entity: "us:total", label: "United States", name: "The United States" },
  { slug: "caiso", entity: "iso:caiso", label: "CAISO", name: "CAISO" },
  { slug: "ercot", entity: "iso:ercot", label: "ERCOT", name: "ERCOT" },
  { slug: "isone", entity: "iso:isone", label: "ISO-NE", name: "ISO-NE" },
  { slug: "miso", entity: "iso:miso", label: "MISO", name: "MISO" },
  { slug: "nyiso", entity: "iso:nyiso", label: "NYISO", name: "NYISO" },
  { slug: "pjm", entity: "iso:pjm", label: "PJM", name: "PJM" },
  { slug: "spp", entity: "iso:spp", label: "SPP", name: "SPP" },
] as const;
export type Grid = (typeof GRIDS)[number];
export const OUTSIDE = { slug: "outside", entity: "us:outside_isos", label: "Outside the ISOs" } as const;

// the duration buckets, shortest first; the chart draws them light to dark in this order
export const BUCKETS = [
  { key: "lt2h", label: "Under 2 hours" },
  { key: "2to4h", label: "2 to under 4 hours" },
  { key: "4to6h", label: "4 to under 6 hours" },
  { key: "ge6h", label: "6 hours and more" },
] as const;
export const NOT_REPORTED = { key: "energy_not_reported", label: "Energy not reported" } as const;

export const MEASURES: Record<Measure, { label: string; unit: string }> = {
  mw: { label: "Power, MW", unit: "MW" },
  mwh: { label: "Energy, MWh", unit: "MWh" },
};

/** The grid and measure a query string names; the United States in MW when it names none or a wrong one. */
export function choices(q: Record<string, string | undefined>): { grid: Grid; measure: Measure } {
  return { grid: GRIDS.find((g) => g.slug === q.grid) ?? GRIDS[0], measure: q.measure === "mwh" ? "mwh" : "mw" };
}

export const tsOf = (month: string) => `${month}-01T00:00:00Z`;
export const monthOf = (ts: string) => ts.slice(0, 7);
export const yearBefore = (month: string) => `${Number(month.slice(0, 4)) - 1}${month.slice(4)}`;

/** The months the page reads, oldest first: every December from 2015 to the year before the newest month, the newest
 * month, and the month twelve before it. */
export function monthsNeeded(newest: string): string[] {
  const y = Number(newest.slice(0, 4));
  const ms = new Set<string>([newest, yearBefore(newest)]);
  for (let k = FIRST_YEAR; k < y; k++) ms.add(`${k}-12`);
  return [...ms].sort();
}

const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
/** "August 2026" from "2026-08". */
export const monthName = (m: string) => `${MONTHS[Number(m.slice(5, 7)) - 1]} ${m.slice(0, 4)}`;

export type Lookup = (entity: string, variable: string, month: string) => Row | undefined;

/** Rows by (entity, variable, month), and the newest month any row holds. */
export function index(rows: Row[]): { get: Lookup; newest: string | null } {
  const by = new Map<string, Row>();
  let newest: string | null = null;
  for (const r of rows) {
    const m = monthOf(r.ts_utc);
    by.set(`${r.entity}|${r.variable}|${m}`, r);
    if (newest === null || m > newest) newest = m;
  }
  return { get: (e, v, m) => by.get(`${e}|${v}|${m}`), newest };
}

/** One bar of the chart by year: a year's end, or the newest month for the year in progress. */
export type YearPoint = {
  month: string;
  label: string; // "2024", or "2026 to August" for the year in progress
  total: Row | undefined;
  buckets: { key: string; label: string; row: Row | undefined }[];
  notReported: Row | undefined; // MW of units with no energy value (in the MW chart; the MWh chart cannot hold them)
  hours: Row | undefined;
  solar: Row | undefined;
  perSolar: Row | undefined;
};

export type View = {
  grid: Grid;
  measure: Measure;
  newest: string;
  before: string;
  mw: Row | undefined;
  mwh: Row | undefined;
  hours: Row | undefined;
  units: Row | undefined;
  mwBefore: Row | undefined;
  mwhBefore: Row | undefined;
  addedMw: Row | undefined;
  addedMwh: Row | undefined;
  notReportedMw: Row | undefined;
  years: YearPoint[];
  plannedYears: string[];
  table: GridLine[];
};

export type GridLine = {
  slug: string;
  label: string;
  entity: string;
  mw: Row | undefined;
  mwh: Row | undefined;
  hours: Row | undefined;
  units: Row | undefined;
  addedMw: Row | undefined;
  addedMwh: Row | undefined;
  planned: Row | undefined;
  underConstruction: Row | undefined;
  plannedByYear: { year: string; row: Row | undefined }[];
};

/** Everything the page shows for one grid and measure. Null when the rows hold no month. */
export function view(rows: Row[], grid: Grid, measure: Measure): View | null {
  const { get, newest } = index(rows);
  if (!newest) return null;
  const before = yearBefore(newest);
  const e = grid.entity;
  const plannedYears = [...new Set(rows.filter((r) => r.variable.startsWith("battery_planned_mw_online_") && monthOf(r.ts_utc) === newest)
    .map((r) => r.variable.slice(-4)))].sort();
  const months = monthsNeeded(newest).filter((m) => m === newest || m.endsWith("-12"));
  const years = months.map((m): YearPoint => ({
    month: m,
    label: m.endsWith("-12") ? m.slice(0, 4) : `${m.slice(0, 4)} to ${MONTHS[Number(m.slice(5, 7)) - 1]}`,
    total: get(e, `battery_operating_${measure}`, m),
    buckets: BUCKETS.map((b) => ({ key: b.key, label: b.label, row: get(e, `battery_operating_${measure}_${b.key}`, m) })),
    notReported: get(e, `battery_operating_mw_${NOT_REPORTED.key}`, m),
    hours: get(e, "battery_operating_mwh_per_mw", m),
    solar: get(e, "solar_operating_mw", m),
    perSolar: get(e, "battery_mwh_per_solar_mw", m),
  }));
  const line = (g: { slug: string; label: string; entity: string }): GridLine => ({
    slug: g.slug, label: g.label, entity: g.entity,
    mw: get(g.entity, "battery_operating_mw", newest),
    mwh: get(g.entity, "battery_operating_mwh", newest),
    hours: get(g.entity, "battery_operating_mwh_per_mw", newest),
    units: get(g.entity, "battery_operating_units", newest),
    addedMw: get(g.entity, "battery_operating_mw_net_added_12m", newest),
    addedMwh: get(g.entity, "battery_operating_mwh_net_added_12m", newest),
    planned: get(g.entity, "battery_planned_mw", newest),
    underConstruction: get(g.entity, "battery_planned_mw_under_construction", newest),
    plannedByYear: plannedYears.map((y) => ({ year: y, row: get(g.entity, `battery_planned_mw_online_${y}`, newest) })),
  });
  return {
    grid, measure, newest, before,
    mw: get(e, "battery_operating_mw", newest),
    mwh: get(e, "battery_operating_mwh", newest),
    hours: get(e, "battery_operating_mwh_per_mw", newest),
    units: get(e, "battery_operating_units", newest),
    mwBefore: get(e, "battery_operating_mw", before),
    mwhBefore: get(e, "battery_operating_mwh", before),
    addedMw: get(e, "battery_operating_mw_net_added_12m", newest),
    addedMwh: get(e, "battery_operating_mwh_net_added_12m", newest),
    notReportedMw: get(e, `battery_operating_mw_${NOT_REPORTED.key}`, newest),
    years,
    plannedYears,
    table: [...GRIDS.slice(1), OUTSIDE, GRIDS[0]].map(line),
  };
}

/** A number as the page writes it and scripts/check-values.mjs expects it: whole with separators, else 2 decimals. */
export function shown(v: number): string {
  return Number.isInteger(v) ? v.toLocaleString("en-US") : v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

/** Session 90: MW and MWh are written without decimals. EIA reports a unit to a tenth of a megawatt, and a fleet of
 * 54,489 MW gains nothing from ".30". A half rounds up, as a reader rounds it and as the rest of the site does
 * (lib/format.ts count). The value read from the table is unchanged: it is in the number's data-raw. */
export function whole(v: number): string {
  return Math.round(v).toLocaleString("en-US");
}
/** The variables that are MW or MWh: the fleet's power and energy, their duration buckets, what was added and what is
 * planned, and solar's MW. Not the two ratios (MWh per MW, and MWh per MW of solar), which are hours and keep their
 * decimals, nor the counts of units, which are whole already. scripts/check-values.mjs holds the same pattern. */
export const WHOLE = /^(battery|solar)_(operating|planned)_(mw|mwh)(?!_per_)(_|$)/;
/** A value of the table as the page writes it: MW and MWh whole, everything else as `shown`. */
export function written(variable: string, v: number): string {
  return WHOLE.test(variable) ? whole(v) : shown(v);
}

/** The check key of a row, as scripts/check-values.mjs reads series values: series|<table>|<entity>|<variable>|<ts>. */
export const checkKey = (r: Row) => `series|${TABLE}|${r.entity}|${r.variable}|${tsOf(monthOf(r.ts_utc))}`;

/** "up from", "down from" or "unchanged from", by the two MW values of the summary sentence. */
export function direction(now: number, before: number): string {
  return now > before ? "up from" : now < before ? "down from" : "unchanged from";
}
