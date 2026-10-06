// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis), the server's side. Who may read a run,
// and the four database functions of migration 024, each through the site's one reader of Supabase (lib/supabase.ts,
// the public key: the functions check the internal token or the run's one-time key themselves).
//
// A run and its report are internal: the page, and the route that queues a run, answer only a browser in the internal
// view (the cookie /internal/unlock sets, a digest of INTERNAL_COSTS_TOKEN, as the proxy checks it). The release gate
// is a curtain for visitors and nothing confidential may rely on it (docs/release-gate.md), so the page checks the
// cookie itself as well, and /api/* is not behind the gate at all.
import "server-only";
import { digest } from "@/lib/release";
import { rpc } from "@/lib/supabase";
import type { PitchbookPayload, Run, RunRow } from "./types";

/** Nothing of a run is cached, by a browser or anything between. */
export const NO_STORE = { "Cache-Control": "no-store", "X-Robots-Tag": "noindex" } as const;

/** Is this the internal view's cookie? Compared in constant time. */
export async function internalOk(have: string | undefined): Promise<boolean> {
  const token = process.env.INTERNAL_COSTS_TOKEN;
  if (!token || !have) return false;
  const want = await digest(token);
  if (have.length !== want.length) return false;
  let d = 0;
  for (let i = 0; i < want.length; i += 1) d |= have.charCodeAt(i) ^ want.charCodeAt(i);
  return d === 0;
}

const token = () => process.env.INTERNAL_COSTS_TOKEN ?? "";

export type Submitted = { ok: true; run_id: string; dispatched?: boolean } | { ok: false; reason: string; runs_today?: number };
export const submitRun = (niche: string, stage: string, geography: string) =>
  rpc<Submitted>("thesis_submit", { p_token: token(), p_niche: niche, p_stage: stage, p_geography: geography });
export const listRuns = () => rpc<RunRow[] | null>("thesis_list", { p_token: token() });
export const getRun = (runId: string) => rpc<Run | null>("thesis_get", { p_token: token(), p_run_id: runId });
/** The PitchBook answer, stored once under the run's one-time key. The payload goes as JSON, not as text: rpc() sends
 * its arguments through JSON.stringify, and its type names strings only because every earlier function took strings. */
export const acceptPitchbook = (runId: string, key: string, payload: PitchbookPayload) =>
  rpc<{ ok: boolean; reason?: string; companies?: number }>("thesis_pitchbook_accept", { p_run_id: runId, p_key: key, p_payload: payload } as unknown as Record<string, string>);
