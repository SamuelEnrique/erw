// Energy Research Warehouse (ERW) site, session 169: Thesis Builder (/thesis), the one small model call of the gate
// on the niche (lib/thesis/niche.ts, judge). It is made only for an input the curated table does not hold, by the
// route alone (the form holds no key), and it answers {verdict, reason, suggestions}. Anything that goes wrong here
// is an error to the caller, and the caller's rules then decide: nothing waits on this call and no run is lost to it.
//
// What keeps its spend small: one call of at most GATE_MAX_TOKENS output tokens on the small model, no retry, eight
// seconds at most, at most GATE_CALLS_PER_HOUR in an hour on a server instance (the rules decide beyond that), and
// the route answers only a browser in the internal view. THESIS_GATE_MODEL=0 switches the call off: the rules decide.
// Each call is one row of the site's cost ledger (site_api_calls, step site_thesis_gate; migration 026 admits the step).
import "server-only";
import Anthropic from "@anthropic-ai/sdk";
import { recordCall } from "@/lib/chat/ledger";
import { GATE_MAX_TOKENS, GATE_MODEL, GATE_SCHEMA, GATE_SYSTEM, gatePrompt, type AskModel } from "./niche";

export const GATE_CALLS_PER_HOUR = 40;
const made: number[] = [];

/** May a call be made now? Counts it when it may. */
function admitted(now: number): boolean {
  while (made.length && now - made[0] > 3_600_000) made.shift();
  if (made.length >= GATE_CALLS_PER_HOUR) return false;
  made.push(now);
  return true;
}

export type GateUsage = { model: string; input_tokens: number; output_tokens: number; request_id: string | null };
/** The call. `record` writes the cost ledger's row (the site's by default); `seen` is told what the call used. */
export function gateModel(opts: { record?: (model: string, resp: Anthropic.Message, requestId: string | null) => Promise<void>; seen?: (u: GateUsage) => void } = {}): AskModel | null {
  if (process.env.THESIS_GATE_MODEL === "0") return null;
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) return null;
  return async (input: string) => {
    if (!admitted(Date.now())) throw new Error("the gate's calls of this hour are used");
    const client = new Anthropic({ apiKey: key, maxRetries: 0, timeout: 8000 });
    const params = {
      model: GATE_MODEL, max_tokens: GATE_MAX_TOKENS, system: GATE_SYSTEM,
      messages: [{ role: "user", content: gatePrompt(input) }],
      output_config: { format: { type: "json_schema", schema: GATE_SCHEMA } },
    };
    const { data: resp, request_id } = await client.messages.create(params as unknown as Anthropic.MessageCreateParamsNonStreaming).withResponse();
    opts.seen?.({ model: resp.model || GATE_MODEL, input_tokens: resp.usage.input_tokens, output_tokens: resp.usage.output_tokens, request_id: request_id ?? null });
    await (opts.record ?? ((m, r, id) => recordCall(m, r, id, "site_thesis_gate")))(GATE_MODEL, resp, request_id ?? null);
    if (resp.stop_reason !== "end_turn") throw new Error(`the gate's call stopped with ${resp.stop_reason}`);
    return JSON.parse(resp.content.map((b) => (b.type === "text" ? b.text : "")).join(""));
  };
}
