// Energy Research Warehouse (ERW) site: the question-answering tools, over the Supabase live set.
//
// The same four tools as warehouse/chat/tools.py (list_tables, describe_table, query, compare),
// with the same input schemas (lib/chat/spec.json, exported from the Python loop) and the same
// fixed aggregations and groupings. The Python tools read the erw package; these read Supabase
// with the anon key, so they see public tables only, and only the live set: the last 35 days of
// power prices and demand, and the derived, fuel, generator, queue and news tables whole.
// Differences from the Python tools are named where they occur.
import "server-only";
import { DataError, HOURLY, rest, restCount } from "@/lib/supabase";
import spec from "./spec.json";
import { DOCS, type GridConfig } from "@/lib/markdown";
import { LIFE_MS, keep, within, type Summary } from "./summaries";
import { hourlyRefusal } from "./rollup";
import { HOUR_OF_DAY, NEWEST, THIS_WEEK, NEWEST_READ, NEWEST_READ_DATED, dateColumns, dateLabel, hourFamily, newestWholeDay, stepsPerHour } from "./forms";
import { addLocalTimes, zoneOfEntity } from "./plaintime";

// Session 35: a scoped chat (/ask?grid=<slug>): one grid's tables (docs/grids/grids.json) and its rows only, as
// warehouse/chat/tools.py set_scope does. null: the whole live set.
// Session 92: a profile's scope (lib/chat/ercot.ts) also names each table's rows outright (filters: {table: {column:
// value or values}}, as warehouse/chat/tools.py scope_rows) and may raise the rows one grouped result returns.
// Session 148: a profile's scope may name an hourly table that has tables of days and months beside it (lib/chat/rollup.ts):
// while every one of `tables` is in the live set, a query of `hourly` must give a start and span a few weeks at most.
export type Scope = (GridConfig & { filters?: Record<string, Record<string, string | string[]>>; max_groups?: number; dated_groups?: boolean; rollup?: { hourly: string; tables: string[] } }) | null;
export const scopeOf = (slug: string | null | undefined): Scope => (slug ? DOCS.grid_config.find((g) => g.slug === slug) ?? null : null);
const BA_TABLES = new Set(["eia930_all_demand", "eia930_all_generation", "eia930_all_emissions", "eia930_all_storage", "eia930_all_interchange",
  "carbon_intensity_hourly", "carbon_intensity_daily", "carbon_intensity_monthly", "storage_daily_cycle"]);

/** The PostgREST filters that keep a table's rows of the scoped grid. */
function scopeFilter(scope: Scope, name: string, shape: Shape, columns: string[]): Record<string, string> {
  if (!scope) return {};
  const f = scope.filters?.[name];
  if (f) {
    // a series table keeps only its standard columns in Supabase: a filter on another column cannot be applied here
    const out: Record<string, string> = {};
    for (const [col, val] of Object.entries(f)) {
      if (shape === "series" && !SHAPE_COLS.series.includes(col)) throw new ToolError(`${name} cannot be read for ${scope.iso} alone on this site: its column ${col} is not in the site's copy`);
      out[colRef(shape, col)] = `in.(${(Array.isArray(val) ? val : [val]).map((v) => quote(v)).join(",")})`;
    }
    return out;
  }
  if (shape === "series" && BA_TABLES.has(name)) return { ba: `eq.${scope.ba}` };
  if (name === "storage_capacity") return { "extra->>iso": `eq.${scope.iso}` };
  if (name === "energy_projects") return { entity_id: `like.${(scope.queue_table ?? "none").replace(/_interconnection_queue$/, "_queue")}:*` };
  if (shape === "series" && scope.market_prefix && columns.includes("market")) return { market: `like.${scope.market_prefix}*` };
  return {};
}

export class ToolError extends Error {}

type Json = Record<string, unknown>;
type Shape = "series" | "entities" | "events";

type Cat = {
  table_name: string;
  iso: string | null;
  interval: string | null;
  ts_min: string | null;
  ts_max: string | null;
  n_rows: number | null;
  source_report: string | null;
  last_run: string | null;
  license: string;
  sector: string | null;
  derived: string | null;
  tier: string | null;
  in_live_set: string;
  columns: string | null;
};

const SHAPE_COLS: Record<Shape, string[]> = {
  series: ["entity", "variable", "ts_utc", "value", "unit", "freq", "geo", "market", "node", "source", "source_url", "retrieved_at", "vintage"],
  entities: ["entity_id", "entity_type", "name", "geo", "lat", "lon", "capacity_mw", "status", "status_date", "operator", "source", "source_url", "retrieved_at", "vintage"],
  events: ["event_id", "event_date", "event_type", "parties", "entity_ids", "mw", "price", "currency", "status", "source", "source_url"],
};
const TIME_COL: Record<Shape, string> = { series: "ts_utc", entities: "status_date", events: "event_date" };
const DEFAULT_VALUE: Record<Shape, string> = { series: "value", entities: "capacity_mw", events: "mw" };
const MAX_GROUPS: number = spec.max_groups;
const DIGITS: number = spec.digits;
const AGGREGATIONS: string[] = spec.aggregations;
const TIME_GROUPS: string[] = spec.time_groups;
const MAX_ROWS = 60_000; // rows one query may read from Supabase
const LIVE_NOTE =
  "This site reads the Supabase live set: public tables only; the interval tables of power prices, demand, generation and hourly emissions hold only their last 35 days; derived, fuel, generator, queue and news tables are whole, and so are ERCOT's hub prices by day (ercot_hub_prices_daily, since 2015) and its reserve prices (ercot_as_prices, since 2018). Tables with in_live_set no cannot be queried here (their full history is on Redivis).";

// ------------------------------------------------------------------ helpers

let catCache: { at: number; rows: Cat[] } | null = null;
async function catalogue(): Promise<Cat[]> {
  if (catCache && Date.now() - catCache.at < 600_000) return catCache.rows;
  const rows = await rest<Cat>("catalogue", { select: "*", order: "table_name" }, 600); // session 143: ten minutes, as the summaries that are read from it
  if (!rows.length) throw new DataError("the catalogue returned no rows");
  catCache = { at: Date.now(), rows };
  return rows;
}

async function tableInfo(name: string, scope: Scope = null) {
  const c = (await catalogue()).find((r) => r.table_name === name);
  if (!c) throw new ToolError(`no public table named ${JSON.stringify(name)}; call list_tables for the table names`);
  if (scope && !scope.tables.includes(name)) throw new ToolError(`${name} does not carry ${scope.iso}; this chat reads only ${scope.iso}'s tables (list_tables)`);
  // session 102: "review" is a table loaded for a page in review (live_set.yaml, review_hold); Ask is in review too
  if (c.in_live_set !== "yes" && c.in_live_set !== "review") throw new ToolError(`table ${name} is not in this site's live set; its full history is on Redivis`);
  const columns: string[] = c.columns ? JSON.parse(c.columns) : [];
  const shape: Shape = columns[0] === "entity_id" ? "entities" : columns[0] === "event_id" ? "events" : "series";
  return { c, columns, shape };
}

/** Session 148: whether every one of these tables is in the site's live set now, by the catalogue (kept ten minutes). */
async function allHeld(names: string[]): Promise<boolean> {
  const rows = await catalogue();
  return names.every((n) => rows.some((r) => r.table_name === n && (r.in_live_set === "yes" || r.in_live_set === "review")));
}

const round = (x: number) => Math.round(x * 10 ** DIGITS) / 10 ** DIGITS;
const quote = (v: string) => `"${v.replace(/\\/g, "\\\\").replace(/"/g, '\\"')}"`;
const colRef = (shape: Shape, col: string) => (SHAPE_COLS[shape].includes(col) ? col : `extra->>${col}`);

function isoTs(v: unknown): string | null {
  if (v === null || v === undefined || v === "") return null;
  const s = String(v);
  if (/^\d{4}-\d{2}-\d{2}$/.test(s)) return s;
  const d = new Date(s);
  return Number.isNaN(d.getTime()) ? s : d.toISOString().replace(/\.\d{3}Z$/, "Z");
}

/** Offset of a time zone from UTC at a UTC instant, in milliseconds. */
function tzOffsetMs(utcMs: number, tz: string): number {
  let parts: Intl.DateTimeFormatPart[];
  try {
    parts = new Intl.DateTimeFormat("en-US", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit", hourCycle: "h23" }).formatToParts(new Date(utcMs));
  } catch {
    throw new ToolError(`unknown time zone ${JSON.stringify(tz)}; use an IANA name such as America/Chicago`);
  }
  const p = Object.fromEntries(parts.map((x) => [x.type, x.value]));
  return Date.UTC(+p.year, +p.month - 1, +p.day, +p.hour, +p.minute, +p.second) - utcMs;
}

/**
 * A start or end bound as an ISO UTC time. A time with Z or an offset is taken as given; a date
 * or a time without one is read in tz (session 13, as warehouse/chat/tools.py: it was always read
 * as UTC, so local-day questions got the UTC day).
 */
function parseTime(v: string, tz: string): string {
  if (/([zZ]|[+-]\d{2}:?\d{2})$/.test(v)) {
    const d = new Date(v);
    if (Number.isNaN(d.getTime())) throw new ToolError(`cannot read the time ${JSON.stringify(v)}; use ISO 8601`);
    return d.toISOString();
  }
  const m = v.match(/^(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2}))?)?$/);
  if (!m) throw new ToolError(`cannot read the time ${JSON.stringify(v)}; use ISO 8601`);
  const wall = Date.UTC(+m[1], +m[2] - 1, +m[3], +(m[4] ?? 0), +(m[5] ?? 0), +(m[6] ?? 0));
  let utc = wall - tzOffsetMs(wall, tz);
  const second = wall - tzOffsetMs(utc, tz); // across a daylight saving change, the offset at the result wins
  if (second !== utc) utc = second;
  return new Date(utc).toISOString();
}

/** numpy.percentile(x, p) with the default linear method. */
function percentile(sorted: number[], p: number): number {
  const pos = ((sorted.length - 1) * p) / 100;
  const lo = Math.floor(pos), hi = Math.ceil(pos);
  return sorted[lo] + (sorted[hi] - sorted[lo]) * (pos - lo);
}

function tzKey(ts: string, tz: string, group: string): string {
  let parts: Intl.DateTimeFormatPart[];
  try {
    parts = new Intl.DateTimeFormat("en-CA", { timeZone: tz, year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", hourCycle: "h23" }).formatToParts(new Date(ts));
  } catch {
    throw new ToolError(`unknown time zone ${JSON.stringify(tz)}; use an IANA name such as America/Chicago`);
  }
  const p = Object.fromEntries(parts.map((x) => [x.type, x.value]));
  return { year: p.year, month: `${p.year}-${p.month}`, day: `${p.year}-${p.month}-${p.day}`, hour: `${p.year}-${p.month}-${p.day} ${p.hour}:00` }[group]!;
}

async function sourceReports(c: Cat) {
  const ids = (c.source_report ?? "").split(";").map((s) => s.trim()).filter(Boolean);
  if (!ids.length) return [];
  return rest<{ source: string; publisher: string | null; report: string | null; report_url: string | null }>(
    "sources",
    { select: "source,publisher,report,report_url", source: `in.(${ids.map(quote).join(",")})` },
    HOURLY,
  );
}

async function provenance(name: string): Promise<Json> {
  const { c } = await tableInfo(name);
  const reports = await sourceReports(c).catch(() => []);
  const last = isoTs(c.last_run);
  const cite =
    reports.map((r) => `${r.publisher ?? r.source.split(":")[0].toUpperCase()}. ${r.source.split(":").slice(1).join(":")}${r.report ? `: ${r.report}` : ""}.${r.report_url ? ` ${r.report_url}.` : ""}`).join(" ") +
    `${last ? ` Retrieved ${last.slice(0, 10)}` : ""} via the ERW, table ${name}, Supabase live set.`;
  return {
    table: name,
    data_version: `Supabase live set (public site)${last ? `; table last run ${last}` : ""}`,
    source_report: c.source_report,
    license: c.license,
    // session 28: source, derived or model_extracted (docs/datastandard.md)
    tier: c.tier,
    citation: cite,
  };
}

// ------------------------------------------------------------------ list_tables

async function listTables(a: { sector?: string; license?: string; iso?: string }, scope: Scope = null): Promise<Json> {
  let rows = await catalogue();
  if (scope) rows = rows.filter((r) => scope.tables.includes(r.table_name)); // session 35
  if (a.sector) rows = rows.filter((r) => (r.sector ?? "").split(";").includes(a.sector!));
  if (a.license) rows = rows.filter((r) => r.license === a.license);
  // session 35, as tools.py: a consolidated table lists its ISOs joined by ";"
  if (a.iso) rows = rows.filter((r) => (r.iso ?? "").toUpperCase().split(";").includes(a.iso!.toUpperCase()));
  return {
    n_tables: rows.length,
    tables: rows.map((r) => ({
      table: r.table_name,
      sector: (r.sector ?? "").split(";").join(", "),
      license: r.license,
      iso: r.iso,
      interval: r.interval,
      first: isoTs(r.ts_min),
      last: isoTs(r.ts_max),
      rows: r.n_rows,
      source_report: r.source_report,
      derived: r.derived,
      tier: r.tier,
      in_live_set: r.in_live_set,
    })),
    backend: "supabase",
    note: `${LIVE_NOTE} first, last and rows describe the whole ERW table, not the live set. Internal tables are not visible here.`,
  };
}

// ------------------------------------------------------------------ describe_table

async function describeTable(a: { table: string }, scope: Scope = null): Promise<Json> {
  const { c, columns, shape } = await tableInfo(a.table, scope);
  const base = { table_name: `eq.${a.table}`, ...scopeFilter(scope, a.table, shape, columns) };
  const tcol = TIME_COL[shape];
  const [n, firstRow, lastRow] = await Promise.all([
    restCount(shape, base, HOURLY),
    rest<Json>(shape, { ...base, select: tcol, order: `${tcol}.asc.nullslast` }, HOURLY, 1),
    rest<Json>(shape, { ...base, select: tcol, order: `${tcol}.desc.nullslast` }, HOURLY, 1),
  ]);
  const out: Json = {
    shape,
    rows_in_live_set: n,
    columns,
    first: isoTs(firstRow[0]?.[tcol]),
    last: isoTs(lastRow[0]?.[tcol]),
    source_reports: await sourceReports(c).catch(() => "unavailable"),
  };
  if (shape === "series") {
    const rows = await rest<{ entity: string; node: string | null; variable: string; unit: string; freq: string }>(
      "series", { ...base, select: "entity,node,variable,unit,freq", order: "entity,variable,ts_utc" }, HOURLY, MAX_ROWS);
    const uniq = (xs: (string | null)[]) => Array.from(new Set(xs.filter((x): x is string => !!x))).sort();
    const ents = uniq(rows.map((r) => r.entity));
    Object.assign(out, {
      entities: ents.slice(0, 80), n_entities: ents.length,
      nodes: uniq(rows.map((r) => r.node)).slice(0, 80),
      variables: uniq(rows.map((r) => r.variable)).slice(0, 80),
      units: uniq(rows.map((r) => r.unit)), freq: uniq(rows.map((r) => r.freq)),
    });
  } else {
    // Unlike the Python tool, which counts every value, this lists the values seen in a
    // sample of rows (reading a whole generator table per question would be too slow here).
    const sample = await rest<Json>(shape, { ...base, select: "*", order: shape === "entities" ? "entity_id" : "event_id" }, HOURLY, 2000);
    const vals: Record<string, Set<string>> = {};
    for (const r of sample) {
      const flat = { ...r, ...((r.extra as Json) ?? {}) };
      for (const col of columns) {
        if (["entity_id", "event_id", "name", "source_url", "headline", "retrieved_at", "lat", "lon"].includes(col)) continue;
        const v = flat[col];
        if (v === null || v === undefined || v === "" || typeof v === "number") continue;
        (vals[col] ??= new Set()).add(String(v));
      }
    }
    out.text_column_values = Object.fromEntries(
      Object.entries(vals).filter(([, s]) => s.size <= 60).map(([k, s]) => [k, Array.from(s).sort()]),
    );
    out.text_column_values_note = `values seen in the first ${sample.length} rows, without counts; use query with aggregation count to count`;
    out.time_column = tcol;
  }
  const hdr = await rest<{ line: string }>("headers", { select: "line", table_name: `eq.${a.table}`, order: "line_no" }, HOURLY, 12).catch(() => []);
  out.notes = hdr.map((h) => h.line).filter((l) => /^(Note|Notes|Method|License|Last input)/i.test(l)).slice(0, 5);
  Object.assign(out, await provenance(a.table));
  return out;
}

// ------------------------------------------------------------------ held ready (session 143)

// describe_table reads up to 60,000 rows to list a table's names. Its answer is kept ten minutes (lib/chat/summaries.ts),
// so a second question that asks it waits for nothing. The answer is the tool's own, unchanged.
const describeArgs = new Map<string, [{ table: string }, Scope]>();
const described = keep<Json>(LIFE_MS, (k) => { const [a, sc] = describeArgs.get(k)!; return describeTable(a, sc); });
async function describeHeld(a: { table: string }, scope: Scope = null): Promise<Json> {
  const k = `${scope?.slug ?? ""}|${a.table}`;
  describeArgs.set(k, [a, scope]);
  return { ...(await described.get(k)) };
}

const SUMMARY_READ = 600; // seconds a summary's own reads are kept by the data cache: no longer than the summary lives
type Held = Summary & { at: string };
// A table's summary is its row of the catalogue (its first and last date as of its last load: one small read serves
// every table) and, where asked, the variable names of its newest period (one small read). A first version read each
// table's own first and last row for the grid: on the large interval tables that read took seconds and was cancelled,
// every question sent it again, and every question waited for it. A read that fails is kept as unread for the summary's
// life, so that a failing read is sent once in ten minutes and not once a question.
async function readSummary(name: string, scope: Scope, wantVariables: boolean): Promise<Held> {
  const at = new Date().toISOString();
  try {
    const { c, shape, columns } = await tableInfo(name, scope);
    const out: Held = { table: name, first: isoTs(c.ts_min), last: isoTs(c.ts_max), rows: null, held: true, dated: shape === "series", at };
    if (wantVariables && shape === "series" && out.last) {
      const base = { table_name: `eq.${name}`, ...scopeFilter(scope, name, shape, columns) };
      const rows = await rest<{ variable: string }>("series", { ...base, select: "variable", ts_utc: `eq.${out.last}`, order: "variable" }, SUMMARY_READ, 3000);
      out.variables = Array.from(new Set(rows.map((r) => r.variable))).sort();
    }
    return out;
  } catch (e) {
    if (e instanceof ToolError) return { table: name, first: null, last: null, rows: null, held: false, at };   // not in the live set, or not readable for this grid
    console.error(`[erw ask] summary of ${name}: ${(e as Error).message}`);
    return { table: name, first: null, last: null, rows: null, held: true, unread: true, at };
  }
}
const summaryArgs = new Map<string, [string, Scope, boolean]>();
const summaries = keep<Held>(LIFE_MS, (k) => { const [name, sc, v] = summaryArgs.get(k)!; return readSummary(name, sc, v); });

/** Session 143: each table's summary for a scope (its first and last date and its rows in the live set; for the tables
 * named in `withVariables`, the variables of its newest period), from the server's memory when it is under ten minutes
 * old. A question waits at most `waitMs` for a summary that is not ready: the table is then left out of this answer's
 * list and is ready for the next. `readAt` is the oldest reading among those returned. */
export async function tableSummaries(scope: Scope, names: string[], withVariables: string[] = [], waitMs = 1500): Promise<{ rows: Summary[]; readAt: string | null }> {
  const got = await Promise.all(names.map((name) => {
    const k = `${scope?.slug ?? ""}|${name}`;
    summaryArgs.set(k, [name, scope, withVariables.includes(name)]);
    return within(summaries.get(k), waitMs);
  }));
  const rows = got.filter((x): x is Held => x !== null && !x.unread);
  const bare = (h: Held): Summary => { const s: Partial<Held> = { ...h }; delete s.at; return s as Summary; };
  return { rows: rows.map(bare), readAt: rows.length ? rows.map((r) => r.at).sort()[0] : null };
}

// ------------------------------------------------------------------ query

type QueryArgs = {
  table: string;
  aggregation: string;
  entity?: string;
  variable?: string;
  start?: string;
  end?: string;
  where?: Record<string, string | string[]>;
  percentile?: number;
  value_column?: string;
  group_by?: string;
  tz?: string;
  /** session 156 (lib/chat/forms.ts): a date column of an entities or events table to group and bound by; "newest" for the newest whole day held */
  date_column?: string;
  day?: string;
};

type Row = { t: string | null; v: number | null; g: string | null; entity?: string; variable?: string; unit?: string; id?: string };

function aggregate(rows: Row[], agg: string, pct: number | undefined, shape: Shape): Json {
  if (agg === "count") return { count: rows.length };
  if (!rows.length) return { value: null, n: 0 };
  if (agg === "latest") {
    const withT = rows.filter((r) => r.t);
    if (!withT.length) throw new ToolError("latest needs a time column");
    const r = withT.reduce((a, b) => (new Date(b.t!) > new Date(a.t!) ? b : a));
    const out: Json = { value: r.v === null ? null : round(r.v), at: isoTs(r.t) };
    if (shape === "series") Object.assign(out, { entity: r.entity, variable: r.variable, unit: r.unit });
    return out;
  }
  const vs = rows.filter((r) => r.v !== null && !Number.isNaN(r.v));
  if (!vs.length) return { value: null, n: 0 };
  if (agg === "min" || agg === "max") {
    const r = vs.reduce((a, b) => ((agg === "min" ? b.v! < a.v! : b.v! > a.v!) ? b : a));
    const out: Json = { value: round(r.v!), n: vs.length, at: isoTs(r.t) };
    if (shape === "series") out.entity = r.entity;
    else if (shape === "entities") out.entity_id = r.id;
    return out;
  }
  const xs = vs.map((r) => r.v!).sort((a, b) => a - b);
  if (agg === "percentile") {
    if (pct === undefined || pct < 0 || pct > 100) throw new ToolError("percentile needs a percentile value from 0 to 100");
    return { value: round(percentile(xs, pct)), n: xs.length };
  }
  if (agg === "median") return { value: round(percentile(xs, 50)), n: xs.length };
  const sum = xs.reduce((a, b) => a + b, 0);
  return { value: round(agg === "sum" ? sum : sum / xs.length), n: xs.length };
}

/** Session 143: the summary of a grouped result: its lowest and highest row, its first and last, the change between
 * them, the mean and the median of the rows' values, and the same aggregation over every matched row at once. Computed
 * here, by the tool, from the rows of the result itself (every group, also those past the number shown), so that the
 * model reads them and computes nothing. null for a result of fewer than two rows with a value. */
export function groupSummary(g: string, res: Json[], rows: Row[], agg: string, pct: number | undefined, shape: Shape): Json | null {
  const vals = res.map((r) => ({ key: r[g], v: (r.value ?? r.count) as number | null | undefined })).filter((x): x is { key: unknown; v: number } => typeof x.v === "number" && Number.isFinite(x.v));
  if (vals.length < 2) return null;
  const pick = (x: { key: unknown; v: number }) => ({ [g]: x.key, value: x.v });
  const lowest = vals.reduce((a, b) => (b.v < a.v ? b : a)), highest = vals.reduce((a, b) => (b.v > a.v ? b : a));
  const first = vals[0], last = vals[vals.length - 1];
  const sorted = vals.map((x) => x.v).sort((a, b) => a - b);
  const sum = sorted.reduce((a, b) => a + b, 0);
  const out: Json = {
    rows: vals.length, lowest: pick(lowest), highest: pick(highest), first: pick(first), last: pick(last),
    change_first_to_last: round(last.v - first.v), mean_of_rows: round(sum / sorted.length), median_of_rows: round(percentile(sorted, 50)),
  };
  if (agg === "sum" || agg === "count") out.sum_of_rows = round(sum);
  if (agg !== "latest") out.all_rows_together = aggregate(rows, agg, pct, shape);
  out.note = "lowest, highest, first and last are rows of this result; mean_of_rows and median_of_rows are over the rows' values; all_rows_together is the same aggregation over every matched row at once";
  return out;
}

const nextDay = (day: string) => new Date(Date.parse(`${day}T00:00:00Z`) + 86_400_000).toISOString().slice(0, 10);
const shiftDay = (day: string, n: number) => new Date(Date.parse(`${day}T00:00:00Z`) + n * 86_400_000).toISOString().slice(0, 10);

async function query(a: QueryArgs, scope: Scope = null): Promise<Json> {
  if (!AGGREGATIONS.includes(a.aggregation)) throw new ToolError(`aggregation must be one of ${AGGREGATIONS.join(", ")}`);
  const { c, columns, shape } = await tableInfo(a.table, scope);
  const tcol = TIME_COL[shape];
  const vcol = a.value_column ?? DEFAULT_VALUE[shape];
  if (a.aggregation !== "count" && !columns.includes(vcol)) throw new ToolError(`no column ${JSON.stringify(vcol)} in ${a.table}`);
  const tz = a.tz ?? "UTC";
  const g = a.group_by;
  // session 156: the average day by hour (lib/chat/forms.ts): 24 rows, "00" to "23", as one series
  const hod = g === HOUR_OF_DAY;
  if (g && !TIME_GROUPS.includes(g) && !hod && g !== "entity" && !columns.includes(g)) {
    throw new ToolError(`group_by must be one of ${[...TIME_GROUPS, HOUR_OF_DAY, "entity"].join(", ")} or a text column of the table`);
  }
  if (hod && shape !== "series") throw new ToolError(`group_by "${HOUR_OF_DAY}" applies to series tables only: an entities or events table has no hours`);
  const timed = !!g && TIME_GROUPS.includes(g);
  // session 156: a date column of an entities or events table, to group by (year, month, day) and to bound (start, end)
  const dcol = a.date_column;
  if (dcol !== undefined) {
    if (shape === "series") throw new ToolError("date_column applies to entities and events tables only: a series table's rows are grouped by their own time (group_by year, month, day or hour)");
    if (!columns.includes(dcol)) throw new ToolError(`no column ${JSON.stringify(dcol)} in ${a.table}; its date columns: ${dateColumns(columns).join(", ") || "none"}`);
    if (g === "hour") throw new ToolError("a date column gives a year, a month or a day, not an hour");
    for (const b of [a.start, a.end]) if (b !== undefined && !/^\d{4}-\d{2}-\d{2}$/.test(b)) throw new ToolError(`with date_column, start and end are plain dates (2027-01-01), not ${JSON.stringify(b)}`);
  }

  const sel = [`t:${dcol ? colRef(shape, dcol) : tcol}`];
  if (a.aggregation !== "count") sel.push(`v:${colRef(shape, vcol)}`);
  if (g && !timed && !hod) {
    const gc = g === "entity" ? { series: "entity", entities: "entity_id", events: "source" }[shape] : g;
    sel.push(`g:${colRef(shape, gc)}`);
  }
  if (shape === "series") sel.push("entity", "variable", "unit");
  if (shape === "series" && a.day === THIS_WEEK) sel.push("freq");   // session 161: the step, to say whether a day of the week is whole
  if (shape === "entities") sel.push("id:entity_id");
  // a read by a date column is in the order of the rows' own ids, so that a read of more than one page holds each row once
  const order = dcol ? (shape === "entities" ? "entity_id.asc" : "event_id.asc") : `${tcol}.asc.nullslast`;
  const q: Record<string, string> = { select: sel.join(","), table_name: `eq.${a.table}`, order, ...scopeFilter(scope, a.table, shape, columns) };
  if (a.entity && shape !== "series") {
    q.or = shape === "entities" ? `(entity_id.eq.${quote(a.entity)},name.eq.${quote(a.entity)})` : `(source.eq.${quote(a.entity)})`;
  }
  // session 20, as warehouse/chat/tools.py: a series table of days or longer labels each row with its
  // local date at 00:00Z (Decision 11), so a date bound is that label; reading it in tz returned the
  // next day's row (evaluation questions s20q10 and s20q12)
  const dated = shape === "series" && (c.interval ?? "").split(";").every((f) => ["P1D", "P1W", "P1M", "P1Y"].includes(f)) && !!c.interval;
  const btz = dated ? "UTC" : tz;
  // session 156: on a table of days or longer the hours of a day are its variables (avg_wind_mw_h00 to _h23): the 24 are
  // read in one request, with the table's own counts of days (a family of days beside a family of means; days_held)
  const family = hod && dated ? hourFamily(a.variable) : null;
  if (hod && dated && !family) {
    throw new ToolError(`${a.table} is a table of days or longer periods: its rows have no hour of their own. Where its variables are the hours of a day (names that end _h00 to _h23), give variable as the stem without the hour, for example "avg_wind_mw_h", with group_by "${HOUR_OF_DAY}"`);
  }
  const DAYS_HELD = "days_held";
  if (a.variable) {
    if (shape !== "series") throw new ToolError("variable applies to series tables only; use where for entities and events tables");
    q.variable = family ? `in.(${[...family.names, ...(family.days ?? []), DAYS_HELD].map(quote).join(",")})` : `eq.${a.variable}`;
  }
  for (const [col, val] of Object.entries(a.where ?? {})) {
    if (!columns.includes(col)) throw new ToolError(`no column ${JSON.stringify(col)} in this table; columns: ${columns.join(", ")}`);
    const vals = Array.isArray(val) ? val : [val];
    q[colRef(shape, col)] = `in.(${vals.map((v) => quote(String(v))).join(",")})`;
  }

  // Session 156: a series is asked for by its entity first. Until now the filter was "this entity or this node" in one
  // request, which the database answered about five times slower than "this entity" alone (session 148 measured 0.4
  // seconds against 0.06 to 0.17, and one read of 30 rows that took 12.6 seconds). The entity is now a term of the
  // request's own "and", beside the time bounds, so it also stands beside a scope's filter on the same column and never
  // replaces it. Only when no row has that entity is the same read made for the node of that name (a node as the ISO
  // writes it, "HB_NORTH"). An entity is written namespace:id and a node is the id alone (docs/datastandard.md), so no
  // name is both: the rows returned are the rows the one request returned.
  let entityCol: "entity" | "node" | null = null;
  const read = async (bounds: string[], more: Record<string, string> = {}, max = MAX_ROWS + 1): Promise<Json[]> => {
    const one = (col: "entity" | "node" | null) => {
      const terms = [...(col ? [`${col}.eq.${quote(a.entity!)}`] : []), ...bounds];
      return rest<Json>(shape, { ...q, ...more, ...(terms.length ? { and: `(${terms.join(",")})` } : {}) }, HOURLY, max);
    };
    if (shape !== "series" || !a.entity) return one(null);
    if (entityCol) return one(entityCol);
    const byEntity = await one("entity");
    if (byEntity.length) { entityCol = "entity"; return byEntity; }
    const byNode = await one("node");
    if (byNode.length) entityCol = "node";
    return byNode;
  };

  // session 156: "the newest day held" (lib/chat/forms.ts). One small read, newest first, finds the newest whole day of
  // this table, entity and variable (before `end` when it is given); the query then answers over that day.
  let newest: Json | null = null, nothingHeld = false;
  const bounds: string[] = [];
  // session 161: "this week" (lib/chat/forms.ts): the local calendar week now running, Monday to today. The one read is
  // of that week; the result says which of its days are held and is over those. When none is held yet, one more read
  // finds the newest day held and the result is over the seven local days that end there, and says so.
  const thisWeek = a.day === THIS_WEEK;
  let weekOf: { monday: string; today: string } | null = null;
  if (thisWeek) {
    if (shape !== "series") throw new ToolError(`day "${THIS_WEEK}" applies to series tables only`);
    if (a.start || a.end) throw new ToolError(`day "${THIS_WEEK}" finds the week itself: give no start and no end`);
    if (dated && !(c.interval ?? "").split(";").every((f) => f === "P1D")) throw new ToolError(`${a.table} is a table of months or years: it has no days of a week. Ask its newest row with day "${NEWEST}"`);
    const today = tzKey(new Date(Date.now()).toISOString(), tz, "day");
    const monday = shiftDay(today, -((new Date(`${today}T00:00:00Z`).getUTCDay() + 6) % 7));
    weekOf = { monday, today };
    bounds.push(`${tcol}.gte.${parseTime(monday, btz)}`, `${tcol}.lt.${parseTime(nextDay(today), btz)}`);
  } else if (a.day !== undefined) {
    if (a.day !== NEWEST) throw new ToolError(`day must be "${NEWEST}" or "${THIS_WEEK}"; for a named day give start and end`);
    if (shape !== "series") throw new ToolError(`day "${NEWEST}" applies to series tables only`);
    if (a.start) throw new ToolError(`day "${NEWEST}" finds the day itself: give no start (end may be given: the newest whole day before it)`);
    const before = a.end ? [`${tcol}.lt.${parseTime(a.end, btz)}`] : [];
    const recent = await read(before, { select: "t:ts_utc,entity,variable,freq", order: "ts_utc.desc.nullslast", ...(family ? { variable: `eq.${family.names[0]}` } : {}) }, dated ? NEWEST_READ_DATED : NEWEST_READ);
    const pairs = new Set(recent.map((r) => `${r.entity}|${r.variable}`));
    if (pairs.size > 1) throw new ToolError(`day "${NEWEST}" is one series' own newest day, and these filters match more than one entity and variable (${Array.from(pairs).slice(0, 4).join(", ")}): give entity and variable`);
    // the day before `end`, in the same clock as the days: what "yesterday" is when end is today's date
    const asked = a.end ? { before: a.end, day_before: tzKey(new Date(Date.parse(parseTime(a.end, btz)) - 1).toISOString(), btz, "day") } : null;
    if (!recent.length) {
      nothingHeld = true;
      newest = { asked: NEWEST, held: false, ...(asked ?? {}), note: `no row is held for these filters${a.end ? ` before ${a.end}` : ""}` };
    } else if (dated) {
      // a table of days, months or years: the newest row's own date (its label at 00:00Z)
      const t = new Date(String(recent[0].t)).getTime();
      const label = new Date(t).toISOString().slice(0, 10);
      bounds.push(`${tcol}.gte.${new Date(t).toISOString()}`, `${tcol}.lt.${new Date(t + 1000).toISOString()}`);
      newest = { asked: NEWEST, held: true, day: label, newest_row_at: isoTs(recent[0].t), step: Array.from(new Set(recent.map((r) => String(r.freq ?? "")))).filter(Boolean).join(";"),
        ...(asked ? { ...asked, day_before_held: label === asked.day_before } : {}),
        note: "a table of days or longer periods: day is the date of its newest row (a month's or a year's row is dated its first day); whether that period is complete is the table's own to say (its days_held or hours variables)" };
    } else {
      const per = stepsPerHour(recent.map((r) => r.freq as string | null));
      const hours = (day: string) => (Date.parse(parseTime(nextDay(day), tz)) - Date.parse(parseTime(day, tz))) / 3_600_000;
      const { days, pick } = newestWholeDay(recent.map((r) => String(r.t)), (t) => tzKey(t, tz, "day"), (day) => (per === null ? null : Math.round(per * hours(day))), recent.length >= NEWEST_READ);
      const day = pick!.day;
      bounds.push(`${tcol}.gte.${parseTime(day, tz)}`, `${tcol}.lt.${parseTime(nextDay(day), tz)}`);
      newest = { asked: NEWEST, held: true, day, tz, whole: pick!.whole, rows: pick!.rows, rows_in_a_whole_day: pick!.of, newest_row_at: isoTs(recent[0].t),
        newer_days_not_whole: days.filter((d) => d.day > day).map((d) => ({ day: d.day, rows: d.rows, of: d.of })),
        ...(asked ? { ...asked, day_before_held: day === asked.day_before && pick!.whole === true } : {}),
        note: pick!.whole === true ? "day is the newest local day that holds every step it has; days after it are held in part only and are listed, with their rows, under newer_days_not_whole"
          : pick!.whole === false ? "no day among the newest rows is whole: day is the newest day held, in part only (rows of rows_in_a_whole_day); nothing is filled" : "the table's step is not one the tool can count a whole day by: day is the newest day held, and whether it is whole is not known" };
    }
  } else if (!dcol) {
    if (a.start) bounds.push(`${tcol}.gte.${parseTime(a.start, btz)}`);
    if (a.end) bounds.push(`${tcol}.lt.${parseTime(a.end, btz)}`);
  }
  // session 148: no question reads a year of hourly reserve prices. While the tables of days and months are in the live
  // set, a query of the hourly table that gives no start, or spans more than a few weeks, is refused before any row is
  // read, with a message that names the two tables (lib/chat/rollup.ts). Until they are loaded the table is read as before.
  // (Session 156: a query of "the newest day" spans one day, the one its own small read found.)
  if (scope?.rollup && a.table === scope.rollup.hourly && (await allHeld(scope.rollup.tables))) {
    const bound = (op: string) => bounds.find((b) => b.startsWith(`${tcol}.${op}.`))?.slice(tcol.length + op.length + 2) ?? null;
    const why = hourlyRefusal(bound("gte"), bound("lt"), Date.now());
    if (why && !nothingHeld) throw new ToolError(why);
  }

  let raw = nothingHeld ? [] : await read(bounds);
  let week: Json | null = null;
  if (weekOf) {
    const { monday, today } = weekOf;
    let from = monday, to = today;
    const inWeek = raw.length > 0;
    if (!inWeek) {
      // no day of the week is held: the newest row before it, and the seven local days that end on its day
      const recent = await read([`${tcol}.lt.${parseTime(monday, btz)}`], { select: "t:ts_utc", order: "ts_utc.desc.nullslast" }, 1);
      if (recent.length) {
        to = tzKey(String(recent[0].t), btz, "day");
        from = shiftDay(to, -6);
        raw = await read([`${tcol}.gte.${parseTime(from, btz)}`, `${tcol}.lt.${parseTime(nextDay(to), btz)}`]);
      }
    }
    // each day of the period read, with the rows it holds and the rows a whole day has (one series only: several
    // entities or variables together have no one count of a whole day)
    const one = new Set(raw.map((r) => `${r.entity}|${r.variable}`)).size === 1;
    const per = dated ? null : stepsPerHour(raw.map((r) => r.freq as string | null));
    const hours = (day: string) => (Date.parse(parseTime(nextDay(day), tz)) - Date.parse(parseTime(day, tz))) / 3_600_000;
    const count = new Map<string, number>();
    for (const r of raw) if (r.t) { const d = tzKey(String(r.t), btz, "day"); count.set(d, (count.get(d) ?? 0) + 1); }
    const days: { day: string; rows: number; of: number | null; whole: boolean | null }[] = [];
    for (let d = from; d <= to && days.length < 14; d = nextDay(d)) {
      const rows = count.get(d) ?? 0, of = !one ? null : dated ? 1 : per === null ? null : Math.round(per * hours(d));
      days.push({ day: d, rows, of, whole: of === null ? null : rows === of });
    }
    const heldDays = days.filter((d) => d.rows > 0).map((d) => d.day);
    week = {
      asked: THIS_WEEK, tz, week: { from: monday, to: today }, held: inWeek, period_read: raw.length ? { from, to } : null, days,
      days_held: heldDays, days_not_held: days.filter((d) => d.rows === 0).map((d) => d.day), days_held_in_part: days.filter((d) => d.rows > 0 && d.whole === false).map((d) => d.day),
      newest_row_at: raw.length ? isoTs(raw[raw.length - 1].t) : null,
      note: !raw.length ? "no row is held for these filters, in this week or before it"
        : inWeek ? "the result is over the days of this week that are held (days_held); a day under days_not_held holds no row yet and one under days_held_in_part holds some of its rows; nothing is filled. Say which days the answer covers and answer from this result"
        : "no day of this week is held yet: the result is over the newest seven local days held instead (period_read). Say first that this week is not held, then give the figure and the days it covers",
    };
  }
  if (raw.length > MAX_ROWS) throw new ToolError(`more than ${MAX_ROWS} rows match; narrow the query (entity, variable, start, end)`);
  // a date column is bounded here, on the dates as the rows write them; a row with no date is in no period
  let undated = 0;
  if (dcol) {
    undated = raw.filter((r) => dateLabel(r.t as string | null, "day") === null).length;
    if (a.start || a.end) raw = raw.filter((r) => { const d = dateLabel(r.t as string | null, "day"); return d !== null && (!a.start || d >= a.start) && (!a.end || d < a.end); });
  }
  const all: Row[] = raw.map((r) => ({
    t: (r.t as string) ?? null,
    v: r.v === null || r.v === undefined || r.v === "" ? null : Number(r.v),
    g: r.g === null || r.g === undefined ? null : String(r.g),
    entity: r.entity as string | undefined,
    variable: r.variable as string | undefined,
    unit: r.unit as string | undefined,
    id: r.id as string | undefined,
  }));
  // of a family of hours, the rows of the answer are the 24 variables; the counts of days read beside them are set apart
  const rows = family ? all.filter((r) => family.names.includes(r.variable ?? "")) : all;

  const out: Json = {
    aggregation: a.aggregation,
    value_column: a.aggregation === "count" ? null : vcol,
    filters: Object.fromEntries(Object.entries({ entity: a.entity, variable: a.variable, start: a.start, end: a.end, where: a.where, percentile: a.percentile, date_column: dcol, day: a.day,
      tz: (((g && TIME_GROUPS.includes(g)) || a.start || a.end || a.day || (hod && !family)) && tz !== "UTC") ? tz : undefined }).filter(([, v]) => v !== undefined)),
    rows_matched: rows.length,
  };
  if (newest) out.newest = newest;
  if (week) out.week = week;
  if (dcol) out.date_column = { column: dcol, rows_without_a_date: undated, note: "rows are grouped and bounded by this column's date as the source writes it; a row whose date is empty is in no group and is counted in rows_without_a_date" };
  if (shape === "series" && rows.length) {
    const vars = Array.from(new Set(rows.map((r) => r.variable!))).sort();
    out.units = Array.from(new Set(rows.map((r) => r.unit!))).sort();
    out.variables = vars.slice(0, 10);
    out.time_span = { first: isoTs(rows[0].t), last: isoTs(rows[rows.length - 1].t) };
    if (vars.length > 1 && !family && g !== "variable" && !["count", "latest"].includes(a.aggregation)) out.warning = "more than one variable matched: the aggregation mixes them; filter by variable";
  }
  if (!rows.length) {
    out.result = [];
    out.note = "no rows match these filters (this site holds only the live set: see list_tables)";
  } else if (!g) {
    if (a.aggregation === "latest" && shape === "series") {
      const pairs = new Map<string, Row[]>();
      for (const r of rows) {
        const k = `${r.entity}|${r.variable}`;
        if (!pairs.has(k)) pairs.set(k, []);
        pairs.get(k)!.push(r);
      }
      const res = Array.from(pairs.keys()).sort().map((k) => aggregate(pairs.get(k)!, "latest", undefined, shape));
      out.result = res.slice(0, MAX_GROUPS);
      if (res.length > MAX_GROUPS) out.result_note = `${res.length} entity and variable pairs; the first ${MAX_GROUPS} are shown`;
    } else {
      out.result = [aggregate(rows, a.aggregation, a.percentile, shape)];
    }
  } else {
    const groups = new Map<string, Row[]>();
    for (const r of rows) {
      // session 92, as tools.py under a scope that asks for it: rows of a day or longer are grouped by their own label
      // session 156: the hour of the day (the last two digits of a family's variable, or the row's local hour); a date column's own date
      const k = hod ? (family ? (r.variable ?? "").slice(-2) : r.t ? tzKey(r.t, tz, "hour").slice(11, 13) : null)
        : timed ? (dcol ? dateLabel(r.t, g) : r.t ? tzKey(r.t, dated ? "UTC" : tz, g) : null) : r.g;
      if (k === null) continue;
      if (!groups.has(k)) groups.set(k, []);
      groups.get(k)!.push(r);
    }
    // the days behind an hour of the day: the local days of its rows; or, of a family of hours, the table's own count
    // for each period read (the family of days beside it, else days_held), added up; left out when a period has none
    const stamp = (t: string | null) => (t ? new Date(t).getTime() : NaN);
    const counted = new Map<string, number>();
    if (family) for (const r of all) if (r.v !== null && (r.variable === DAYS_HELD || family.days?.includes(r.variable ?? ""))) counted.set(`${r.variable}|${stamp(r.t)}`, r.v);
    const daysOf = (hour: string, rs: Row[]): number | null => {
      // of several periods, the newest, the lowest or the highest row is one period's: the days of all of them are not its count
      if (family && rs.length > 1 && ["latest", "min", "max"].includes(a.aggregation)) return null;
      if (!family) return new Set(rs.filter((r) => r.t).map((r) => tzKey(r.t!, tz, "day"))).size;
      let sum = 0;
      for (const r of rs) {
        const own = family.days ? counted.get(`${family.days[Number(hour)]}|${stamp(r.t)}`) : undefined;
        const n = own ?? counted.get(`${DAYS_HELD}|${stamp(r.t)}`);
        if (n === undefined) return null;
        sum += n;
      }
      return round(sum);
    };
    const res: Json[] = Array.from(groups.keys()).sort().map((k) => {
      const days = hod ? daysOf(k, groups.get(k)!) : null;
      return { [g]: k, ...aggregate(groups.get(k)!, a.aggregation, a.percentile, shape), ...(days === null ? {} : { days }) };
    });
    out.n_groups = res.length;
    // session 143: what an answer says about a series besides its rows (its high and low, where it began and ended, its
    // level) comes with the rows, so a question about a movement is one query, not one query a figure
    const summary = groupSummary(g, res, rows.filter((r) => (hod ? (family ? true : !!r.t) : timed ? (dcol ? dateLabel(r.t, g) !== null : !!r.t) : r.g !== null)), a.aggregation, a.percentile, shape);
    if (summary) out.summary = summary;
    const cap = scope?.max_groups ?? MAX_GROUPS; // session 92: a profile may show a month per row since 2018
    if (res.length > cap) out.result_note = `${res.length} groups; the first ${cap} (sorted by ${g}) are shown`;
    out.result = res.slice(0, cap);
    if (hod) {
      const held = new Set(res.map((r) => String(r[g])));
      const missing = Array.from({ length: 24 }, (_, i) => String(i).padStart(2, "0")).filter((h) => !held.has(h));
      if (family) {
        const periods = Array.from(new Set(rows.map((r) => isoTs(r.t)?.slice(0, 10) ?? ""))).filter(Boolean).sort();
        out.average_day = { hours: res.length, of: 24, hours_not_held: missing, periods: periods.length, first_period: periods[0] ?? null, last_period: periods[periods.length - 1] ?? null,
          note: `each row is the table's own variable for that hour of the local day (${family.stem}00 to ${family.stem}23)${periods.length > 1 ? `: the ${a.aggregation} over the ${periods.length} periods read (n is the periods behind the hour), not weighted by their days` : ", for the one period read"}; days is the table's own count of days behind the hour (${family.days ? `${family.days[0]} to ${family.days[23]}, else ` : ""}${DAYS_HELD}), added over the periods, and is left out where the table gives none; an hour the table does not hold is under hours_not_held; nothing is filled` };
      } else {
        const inPeriod = new Set(rows.filter((r) => r.t).map((r) => tzKey(r.t!, tz, "day"))).size;
        out.average_day = { hours: res.length, of: 24, hours_not_held: missing, tz, days_in_period: inPeriod,
          short_hours: res.filter((r) => typeof r.days === "number" && (r.days as number) < inPeriod).map((r) => ({ [g]: r[g], days: r.days })),
          note: `each row is an hour of the local day (${tz}): the ${a.aggregation} of that hour's rows over the period; n is the rows and days the local days behind it. An hour with fewer days than days_in_period (a day held in part, the hour the clocks skip) is under short_hours with its own count; an hour with no row is under hours_not_held; nothing is filled` };
      }
    } else if (timed && !dcol && shape !== "series" && !res.length) {
      // session 156: an entities or events table whose own time column is empty groups into nothing: say what to give
      out.note = `no row of ${a.table} has a ${tcol}, so group_by ${g} finds no group. To group by another date of the table give date_column${dateColumns(columns).filter((x) => x !== tcol).length ? ` (its date columns: ${dateColumns(columns).filter((x) => x !== tcol).join(", ")})` : ""}`;
    }
  }
  // session 168: each time the result gives, with the same moment in the grid's own local words beside it ("at_local":
  // "4 pm Central, 3 October 2026"; a day's label as a date), so an answer can say the time in words that are in a tool
  // result (lib/chat/plaintime.ts). The zone is the query's own, else the grid of the entity read; none, no words
  if (shape === "series") addLocalTimes(out, dated, tz !== "UTC" ? tz : zoneOfEntity(a.entity ?? all.find((r) => r.entity)?.entity));
  Object.assign(out, await provenance(a.table));
  return out;
}

async function compare(a: { a: QueryArgs; b: QueryArgs }, scope: Scope = null): Promise<Json> {
  const [ra, rb] = await Promise.all([query(a.a, scope), query(a.b, scope)]);
  const single = (r: Json) => {
    const res = r.result as Json[];
    if (res.length !== 1) return null;
    const v = res[0].value ?? res[0].count;
    return typeof v === "number" ? v : null;
  };
  const out: Json = { a: ra, b: rb };
  const va = single(ra), vb = single(rb);
  if (va !== null && vb !== null) {
    out.difference_b_minus_a = round(vb - va);
    out.ratio_b_over_a = va ? round(vb / va) : null;
  }
  return out;
}

/** Session 35: a grid page's written layer, as warehouse/chat/tools.py grid_notes. */
function gridNotes(a: { grid?: string }, scope: Scope): Json {
  const g = scopeOf(a.grid);
  if (!g) throw new ToolError(`no grid ${JSON.stringify(a.grid)}; grids: ${DOCS.grid_config.map((x) => x.slug).join(", ")}`);
  // session 156: the words say what is read here and no more (Ask ERCOT answers for other grids what four pages show; no chat reads another grid's notes)
  if (scope && g.slug !== scope.slug) throw new ToolError(`this chat reads the written notes of ${scope.iso} only (grid_notes ${JSON.stringify(scope.slug)}); ${g.iso}'s are on its own page, /grid/${g.slug}`);
  const table = `docs/grids/${g.slug}.md`;
  return { table, grid: g.slug, tier: "written", license: "public", source_report: `${table}: text written for the ERW's grid page; each section names its ISO and EIA sources`, data_version: "the site's build", text: DOCS.grids[g.slug] };
}

/** Run one tool. Returns the result and whether it is an error the model should see. */
export async function runTool(name: string, input: unknown, scope: Scope = null): Promise<{ out: Json; isError: boolean }> {
  try {
    const a = (input ?? {}) as Json;
    if (name === "list_tables") return { out: await listTables(a, scope), isError: false };
    if (name === "describe_table") return { out: await describeHeld(a as { table: string }, scope), isError: false };
    if (name === "query") return { out: await query(a as unknown as QueryArgs, scope), isError: false };
    if (name === "compare") return { out: await compare(a as unknown as { a: QueryArgs; b: QueryArgs }, scope), isError: false };
    if (name === "grid_notes") return { out: gridNotes(a as { grid?: string }, scope), isError: false };
    return { out: { error: `unknown tool ${JSON.stringify(name)}` }, isError: true };
  } catch (e) {
    if (e instanceof ToolError || e instanceof DataError) return { out: { error: e.message }, isError: true };
    throw e;
  }
}
