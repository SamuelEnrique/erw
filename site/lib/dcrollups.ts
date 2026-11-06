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

// ---------------------------------------------------------------------------------------------------------------------
// Session 2244 (chain 156): the facilities of each grid against what the grid holds. By grid, the MW the counted
// facilities state, planned (announced, applied or permitted: the entities vocabulary's "planned"), under construction
// and operating, with the facilities that state none; the page sets them beside the grid's peak and capacity
// (grid_peak_vs_capacity, as site/data/siting/headroom.json carries it) and ERCOT's planning reserve margin.

export type GridLoad = { grid: string; facilities: number; withMw: number; without: number; planned: number | null;
  underConstruction: number | null; operating: number | null };

const STAGE_OF: Record<string, "planned" | "underConstruction" | "operating"> = {
  planned: "planned", under_construction: "underConstruction", operating: "operating",
};

export function gridLoads(rows: FacRow[]): GridLoad[] {
  const by = new Map<string, FacRow[]>();
  for (const r of rows.filter(counted)) { const g = gridOf(r); if (g) by.set(g, [...(by.get(g) ?? []), r]); }
  return [...by.entries()].map(([grid, rs]) => {
    const sums: Record<string, number[]> = { planned: [], underConstruction: [], operating: [] };
    let withMw = 0;
    for (const r of rs) {
      const m = num(r.capacity_mw);
      if (m === null) continue;
      withMw += 1;
      const s = STAGE_OF[(r.status ?? "").toLowerCase()];
      if (s) sums[s].push(m);
    }
    const sum = (xs: number[]) => (xs.length ? xs.reduce((a, b) => a + b, 0) : null);
    return { grid, facilities: rs.length, withMw, without: rs.length - withMw, planned: sum(sums.planned),
      underConstruction: sum(sums.underConstruction), operating: sum(sums.operating) };
  }).sort((a, b) => (b.planned ?? 0) + (b.underConstruction ?? 0) - (a.planned ?? 0) - (a.underConstruction ?? 0) || a.grid.localeCompare(b.grid));
}

/** The planned and under-construction MW a grid's facilities state, as a share of the grid's peak hour, to a tenth of a
 * percent; null where the facilities state none or the peak is not held. */
export function shareOfPeak(g: GridLoad, peakMw: number | null): number | null {
  const mw = (g.planned ?? 0) + (g.underConstruction ?? 0);
  if (!peakMw || (g.planned === null && g.underConstruction === null)) return null;
  return Math.round((1000 * mw) / peakMw) / 10;
}

/** The check key: dcgrid|<facilities|with_mw|without|planned|under_construction|operating|share_of_peak>|<grid>. */
export const gridKey = (stat: string, grid: string) => `dcgrid|${stat}|${grid}`;
