// Energy Research Warehouse (ERW) site, session 471: the short reading at the head of /data/licenses, from the two
// files the licensing record writes (scripts/licenses.py): site/data/license_status.json (the holds of 21 October, as
// lib/license.ts reads them) and the publishers' verdicts (warehouse/metadata/license_verdicts.csv, bundled by
// scripts/build-content.mjs). Nothing here reads a publisher or the database. scripts/check-values.mjs recomputes each
// figure from warehouse/metadata/license_status.csv and license_verdicts.csv (the keys lic|...).

export type StatusFile = { from: string; tables: Record<string, { status: string; from: string; publishers: string[] }> };
export type Verdict = { key: string; verdict: string; if_commercial: string; note: string };

export const MAY_BE_PUBLIC = "may be public";
export const NEEDED = "license needed";

/** The tables held ("license needed") and, for each deciding publisher, how many of them it decides; most first, then
 *  by name. A table decided by several publishers counts once under each. */
export function holds(status: StatusFile): { count: number; from: string; byPublisher: { publisher: string; tables: number }[] } {
  const held = Object.values(status.tables).filter((r) => r.status === NEEDED);
  const n = new Map<string, number>();
  for (const r of held) for (const p of r.publishers) n.set(p, (n.get(p) ?? 0) + 1);
  const byPublisher = [...n.entries()].map(([publisher, tables]) => ({ publisher, tables }))
    .sort((a, b) => b.tables - a.tables || a.publisher.localeCompare(b.publisher));
  return { count: held.length, from: status.from, byPublisher };
}

/** The publishers whose own sentence allows the ERW as it is today: those that allow it whatever the ERW does, and those
 *  that would need written permission if the ERW sold anything. In the record's order. */
export function permissive(verdicts: Verdict[]): { both: Verdict[]; todayOnly: Verdict[] } {
  const today = verdicts.filter((v) => v.verdict === MAY_BE_PUBLIC);
  return { both: today.filter((v) => v.if_commercial === MAY_BE_PUBLIC), todayOnly: today.filter((v) => v.if_commercial !== MAY_BE_PUBLIC) };
}

/** The four permission letters session 378 drafted (docs/reviews/licenses/), in the order of the hold's grids first.
 *  None was sent when this page was written; a permission, once granted, is recorded in license_status.csv's columns
 *  permission and permission_ref, and the hold of the tables it covers ends. */
export const LETTERS: { publisher: string; asks: string; file: string }[] = [
  { publisher: "NYISO", asks: "permission to republish NYISO's public market data in a research warehouse", file: "docs/reviews/licenses/nyiso-permission-letter.md" },
  { publisher: "MISO", asks: "permission to read MISO's public market data by script and to republish it (MISO is paused since 4 October 2026: nothing is asked of its servers)", file: "docs/reviews/licenses/miso-permission-letter.md" },
  { publisher: "PJM", asks: "whether a non-member research project may republish PJM's capacity auction results", file: "docs/reviews/licenses/pjm-permission-letter.md" },
  { publisher: "SPP", asks: "written authorization should the ERW ever be a commercial publication (SPP allows the ERW as it is today)", file: "docs/reviews/licenses/spp-permission-letter.md" },
];
