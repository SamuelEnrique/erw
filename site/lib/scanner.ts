// Energy Research Warehouse (ERW) site, session 181: the scanner's review list (public.scanner_drafts, migration 029).
// A draft is a flag the scanner raised (warehouse/analysis/findings/findings_scanner.py) and the card computed for it
// by code. The table is internal: the anon key reads nothing in it. The site's server reaches it through two functions
// that check the internal token (erw_private.site_token_ok), as /internal/usage reaches its counts.
import "server-only";
import { rpc } from "@/lib/supabase";
import type { Card } from "@/lib/findings";

export type DraftState = "draft" | "approved" | "dismissed" | "full_card_asked";
export type StateChange = { state: DraftState; from: DraftState; at: string };
export type Draft = {
  id: string; rule: string; table_name: string; series_key: string; flag_date: string; value: number | null; strength: number;
  scanner_version: string; state: DraftState; raised_at: string; state_at: string | null; state_history: StateChange[];
  request_id: string | null; card: Card;
};
export const STATES: DraftState[] = ["approved", "dismissed", "full_card_asked"];
export const STATE_WORDS: Record<DraftState, string> = {
  draft: "draft, not reviewed", approved: "approved", dismissed: "dismissed", full_card_asked: "full card asked",
};
export const ID = /^scan-[a-z]+-[0-9a-f]{12}$/;
// session 233: one file of a draft (the weekly hunt's CSV, do-file, Python mirror, LinkedIn pictures and caption)
export const FILE_NAME = /^[A-Za-z0-9_.-]{3,120}$/;
export type DraftFile = { id: string; name: string; state: DraftState; kind: "text" | "png" | null; content: string | null };

const token = () => process.env.INTERNAL_COSTS_TOKEN ?? "";

/** The drafts, newest and strongest first; with a state, only that state. Throws when the list cannot be read. */
export async function listDrafts(state?: DraftState): Promise<Draft[]> {
  const args: Record<string, string> = { p_token: token() };
  if (state) args.p_state = state;
  return (await rpc<Draft[] | null>("scanner_drafts_list", args)) ?? [];
}

/** One file of one draft (scanner_draft_file, migration 031); null when the draft or the name is not there. */
export async function draftFile(id: string, name: string): Promise<DraftFile | null> {
  return rpc<DraftFile | null>("scanner_draft_file", { p_token: token(), p_id: id, p_name: name });
}

export async function setDraftState(id: string, state: DraftState, requestId?: string): Promise<{ ok: boolean; reason?: string; state?: DraftState; at?: string; from?: DraftState }> {
  const args: Record<string, string> = { p_token: token(), p_id: id, p_state: state };
  if (requestId) args.p_request_id = requestId;
  return rpc("scanner_draft_set_state", args);
}
