// Energy Research Warehouse (ERW) site: the site's side of the API cost ledger (session 30, Part B1).
//
// warehouse/llm.py records every model call of the warehouse's scripts in api_cost_ledger. The site
// cannot write that table (it holds only the anon key), so each /ask call is recorded here instead, as
// one row of site_api_calls, which the anon key may insert into and never read (migration 010). The
// internal costs page (/internal/costs) reads both through internal_costs(token).
// Prices: spec.json's model_prices, exported from warehouse/config/model_prices.yaml by ask.py.
import "server-only";
import type Anthropic from "@anthropic-ai/sdk";
import spec from "./spec.json";
import { insertRow } from "@/lib/supabase";

type Price = { input: number; output: number; cache_write_5m: number; cache_write_1h: number; cache_read: number };
const MODEL_PRICES = (spec as unknown as { model_prices?: Record<string, Price> }).model_prices ?? {};

/** USD of one call's usage at the configured prices, or null for a model with no price. */
export function callUsd(model: string, u: Anthropic.Usage): number | null {
  const p = MODEL_PRICES[model];
  if (!p) return null;
  const write = u.cache_creation_input_tokens ?? 0;
  const read = u.cache_read_input_tokens ?? 0;
  return (u.input_tokens * p.input + u.output_tokens * p.output + read * p.cache_read + write * p.cache_write_5m) / 1e6;
}

/** One /ask call, into site_api_calls. A failed write is logged and never fails the answer. */
export async function recordCall(model: string, resp: Anthropic.Message, requestId?: string | null): Promise<void> {
  const u = resp.usage;
  const cost = callUsd(model, u);
  try {
    await insertRow("site_api_calls", {
      step: "site_ask",
      model,
      input_tokens: u.input_tokens,
      cached_input_tokens: u.cache_read_input_tokens ?? 0,
      cache_write_tokens: u.cache_creation_input_tokens ?? 0,
      output_tokens: u.output_tokens,
      usd: cost === null ? null : Number(cost.toFixed(6)),
      request_id: requestId ?? null,
    });
  } catch (e) {
    console.error(`[erw] cost ledger: ${(e as Error).message}`);
  }
}
