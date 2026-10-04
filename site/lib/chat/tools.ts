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

// Session 35: a scoped chat (/ask?grid=<slug>): one grid's tables (docs/grids/grids.json) and its rows only, as
// warehouse/chat/tools.py set_scope does. null: the whole live set.
// Session 92: a profile's scope (lib/chat/ercot.ts) also names each table's rows outright (filters: {table: {column:
// value or values}}, as warehouse/chat/tools.py scope_rows) and may raise the rows one grouped result returns.
export type Scope = (GridConfig & { filters?: Record<string, Record<string, string | string[]>>; max_groups?: number; dated_groups?: boolean }) | null;
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
  "This site reads the Supabase live set: public tables only; power price, demand, generation and hourly emissions tables hold only their last 35 days; derived, fuel, generator, queue and news tables are whole. Tables with in_live_set no cannot be queried here (their full history is on Redivis).";

// ------------------------------------------------------------------ helpers

let catCache: { at: number; rows: Cat[] } | null = null;
async function catalogue(): Promise<Cat[]> {
  if (catCache && Date.now() - catCache.at < 600_000) return catCache.rows;
  const rows = await rest<Cat>("catalogue", { select: "*", order: "table_name" }, HOURLY);
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

async function query(a: QueryArgs, scope: Scope = null): Promise<Json> {
  if (!AGGREGATIONS.includes(a.aggregation)) throw new ToolError(`aggregation must be one of ${AGGREGATIONS.join(", ")}`);
  const { c, columns, shape } = await tableInfo(a.table, scope);
  const tcol = TIME_COL[shape];
  const vcol = a.value_column ?? DEFAULT_VALUE[shape];
  if (a.aggregation !== "count" && !columns.includes(vcol)) throw new ToolError(`no column ${JSON.stringify(vcol)} in ${a.table}`);
  const tz = a.tz ?? "UTC";
  const g = a.group_by;
  if (g && !TIME_GROUPS.includes(g) && g !== "entity" && !columns.includes(g)) {
    throw new ToolError(`group_by must be one of ${[...TIME_GROUPS, "entity"].join(", ")} or a text column of the table`);
  }

  const sel = [`t:${tcol}`];
  if (a.aggregation !== "count") sel.push(`v:${colRef(shape, vcol)}`);
  if (g && !TIME_GROUPS.includes(g)) {
    const gc = g === "entity" ? { series: "entity", entities: "entity_id", events: "source" }[shape] : g;
    sel.push(`g:${colRef(shape, gc)}`);
  }
  if (shape === "series") sel.push("entity", "variable", "unit");
  if (shape === "entities") sel.push("id:entity_id");
  const q: Record<string, string> = { select: sel.join(","), table_name: `eq.${a.table}`, order: `${tcol}.asc.nullslast`, ...scopeFilter(scope, a.table, shape, columns) };
  if (a.entity) {
    q.or = shape === "series" ? `(entity.eq.${quote(a.entity)},node.eq.${quote(a.entity)})`
      : shape === "entities" ? `(entity_id.eq.${quote(a.entity)},name.eq.${quote(a.entity)})`
      : `(source.eq.${quote(a.entity)})`;
  }
  if (a.variable) {
    if (shape !== "series") throw new ToolError("variable applies to series tables only; use where for entities and events tables");
    q.variable = `eq.${a.variable}`;
  }
  // session 20, as warehouse/chat/tools.py: a series table of days or longer labels each row with its
  // local date at 00:00Z (Decision 11), so a date bound is that label; reading it in tz returned the
  // next day's row (evaluation questions s20q10 and s20q12)
  const dated = shape === "series" && (c.interval ?? "").split(";").every((f) => ["P1D", "P1W", "P1M", "P1Y"].includes(f)) && !!c.interval;
  const btz = dated ? "UTC" : tz;
  const bounds: string[] = [];
  if (a.start) bounds.push(`${tcol}.gte.${parseTime(a.start, btz)}`);
  if (a.end) bounds.push(`${tcol}.lt.${parseTime(a.end, btz)}`);
  if (bounds.length) q.and = `(${bounds.join(",")})`;
  for (const [col, val] of Object.entries(a.where ?? {})) {
    if (!columns.includes(col)) throw new ToolError(`no column ${JSON.stringify(col)} in this table; columns: ${columns.join(", ")}`);
    const vals = Array.isArray(val) ? val : [val];
    q[colRef(shape, col)] = `in.(${vals.map((v) => quote(String(v))).join(",")})`;
  }

  const raw = await rest<Json>(shape, q, HOURLY, MAX_ROWS + 1);
  if (raw.length > MAX_ROWS) throw new ToolError(`more than ${MAX_ROWS} rows match; narrow the query (entity, variable, start, end)`);
  const rows: Row[] = raw.map((r) => ({
    t: (r.t as string) ?? null,
    v: r.v === null || r.v === undefined || r.v === "" ? null : Number(r.v),
    g: r.g === null || r.g === undefined ? null : String(r.g),
    entity: r.entity as string | undefined,
    variable: r.variable as string | undefined,
    unit: r.unit as string | undefined,
    id: r.id as string | undefined,
  }));

  const out: Json = {
    aggregation: a.aggregation,
    value_column: a.aggregation === "count" ? null : vcol,
    filters: Object.fromEntries(Object.entries({ entity: a.entity, variable: a.variable, start: a.start, end: a.end, where: a.where, percentile: a.percentile, tz: ((g && TIME_GROUPS.includes(g)) || a.start || a.end) && tz !== "UTC" ? tz : undefined }).filter(([, v]) => v !== undefined)),
    rows_matched: rows.length,
  };
  if (shape === "series" && rows.length) {
    const vars = Array.from(new Set(rows.map((r) => r.variable!))).sort();
    out.units = Array.from(new Set(rows.map((r) => r.unit!))).sort();
    out.variables = vars.slice(0, 10);
    out.time_span = { first: isoTs(rows[0].t), last: isoTs(rows[rows.length - 1].t) };
    if (vars.length > 1 && !["count", "latest"].includes(a.aggregation)) out.warning = "more than one variable matched: the aggregation mixes them; filter by variable";
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
      const k = TIME_GROUPS.includes(g) ? (r.t ? tzKey(r.t, dated && scope?.dated_groups ? "UTC" : tz, g) : null) : r.g;
      if (k === null) continue;
      if (!groups.has(k)) groups.set(k, []);
      groups.get(k)!.push(r);
    }
    const res = Array.from(groups.keys()).sort().map((k) => ({ [g]: k, ...aggregate(groups.get(k)!, a.aggregation, a.percentile, shape) }));
    out.n_groups = res.length;
    const cap = scope?.max_groups ?? MAX_GROUPS; // session 92: a profile may show a month per row since 2018
    if (res.length > cap) out.result_note = `${res.length} groups; the first ${cap} (sorted by ${g}) are shown`;
    out.result = res.slice(0, cap);
  }
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
  if (scope && g.slug !== scope.slug) throw new ToolError(`this chat speaks for ${scope.iso} only; its notes are grid_notes ${JSON.stringify(scope.slug)}`);
  const table = `docs/grids/${g.slug}.md`;
  return { table, grid: g.slug, tier: "written", license: "public", source_report: `${table}: text written for the ERW's grid page; each section names its ISO and EIA sources`, data_version: "the site's build", text: DOCS.grids[g.slug] };
}

/** Run one tool. Returns the result and whether it is an error the model should see. */
export async function runTool(name: string, input: unknown, scope: Scope = null): Promise<{ out: Json; isError: boolean }> {
  try {
    const a = (input ?? {}) as Json;
    if (name === "list_tables") return { out: await listTables(a, scope), isError: false };
    if (name === "describe_table") return { out: await describeTable(a as { table: string }, scope), isError: false };
    if (name === "query") return { out: await query(a as unknown as QueryArgs, scope), isError: false };
    if (name === "compare") return { out: await compare(a as unknown as { a: QueryArgs; b: QueryArgs }, scope), isError: false };
    if (name === "grid_notes") return { out: gridNotes(a as { grid?: string }, scope), isError: false };
    return { out: { error: `unknown tool ${JSON.stringify(name)}` }, isError: true };
  } catch (e) {
    if (e instanceof ToolError || e instanceof DataError) return { out: { error: e.message }, isError: true };
    throw e;
  }
}
