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
import { stageClock, type StageMs, type Step } from "./stages";

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
};
/** Session 121: what a reader can be shown before the answer: the table a tool call has gone to read. */
export type AskEvent = { type: "reading"; tool: string; table: string | null };
export type AskOptions = { history?: unknown; onEvent?: (e: AskEvent) => void; /** session 128: the question's number in the cost ledger */ questionId?: string;
  /** session 143: when the request arrived (the stages are counted from it), and the steps the route took before the loop */
  startedAt?: number; before?: Step[] };

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
};

// ------------------------------------------------------------------ post-check (as ask.py)

const NUM = /(?<![A-Za-z_\d.])(-?)(\d{1,3}(?:,\d{3})+|\d+)(\.\d+)?(?!\d)/g;

export function numbers(text: string): [number, number][] {
  const t = text.replace(/−/g, "-");
  const out: [number, number][] = [];
  for (const m of t.matchAll(NUM)) {
    let sign = m[1];
    const whole = m[2], frac = m[3] ?? "";
    const at = m.index ?? 0;
    if (sign) {
      const before = at > 0 ? t[at - 1] : " ";
      if (!(/\s/.test(before) || "([:,=".includes(before) || at === 0)) sign = "";
    }
    out.push([parseFloat(sign + whole.replace(/,/g, "") + frac), frac ? frac.length - 1 : 0]);
  }
  return out;
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
  const model = await clock.time("other", "models", () => pickModel(client));
  const messages: Anthropic.MessageParam[] = [{ role: "user", content: profile ? profile.opening(question, today, context, opts.history) : `Today is ${today} (UTC).\n\nQuestion: ${question}` }];
  const usage = { input: 0, output: 0, cache_write: 0, cache_read: 0, requests: 0 };
  // session 137: the date the opening line gives the model counts as given, as the question's own numbers do
  const given: string[] = [question, `Today is ${today} (UTC).`, ...(profile ? profile.extraSources(context, opts.history) : []), ...(profile?.preSources ?? [])];
  const sources: string[] = [...given];
  const records: ToolRecord[] = []; // session 92: every tool result, in order, for a profile's checks and its result
  const tablesRead = new Set<string>([...(profile?.knownTables ? profile.knownTables(opts.history) : []), ...(profile?.preRead ?? [])]);
  // session 137: a profile's own tool is run by the profile; every other name goes to the warehouse's tools as before
  // session 143: each tool call's own milliseconds are kept (they overlap within a turn, so the stage is the turn's wall time)
  const toolMs: { tool: string; table: string | null; ms: number }[] = [];
  const runTool = async (name: string, input: unknown, sc: Scope) => {
    const t = Date.now();
    try { return await (profile?.ownTool?.(name, input) ?? runWarehouseTool(name, input, sc)); }
    finally { toolMs.push({ tool: name, table: typeof (input as Record<string, unknown> | null)?.table === "string" ? String((input as Record<string, unknown>).table) : null, ms: Date.now() - t }); }
  };
  const tiers = new Map<string, string>(); // session 28: each table's tier, from the tool results
  let calls = 0, attempts = 0, retried = false;

  for (;;) {
    const params = {
      model,
      max_tokens: spec.max_tokens,
      system,
      tools: profile?.tools ? [...TOOLS, ...profile.tools] : TOOLS,
      tool_choice: { type: calls < spec.max_tool_calls ? "auto" : "none" },
      output_config: { effort: profile ? profile.effort : spec.effort, format: { type: "json_schema", schema: profile ? profile.schema : spec.answer_schema } },
      cache_control: { type: "ephemeral" }, // session 30 (B2): the growing conversation is cached, as in ask.py
      messages,
    };
    // session 143: the call is read as a stream, so that the moment of its first text is known. The request is the same
    const tCall = Date.now();
    let firstText: number | null = null;
    const stream = client.messages.stream(params as unknown as Anthropic.MessageStreamParams);
    stream.on("text", () => { if (firstText === null) firstText = Date.now() - tCall; });
    const resp = (await stream.finalMessage()) as Anthropic.Message;
    const raw = { data: resp, request_id: stream.request_id };
    clock.add(resp.stop_reason === "tool_use" ? "planning" : "writing", "model", Date.now() - tCall, { model, first_text_ms: firstText, output_tokens: resp.usage.output_tokens, stop: resp.stop_reason });
    ledger.push(recordCall(model, resp, raw.request_id, profile ? "site_ask_ercot" : "site_ask", opts.questionId)); // session 30: every call into the cost ledger (site_api_calls)
    if (secondsFirst === null) secondsFirst = Math.round((Date.now() - t0) / 100) / 10;
    usage.input += resp.usage.input_tokens;
    usage.output += resp.usage.output_tokens;
    usage.cache_write += resp.usage.cache_creation_input_tokens ?? 0;
    usage.cache_read += resp.usage.cache_read_input_tokens ?? 0;
    usage.requests += 1;
    messages.push({ role: "assistant", content: resp.content });

    if (resp.stop_reason === "tool_use") {
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
      for (const [i, b] of blocks.entries()) {
        let out: Record<string, unknown>, isError: boolean;
        const got = outs[i];
        if (!got) {
          out = { error: `tool call limit (${spec.max_tool_calls}) reached; answer now` };
          isError = true;
        } else {
          ({ out, isError } = got);
          if (profile) {
            out = profile.tag(b.name, (b.input ?? {}) as Record<string, unknown>, out, slots[i]);
            records.push({ tool: b.name, input: (b.input ?? {}) as Record<string, unknown>, out, isError });
            sources.push(...profile.sourceTexts(b.name, (b.input ?? {}) as Record<string, unknown>, out));
          }
          sources.push(JSON.stringify(out), JSON.stringify(b.input));
          if (typeof out.table === "string") tablesRead.add(out.table);
          if (typeof out.table === "string" && typeof out.tier === "string") tiers.set(out.table, out.tier);
          for (const sub of ["a", "b"]) {
            const s = out[sub] as Record<string, unknown> | undefined;
            if (s && typeof s.table === "string") tablesRead.add(s.table);
            if (s && typeof s.table === "string" && typeof s.tier === "string") tiers.set(s.table, s.tier);
          }
          if (b.name === "list_tables")
            for (const t of (out.tables as { table: string; tier?: string | null }[]) ?? []) {
              tablesRead.add(t.table);
              if (t.tier) tiers.set(t.table, t.tier);
            }
        }
        results.push({ type: "tool_result", tool_use_id: b.id, content: JSON.stringify(out), is_error: isError });
      }
      messages.push({ role: "user", content: results });
      continue;
    }
    const base = { model, tool_calls: calls, retried, usage, cost_usd: cost(model, usage) };
    if (resp.stop_reason === "refusal") {
      return done({ answer: spec.refusal, citations: [], not_in_warehouse: false, status: "model_refusal" as const, ...base, ...(profile ? profile.finish("model_refusal", null, records) : {}) });
    }
    if (resp.stop_reason !== "end_turn") throw new Error(`stop_reason ${resp.stop_reason}`);
    const text = resp.content.map((b) => (b.type === "text" ? b.text : "")).join("");
    const draft = JSON.parse(text) as Draft;
    const tCheck = Date.now();
    const bad = unverified(draft.answer, sources);
    const uncited = draft.citations.map((c) => c.table).filter((t) => !tablesRead.has(t));
    // session 35, as ask.py: an empty or uncited answer is sent back; "not in the warehouse" needs no citation
    const noCite = !draft.not_in_warehouse && (!draft.citations.length || !draft.answer.trim());
    const more = profile ? profile.extraProblems(draft, records, given) : [];
    clock.add("writing", "check", Date.now() - tCheck);
    // session 137: what a draft is sent back for goes to the server's log, never to the reader
    if (bad.length || uncited.length || noCite || more.length)
      console.log(JSON.stringify({ erw_ask_check: { question_id: opts.questionId ?? null, attempt: attempts + 1, untraced_numbers: bad.slice(0, 12), uncited_tables: uncited.slice(0, 6), no_citation: noCite, problems: more.slice(0, 6) } }));
    if (!bad.length && !uncited.length && !noCite && !more.length) {
      // no em dashes in ERW copy (CLAUDE.md): model text is normalised, as in ask.py
      const answer = draft.answer.split(String.fromCharCode(0x2014)).join(" - ").replace(/ {2}- {2}/g, " - ");
      // session 28: each citation's tier is the warehouse's, whatever the model copied
      const citations = draft.citations.map((c) => ({ ...c, tier: tiers.get(c.table) ?? c.tier ?? "" }));
      const status = draft.not_in_warehouse ? ("not_in_warehouse" as const) : ("answered" as const);
      const tDraw = Date.now();
      const drawn = profile ? profile.finish(status, { ...draft, citations }, records) : {};
      clock.add("drawing", "series", Date.now() - tDraw);
      return done({ ...draft, answer, citations, status, ...base, ...drawn });
    }
    attempts += 1;
    if (attempts === 1) {
      retried = true;
      const problems: string[] = [];
      if (bad.length) problems.push(`numbers in no tool result: ${bad.join(", ")}`);
      if (uncited.length) problems.push(`cited tables no tool read: ${uncited.join(", ")}`);
      if (noCite) problems.push("an empty answer, or no citations");
      problems.push(...more);
      messages.push({ role: "user", content: (profile ? profile.retry : spec.retry).replace("{problems}", problems.join("; ")) });
      continue;
    }
    return done({ answer: spec.refusal, citations: [], not_in_warehouse: false, status: "refused_unverified" as const, ...base, retried: true,
      ...(profile ? profile.finish("refused_unverified", null, records) : {}) });
  }
}
