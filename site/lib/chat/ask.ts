// Energy Research Warehouse (ERW) site: the question-answering loop, server-side only.
//
// The same loop as warehouse/chat/ask.py: the system prompt, tools, answer schema, limits,
// retry message and prices all come from lib/chat/spec.json, which ask.py --export-spec
// writes. The model is the newest Sonnet-class model in the API's models list. At most
// 8 tool calls; then a post-check that every number in the answer appears in a tool result
// (or the question, or a tool argument) at the precision the answer states, and that every
// cited table was read. One retry with the violations named, then refusal.
// ANTHROPIC_API_KEY is read on the server and never reaches a browser.
import "server-only";
import Anthropic from "@anthropic-ai/sdk";
import spec from "./spec.json";
import { runTool as runWarehouseTool, scopeOf, type Scope } from "./tools";
import { recordCall } from "./ledger";
import { callKey, partialDraft, stageClock, type StageMs, type Step } from "./stages";
import { readerEffort, rulePlanOn } from "./switches";
import { plainTimes } from "./plaintime";

export type Citation = { table: string; source_report: string; data_version: string; tier: string };
export type AskResult = {
  answer: string;
  citations: Citation[];
  not_in_warehouse: boolean;
  status: "answered" | "not_in_warehouse" | "refused_unverified" | "model_refusal";
  model: string;
  tool_calls: number;
  retried: boolean;
  usage: { input: number; output: number; cache_write: number; cache_read: number; requests: number };
  cost_usd: number | null;
  /** session 121: seconds from the question to the full answer, and to the model's first reply (the first thing a reader can be shown) */
  seconds?: number;
  seconds_first?: number | null;
  /** session 143: the milliseconds of each stage (planning, fetching, drawing, writing, other), which sum to total; the
   * steps they are summed from; and the seconds to the answer's words. For the evaluation and the log, never the page */
  stages_ms?: StageMs;
  steps?: Step[];
  seconds_words?: number | null;
  /** session 1111: why a refused_unverified answer was refused, one sentence with no figure in it */
  why?: string;
};
/** Session 121: what a reader can be shown before the answer: the table a tool call has gone to read. */
export type AskEvent = { type: "reading"; tool: string; table: string | null }
  /** session 143: the answer's words, once its numbers, its form and its premise have passed the check, before the chart, the sources and the questions to ask next; and their withdrawal when the whole draft did not bear them out */
  | { type: "words"; answer: string; form: string | null; not_in_warehouse: boolean; premise: string }
  | { type: "withdrawn" };
export type AskOptions = { history?: unknown; onEvent?: (e: AskEvent) => void; /** session 128: the question's number in the cost ledger */ questionId?: string;
  /** session 143: when the request arrived (the stages are counted from it), and the steps the route took before the loop */
  startedAt?: number; before?: Step[];
  /** session 143, a session's own diagnosis only (scripts/probe-ask-ercot.mjs): asks for the summary of the model's reasoning and hands it over */
  thinking?: (text: string) => void;
  /** session 314: the ledger step the calls are written under (an evaluation's own, site_ask_eval) and whether a refused
   * write fails the question (an evaluation never spends unrecorded) */
  step?: string; strictLedger?: boolean;
  /** session 1111: record every tool call and its result in the answer (an evaluation only; the route sets it) */
  record?: boolean };

const PRICES = spec.prices as unknown as Record<string, [number, number]>;
const TOOLS = spec.tools as unknown as Anthropic.Tool[];

// Session 92: a profile of the loop, as warehouse/chat/ask.py's hooks (lib/chat/ercot.ts is the first). Without one
// the loop is the general chat's, unchanged. A profile brings its own system prompt, answer schema, effort and scope,
// may mark each tool result (a result id), may send a draft back for reasons of its own, and adds to the result.
export type ToolRecord = { tool: string; input: Record<string, unknown>; out: Record<string, unknown>; isError: boolean };
export type Draft = { answer: string; citations: Citation[]; not_in_warehouse: boolean } & Record<string, unknown>;
export type Profile = {
  system: string;
  schema: unknown;
  effort: string;
  retry: string;
  scope: Scope;
  opening: (question: string, today: string, context: unknown, history?: unknown) => string;
  /** session 168: the grid's own zone: a UTC stamp left in an answer is shown in its plain local words (lib/chat/plaintime.ts) */
  zone?: string;
  extraSources: (context: unknown, history?: unknown) => string[];
  /** session 121: tables an earlier answer of the conversation cited (citing one again is not citing a table unread) */
  knownTables?: (history: unknown) => string[];
  sourceTexts: (name: string, input: Record<string, unknown>, out: Record<string, unknown>) => string[];
  tag: (name: string, input: Record<string, unknown>, out: Record<string, unknown>, n: number) => Record<string, unknown>;
  /** `given`: the question and the other texts whose numbers count as given (session 121: a premise is checked against them) */
  extraProblems: (draft: Draft, results: ToolRecord[], given?: string[]) => string[];
  finish: (status: AskResult["status"], draft: Draft | null, results: ToolRecord[]) => Record<string, unknown>;
  /** session 137: tools of the profile's own, beside the warehouse's (the site's page files), and their runner (null: not its tool) */
  tools?: Anthropic.Tool[];
  ownTool?: (name: string, input: unknown) => Promise<{ out: Record<string, unknown>; isError: boolean }> | null;
  /** session 137: tables that count as read before any tool call (a text the system prompt already carries) */
  preRead?: string[];
  /** session 137: texts the system prompt carries whose numbers count as given (a written page's years and dates) */
  preSources?: string[];
  /** session 143: a smaller model for the first turn, the one that decides what to read (lib/chat/ask.ts says when its own answer stands) */
  planner?: string;
  /** session 143: "between_tools" asks the writer for its lowest thinking setting */
  thinking?: string;
  /** session 143: the tables' summaries, held ready, as a second block of the system prompt ("" when none is ready) */
  brief?: () => Promise<string>;
  /** session 143: the reasons the head of a draft (its form, series, premise and answer, before its citations and follow-ups are written) may not be shown yet */
  early?: (head: Draft, results: ToolRecord[], given: string[]) => string[];
  /** session 143: the message of the writing turn of the fast path: the question and everything the reading turn fetched */
  writing?: (opening: string, results: ToolRecord[]) => string;
  /** session 143: whether a draft's only problems are in its questions to ask next, and the draft with the ones that fail left out */
  tailOnly?: (problems: string[]) => boolean;
  mend?: (draft: Draft, results: ToolRecord[]) => Draft;
  /** session 148: the read a rule writes for a question of a known shape, with no reading turn by the model; null for
   * every question the rule does not account for word by word (lib/chat/plan.ts). Used unless ASK_RULE_PLAN=off (session 156) */
  plan?: (question: string, today: string, context: unknown, history?: unknown) => { shape: string; calls: { name: string; input: Record<string, unknown> }[] } | null;
  /** session 148: the first message of the loop when the rule's read did not settle the answer: the question, and what was already read */
  resume?: (opening: string, results: ToolRecord[]) => string;
  /** session 156: the tools as the model is shown them, after the profile's own are added: a profile may give one of the
   * warehouse's tools more arguments (lib/chat/forms.ts gives query and compare three). The tool that runs is the same */
  retool?: (tools: Anthropic.Tool[]) => Anthropic.Tool[];
};

/** Session 148: the effort the reading turn may be given by the server (ASK_READER_EFFORT); anything else is ignored. */
export const READER_EFFORTS = ["low", "medium", "high"];
/** The effort of one model call. The reading turn (the first turn of a profile that names a planner: the call that
 * decides what to read) takes the reader's effort when it is one of READER_EFFORTS; every other call, the writing turn
 * among them, is as it was: ASK_WRITER_EFFORT when set, else the profile's or the spec's own.
 * Session 156, the owner's ruling of 8 October 2026: the reader's effort is "low" unless the server's ASK_READER_EFFORT
 * says otherwise ("off", or any value that is not a setting, leaves the reading turn as every other call). The default
 * lives in lib/chat/switches.ts and nowhere else. */
export function effortOf(role: "planner" | "writer", own: string, env: Record<string, string | undefined> = process.env): string {
  const reader = readerEffort(env);
  if (role === "planner" && READER_EFFORTS.includes(reader)) return reader;
  return env.ASK_WRITER_EFFORT || own;
}

// ------------------------------------------------------------------ post-check (as ask.py)

const NUM = /(?<![A-Za-z_\d.])(-?)(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?!\d)/g;

export function numbers(text: string): [number, number][] {
  const t = text.replace(/−/g, "-");
  const out: [number, number][] = [];
  for (const m of t.matchAll(NUM)) {
    let sign = m[1];
    const whole = m[2], frac = m[3] ?? "";
    const at = m.index ?? 0;
    if (isName(t, at + sign.length)) continue;
    if (sign) {
      const before = at > 0 ? t[at - 1] : " ";
      if (!(/\s/.test(before) || "([:,=".includes(before) || at === 0)) sign = "";
    }
    out.push([parseFloat(sign + whole.replace(/,/g, "") + frac), frac ? frac.length - 1 : 0]);
  }
  return out;
}

/** Session 1110, as ask.py is_name: digits after a letter and a hyphen are a name, not a figure (EIA-930, EIA-860M). */
export function isName(text: string, at: number): boolean {
  return at >= 2 && text[at - 1] === "-" && /[A-Za-z]/.test(text[at - 2]);
}

function listMarkers(text: string): Set<number> {
  return new Set(Array.from(text.matchAll(/^\s*(\d+)[.)]\s/gm)).map((m) => parseFloat(m[1])));
}

export function unverified(answer: string, sources: string[]): string[] {
  const pool = sources.flatMap((s) => numbers(s).map(([v]) => v));
  const markers = listMarkers(answer);
  const bad: string[] = [];
  for (const [v, d] of numbers(answer)) {
    if (d === 0 && markers.has(v)) continue;
    const tol = 0.5 * 10 ** -d + 1e-9;
    if (!pool.some((p) => Math.abs(Math.abs(p) - Math.abs(v)) <= tol)) {
      const s = v.toFixed(d);
      if (!bad.includes(s)) bad.push(s);
    }
  }
  return bad;
}

// Session 1110, as ask.py unit_mismatches: a figure stated in a money unit (USD per MWh, per MW, per kW, per kWh) must be
// one a tool returned in that unit. A tool number takes its unit from its own key (..._usd_per_mw, value_usd_per_kw),
// else from the nearest unit or single units above it; a number no result places in a unit is not judged. A draft is
// sent back only when every returned number it matches is in another unit.
const UNIT_AFTER = /^\s*(USD|US dollars|dollars)?\s*(?:\/|per\s+)(kWh|kW|MWh|MW)(?![\w-])/i;
const MONEY_BEFORE = /(?:\$|USD\s)\s*$/;  // "$81.40/kW", "USD 81.40 per kW": the money is written before the figure
const UNIT_NAMES: Record<string, string> = { kwh: "kWh", kw: "kW", mwh: "MWh", mw: "MW" };
export function normUnit(u: unknown): string | null {
  if (typeof u !== "string") return null;
  const t = u.trim().toLowerCase().replace(/ per /g, "/").replace(/ /g, "").replace(/\$/g, "usd");
  const m = /^usd\/(kwh|kw|mwh|mw)$/.exec(t);
  return m ? `USD/${UNIT_NAMES[m[1]]}` : `other:${t}`;
}
const keyUnit = (key: string | null): string | null => {
  const m = /_usd_per_(kwh|kw|mwh|mw)$/i.exec(key ?? "");
  return m ? `USD/${UNIT_NAMES[m[1].toLowerCase()]}` : null;
};
export function placedNumbers(sources: string[]): [number, string | null][] {
  const out: [number, string | null][] = [];
  const walk = (x: unknown, unit: string | null, key: string | null) => {
    if (x === null || x === undefined || typeof x === "boolean") return;
    if (typeof x === "number") { out.push([x, keyUnit(key) ?? unit]); return; }
    if (Array.isArray(x)) { for (const v of x) walk(v, unit, key); return; }
    if (typeof x === "object") {
      const o = x as Record<string, unknown>;
      let own: string | null = null;
      if (typeof o.unit === "string") own = normUnit(o.unit);
      else if (Array.isArray(o.units) && o.units.length) own = o.units.length === 1 ? normUnit(o.units[0]) : "mixed";
      for (const [k, v] of Object.entries(o)) walk(v, own ?? unit, k);
    }
  };
  for (const s of sources) {
    try { walk(JSON.parse(s), null, null); } catch { /* not JSON: its numbers are placed in no unit */ }
  }
  return out;
}
export function unitMismatches(answer: string, sources: string[]): string[] {
  const t = answer.replace(/−/g, "-");
  const placed = placedNumbers(sources);
  const bad: string[] = [];
  for (const m of t.matchAll(NUM)) {
    const at = (m.index ?? 0) + m[1].length;
    if (isName(t, at)) continue;
    const u = UNIT_AFTER.exec(t.slice((m.index ?? 0) + m[0].length, (m.index ?? 0) + m[0].length + 40));
    if (!u || !(u[1] || MONEY_BEFORE.test(t.slice(Math.max(0, (m.index ?? 0) - 5), m.index ?? 0)))) continue;  // MWh per MW, USD per MW-month: not judged here
    const frac = m[3] ?? "";
    const v = parseFloat(m[2].replace(/,/g, "") + frac), d = frac ? frac.length - 1 : 0;
    const said = `USD/${UNIT_NAMES[u[2].toLowerCase()]}`;
    const tol = 0.5 * 10 ** -d + 1e-9;
    const hits = placed.filter(([p]) => Math.abs(Math.abs(p) - Math.abs(v)) <= tol).map(([, unit]) => unit);
    if (hits.length && hits.every((h) => h !== null && h !== "mixed") && !hits.includes(said)) {
      const gave = Array.from(new Set(hits.map((h) => h!.replace("other:", "")))).sort().join(", ");
      const s = `${v.toFixed(d)} ${said} (the tools gave it in ${gave})`;
      if (!bad.includes(s)) bad.push(s);
    }
  }
  return bad;
}

/** Session 1115: what one query or compare read, for the line under an answer: the table, the rows asked for and the
 * window, never a figure (the figures are the answer's own, checked). A failed call reads nothing and is not listed. */
export type Read = { table: string; entity?: string; variable?: string; start?: string; end?: string; aggregation?: string; group_by?: string; tz?: string };
export function readsOf(name: string, input: Record<string, unknown>): Read[] {
  const one = (a: Record<string, unknown> | undefined): Read[] => {
    if (!a || typeof a.table !== "string") return [];
    const r: Read = { table: a.table };
    for (const k of ["entity", "variable", "start", "end", "aggregation", "group_by", "tz"] as const) if (typeof a[k] === "string" && a[k]) r[k] = a[k] as string;
    return [r];
  };
  if (name === "query") return one(input);
  if (name === "compare") return [...one(input.a as Record<string, unknown>), ...one(input.b as Record<string, unknown>)];
  return [];
}

/** Session 1111, as ask.py why_refused: why a draft was refused, in one sentence with no figure in it. */
export function whyRefused(c: { bad: string[]; units: string[]; uncited: string[]; noCite: boolean; more: string[] }): string {
  const parts: string[] = [];
  if (c.bad.length) parts.push(c.bad.length === 1 ? "a figure in it was in no tool result" : "figures in it were in no tool result");
  if (c.units.length) parts.push(c.units.length === 1 ? "a figure was stated in a unit no tool gave it in" : "figures were stated in a unit no tool gave them in");
  if (c.uncited.length) parts.push("it cited a table no tool read");
  if (c.noCite) parts.push("it was empty or cited nothing");
  if (c.more.length && !parts.length) parts.push("it failed this chat's own checks");
  if (!parts.length) return "";
  const body = parts.length === 1 ? parts[0] : `${parts.slice(0, -1).join(", ")} and ${parts[parts.length - 1]}`;
  return `Why: the draft was checked twice and ${body}.`;
}

// ------------------------------------------------------------------ the loop

let modelCache: string | null = null;
async function pickModel(client: Anthropic): Promise<string> {
  if (modelCache) return modelCache;
  const sonnets: { id: string; created_at: string }[] = [];
  for await (const m of client.models.list()) if (m.id.toLowerCase().includes("sonnet")) sonnets.push(m);
  if (!sonnets.length) throw new Error("the models list has no Sonnet-class model");
  modelCache = sonnets.reduce((a, b) => (new Date(b.created_at) > new Date(a.created_at) ? b : a)).id;
  return modelCache;
}

function cost(model: string, u: AskResult["usage"]): number | null {
  const p = PRICES[model];
  if (!p) return null;
  const [pi, po] = p;
  return (u.input * pi + u.cache_write * pi * 1.25 + u.cache_read * pi * 0.1 + u.output * po) / 1e6;
}

export async function ask(question: string, today = new Date().toISOString().slice(0, 10), grid: string | null = null,
  profile: Profile | null = null, context: unknown = null, opts: AskOptions = {}): Promise<AskResult & Record<string, unknown>> {
  const t0 = opts.startedAt ?? Date.now();
  let secondsFirst: number | null = null;
  // session 143: every step is timed; the stages sum to the whole (lib/chat/stages.ts)
  const clock = stageClock(t0);
  for (const s of opts.before ?? []) clock.add(s.stage, s.what, s.ms);
  // session 121: the cost ledger's rows are written beside the loop and awaited once, before the answer is returned:
  // a row's insert no longer stands between one model call and the next
  const ledger: Promise<void>[] = [];
  const done = async <T extends object>(r: T) => {
    await Promise.allSettled(ledger);
    const stages_ms = clock.done();
    return { ...r, seconds: Math.round((Date.now() - t0) / 100) / 10, seconds_first: secondsFirst, stages_ms, steps: clock.steps,
      seconds_words: clock.wordsMs === null ? null : Math.round(clock.wordsMs / 100) / 10 };
  };
  // session 35: /ask?grid=<slug>: the grid's block after the system prompt, and the tools scoped to its tables and rows
  const scope = profile ? profile.scope : scopeOf(grid);
  const system: { type: "text"; text: string; cache_control?: { type: "ephemeral" } }[] = [{ type: "text", text: profile ? profile.system : spec.system, cache_control: { type: "ephemeral" } }];
  if (scope && !profile) {
    const fill: Record<string, string> = { ...(scope as unknown as Record<string, string>), ba_code: scope.entity.split(":")[1] };
    system.push({ type: "text", text: spec.grid_system.replace(/\{(\w+)\}/g, (m: string, k: string) => (k in fill ? String(fill[k]) : m)) });
  }
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) throw new Error("ANTHROPIC_API_KEY is not set on the server");
  const client = new Anthropic({ apiKey: key });
  // session 143: the list of models and the tables' summaries are asked for together; a summary that fails is left out
  const [writer, brief] = await clock.time("other", "models and summaries", () => Promise.all([pickModel(client), profile?.brief ? profile.brief().catch(() => "") : Promise.resolve("")]));
  if (brief) system.push({ type: "text", text: brief, cache_control: { type: "ephemeral" } });
  // session 143: the smaller model that plans the reading, when the profile names one that has a price (a call with no
  // price would close the tool: lib/chat/limits.ts). ASK_PLANNER=off on the server leaves every call to the writer.
  const named = profile?.planner ? (process.env.ASK_PLANNER || profile.planner) : null;   // ASK_PLANNER names another model for a trial
  const planner = named === "writer" ? writer : named && named !== "off" && PRICES[named] ? named : null;
  const opening = profile ? profile.opening(question, today, context, opts.history) : `Today is ${today} (UTC).\n\nQuestion: ${question}`;
  const messages: Anthropic.MessageParam[] = [{ role: "user", content: opening }];
  const usage = { input: 0, output: 0, cache_write: 0, cache_read: 0, requests: 0 };
  let spent: number | null = 0; // session 143: the calls of one answer may be two models': each is priced as its own
  // session 137: the date the opening line gives the model counts as given, as the question's own numbers do
  const given: string[] = [question, `Today is ${today} (UTC).`, ...(profile ? profile.extraSources(context, opts.history) : []), ...(profile?.preSources ?? [])];
  const sources: string[] = [...given];
  const records: ToolRecord[] = []; // session 92: every tool result, in order, for a profile's checks and its result
  const tablesRead = new Set<string>([...(profile?.knownTables ? profile.knownTables(opts.history) : []), ...(profile?.preRead ?? [])]);
  // session 137: a profile's own tool is run by the profile; every other name goes to the warehouse's tools as before
  // session 143: each tool call's own milliseconds are kept (they overlap within a turn, so the stage is the turn's wall
  // time). A call already made for this question, with the same arguments, is not made again: the model is told that
  // its result is above (the tool as it stood asked the same query up to eight times, a model call each)
  const toolMs: { tool: string; table: string | null; ms: number; args?: unknown; repeat?: boolean }[] = [];
  const ran = new Set<string>();
  type Ran = { out: Record<string, unknown>; isError: boolean; repeat?: boolean };
  const runTool = async (name: string, input: unknown, sc: Scope): Promise<Ran> => {
    const t = Date.now(), k = profile ? callKey(name, input) : null;
    const repeat = k !== null && ran.has(k);
    if (k !== null) ran.add(k);
    try {
      if (repeat) return { out: { note: "this exact call was already made for this question and its result is above: answer from it; do not call it again" }, isError: false, repeat: true };
      return await (profile?.ownTool?.(name, input) ?? runWarehouseTool(name, input, sc));
    } finally {
      toolMs.push({ tool: name, table: typeof (input as Record<string, unknown> | null)?.table === "string" ? String((input as Record<string, unknown>).table) : null, ms: Date.now() - t, args: input, ...(repeat ? { repeat: true } : {}) });
    }
  };
  const tiers = new Map<string, string>(); // session 28: each table's tier, from the tool results
  let calls = 0, attempts = 0, retried = false, turn = 0, forceWrite = false, wordsOut = false;
  const nodash = (t: string) => t.split(String.fromCharCode(0x2014)).join(" - ").replace(/ {2}- {2}/g, " - ");
  // session 168: the local words the tool results gave for each stamp, and a profile's text with no UTC stamp left in it.
  // Applied to what the reader is shown, after the number check has run on the text as the model wrote it
  const localWords = new Map<string, string>();
  const plain = (t: string) => (profile?.zone ? plainTimes(t, profile.zone, localWords) : t);
  const withdraw = () => { if (wordsOut) { wordsOut = false; clock.wordsReset(); opts.onEvent?.({ type: "withdrawn" }); } };

  // One model call, read as a stream (session 143). `tools`: whether the call may ask for tools at all (the writing
  // turn of the fast path may not). `show`: whose words may be shown before the whole draft is in: "any" answer's, only
  // an answer in "words" (the planner's own), only an "answered" one, or "none". The words are shown when the answer's
  // string has closed and its numbers, its form and its premise have passed the same checks the whole draft passes
  // below; the whole draft is still checked when it is in, and words that it does not bear out are taken back.
  const call = async (model: string, tools: "auto" | "none" | "absent", msgs: Anthropic.MessageParam[], show: "any" | "words" | "answered" | "none", role: "planner" | "writer" = "writer") => {
    const params: Record<string, unknown> = {
      model,
      max_tokens: spec.max_tokens,
      system,
      tools: profile?.tools ? [...TOOLS, ...profile.tools] : TOOLS,
      tool_choice: { type: tools === "auto" ? "auto" : "none" },
      // a model that takes no effort setting (the planner's) is sent none
      // session 148: the reading turn may be given a lower effort by the server (effortOf above); the writing turn is as it was
      output_config: { ...(/haiku-4-5/.test(model) ? {} : { effort: effortOf(role, profile ? profile.effort : spec.effort) }), format: { type: "json_schema", schema: profile ? profile.schema : spec.answer_schema } },
      cache_control: { type: "ephemeral" }, // session 30 (B2): the growing conversation is cached, as in ask.py
      messages: msgs,
      ...(opts.thinking ? { thinking: { type: "adaptive", display: "summarized" } } : {}),
      // the writer's lowest thinking setting, where the profile or the server asks for it and the model takes it
      ...(!opts.thinking && /sonnet-5-5/.test(model) && (process.env.ASK_THINKING || profile?.thinking) === "between_tools" ? { thinking: { type: "between_tools" } } : {}),
    };
    // session 156: a profile may show the model one of the warehouse's tools with more arguments (the same tool runs)
    if (profile?.retool) params.tools = profile.retool(params.tools as Anthropic.Tool[]);
    if (tools === "absent") { delete params.tools; delete params.tool_choice; }
    const tCall = Date.now();
    let firstText: number | null = null, tried = false, wordsMs: number | null = null;
    const stream = client.messages.stream(params as unknown as Anthropic.MessageStreamParams);
    stream.on("text", (_delta, snapshot) => {
      if (firstText === null) firstText = Date.now() - tCall;
      if (tried || wordsOut || show === "none" || !profile?.early || !opts.onEvent) return;
      const head = partialDraft(snapshot);
      if (!head) return;
      tried = true; // once a call: the answer's string has closed
      const words = String(head.answer);
      if (!words.trim() || (show === "words" && head.form !== "words") || (show === "answered" && head.not_in_warehouse)) return;
      if (unverified(words, sources).length || profile.early(head as Draft, records, given).length) return;
      wordsOut = true;
      wordsMs = Date.now() - tCall;
      clock.wordsAt();
      opts.onEvent({ type: "words", answer: plain(nodash(words)), form: typeof head.form === "string" ? head.form : null, not_in_warehouse: head.not_in_warehouse === true, premise: typeof head.premise === "string" ? plain(nodash(head.premise.trim())) : "" });
    });
    const resp = (await stream.finalMessage()) as Anthropic.Message;
    const raw = { data: resp, request_id: stream.request_id };
    if (opts.thinking) opts.thinking(JSON.stringify(resp.content.map((b) => (b.type === "thinking" ? { thinking: b.thinking } : b.type === "text" ? { text: b.text.slice(0, 300) } : b.type === "tool_use" ? { tool_use: b.name } : { type: b.type }))));
    const row = recordCall(model, resp, raw.request_id, opts.step ?? (profile ? "site_ask_ercot" : "site_ask"), opts.questionId, opts.strictLedger === true); // session 30: every call into the cost ledger (site_api_calls)
    if (opts.strictLedger) await row; else ledger.push(row);
    if (secondsFirst === null) secondsFirst = Math.round((Date.now() - t0) / 100) / 10;
    const u = { input: resp.usage.input_tokens, output: resp.usage.output_tokens, cache_write: resp.usage.cache_creation_input_tokens ?? 0, cache_read: resp.usage.cache_read_input_tokens ?? 0, requests: 1 };
    usage.input += u.input; usage.output += u.output; usage.cache_write += u.cache_write; usage.cache_read += u.cache_read; usage.requests += 1;
    const c = cost(model, u);
    spent = spent === null || c === null ? null : spent + c;
    return { resp, ms: Date.now() - tCall, note: { model, role, first_text_ms: firstText, words_ms: wordsMs, output_tokens: resp.usage.output_tokens, stop: resp.stop_reason,
      ...(/haiku-4-5/.test(model) ? {} : { effort: effortOf(role, profile ? profile.effort : spec.effort) }) } };
  };
  // session 267: the evaluation's record of every tool call and its result (ASK_RECORD_TOOLS=1 on a local server only;
  // off by default, so a visitor's answer never carries it). The offline fixtures of warehouse/chat/eval are made from it.
  const traced: { tool: string; input: unknown; out: unknown; isError: boolean }[] = [];
  // session 1111: an evaluation admitted by its own token records them too (opts.record, set by the route); a visitor never
  const tracing = process.env.ASK_RECORD_TOOLS === "1" || opts.record === true;
  // session 1115: what each query read, shown under the answer (readsOf); every answer carries it when there is one
  const readsLog: Read[] = [];
  const base = () => ({ model: writer, ...(planner ? { planner } : {}), tool_calls: calls, retried, usage, cost_usd: spent, ...(tracing ? { trace: traced } : {}), ...(readsLog.length ? { reads: readsLog } : {}) });
  const textOf = (resp: Anthropic.Message) => resp.content.map((b) => (b.type === "text" ? b.text : "")).join("");
  // The check of a whole draft, as it always was: every number in a tool result, every cited table read, an answer and
  // a citation, and the profile's own reasons.
  const check = (draft: Draft) => {
    const tCheck = Date.now();
    const bad = unverified(draft.answer, sources);
    const units = unitMismatches(draft.answer, sources);  // session 1110
    const uncited = draft.citations.map((c) => c.table).filter((t) => !tablesRead.has(t));
    // session 35, as ask.py: an empty or uncited answer is sent back; "not in the warehouse" needs no citation
    const noCite = !draft.not_in_warehouse && (!draft.citations.length || !draft.answer.trim());
    const more = profile ? profile.extraProblems(draft, records, given) : [];
    clock.add("writing", "check", Date.now() - tCheck);
    const ok = !bad.length && !units.length && !uncited.length && !noCite && !more.length;
    return { ok, bad, units, uncited, noCite, more };
  };
  // session 137: what a draft is sent back for goes to the server's log, never to the reader
  const logCheck = (c: ReturnType<typeof check>, where: string) => console.log(JSON.stringify({ erw_ask_check: { question_id: opts.questionId ?? null, attempt: attempts + 1, where, untraced_numbers: c.bad.slice(0, 12), unit_mismatches: c.units.slice(0, 6), uncited_tables: c.uncited.slice(0, 6), no_citation: c.noCite, problems: c.more.slice(0, 6) } }));
  const accept = (draft: Draft) => {
    // no em dashes in ERW copy (CLAUDE.md): model text is normalised, as in ask.py
    const answer = plain(nodash(draft.answer));
    // session 28: each citation's tier is the warehouse's, whatever the model copied
    const citations = draft.citations.map((c) => ({ ...c, tier: tiers.get(c.table) ?? c.tier ?? "" }));
    const status = draft.not_in_warehouse ? ("not_in_warehouse" as const) : ("answered" as const);
    const tDraw = Date.now();
    const drawn: Record<string, unknown> = profile ? profile.finish(status, { ...draft, citations }, records) : {};
    if (typeof drawn.premise === "string") drawn.premise = plain(drawn.premise);
    clock.add("drawing", "series", Date.now() - tDraw);
    return done({ ...draft, answer, citations, status, ...base(), ...drawn });
  };

  // session 143: a draft whose answer passes every check and whose only fault is in its questions to ask next (a
  // number in one of them, or too few of them) stands, without the questions that failed: nothing unchecked is shown,
  // and the reader's answer is not written again for the sake of a suggestion. null: the draft does not stand.
  const settle = (draft: Draft, where: string) => {
    const c = check(draft);
    if (c.ok) return { c, answer: accept(draft) };
    logCheck(c, where);
    if (!c.bad.length && !c.units.length && !c.uncited.length && !c.noCite && profile?.mend && profile.tailOnly?.(c.more)) return { c, answer: accept(profile.mend(draft, records)) };
    return { c, answer: null };
  };

  // What a tool result that was read brings: the profile's mark on it (a result id), its record, its texts as sources of
  // numbers, the tables it read and their tiers. The same for a call the model asked for and for one a rule wrote
  // (session 148). `n` is the call's ordinal; `raw` the arguments as the model sent them. Returns the result as marked.
  function take(name: string, input: Record<string, unknown>, got: { out: Record<string, unknown>; isError: boolean }, n: number, raw: unknown = input) {
    let { out } = got;
    const { isError } = got;
    // session 168: the stamps the tools gave words for (lib/chat/plaintime.ts addLocalTimes), for the answer's text
    const words = (o: unknown) => { if (!o || typeof o !== "object") return; for (const [k, v] of Object.entries(o as Record<string, unknown>)) {
      if (k.endsWith("_local") && typeof v === "string") { const at = (o as Record<string, unknown>)[k.slice(0, -6)]; if (typeof at === "string") localWords.set(at, v); }
      else if (v && typeof v === "object") words(v); } };
    if (profile?.zone) words(out);
    if (tracing) traced.push({ tool: name, input, out, isError });
    if (!isError && !out.held) for (const r of readsOf(name, input)) if (!readsLog.some((x) => JSON.stringify(x) === JSON.stringify(r))) readsLog.push(r);
    if (profile) {
      out = profile.tag(name, input, out, n);
      records.push({ tool: name, input, out, isError });
      sources.push(...profile.sourceTexts(name, input, out));
    }
    sources.push(JSON.stringify(out), JSON.stringify(raw));
    if (typeof out.table === "string") tablesRead.add(out.table);
    if (typeof out.table === "string" && typeof out.tier === "string") tiers.set(out.table, out.tier);
    for (const sub of ["a", "b"]) {
      const s = out[sub] as Record<string, unknown> | undefined;
      if (s && typeof s.table === "string") tablesRead.add(s.table);
      if (s && typeof s.table === "string" && typeof s.tier === "string") tiers.set(s.table, s.tier);
    }
    if (name === "list_tables")
      for (const t of (out.tables as { table: string; tier?: string | null }[]) ?? []) {
        tablesRead.add(t.table);
        if (t.tier) tiers.set(t.table, t.tier);
      }
    return { out, isError };
  }

  // The writing turn of the fast path (session 143), also the writing turn after a plan made by rule (session 148,
  // `path` "rule"): the writer writes from what was read, in a call that can ask for no tool. The answer when a draft
  // passes the whole check; null when none does, and the loop below takes the question as it always did.
  const fastWrite = async (path: "fast" | "rule") => {
    const asked: Anthropic.MessageParam[] = [{ role: "user", content: profile!.writing!(opening, records) }];
    for (let pass = 0; pass < 2; pass++) {
      const w = await call(writer, "absent", asked, "answered");
      clock.add("writing", "model", w.ms, { ...w.note, path: pass ? `${path}, again` : path });
      if (w.resp.stop_reason !== "end_turn") break;
      let draft: Draft | null = null;
      try { draft = JSON.parse(textOf(w.resp)) as Draft; } catch { draft = null; }
      // an empty answer is the writer saying the results do not hold what the question needs; "not in the
      // warehouse" after one reading turn is not taken on trust either: both go to the loop below
      if (!draft || draft.not_in_warehouse || !draft.answer.trim()) break;
      const s = settle(draft, pass ? `${path} path, again` : `${path} path`);
      if (s.answer) return s.answer;
      withdraw();
      if (pass) break;
      // one more writing turn, still with no tool to call, with what failed named: a number that cannot be traced
      // is taken out here in seconds, where the loop below would read everything again
      retried = true;
      const problems: string[] = [];
      if (s.c.bad.length) problems.push(`numbers in no tool result: ${s.c.bad.join(", ")}`);
      if (s.c.units.length) problems.push(`numbers stated in a unit no tool result gives them in: ${s.c.units.join(", ")}`);
      if (s.c.uncited.length) problems.push(`cited tables no tool read: ${s.c.uncited.join(", ")}`);
      if (s.c.noCite) problems.push("an empty answer, or no citations");
      problems.push(...s.c.more);
      asked.push({ role: "assistant", content: w.resp.content }, { role: "user", content: `${profile!.retry.replace("{problems}", problems.join("; "))} No tool can be called in this turn: write only what these results bear out.` });
    }
    withdraw();
    return null;
  };

  // Session 148, a plan made by rule. Session 156, the owner's ruling of 8 October 2026: it is on by default
  // (lib/chat/switches.ts holds the default; ASK_RULE_PLAN=off on the server turns it off). For a question whose
  // every word the profile's rule accounts for (lib/chat/plan.ts), the read is written by code and made at once: there
  // is no reading turn by the model. The writer then writes from the rows, in the same writing turn and under the same
  // checks as the fast path: the numbers, the cited tables, the form, the series against the rows fetched. When that
  // turn does not settle the answer (a row is missing, the writer says the results do not hold it), nothing is shown and
  // the question goes to the model with its tools as it always did, told what was already read; the calls the rule made
  // count toward the limit and are never made twice.
  if (profile?.plan && profile.writing && profile.resume && rulePlanOn()) {
    const tRule = Date.now();
    const plan = profile.plan(question, today, context, opts.history);
    if (plan && plan.calls.length && plan.calls.length <= spec.max_tool_calls) {
      clock.add("planning", "rule", Date.now() - tRule, { shape: plan.shape, calls: plan.calls.length });
      const slots = plan.calls.map(() => ++calls);
      for (const c of plan.calls) opts.onEvent?.({ type: "reading", tool: c.name, table: typeof c.input.table === "string" ? c.input.table : null });
      const tTools = Date.now();
      const outs = await Promise.all(plan.calls.map((c) => runTool(c.name, c.input, scope)));
      clock.add("fetching", "tools", Date.now() - tTools, { calls: toolMs.slice(0), by: "rule" });
      outs.forEach((got, i) => take(plan.calls[i].name, plan.calls[i].input, got, slots[i]));
      // a read that came back an error is not written from: the model takes the question
      if (outs.every((o) => !o.isError)) {
        const ruled = await fastWrite("rule");
        if (ruled) return { ...(await ruled), planned_by: "rule", plan_shape: plan.shape };
      }
      messages[0] = { role: "user", content: profile.resume(opening, records) };
    }
  }

  for (;;) {
    // session 143: the first turn is the planner's when the profile names one: it decides what to read
    const planning = planner !== null && turn === 0;
    turn += 1;
    const model = planning ? planner : writer;
    const { resp, ms, note } = await call(model, calls < spec.max_tool_calls && !forceWrite ? "auto" : "none", messages, planning && planner !== writer ? "words" : "any", planning ? "planner" : "writer");
    messages.push({ role: "assistant", content: resp.content });

    if (resp.stop_reason === "tool_use") {
      clock.add("planning", "model", ms, note);
      withdraw();
      const results: Anthropic.ToolResultBlockParam[] = [];
      // session 121: the tool calls of one model turn are read together, not one after another. Each keeps the ordinal it
      // would have had (0: past the limit), so the result ids are the ones a sequential loop gives
      const blocks = resp.content.filter((b): b is Anthropic.ToolUseBlock => b.type === "tool_use");
      const slots = blocks.map(() => (calls < spec.max_tool_calls ? ++calls : 0));
      for (const [i, b] of blocks.entries())
        if (slots[i]) opts.onEvent?.({ type: "reading", tool: b.name, table: typeof (b.input as Record<string, unknown> | null)?.table === "string" ? String((b.input as Record<string, unknown>).table) : null });
      const tTools = Date.now(), firstTool = toolMs.length;
      const outs = await Promise.all(blocks.map((b, i) => (slots[i] ? runTool(b.name, b.input, scope) : null)));
      clock.add("fetching", "tools", Date.now() - tTools, { calls: toolMs.slice(firstTool) });
      let fresh = 0;
      for (const [i, b] of blocks.entries()) {
        let out: Record<string, unknown>, isError: boolean;
        const got = outs[i];
        if (!got) {
          out = { error: `tool call limit (${spec.max_tool_calls}) reached; answer now` };
          isError = true;
        } else if (got.repeat) {
          ({ out, isError } = got);          // nothing was read: it is no source and no record
        } else {
          fresh += 1;
          ({ out, isError } = take(b.name, (b.input ?? {}) as Record<string, unknown>, got, slots[i], b.input));
        }
        results.push({ type: "tool_result", tool_use_id: b.id, content: JSON.stringify(out), is_error: isError });
      }
      messages.push({ role: "user", content: results });
      // session 143: a turn that only repeated calls already made has nothing new to read: the next call must write
      if (profile && blocks.length && fresh === 0) forceWrite = true;
      // session 143, the fast path: after the planner's one reading turn the writer writes from what was read, in a
      // call that can ask for no tool, so its words arrive as they are written. A draft that passes the whole check is
      // the answer. One that does not (the results do not hold what the question needs, a number is untraced, the writer
      // says "not in the warehouse") is not shown: the loop goes on below as it always did, the writer with its tools.
      if (planning && profile?.writing && fresh > 0 && process.env.ASK_FAST !== "off") {
        const fast = await fastWrite("fast");
        if (fast) return fast;
      }
      continue;
    }
    if (resp.stop_reason === "refusal") {
      clock.add("writing", "model", ms, note);
      withdraw();
      return done({ answer: spec.refusal, citations: [], not_in_warehouse: false, status: "model_refusal" as const, ...base(), ...(profile ? profile.finish("model_refusal", null, records) : {}) });
    }
    if (resp.stop_reason !== "end_turn") throw new Error(`stop_reason ${resp.stop_reason}`);
    const draft = JSON.parse(textOf(resp)) as Draft;
    if (planning && planner !== writer) {
      // session 143: a planner that is another model than the writer answered without reading. Its answer stands only when it is an answer in words (an
      // idea from the page's text, or a refusal that says where to look) and passes the whole check; anything else is
      // set aside unseen and the writer takes the question from the start, as before this session.
      const c = draft.form === "words" ? check(draft) : null;
      if (c?.ok) { clock.add("writing", "model", ms, { ...note, path: "planner" }); return accept(draft); }
      clock.add("planning", "model", ms, { ...note, set_aside: true });
      if (c) logCheck(c, "planner");
      withdraw();
      messages.pop();
      continue;
    }
    clock.add("writing", "model", ms, note);
    const { c, answer: settled } = settle(draft, "loop");
    if (settled) return settled;
    withdraw();
    attempts += 1;
    if (attempts === 1) {
      retried = true;
      const problems: string[] = [];
      if (c.bad.length) problems.push(`numbers in no tool result: ${c.bad.join(", ")}`);
      if (c.units.length) problems.push(`numbers stated in a unit no tool result gives them in: ${c.units.join(", ")}`);
      if (c.uncited.length) problems.push(`cited tables no tool read: ${c.uncited.join(", ")}`);
      if (c.noCite) problems.push("an empty answer, or no citations");
      problems.push(...c.more);
      messages.push({ role: "user", content: (profile ? profile.retry : spec.retry).replace("{problems}", problems.join("; ")) });
      forceWrite = false; // the retry may read again
      continue;
    }
    const why = whyRefused(c);  // session 1111: the refusal says why in one sentence, with no figure in it
    return done({ answer: `${spec.refusal} ${why}`.trim(), why, citations: [], not_in_warehouse: false, status: "refused_unverified" as const, ...base(), retried: true,
      ...(profile ? profile.finish("refused_unverified", null, records) : {}) });
  }
}
