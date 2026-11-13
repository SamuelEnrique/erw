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

// ---------------------------------------------------------------------------------------------------------------------
// Session 2245 (chain 156): the timeline, from first reported to energized. Only a facility whose sources state both
// is on it: the first story's date (first_story_at) and the year it is to be energized or come online, as stated
// (energized_year, session 2236). Its wait is the difference of the two years, in whole years: a year is all the
// energized date states, so nothing finer is claimed, and a wait is never estimated from one date. The median of a
// grid or of a year of first report needs three facilities with both (the deal tracker's rule).

export type TimelineRow = { id: string; operator: string; grid: string; reported: string; energized: number; wait: number };
export type TimelineCell = { value: string; count: number; median: number | null };

export function timeline(rows: FacRow[]): TimelineRow[] {
  const out: TimelineRow[] = [];
  for (const r of rows) {
    // session 1855 (datacenter faults row 9): a row built before chain 156 wrote the year as planned_year
    const rep = r.extra?.first_story_at ?? "", y = Number(r.extra?.energized_year ?? r.extra?.planned_year ?? "");
    if (!/^\d{4}-\d{2}/.test(rep) || !Number.isInteger(y) || y < 2000) continue;
    out.push({ id: r.entity_id, operator: r.operator ?? "", grid: gridOf(r), reported: rep.slice(0, 10), energized: y, wait: y - Number(rep.slice(0, 4)) });
  }
  return out.sort((a, b) => a.reported.localeCompare(b.reported) || a.id.localeCompare(b.id));
}

const median3 = (xs: number[]): number | null => {
  if (xs.length < 3) return null;
  const s = [...xs].sort((a, b) => a - b), h = Math.floor(s.length / 2);
  return s.length % 2 ? s[h] : (s[h - 1] + s[h]) / 2;
};

export function timelineCells(rows: TimelineRow[], dim: "grid" | "year"): TimelineCell[] {
  const by = new Map<string, number[]>();
  for (const r of rows) { const v = dim === "grid" ? r.grid : r.reported.slice(0, 4); by.set(v, [...(by.get(v) ?? []), r.wait]); }
  return [...by.entries()].map(([value, ws]) => ({ value, count: ws.length, median: median3(ws) }))
    .sort((a, b) => (dim === "year" ? a.value.localeCompare(b.value) : b.count - a.count || a.value.localeCompare(b.value)));
}

/** The check key: dctime|<count|median>|<grid|year>|<value> ("-" for none). */
export const timeKey = (stat: "count" | "median", dim: string, value: string) => `dctime|${stat}|${dim}|${value === "" ? "-" : value}`;

// ---------------------------------------------------------------------------------------------------------------------
// Session 2246 (chain 156): the tracker's three charts. 1. The MW the counted facilities state that are planned or
// under construction, by the quarter they were first reported, stacked by grid (the four grids with the most, the
// rest together); 2. the operators with the most MW stated; 3. the share of the counted facilities by the kind of
// power their sources state (power_kind, session 2236), with the facilities that state none as their own bar. Every
// figure has its key, dcchart|<chart>|<x>|<series>, which scripts/check_datacenters.py recomputes with its own Python.

const quarterOfDate = (d: string): string => `${d.slice(0, 4)}-Q${Math.floor((Number(d.slice(5, 7)) - 1) / 3) + 1}`;
const ahead = (r: FacRow) => ["planned", "under_construction"].includes((r.status ?? "").toLowerCase());

export function chartGrids(rows: FacRow[]): string[] {
  const mw = new Map<string, number>();
  for (const r of rows.filter((x) => counted(x) && ahead(x))) {
    const m = num(r.capacity_mw), g = gridOf(r);
    if (m !== null && g) mw.set(g, (mw.get(g) ?? 0) + m);
  }
  return [...mw.entries()].sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0])).slice(0, 4).map(([g]) => g);
}

export function plannedByQuarter(rows: FacRow[]): { quarter: string; parts: { grid: string; mw: number }[]; without: number }[] {
  const top = chartGrids(rows);
  const c = rows.filter((x) => counted(x) && ahead(x) && /^\d{4}-\d{2}/.test(x.extra?.first_story_at ?? ""));
  const qs = [...new Set(c.map((r) => quarterOfDate(r.extra!.first_story_at!)))].sort();
  return qs.map((q) => {
    const inQ = c.filter((r) => quarterOfDate(r.extra!.first_story_at!) === q);
    const parts = [...top, "other"].map((g) => ({ grid: g, mw: inQ.filter((r) => (top.includes(gridOf(r)) ? gridOf(r) : "other") === g)
      .reduce((a, r) => a + (num(r.capacity_mw) ?? 0), 0) }));
    return { quarter: q, parts, without: inQ.filter((r) => num(r.capacity_mw) === null).length };
  });
}

export function operatorMw(rows: FacRow[], n = 10): { operator: string; mw: number; withMw: number; facilities: number }[] {
  return rollups(rows, "operator").filter((r) => r.value && r.mw !== null).slice(0, n)
    .map((r) => ({ operator: r.value, mw: r.mw!, withMw: r.withMw, facilities: r.counted }));
}

export function powerShares(rows: FacRow[]): { kind: string; facilities: number; pct: number }[] {
  const c = rows.filter(counted);
  const by = new Map<string, number>();
  for (const r of c) { const k = r.extra?.power_kind || "none"; by.set(k, (by.get(k) ?? 0) + 1); }
  return [...by.entries()].map(([kind, n]) => ({ kind, facilities: n, pct: c.length ? Math.round((1000 * n) / c.length) / 10 : 0 }))
    .sort((a, b) => (a.kind === "none" ? 1 : 0) - (b.kind === "none" ? 1 : 0) || b.facilities - a.facilities || a.kind.localeCompare(b.kind));
}

export function dcFigures(rows: FacRow[]): Record<string, number> {
  const out: Record<string, number> = {};
  for (const s of plannedByQuarter(rows)) {
    for (const p of s.parts) out[`dcchart|planned|${s.quarter}|${p.grid}`] = p.mw;
    out[`dcchart|planned|${s.quarter}|without`] = s.without;
  }
  for (const o of operatorMw(rows)) out[`dcchart|operator|${o.operator}|mw`] = o.mw;
  for (const p of powerShares(rows)) { out[`dcchart|power|${p.kind}|facilities`] = p.facilities; out[`dcchart|power|${p.kind}|pct`] = p.pct; }
  return out;
}
