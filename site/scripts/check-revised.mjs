// Energy Research Warehouse (ERW) site, session 1171 (chain 078): a revised EIA-930 hour, told apart from a wrong figure.
// The Grid pack's blind spot 9 (docs/reviews/packs/grid.md, section 6): EIA revises its preliminary hourly data, and on
// 13 October 2026 one revised hour moved two of MISO's figures between a page's read and the checker's, which failed the
// run as a value difference. The rule, written in docs/methods/grid_network.md ("Revisions, said and checked"):
//
//   A figure whose key is series|eia930_<table>|<entity>|<variable>|<hour> and whose value on the page differs from
//   Supabase's is a revision only when (1) the page's text is its own value written as the page writes it, (2) the row
//   is hourly (freq PT1H) and (3) the row's loaded_at, the load run that last wrote it (warehouse/supabase/load.py
//   writes only the rows that are new or changed), is later than the page's drawing time, which every Grid tab carries
//   as data-eia930-drawn (components/grid/Preliminary.tsx). A revision passes only for a table the method note names on
//   its line "Revised hours tolerated by check-values: ..."; any other difference fails as before.
//
// A row written before the page was drawn is the row the page read, so a difference there is an error, never a revision.
// No other key kind (a sum, a maximum, a calc, a snapshot's net|) is judged here: each still fails on a difference.
// This file holds the rule; check-values reads the row and the note. Its test: scripts/test-check-revised.mjs.

const KEY = /^series\|(eia930_[a-z0-9_]+)\|([^|]+)\|([^|]+)\|(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?(?:Z|[+-]\d{2}:\d{2}))$/;

/** The parts of a key this rule may judge ({ table, entity, variable, ts }), else null. */
export function revisedKey(check) {
  const m = KEY.exec(check);
  return m ? { table: m[1], entity: m[2], variable: m[3], ts: m[4] } : null;
}

/** The page's drawing time: the latest data-eia930-drawn the page carries (ISO, UTC), else null. */
export function drawnOf(html) {
  let best = null;
  for (const m of html.matchAll(/data-eia930-drawn="([^"]+)"/g)) {
    const t = Date.parse(m[1]);
    if (Number.isFinite(t) && (best === null || t > Date.parse(best))) best = new Date(t).toISOString();
  }
  return best;
}

/** The tables the method note tolerates a revised hour for, from its line "Revised hours tolerated by check-values:
 *  `a`, `b`." (a Set; empty when the note or the line is missing, so nothing is tolerated). */
export function toleratedOf(note) {
  const m = /^Revised hours tolerated by check-values: (.+?)\.?\s*$/m.exec(note ?? "");
  if (!m) return new Set();
  return new Set(m[1].split(",").map((x) => x.trim().replace(/^`|`$/g, "")).filter((x) => /^eia930_[a-z0-9_]+$/.test(x)));
}

/**
 * Judge a figure that already failed on its value. `row` is { loaded_at, freq } as Supabase holds it (or null), `drawn`
 * the page's drawing time, `textHolds` whether the page's text is its own value as written.
 * Returns null when the rule does not apply (the failure stands as it is); { revised: false, why } when the row was
 * written before the page was drawn (the failure stands, with that said); { revised: true, pass, table, loaded, drawn }
 * when the row was written after it: pass only for a table the note tolerates.
 */
export function judgeRevised({ check, row, drawn, textHolds, tolerated }) {
  const k = revisedKey(check);
  if (!k || !textHolds || !row || !drawn || row.freq !== "PT1H") return null;
  const loaded = Date.parse(row.loaded_at), at = Date.parse(drawn);
  if (!Number.isFinite(loaded) || !Number.isFinite(at)) return null;
  const L = new Date(loaded).toISOString(), D = new Date(at).toISOString();
  if (loaded <= at) return { revised: false, table: k.table, loaded: L, drawn: D, why: `the row was last written ${L}, before the page was drawn ${D}: not a revision` };
  return { revised: true, pass: tolerated.has(k.table), table: k.table, loaded: L, drawn: D };
}

/** The line check-values prints for a figure judged a revision. */
export function revisedLine({ page, check, text, raw, value, j }) {
  const head = `${j.pass ? "revised" : "FAIL"} | ${page} | ${check} | page shows "${text}" | page read ${raw}, drawn ${j.drawn} | Supabase ${value}, the row written ${j.loaded}, after the page was drawn`;
  return j.pass
    ? `${head}: a revision of EIA-930's preliminary hour, tolerated for ${j.table} by docs/methods/grid_network.md`
    : `${head}: a revision, but docs/methods/grid_network.md does not tolerate one for ${j.table}`;
}
