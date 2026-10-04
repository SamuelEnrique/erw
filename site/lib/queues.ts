// Session 95: the interconnection queue explorer (/queues, in review). The pure part: what the page chooses from its
// address and how it reads the site's own copy of interconnection_queue_summary (data/queues.json, written by
// warehouse/derived/queue_summary.py; docs/methods/interconnection_queue_summary.md). No arithmetic: every number is a
// row of the table.
export const TABLE = "interconnection_queue_summary";

export type YearRow = {
  requests_entered: number; mw_entered: number; requests_active: number; mw_active: number; requests_suspended: number; mw_suspended: number;
  requests_operating: number; mw_operating: number; requests_withdrawn: number; mw_withdrawn: number;
};
export type OnRow = { on_median_years_to_operation: number; on_requests_dated: number };
export type Whole = {
  total_requests: number; total_mw: number; requests_without_year: number; total_active_requests: number; total_active_mw: number;
  total_suspended_requests: number; total_suspended_mw: number; past_requests: number; past_mw: number;
  past_operating_share_pct?: number; past_withdrawn_share_pct?: number; past_open_share_pct?: number;
  past_mw_operating_share_pct?: number; past_mw_withdrawn_share_pct?: number; past_mw_open_share_pct?: number;
  operating_requests: number; years_to_operation_n: number; median_years_to_operation?: number;
};
export type View = { years: Record<string, YearRow>; on: Record<string, OnRow>; whole: Whole };
export type QueueFile = {
  table: string; built: string; vintage: string; input_retrieved: string; last_year: number; past: [number, number]; min_share: number; min_median: number;
  grids: string[]; techs: string[]; counts: Record<string, number>; views: Record<string, View>;
};

export const GRIDS = [
  { slug: "us", name: "All regions", place: "the United States" },
  { slug: "ercot", name: "ERCOT", place: "ERCOT" },
  { slug: "caiso", name: "CAISO", place: "CAISO" },
  { slug: "pjm", name: "PJM", place: "PJM" },
  { slug: "miso", name: "MISO", place: "MISO" },
  { slug: "spp", name: "SPP", place: "SPP" },
  { slug: "nyiso", name: "NYISO", place: "NYISO" },
  { slug: "isone", name: "ISO-NE", place: "ISO-NE" },
  { slug: "west", name: "West, outside the ISOs", place: "the West outside the ISOs" },
  { slug: "southeast", name: "Southeast, outside the ISOs", place: "the Southeast outside the ISOs" },
] as const;
export const TECHS = [
  { slug: "all", name: "All technologies", noun: "requests of every technology" },
  { slug: "solar", name: "Solar", noun: "solar requests" },
  { slug: "solar_battery", name: "Solar with storage", noun: "solar-with-storage requests" },
  { slug: "battery", name: "Storage (batteries alone)", noun: "standalone battery requests" },
  { slug: "wind", name: "Wind", noun: "onshore wind requests" },
  { slug: "offshore_wind", name: "Offshore wind", noun: "offshore wind requests" },
  { slug: "gas", name: "Natural gas", noun: "natural gas requests" },
  { slug: "other", name: "Everything else", noun: "requests of every other kind" },
] as const;
export type Grid = (typeof GRIDS)[number];
export type Tech = (typeof TECHS)[number];

export type Choice = { grid: Grid; tech: Tech };
/** The page's choices from its address: an unknown grid or technology is the first of its list. */
export function choices(q: Record<string, string | undefined>): Choice {
  return { grid: GRIDS.find((g) => g.slug === q.grid) ?? GRIDS[0], tech: TECHS.find((t) => t.slug === q.tech) ?? TECHS[0] };
}
export const href = (grid: string, tech: string) => `/queues?grid=${grid}&tech=${tech}`;
export const viewOf = (file: QueueFile, grid: string, tech: string): View | null => file.views[`${grid}|${tech}`] ?? null;

/** A count or MW as the site writes it: whole, with separators. */
export const whole = (v: number) => Math.round(v).toLocaleString("en-US");
/** A share or a count of years as the table holds it, to two decimals. */
export const two = (v: number) => v.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });

/** The years entered of a view, in order, from the first year with a request to the edition's last year: a year with
 *  no request of that kind has no row in the table, and is drawn as an empty year, not left out of the axis. */
export function yearsOf(view: View, lastYear: number): { year: number; row: YearRow | null }[] {
  const ys = Object.keys(view.years).map(Number);
  if (!ys.length) return [];
  const out: { year: number; row: YearRow | null }[] = [];
  for (let y = Math.min(...ys); y <= lastYear; y++) out.push({ year: y, row: view.years[String(y)] ?? null });
  return out;
}

/** The outcome of one year's requests as shares of the requests entered that year with a known status (the four
 *  counts); null for a year with none. The only division on the page, and only for the height of a bar. */
export function outcome(row: YearRow | null): { operating: number; withdrawn: number; open: number; n: number } | null {
  if (!row) return null;
  const n = row.requests_operating + row.requests_withdrawn + row.requests_active + row.requests_suspended;
  if (!n) return null;
  return { operating: row.requests_operating / n, withdrawn: row.requests_withdrawn / n, open: (row.requests_active + row.requests_suspended) / n, n };
}

/** The year in which the most active capacity entered. */
export function peakActive(view: View): { year: string; mw: number } | null {
  let best: { year: string; mw: number } | null = null;
  for (const [year, r] of Object.entries(view.years)) if (r.mw_active > 0 && (!best || r.mw_active > best.mw)) best = { year, mw: r.mw_active };
  return best;
}
