// Energy Research Warehouse (ERW) site, session 2243 (chain 156): the datacenter tracker's rollups by grid and by
// operator, read from datacenter_facilities as the live set serves it, so the page and scripts/check-values.mjs compute
// one number one way. A sum is of the MW the sources state, for the rows the page's other sums count (a named US state,
// not cancelled: lib/largeload.ts's rule, restated here so Node runs this file alone); the rows of the group that state
// no MW are counted beside it, never added as zero. Pure, no imports (tests/test_session2243_deals.py).

export type FacRow = { entity_id: string; capacity_mw: number | string | null; status: string | null; operator: string | null;
  extra: Record<string, string> | null };

export type Rollup = { value: string; facilities: number; counted: number; mw: number | null; withMw: number; without: number };

const STATES = new Set(("AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC " +
  "ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY").split(" "));
const num = (v: unknown): number | null => (v === null || v === undefined || v === "" || !Number.isFinite(Number(v)) ? null : Number(v));

/** A row the sums count: a named US state, a status other than withdrawn (cancelled). */
export const counted = (r: FacRow): boolean =>
  STATES.has((r.extra?.state ?? "").toUpperCase()) && !["withdrawn", "cancelled"].includes((r.status ?? "").toLowerCase());

/** The grid that serves most of a state (lib/deals2.ts STATE_GRID; warehouse/derived/datacenter_facilities.py the same). */
const STATE_GRID: Record<string, string> = {
  TX: "ERCOT", CA: "CAISO", NY: "NYISO", CT: "ISO-NE", ME: "ISO-NE", MA: "ISO-NE", NH: "ISO-NE", RI: "ISO-NE", VT: "ISO-NE",
  PA: "PJM", NJ: "PJM", MD: "PJM", DE: "PJM", VA: "PJM", WV: "PJM", OH: "PJM", DC: "PJM",
  MN: "MISO", IA: "MISO", WI: "MISO", MI: "MISO", LA: "MISO", OK: "SPP", KS: "SPP", NE: "SPP",
};
/** A facility's grid: as the table gives it (session 2243: named, its queue's ISO, else its state's), else, for a row
 * built before session 2243, its state's main grid. */
export const gridOf = (r: FacRow): string => r.extra?.grid || STATE_GRID[(r.extra?.state ?? "").toUpperCase()] || "";
export const gridBasisOf = (r: FacRow): string =>
  r.extra?.grid ? (r.extra?.grid_basis ?? "") : STATE_GRID[(r.extra?.state ?? "").toUpperCase()] ? "state" : "";
export const operatorOf = (r: FacRow): string => r.operator ?? "";

/** The rollup of one dimension, the largest MW first, "" (none) last. */
export function rollups(rows: FacRow[], dim: "grid" | "operator"): Rollup[] {
  const of = dim === "grid" ? gridOf : operatorOf;
  const by = new Map<string, FacRow[]>();
  for (const r of rows) { const v = of(r); by.set(v, [...(by.get(v) ?? []), r]); }
  const out = [...by.entries()].map(([value, rs]) => {
    const c = rs.filter(counted);
    const mws = c.flatMap((r) => { const m = num(r.capacity_mw); return m === null ? [] : [m]; });
    return { value, facilities: rs.length, counted: c.length, mw: mws.length ? mws.reduce((a, b) => a + b, 0) : null,
      withMw: mws.length, without: c.length - mws.length };
  });
  return out.sort((a, b) => (a.value === "" ? 1 : 0) - (b.value === "" ? 1 : 0) || (b.mw ?? -1) - (a.mw ?? -1) ||
    b.facilities - a.facilities || a.value.localeCompare(b.value));
}

/** The check key of a rollup's figure: datacenters|rollup_<facilities|mw|with_mw|without>|<grid|operator>|<value>. */
export const rollupKey = (stat: "facilities" | "mw" | "with_mw" | "without", dim: string, value: string) =>
  `datacenters|rollup_${stat}|${dim}|${value === "" ? "-" : value}`;
