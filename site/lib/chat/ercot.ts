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
import { scopeOf, tableSummaries, type Scope } from "./tools";
import { summaryText } from "./summaries";
import { chartPoints, pointsAreRows } from "./series";
import { FORMS, FORM_SCHEMA, MIX_HOLDS, MIX_TABLES, NOTES_TABLE, PAGE_TOOL, addendum, notesOf, pageFigures, type Form } from "./panel";
import { ROLLUP, ROLLUP_HOLDS, ROLLUP_TABLES, rollupGuide, rollupOffered } from "./rollup";
import { rulePlan } from "./plan";
import { HELD_WORDS, PAGES_FILTERS, PAGES_HOLDS, PAGES_NEAR, PAGES_TABLES, PAGE_FILE_TOOL, heldIn, heldRefusal, pageFile, pagesGuide, pagesOffered } from "./pagefiles";

/** session 137: the tables a refusal may name as nearest: the guide's and the energy mix's three */
const NEAR_TABLES = [...spec.tables, ...MIX_TABLES, ...ROLLUP_TABLES, ...PAGES_NEAR];   // session 148: and the reserve prices by day and by month; session 153: and what stands behind four pages

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
      const args = r.tool === "compare" ? ((r.input[id.endsWith("a") ? "a" : "b"] as Json) ?? {}) : r.input;
      m.set(id, [args, out]);
    }
  }
  return m;
}

/** session 137: what a result is grouped by: a query's group_by argument, or the grouping a page_figures series states */
const groupOf = (args: Json, out: Json): string | null => (args.group_by ? String(args.group_by) : typeof out.group_by === "string" ? out.group_by : null);
const chartable = (args: Json, out: Json) => !!groupOf(args, out) && Array.isArray(out.result) && out.result.length >= spec.min_rows;

function seriesOf(id: string, args: Json, out: Json, chosen: string): Series {
  const g = String(groupOf(args, out));
  const rows = (out.result as Json[]).map((r) => ({
    key: String(r[g]), value: (r.value ?? r.count ?? null) as number | null,
    ...(typeof r.n === "number" ? { n: r.n } : {}), ...(typeof r.at === "string" ? { at: r.at } : {}),
  }));
  const what = args.aggregation === "count" ? "count of rows" : `${args.aggregation} of ${args.variable ?? out.value_column ?? "value"}`;
  const where = Object.entries((args.where as Json) ?? {}).map(([k, v]) => `${k} ${v}`).join("; ");
  const units = (out.units as string[] | undefined) ?? [];
  return {
    result_id: id, table: String(out.table), title: typeof out.title === "string" ? out.title : `${what}${args.entity ? `, ${args.entity}` : ""}${where ? ` (${where})` : ""}, by ${g}`,
    group_by: g, kind: TIME_GROUPS.includes(g) ? "line" : "bar", unit: units.length === 1 ? units[0] : null, aggregation: String(args.aggregation ?? "as published"),
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

// Session 143: the order the answer's fields are written in. What the page shows first comes first: the form, whether it
// is an answer at all, the series it names and a premise, then the answer's words. When the words are whole their
// numbers, form and premise are checked and the words are shown; the citations, the nearest tables and the questions to
// ask next are written after, and are checked with the whole draft before they are shown. The fields and what each
// must hold are the exported spec's (lib/chat/spec_ercot.json): only their order is the site's.
export const FIELD_ORDER = ["form", "not_in_warehouse", "series", "premise", "answer", "citations", "nearest", "followups"];
export function inOrder(schema: Json): Json {
  const props = schema.properties as Json, required = schema.required as string[];
  const keys = [...FIELD_ORDER.filter((k) => k in props), ...Object.keys(props).filter((k) => !FIELD_ORDER.includes(k))];
  return { ...schema, properties: Object.fromEntries(keys.map((k) => [k, props[k]])), required: keys.filter((k) => required.includes(k)) };
}
/** Session 143: the model of the first turn, the one that decides what to read. "writer": the same model that writes
 * (the newest Sonnet-class model, as before). A smaller model was tried here ("claude-haiku-4-5") and was slower to its
 * first word and less exact (docs/methods/ask_ercot.md): ASK_PLANNER on the server names another model for a trial; it
 * must have a price in lib/chat/spec.json, or it is not used. */
export const PLANNER = "writer";

/** The profile as session 148 left it: the guide's tables, the energy mix's, the reserve prices by day and month, and the board and Supply and trade. */
function profile148(): Profile {
  const base = scopeOf("ercot");
  if (!base) throw new Error("docs/grids/grids.json has no grid ercot");
  // session 137: the mix tables' rows are a grid's by entity ("iso:ercot"); without this the scope filters on the market column, which they leave empty
  const mixFilters = Object.fromEntries(MIX_TABLES.map((t) => [t, { entity: `iso:${base.slug}` }]));
  // session 148: the reserve prices by day and by month (lib/chat/rollup.ts) are offered unless the server says
  // ASK_ROLLUP=off, which leaves the panel as session 143 left it. `held`: whether the site's live set holds both, as the
  // tables' summaries last said (the query tool asks the catalogue itself before it refuses an hourly read)
  const offered = rollupOffered();
  const more = offered ? ROLLUP_TABLES : [];
  let held = false;
  // the scope as session 143 left it, and on it, when the two tables are offered, their names, their rows whole and the rule on the hourly table
  const scope143 = { ...base, tables: [...spec.tables, ...MIX_TABLES], filters: { ...(spec.filters as Record<string, Record<string, string | string[]>>), ...mixFilters }, max_groups: spec.max_groups, dated_groups: spec.dated_groups };
  const scope: Scope = !offered ? scope143 : { ...scope143, tables: [...scope143.tables, ...more], filters: { ...scope143.filters, ...Object.fromEntries(more.map((t) => [t, {}])) }, rollup: { hourly: ROLLUP.hourly, tables: ROLLUP_TABLES } };
  const profile: Profile = {
    // session 137: the answer panel. The system prompt carries the panel's rules and the page's written content; the
    // answer names its form; the board's and Supply and trade's rows are read by a tool of the profile's own
    system: spec.system + addendum(base.slug, base.iso),
    schema: inOrder({ ...(spec.answer_schema as Json), properties: { ...((spec.answer_schema as Json).properties as Json), form: FORM_SCHEMA }, required: [...((spec.answer_schema as Json).required as string[]), "form"] }),
    // session 143: the planner, the tables' summaries held ready, the head of a draft that may be shown, the writing turn
    planner: PLANNER,
    brief: async () => {
      const { rows, readAt } = await tableSummaries(scope, [...spec.tables, ...MIX_TABLES, ...more], MIX_TABLES);
      held = offered && ROLLUP_TABLES.every((t) => rows.some((r) => r.table === t && r.held !== false));
      return readAt ? summaryText(rows, readAt) : "";
    },
    // session 148: a plan made by rule (lib/chat/plan.ts), for a first question only: a question that continues a
    // conversation takes its meaning from the turns before it, which the rule does not read. A reserve price is planned
    // only when the summaries have just said that the site holds the two tables it would read
    plan: (question, today, _context, history) => (cleanHistory(history).length ? null : rulePlan(question, today, { rollup: held })),
    // what the model is told when the rule's read did not settle the answer and the question is the model's after all
    resume: (opening, results) => `${opening}\n\nALREADY READ FOR THIS QUESTION, before your turn. These tool calls were made and this is what each returned. Do not repeat them: their results are here. Call tools for whatever else the question needs, all in one turn, then answer.\n\n` +
      results.map((r, i) => `CALL ${i + 1}: ${r.tool} ${JSON.stringify(r.input)}\nRESULT${r.isError ? " (an error)" : ""}: ${JSON.stringify(r.out)}`).join("\n\n"),
    early: (head, results, given) => {
      // the checks of extraProblems below that need no citation and no follow-up: the form, the series named, the premise
      const problems: string[] = [];
      const k = known(results);
      const ids = (Array.isArray(head.series) ? head.series : []) as string[];
      const form = FORMS.includes(head.form as Form) ? (head.form as Form) : null;
      if (!form) problems.push("no form");
      if ((form === "words" || form === "sentence") && ids.length) problems.push("a series under an answer in words or a sentence");
      if ((form === "chart" || form === "table") && !head.not_in_warehouse && !ids.length) problems.push("a chart or table that names no series");
      if (ids.some((i) => !k.has(i) || !chartable(...k.get(i)!)) || ids.length > spec.max_series) problems.push("series that are not results of this question");
      if (unverified(typeof head.premise === "string" ? head.premise : "", [...results.map((r) => JSON.stringify(r.out)), ...given]).length) problems.push("a premise with an untraced number");
      return problems;
    },
    // a follow-up question that fails its own check is left out, and the answer stands (lib/chat/ask.ts settle)
    tailOnly: (problems) => problems.length > 0 && problems.every((p) => p.startsWith("follow-up questions contain numbers") || p.startsWith("followups must be two or three")),
    mend: (draft, results) => {
      const pool = results.map((r) => JSON.stringify(r.out));
      const traced = (f: string) => numbers(f).every(([v, d]) => (d === 0 && Number.isInteger(v) && v >= YEAR_LO && v <= YEAR_HI) || !unverified(v.toFixed(d), pool).length);
      return { ...draft, followups: ((Array.isArray(draft.followups) ? draft.followups : []) as unknown[]).filter((f): f is string => typeof f === "string" && !!f.trim() && traced(f)).slice(0, 3) };
    },
    writing: (opening, results) => `${opening}\n\nTHE READING IS DONE. These are the tool calls made for this question, in order, and what each returned. No tool can be called in this turn.\n\n` +
      results.map((r, i) => `CALL ${i + 1}: ${r.tool} ${JSON.stringify(r.input)}\nRESULT${r.isError ? " (an error)" : ""}: ${JSON.stringify(r.out)}`).join("\n\n") +
      `\n\nWrite the answer now, as the JSON described, from these results and under every rule above. If they do not hold what the question needs (a call that is needed was not made, a result is an error, a row is missing), do not guess and do not refuse: reply with form "words", not_in_warehouse false, an empty answer and no citations. The question is then read again with the tools.`,
    effort: spec.effort, retry: spec.retry, scope,
    tools: [PAGE_TOOL],
    ownTool: (name, input) => (name === PAGE_TOOL.name ? Promise.resolve().then(() => { const out = pageFigures((input ?? {}) as Json, base.slug, base.iso); return { out, isError: "error" in out }; }) : null),
    preRead: [NOTES_TABLE(base.slug)],
    preSources: [notesOf(base.slug)],          // the page's written content is in the prompt, so its years and dates count as given
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
      if (name === "query" || (name === PAGE_TOOL.name && Array.isArray(out.result))) return { result_id: `r${n}`, ...out };
      if (name === "compare") return { ...out, a: { result_id: `r${n}a`, ...(out.a as Json) }, b: { result_id: `r${n}b`, ...(out.b as Json) } };
      return out;
    },
    extraProblems: (draft: Draft, results, given = []) => {
      const problems: string[] = [];
      const k = known(results);
      const ids = (Array.isArray(draft.series) ? draft.series : []) as string[];
      // session 137: the form the answer names, and what each form may carry
      // (a draft that names no form at all is the reference loop's, warehouse/chat/ercot.py: it is checked as it always was)
      const form = FORMS.includes(draft.form as Form) ? (draft.form as Form) : null;
      if (draft.form !== undefined && !form) problems.push(`form must be one of ${FORMS.join(", ")}`);
      if ((form === "words" || form === "sentence") && ids.length) problems.push(`form "${form}" carries no series: leave series empty, or use form "chart" if the question asked how something moved`);
      if ((form === "chart" || form === "table") && !draft.not_in_warehouse && !ids.length) problems.push(`form "${form}" needs the result it shows named in series; a single figure is form "sentence"`);
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
        if (near.length < 1 || near.length > S121.max_nearest || near.some((t) => !NEAR_TABLES.includes(t)))
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
      const near = (names: string[]): Nearest[] => names.filter((t) => NEAR_TABLES.includes(t)).slice(0, S121.max_nearest).map((t) => ({ table: t, holds: S121.holds[t] ?? MIX_HOLDS[t] ?? ROLLUP_HOLDS[t] ?? PAGES_HOLDS[t] ?? "" }));
      const legacy = !draft || draft.form === undefined;          // the reference loop's draft: series as sessions 92 and 121 chose them
      const form: Form = draft && FORMS.includes(draft.form as Form) ? (draft.form as Form) : "words";
      if (status === "not_in_warehouse" && draft)
        return { series: [], ...(legacy ? {} : { form: "words" }), followups, profile: "ercot", calls, premise: "", nearest: near(((Array.isArray(draft.nearest) ? draft.nearest : []) as unknown[]).map(String)) };
      if (status === "refused_unverified")  // the fixed refusal names nothing: the tables this question read are the nearest known
        return { series: [], ...(legacy ? {} : { form: "words" }), followups, profile: "ercot", calls, premise: "", nearest: near([...new Set([...k.values()].map(([, o]) => String(o.table)))]) };
      if (status !== "answered" || !draft) return { series: [], ...(legacy ? {} : { form: "words" }), followups, profile: "ercot", calls, premise: "", nearest: [] };
      // session 137: never a chart for its own sake. An answer in words or in a sentence shows no series, whatever was
      // fetched to write it; only "chart" and "table" do
      const shows = legacy || form === "chart" || form === "table";
      let ids = shows ? ((Array.isArray(draft.series) ? draft.series : []) as string[]).filter((i) => k.has(i) && chartable(...k.get(i)!)) : [];
      let chosen = "the answer";
      if (shows && !ids.length) {
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
        const g = String(groupOf(args, out));
        const fetched = (out.result as Json[]).map((r) => [String(r[g]), (r.value ?? r.count ?? null) as number | null] as const);
        const same = fetched.length === s.rows.length && fetched.every(([key, v], j) => s.rows[j].key === key && s.rows[j].value === v);
        const d = chartPoints(s.rows);
        return { ...s, check: { rows_fetched: fetched.length, rows: s.rows.length, same: same && pointsAreRows(s.rows, d), points: d.points.length, not_drawn: d.undrawn.length } };
      });
      const premise = nodash(typeof draft.premise === "string" ? draft.premise.trim() : "");
      return { ...(legacy ? {} : { form }), series: all.filter((s) => s.check.same), series_not_shown: all.filter((s) => !s.check.same).map((s) => s.result_id), followups, profile: "ercot", calls, premise, nearest: [] };
    },
  };
  // session 148: with the two tables offered, their guide follows the guide of the tables and comes before the panel's
  // rules; switched off, the system prompt is session 143's to the letter
  return offered ? { ...profile, system: spec.system + rollupGuide() + addendum(base.slug, base.iso) } : profile;
}

// Session 153: what stands behind four pages built this week (lib/chat/pagefiles.ts): /cost-of-power, /curtailment,
// /cost-of-power/seller and /resources. On the profile above, unless the server says ASK_PAGES=off (then it is session
// 148's to the letter): eight public tables of the live set join the scope, the tool page_file reads the pages' own
// files, the guide says what each is and is not, and a table held internally is refused by its name by every tool,
// before anything is read. A result of page_file that holds rows is marked like a query's, so it can be charted.
export const PAGES_TOOL_NAME = PAGE_FILE_TOOL.name;
export function ercotProfile(): Profile {
  const p = profile148();
  if (!pagesOffered() || !p.scope) return p;
  const scope: Scope = { ...p.scope, tables: [...p.scope.tables, ...PAGES_TABLES], filters: { ...p.scope.filters, ...PAGES_FILTERS } };
  const inner = { ownTool: p.ownTool, tag: p.tag };
  return {
    ...p, scope, system: p.system + pagesGuide(),
    tools: [...(p.tools ?? []), PAGE_FILE_TOOL as unknown as NonNullable<Profile["tools"]>[number]],
    ownTool: (name, input) => {
      // held, not shown: a query, a description or a comparison that names an internal table is refused here, by name
      const held = heldIn(input);
      if (held) return Promise.resolve({ out: heldRefusal(held), isError: true });
      if (name === PAGES_TOOL_NAME) return Promise.resolve().then(() => { const out = pageFile(input); return { out, isError: "error" in out }; });
      return inner.ownTool ? inner.ownTool(name, input) : null;
    },
    tag: (name, input, out, n) => (name === PAGES_TOOL_NAME ? ("error" in out || !Array.isArray(out.result) ? out : { result_id: `r${n}`, ...out }) : inner.tag(name, input, out, n)),
  };
}
export { HELD_WORDS };
