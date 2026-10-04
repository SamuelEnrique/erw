// Energy Research Warehouse (ERW) site, session 92: Ask ERCOT, the reference version. The profile of the loop in
// lib/chat/ask.ts that warehouse/chat/ercot.py defines: its system prompt with the table guide, its answer schema, its
// scope and limits all come from lib/chat/spec_ercot.json, which ercot.py --export-spec writes. This file is the same
// logic as ercot.py's class: a result id on every query result, the checks on series and follow-ups, and the series
// (the rows as the tool returned them, with their table and source) that the page draws its chart and table from.
//
// One difference from the Python loop, and it is the data's, not the code's: this site reads the Supabase live set. A
// table the live set does not hold (the hub price history, the reserve prices, Berkeley Lab's queue, the owners, the
// internal contracts) answers "not in this site's live set", and the model says so. lib/chat/ask.ts is unchanged for
// every chat without a profile.
import "server-only";
import spec from "./spec_ercot.json";
import { numbers, unverified, type Draft, type Profile, type ToolRecord } from "./ask";
import { scopeOf, type Scope } from "./tools";

export type Context = { view: string; title?: string; settings?: Record<string, string> };
export type SeriesRow = { key: string; value: number | null; n?: number; at?: string };
export type Series = {
  result_id: string; table: string; title: string; group_by: string; kind: "line" | "bar"; unit: string | null; aggregation: string;
  rows: SeriesRow[]; rows_matched: number | null; note: string | null; source_report: string | null; license: string | null; tier: string | null;
  data_version: string | null; chosen_by: string;
};

const TIME_GROUPS = ["year", "month", "day", "hour"];
const [YEAR_LO, YEAR_HI] = spec.years as [number, number];
type Json = Record<string, unknown>;

/** The view a reader came from, cleaned: a site path, a short title and a few short settings; null when none. */
export function cleanContext(raw: unknown): Context | null {
  if (!raw || typeof raw !== "object") return null;
  const r = raw as Json;
  if (typeof r.view !== "string" || !/^\/[A-Za-z0-9/_-]{0,80}$/.test(r.view)) return null;
  const short = (v: unknown, n: number) => (typeof v === "string" ? v.replace(/[^\x20-\x7E]/g, " ").replace(/\s+/g, " ").trim().slice(0, n) : "");
  const settings: Record<string, string> = {};
  if (r.settings && typeof r.settings === "object") {
    for (const [k, v] of Object.entries(r.settings as Json).slice(0, 10)) {
      const key = short(k, 24).replace(/[^A-Za-z0-9 _-]/g, ""), val = short(v, 60);
      if (key && val) settings[key] = val;
    }
  }
  const title = short(r.title, 80);
  return { view: r.view, ...(title ? { title } : {}), ...(Object.keys(settings).length ? { settings } : {}) };
}

export function contextLine(c: Context | null): string {
  if (!c) return "";
  const settings = Object.entries(c.settings ?? {}).map(([k, v]) => `${k} ${v}`).join("; ");
  return spec.context_line.replace("{view}", c.view).replace("{title}", c.title ? ` (${c.title})` : "").replace("{settings}", settings ? `, set to: ${settings}` : "");
}

/** The query results inside one tool result: [result id, the query's own output]. */
function resultIds(out: Json): [string, Json][] {
  const found: [string, Json][] = typeof out.result_id === "string" ? [[out.result_id, out]] : [];
  for (const sub of ["a", "b"]) {
    const s = out[sub] as Json | undefined;
    if (s && typeof s.result_id === "string") found.push([s.result_id, s]);
  }
  return found;
}

function known(results: ToolRecord[]): Map<string, [Json, Json]> {
  const m = new Map<string, [Json, Json]>();
  for (const r of results) {
    if (r.isError) continue;
    for (const [id, out] of resultIds(r.out)) {
      const args = r.tool === "query" ? r.input : ((r.input[id.endsWith("a") ? "a" : "b"] as Json) ?? {});
      m.set(id, [args, out]);
    }
  }
  return m;
}

const chartable = (args: Json, out: Json) => !!args.group_by && Array.isArray(out.result) && out.result.length >= spec.min_rows;

function seriesOf(id: string, args: Json, out: Json, chosen: string): Series {
  const g = String(args.group_by);
  const rows = (out.result as Json[]).map((r) => ({
    key: String(r[g]), value: (r.value ?? r.count ?? null) as number | null,
    ...(typeof r.n === "number" ? { n: r.n } : {}), ...(typeof r.at === "string" ? { at: r.at } : {}),
  }));
  const what = args.aggregation === "count" ? "count of rows" : `${args.aggregation} of ${args.variable ?? out.value_column ?? "value"}`;
  const where = Object.entries((args.where as Json) ?? {}).map(([k, v]) => `${k} ${v}`).join("; ");
  const units = (out.units as string[] | undefined) ?? [];
  return {
    result_id: id, table: String(out.table), title: `${what}${args.entity ? `, ${args.entity}` : ""}${where ? ` (${where})` : ""}, by ${g}`,
    group_by: g, kind: TIME_GROUPS.includes(g) ? "line" : "bar", unit: units.length === 1 ? units[0] : null, aggregation: String(args.aggregation),
    rows, rows_matched: (out.rows_matched as number) ?? null, note: (out.result_note as string) ?? null, source_report: (out.source_report as string) ?? null,
    license: (out.license as string) ?? null, tier: (out.tier as string) ?? null, data_version: (out.data_version as string) ?? null, chosen_by: chosen,
  };
}

/** The names in a tool call's arguments with their parts apart ("foresight_4h_revenue" as "foresight 4 h revenue"):
 * a name asked by holds numbers the answer may repeat. As warehouse/chat/ercot.py spelled. */
export function spelled(args: Json): string {
  const words: string[] = [];
  const walk = (v: unknown): void => {
    if (Array.isArray(v)) v.forEach(walk);
    else if (v && typeof v === "object") Object.values(v as Json).forEach(walk);
    else if (typeof v === "string") words.push(v.replace(/[^A-Za-z0-9.]+/g, " ").replace(/(?<=\d)(?=[A-Za-z])|(?<=[A-Za-z])(?=\d)/g, " "));
  };
  walk(Object.fromEntries(Object.entries(args ?? {}).filter(([k]) => ["variable", "entity", "where", "a", "b", "value_column"].includes(k))));
  return words.join(" ");
}

export function ercotProfile(): Profile {
  const base = scopeOf("ercot");
  if (!base) throw new Error("docs/grids/grids.json has no grid ercot");
  const scope: Scope = { ...base, tables: spec.tables, filters: spec.filters as Record<string, Record<string, string | string[]>>, max_groups: spec.max_groups, dated_groups: spec.dated_groups };
  return {
    system: spec.system, schema: spec.answer_schema, effort: spec.effort, retry: spec.retry, scope,
    opening: (question, today, context) => {
      const line = contextLine(cleanContext(context));
      return `Today is ${today} (UTC).${line ? `\n\n${line}` : ""}\n\nQuestion: ${question}`;
    },
    extraSources: (context) => { const c = cleanContext(context); return c ? [JSON.stringify(c)] : []; },
    sourceTexts: (_name, input) => [spelled(input)],
    tag: (name, _input, out, n) => {
      if ("error" in out) return out;
      if (name === "query") return { result_id: `r${n}`, ...out };
      if (name === "compare") return { ...out, a: { result_id: `r${n}a`, ...(out.a as Json) }, b: { result_id: `r${n}b`, ...(out.b as Json) } };
      return out;
    },
    extraProblems: (draft: Draft, results) => {
      const problems: string[] = [];
      const k = known(results);
      const ids = (Array.isArray(draft.series) ? draft.series : []) as string[];
      const bad = ids.filter((i) => !k.has(i));
      if (bad.length) problems.push(`series names result ids no tool returned: ${bad.join(", ")}`);
      const flat = ids.filter((i) => k.has(i) && !chartable(...k.get(i)!));
      if (flat.length) problems.push(`series names results that are not grouped series of at least ${spec.min_rows} rows (use group_by, or leave series empty): ${flat.join(", ")}`);
      if (ids.length > spec.max_series) problems.push(`series names more than ${spec.max_series} results`);
      const ups = ((Array.isArray(draft.followups) ? draft.followups : []) as string[]).map((f) => f.trim()).filter(Boolean);
      if (ups.length < 2 || ups.length > 3) problems.push(`followups must be two or three questions (${ups.length} given)`);
      const pool = results.map((r) => JSON.stringify(r.out));
      const stray = new Set<string>();
      for (const f of ups) {
        for (const [v, d] of numbers(f)) {
          if (d === 0 && Number.isInteger(v) && v >= YEAR_LO && v <= YEAR_HI) continue;
          if (unverified(v.toFixed(d), pool).length) stray.add(v.toFixed(d));
        }
      }
      if (stray.size) problems.push(`follow-up questions contain numbers in no tool result: ${[...stray].sort().join(", ")}`);
      return problems;
    },
    finish: (status, draft, results) => {
      const k = known(results);
      const nodash = (t: string) => t.split(String.fromCharCode(0x2014)).join(" - ").replace(/ {2}- {2}/g, " - ");
      const followups = draft && (status === "answered" || status === "not_in_warehouse")
        ? ((Array.isArray(draft.followups) ? draft.followups : []) as string[]).map((f) => nodash(f.trim())).filter(Boolean).slice(0, 3) : [];
      if (status !== "answered" || !draft) return { series: [], followups, profile: "ercot" };
      let ids = ((Array.isArray(draft.series) ? draft.series : []) as string[]).filter((i) => k.has(i) && chartable(...k.get(i)!));
      let chosen = "the answer";
      if (!ids.length) {
        // an answer that rests on a series returns it: the last grouped result of a table the answer cites
        const cited = new Set(draft.citations.map((c) => c.table));
        ids = [...k.entries()].filter(([, [a, o]]) => chartable(a, o) && cited.has(String(o.table))).map(([i]) => i).slice(-1);
        chosen = "default: the last grouped result of a cited table";
      }
      return { series: ids.slice(0, spec.max_series).map((i) => seriesOf(i, ...k.get(i)!, chosen)), followups, profile: "ercot" };
    },
  };
}
