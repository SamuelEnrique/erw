// Session 265b (the owner's ruling of 14 October 2026, landed by session 272: large_load_public is public as facts with
// a link and no quoted text): what "How soon?" on "What a datacenter pays" (/cost-of-power) says of the large-load
// statements on a public document for the load's grid. Pure arithmetic, no React, no import: the page computes it from
// lib/largeloadpublic.ts's read, and scripts/check-values.mjs recomputes every keyed figure from its own read of the
// same table (check keys dcll|<grid>|<stat>). Nothing is summed across rows: the entities count differently, a document
// often states a total and its parts, and an operator's figures hold its utilities' (docs/methods/large_load_public.md).

/** A row as this file reads it: the columns of large_load_public it uses (the page's read holds more). */
export type Statement = {
  event_date: string; parties: string; mw: number | null; source_url: string; row_kind: string;
  duration_as_stated: string | null; wait_basis: string | null; stage_class: string | null; document_title: string | null; page: string | null;
};
export type Stated = {
  statements: number; entities: number; documents: number; waits: number; mws: number;
  newest: string | null;
  /** the newest row stating a wait, and the newest stating megawatts (ties: the larger figure first, then the entity) */
  wait: Statement | null; mw: Statement | null;
};

const day = (r: Statement) => (r.event_date ?? "").slice(0, 10);
const newestFirst = (a: Statement, b: Statement) => day(b).localeCompare(day(a)) || (Number(b.mw ?? 0) - Number(a.mw ?? 0)) || (a.parties ?? "").localeCompare(b.parties ?? "") || (a.source_url ?? "").localeCompare(b.source_url ?? "");

/** The counts and the two newest facts of a grid's rows. */
export function statedOf(rows: Statement[]): Stated {
  const sorted = [...rows].sort(newestFirst);
  const waits = sorted.filter((r) => r.row_kind === "wait" && (r.duration_as_stated ?? "").trim() !== "");
  const mws = sorted.filter((r) => r.row_kind === "mw" && r.mw !== null && Number.isFinite(Number(r.mw)));
  return {
    statements: rows.length,
    entities: new Set(rows.map((r) => r.parties)).size,
    documents: new Set(rows.map((r) => r.source_url)).size,
    waits: waits.length, mws: mws.length,
    newest: sorted.length ? day(sorted[0]) : null,
    wait: waits[0] ?? null, mw: mws[0] ?? null,
  };
}

/** The first number a wait as written holds ("60 days": 60; "18 to 24 months": 18): what its check key compares. */
export function leadingNumber(s: string | null | undefined): number | null {
  const m = (s ?? "").replace(/,/g, "").match(/\d+(\.\d+)?/);
  return m ? Number(m[0]) : null;
}

/** One figure by its name, for the check key dcll|<grid>|<stat>. */
export function statedStat(s: Stated, stat: string): number | undefined {
  switch (stat) {
    case "statements": return s.statements;
    case "entities": return s.entities;
    case "documents": return s.documents;
    case "waits": return s.waits;
    case "mws": return s.mws;
    case "mw:newest": return s.mw ? Number(s.mw.mw) : undefined;
    case "wait:newest": return leadingNumber(s.wait?.duration_as_stated) ?? undefined;
    default: return undefined;
  }
}

/** The stage as the ERW classes it, in words ("2 study or engineering": "study or engineering"); none when not classed. */
export const stageWords = (c: string | null | undefined) => {
  const w = (c ?? "").replace(/^\d+\s*/, "").trim();
  return w && w !== "none" && w !== "not classed" ? w : null;
};
