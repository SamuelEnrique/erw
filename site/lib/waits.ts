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
};

export const WAITS = waits as unknown as Waits;

/** A line of a report on GitHub, in the file's source view (the rendered view has no line numbers). */
export const lineUrl = (r: { url: string }, line: number) => `${r.url}?plain=1#L${line}`;
