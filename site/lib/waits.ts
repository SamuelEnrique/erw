// Energy Research Warehouse (ERW) site, session 188: what waits for the owner (/internal/waits). The file is written by
// scripts/build-waits.mjs before every build, from archive/sessions/SESSION_<N>_REPORT.md and the marker
// archive/sessions/LAST_ANSWERED; the rules of what counts as waiting are in that script. Server only: the reports'
// text is rendered on the server and no page for visitors imports this.
import "server-only";
import waits from "@/content/waits.json";

export type WaitItem = { section: string; line: number; md: string; kind: "section" | "inline" };
export type DecidedItem = { section: string; line: number; md: string };
export type WaitReport = {
  id: string; n: number; suffix: string; order: number; file: string; path: string; heading: string; title: string;
  date: string | null; date_words: string | null; url: string; waits: WaitItem[]; decided: DecidedItem[];
};
export type Waits = {
  built_at: string;
  repo: string;
  marker: { path: string; last: string | null; order: number | null; on: string | null; error: string | null };
  unread: string | null;
  reports: WaitReport[];
  decided_only: { id: string; title: string; url: string; date_words: string | null; count: number }[];
  counts: { after: number; listed: number; items: number };
  ledger?: Ledger;
};

// Session 414: the ledger of one run of sessions (LEDGER in scripts/build-waits.mjs): every item of a section for the
// owner listed once, placed under what it blocks, the three the state notes rank highest by value first.
export type LedgerLink = { session: string; line: number; path: string; url: string; report_url: string; section: string; md: string };
export type LedgerRank = { note: string; path: string; url: string; heading: string; rank: number; by_value: boolean; best: boolean };
export type LedgerGroup = {
  id: string; block: string; block_rule: number; block_said: string | null; md: string; session: string; path: string; section: string;
  sessions: string[]; asked: LedgerLink[]; restated: LedgerLink[]; reasons: string[]; ranks: LedgerRank[];
  first: { place: number; note: string; path: string; url: string; heading: string; rank: number } | null; line: number;
};
export type Ledger = {
  from: number; to: number; error: string | null;
  held?: string[]; held_words?: string; missing?: string; answered_to?: string | null;
  notes_read?: { file: string; path: string; url: string; date: string; lists: { heading: string; line: number; by_value: boolean; items: number }[] }[];
  ranked_by_value?: boolean;
  counts?: { reports: number; with_items: number; lines: number; items: number; merged: number; by_block: Record<string, number>; first: number; unranked: number };
  blocks?: { key: string; label: string; says: string }[];
  rules?: { block: { n: number; block: string; re: string }[]; subjects: { label: string; re: string }[]; named: { words: number; share: number };
    same: { words: number; share: number }; note: { named: number; words: number; share: number }; by_value: string; pointer: string };
  groups?: LedgerGroup[];
  quiet?: { session: string; url: string; lines: { line: number; md: string; why: string }[] }[];
  silent?: { session: string; url: string }[];
};

export const WAITS = waits as unknown as Waits;

/** A line of a report on GitHub, in the file's source view (the rendered view has no line numbers). */
export const lineUrl = (r: { url: string }, line: number) => `${r.url}?plain=1#L${line}`;
