// Energy Research Warehouse (ERW) site, session 135: Thesis Builder (/thesis). The shape of a run and of its report,
// as the database functions of migration 024 hand them over (thesis_list, thesis_get). The report is what a reader of
// /thesis sees: it is written on the server (warehouse/thesis/) and only drawn here. Any list may be empty, and a
// report from a run that stopped early may lack a part: the page reads every field as possibly absent.
import type { PitchbookPayload } from "./pitchbook";

export type Text = { text: string; sources: string[] };
export type Missing = { missing: "not_disclosed" | "not_confirmed" | "not_held" | "pitchbook_pending"; note: string };
/** A string is shown as it is. */
export type Cell = string | Missing;
export type Source = { id: string; kind: "web" | "erw"; title: string; url: string; retrieved: string };

export type Trend = {
  n: number; title: string; fact: Text; table: { columns: string[]; rows: Cell[][] };
  chart: { kind: "bar" | "line" | "none"; title: string; category: number; values: number[]; unit: string };
  sources: string[];
};
export type LandscapeCompany = {
  name: string; website: string; description: string; founders: Cell; stage: Cell; raised: Cell; location: Cell; signal: string; trends: number[];
  reason: string; sources: string[]; confidence: number; confidence_note: string; sourcing: string[];
};
export type FunnelStage = { id: string; label: string; n: number };
export type FunnelCompany = { name: string; reached: string; stopped: string; score: number | null; sourcing: string[]; sources: string[] };
export type PipelineCompany = { name: string; founders: Cell; signal: string; access: Cell; tam: Cell; trends: number[]; confidence: number; sources: string[] };
export type Round = { date: Cell; company: string; kind: string; amount: Cell; investors: Cell; sources: string[] };
export type Player = { name: string; kind: string; ticker: string; metric: string; value: Cell; as_of: string; sources: string[] };
export type Risk = { risk: string; how: string; not_known: string; sources: string[] };
export type PolicyAction = { date: string; agency: string; title: string; why: string; url: string; read: string };

export type Report = {
  version: 1; niche: string; stage: string; geography: string; built: string;      // built: ISO UTC
  sources: Source[];
  scope: { definition: Text; value_chain: { stage: string; what: Text }[]; excluded: { niche: string; why: string }[]; definitions: { term: string; meaning: Text }[] };
  trends: Trend[];
  landscape: { fact: Text; rule: string; companies: LandscapeCompany[] };
  funnel: { stages: FunnelStage[]; companies: FunnelCompany[] };
  pipeline: { companies: PipelineCompany[] };
  capital: { fact: Text; rounds: Round[] };
  incumbents: { fact: Text; players: Player[] };
  risks: Risk[];
  policy: { fact: string; actions: PolicyAction[] };
};

export type RunStatus = "queued" | "running" | "done" | "failed";
export type PitchbookRequest = {
  format: string; run_id: string; companies: { name: string; website: string; lookups: string[] }[];
  discover: { keywords: string[]; hq: string }; paste_text: string;
};
export type Run = {
  run_id: string; niche: string; stage: string; geography: string; status: RunStatus; note: string;
  requested_at: string; started_at: string | null; finished_at: string | null; report: Report | null;
  pitchbook_request: PitchbookRequest | null; pitchbook_key: string | null; pitchbook: PitchbookPayload | null; pitchbook_received_at: string | null;
};
/** A row of thesis_list: a run without its report. */
export type RunRow = {
  run_id: string; niche: string; stage: string; geography: string; status: RunStatus; note: string;
  requested_at: string; started_at: string | null; finished_at: string | null; companies: number; pitchbook: "received" | "pending" | "none";
};
export type { PitchbookPayload, PbCompany, PbAdditional } from "./pitchbook";
