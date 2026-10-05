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
import { chartPoints, pointsAreRows } from "./series";

export type Context = { view: string; title?: string; settings?: Record<string, string> };
export type SeriesRow = { key: string; value: number | null; n?: number; at?: string };
export type Series = {
  result_id: string; table: string; title: string; group_by: string; kind: "line" | "bar"; unit: string | null; aggregation: string;
  rows: SeriesRow[]; rows_matched: number | null; note: string | null; source_report: string | null; license: string | null; tier: string | null;
  data_version: string | null; chosen_by: string;
  /** session 121: the series against the rows the tool returned, and the chart's points against the series */
  check?: { rows_fetched: number; rows: number; same: boolean; points: number; not_drawn: number };
};
/** Session 121: one earlier turn of the conversation, as the first message carries it. */
export type Turn = { question: string; answer: string; calls: { tool: string; input: Json }[]; citations: { table: string }[] };
export type Nearest = { table: string; holds: string };

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

const S121 = spec as unknown as { history_head: string; history_turn: string; max_history: number; max_history_answer: number; max_nearest: number; holds: Record<string, string> };

/** The conversation so far, cleaned: the newest turns, oldest first, each a question, an answer and the queries run for
 * it. What a browser sends is the reader's own conversation: it is cut to size and to the tables of the guide, and its
 * numbers count as given exactly as the numbers of the question do. As warehouse/chat/ercot.py turns. */
export function cleanHistory(raw: unknown): Turn[] {
  if (!Array.isArray(raw)) return [];
  const text = (v: unknown, n: number) => (typeof v === "string" ? v.trim().slice(0, n) : "");
  const out: Turn[] = [];
  for (const h of raw.slice(-S121.max_history)) {
    if (!h || typeof h !== "object") continue;
    const r = h as Json;
    const question = text(r.question, 500), answer = text(r.answer, S121.max_history_answer);
    if (!question || !answer) continue;
    const calls: Turn["calls"] = [];
    for (const c of Array.isArray(r.calls) ? r.calls.slice(0, 8) : []) {
      const x = c as Json | null;
      if (!x || (x.tool !== "query" && x.tool !== "compare") || !x.input || typeof x.input !== "object") continue;
      if (JSON.stringify(x.input).length > 1200) continue;
      calls.push({ tool: x.tool, input: x.input as Json });
    }
    const citations = (Array.isArray(r.citations) ? r.citations : []).map((c) => ({ table: String((c as Json | null)?.table ?? "") })).filter((c) => spec.tables.includes(c.table));
    out.push({ question, answer, calls, citations });
  }
  return out;
}

const sorted = (v: unknown): unknown => (Array.isArray(v) ? v.map(sorted) : v && typeof v === "object"
  ? Object.fromEntries(Object.keys(v as Json).sort().map((k) => [k, sorted((v as Json)[k])])) : v);

export function historyText(turns: Turn[]): string {
  if (!turns.length) return "";
  const parts = [S121.history_head];
  turns.forEach((t, i) => {
    // as ercot.py: the query's arguments as compact JSON, keys in order
    const queries = t.calls.map((c) => `${c.tool} ${JSON.stringify(sorted(c.input))}`).join("; ") || "none";
    parts.push(S121.history_turn.replace("{n}", String(i + 1)).replace("{question}", () => t.question).replace("{answer}", () => t.answer).replace("{queries}", () => queries));
  });
  return parts.join("\n\n");
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
    opening: (question, today, context, history) => {
      const line = contextLine(cleanContext(context));
      const past = historyText(cleanHistory(history));
      return `Today is ${today} (UTC).${line ? `\n\n${line}` : ""}${past ? `\n\n${past}` : ""}\n\nQuestion: ${question}`;
    },
    extraSources: (context, history) => {
      const c = cleanContext(context);
      const given = c ? [JSON.stringify(c)] : [];
      for (const t of cleanHistory(history)) given.push(t.answer, ...t.calls.map((x) => `${JSON.stringify(x.input)} ${spelled(x.input)}`));
      return given;
    },
    knownTables: (history) => cleanHistory(history).flatMap((t) => t.citations.map((c) => c.table)),
    sourceTexts: (_name, input) => [spelled(input)],
    tag: (name, _input, out, n) => {
      if ("error" in out) return out;
      if (name === "query") return { result_id: `r${n}`, ...out };
      if (name === "compare") return { ...out, a: { result_id: `r${n}a`, ...(out.a as Json) }, b: { result_id: `r${n}b`, ...(out.b as Json) } };
      return out;
    },
    extraProblems: (draft: Draft, results, given = []) => {
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
      // session 121, as ercot.py: a refusal names what is held nearest; a premise's numbers are checked as the answer's
      if (draft.not_in_warehouse) {
        const near = ((Array.isArray(draft.nearest) ? draft.nearest : []) as unknown[]).map(String);
        if (near.length < 1 || near.length > S121.max_nearest || near.some((t) => !spec.tables.includes(t)))
          problems.push(`nearest must name one to ${S121.max_nearest} tables of the guide by their exact names, nearest first (${near.join(", ") || "none"} given)`);
      }
      const loose = unverified(typeof draft.premise === "string" ? draft.premise : "", [...pool, ...given]);
      if (loose.length) problems.push(`premise contains numbers in no tool result and not in the question: ${loose.join(", ")}`);
      return problems;
    },
    finish: (status, draft, results) => {
      const k = known(results);
      const nodash = (t: string) => t.split(String.fromCharCode(0x2014)).join(" - ").replace(/ {2}- {2}/g, " - ");
      const followups = draft && (status === "answered" || status === "not_in_warehouse")
        ? ((Array.isArray(draft.followups) ? draft.followups : []) as string[]).map((f) => nodash(f.trim())).filter(Boolean).slice(0, 3) : [];
      // session 121: the queries run, for the next question of the conversation; and what a refusal points to
      const calls = results.filter((r) => !r.isError && (r.tool === "query" || r.tool === "compare")).map((r) => ({ tool: r.tool, input: r.input }));
      const near = (names: string[]): Nearest[] => names.filter((t) => spec.tables.includes(t)).slice(0, S121.max_nearest).map((t) => ({ table: t, holds: S121.holds[t] ?? "" }));
      if (status === "not_in_warehouse" && draft)
        return { series: [], followups, profile: "ercot", calls, premise: "", nearest: near(((Array.isArray(draft.nearest) ? draft.nearest : []) as unknown[]).map(String)) };
      if (status === "refused_unverified")  // the fixed refusal names nothing: the tables this question read are the nearest known
        return { series: [], followups, profile: "ercot", calls, premise: "", nearest: near([...new Set([...k.values()].map(([, o]) => String(o.table)))]) };
      if (status !== "answered" || !draft) return { series: [], followups, profile: "ercot", calls, premise: "", nearest: [] };
      let ids = ((Array.isArray(draft.series) ? draft.series : []) as string[]).filter((i) => k.has(i) && chartable(...k.get(i)!));
      let chosen = "the answer";
      if (!ids.length) {
        // an answer that rests on a series returns it: the last grouped result of a table the answer cites
        const cited = new Set(draft.citations.map((c) => c.table));
        ids = [...k.entries()].filter(([, [a, o]]) => chartable(a, o) && cited.has(String(o.table))).map(([i]) => i).slice(-1);
        chosen = "default: the last grouped result of a cited table";
      }
      // every series the page will draw is set against the rows the tool returned for that result id, key by key and
      // value by value, and the chart's points against the series; one that differs is not shown
      const all = ids.slice(0, spec.max_series).map((i) => {
        const s = seriesOf(i, ...k.get(i)!, chosen);
        const [args, out] = k.get(i)!;
        const g = String(args.group_by);
        const fetched = (out.result as Json[]).map((r) => [String(r[g]), (r.value ?? r.count ?? null) as number | null] as const);
        const same = fetched.length === s.rows.length && fetched.every(([key, v], j) => s.rows[j].key === key && s.rows[j].value === v);
        const d = chartPoints(s.rows);
        return { ...s, check: { rows_fetched: fetched.length, rows: s.rows.length, same: same && pointsAreRows(s.rows, d), points: d.points.length, not_drawn: d.undrawn.length } };
      });
      const premise = nodash(typeof draft.premise === "string" ? draft.premise.trim() : "");
      return { series: all.filter((s) => s.check.same), series_not_shown: all.filter((s) => !s.check.same).map((s) => s.result_id), followups, profile: "ercot", calls, premise, nearest: [] };
    },
  };
}
