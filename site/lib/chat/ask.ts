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
import { runTool } from "./tools";
import { recordCall } from "./ledger";

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
};

const PRICES = spec.prices as unknown as Record<string, [number, number]>;
const TOOLS = spec.tools as unknown as Anthropic.Tool[];

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

export async function ask(question: string, today = new Date().toISOString().slice(0, 10)): Promise<AskResult> {
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) throw new Error("ANTHROPIC_API_KEY is not set on the server");
  const client = new Anthropic({ apiKey: key });
  const model = await pickModel(client);
  const messages: Anthropic.MessageParam[] = [{ role: "user", content: `Today is ${today} (UTC).\n\nQuestion: ${question}` }];
  const usage = { input: 0, output: 0, cache_write: 0, cache_read: 0, requests: 0 };
  const sources: string[] = [question];
  const tablesRead = new Set<string>();
  const tiers = new Map<string, string>(); // session 28: each table's tier, from the tool results
  let calls = 0, attempts = 0, retried = false;

  for (;;) {
    const params = {
      model,
      max_tokens: spec.max_tokens,
      system: [{ type: "text", text: spec.system, cache_control: { type: "ephemeral" } }],
      tools: TOOLS,
      tool_choice: { type: calls < spec.max_tool_calls ? "auto" : "none" },
      output_config: { effort: spec.effort, format: { type: "json_schema", schema: spec.answer_schema } },
      cache_control: { type: "ephemeral" }, // session 30 (B2): the growing conversation is cached, as in ask.py
      messages,
    };
    const raw = await client.messages
      .create(params as unknown as Anthropic.MessageCreateParamsNonStreaming)
      .withResponse();
    const resp = raw.data as Anthropic.Message;
    await recordCall(model, resp, raw.request_id); // session 30: every call into the cost ledger (site_api_calls)
    usage.input += resp.usage.input_tokens;
    usage.output += resp.usage.output_tokens;
    usage.cache_write += resp.usage.cache_creation_input_tokens ?? 0;
    usage.cache_read += resp.usage.cache_read_input_tokens ?? 0;
    usage.requests += 1;
    messages.push({ role: "assistant", content: resp.content });

    if (resp.stop_reason === "tool_use") {
      const results: Anthropic.ToolResultBlockParam[] = [];
      for (const b of resp.content) {
        if (b.type !== "tool_use") continue;
        let out: Record<string, unknown>, isError: boolean;
        if (calls >= spec.max_tool_calls) {
          out = { error: `tool call limit (${spec.max_tool_calls}) reached; answer now` };
          isError = true;
        } else {
          ({ out, isError } = await runTool(b.name, b.input));
          calls += 1;
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
      return { answer: spec.refusal, citations: [], not_in_warehouse: false, status: "model_refusal", ...base };
    }
    if (resp.stop_reason !== "end_turn") throw new Error(`stop_reason ${resp.stop_reason}`);
    const text = resp.content.map((b) => (b.type === "text" ? b.text : "")).join("");
    const draft = JSON.parse(text) as { answer: string; citations: Citation[]; not_in_warehouse: boolean };
    const bad = unverified(draft.answer, sources);
    const uncited = draft.citations.map((c) => c.table).filter((t) => !tablesRead.has(t));
    const noCite = numbers(draft.answer).length > 0 && !draft.citations.length && !draft.not_in_warehouse;
    if (!bad.length && !uncited.length && !noCite) {
      // no em dashes in ERW copy (CLAUDE.md): model text is normalised, as in ask.py
      const answer = draft.answer.split(String.fromCharCode(0x2014)).join(" - ").replace(/ {2}- {2}/g, " - ");
      // session 28: each citation's tier is the warehouse's, whatever the model copied
      const citations = draft.citations.map((c) => ({ ...c, tier: tiers.get(c.table) ?? c.tier ?? "" }));
      return { ...draft, answer, citations, status: draft.not_in_warehouse ? "not_in_warehouse" : "answered", ...base };
    }
    attempts += 1;
    if (attempts === 1) {
      retried = true;
      const problems: string[] = [];
      if (bad.length) problems.push(`numbers in no tool result: ${bad.join(", ")}`);
      if (uncited.length) problems.push(`cited tables no tool read: ${uncited.join(", ")}`);
      if (noCite) problems.push("numbers but no citations");
      messages.push({ role: "user", content: spec.retry.replace("{problems}", problems.join("; ")) });
      continue;
    }
    return { answer: spec.refusal, citations: [], not_in_warehouse: false, status: "refused_unverified", ...base, retried: true };
  }
}
