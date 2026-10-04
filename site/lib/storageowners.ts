// Energy Research Warehouse (ERW) site, session 87: who owns the batteries (/storage/owners, in review). The page's
// model. Every number is a row of storage_owners_monthly (warehouse/derived/storage_owners.py; EIA-860M, derived),
// carried to the page by data/storage_owners.json: the table is held out of the live set while the live site is
// frozen, so the page reads the committed snapshot and not Supabase. This file picks and sorts the snapshot's values
// and does no arithmetic on them. No imports: Node runs this file as it is.

export const TABLE = "storage_owners_monthly";

export type Metrics = Partial<Record<
  "operating_mw" | "operating_mwh" | "operating_hours" | "operating_units" | "operating_rank" | "operating_share_pct" | "planned_mw" | "planned_units" |
  "owners_operating" | "owners_planned" | "top5_share_pct" | "top10_share_pct", number>>;
export type Snapshot = {
  table: string; month: string; built: string; source: string; source_urls: string[];
  counts: { operating_units: number; planned_units: number; owners_operating: number; owners_planned: number; owners_both: number; no_energy_units: number; vintage: string };
  grids: Record<string, Metrics & { entity: string }>;
  owners: Record<string, { name: string; grids: Record<string, Metrics> }>;
};

/** The grids a reader can pick, in the order of the storage build-out page. */
export const GRIDS = [
  { slug: "us", name: "The United States", label: "United States" },
  { slug: "caiso", name: "CAISO", label: "CAISO" },
  { slug: "ercot", name: "ERCOT", label: "ERCOT" },
  { slug: "pjm", name: "PJM", label: "PJM" },
  { slug: "miso", name: "MISO", label: "MISO" },
  { slug: "spp", name: "SPP", label: "SPP" },
  { slug: "nyiso", name: "NYISO", label: "NYISO" },
  { slug: "isone", name: "ISO-NE", label: "ISO-NE" },
  { slug: "outside_isos", name: "The rest of the country, outside the seven grids", label: "Outside the seven" },
] as const;
export type Grid = (typeof GRIDS)[number];

export const SHOWN = 25;  // the owners listed in each table

export function choices(q: Record<string, string | undefined>): { grid: Grid } {
  return { grid: GRIDS.find((g) => g.slug === q.grid) ?? GRIDS[0] };
}

export type OwnerRow = { entity: string; name: string } & Metrics;

/** The table's check key of one value: the row it is. */
export const rowKey = (entity: string, grid: string, metric: string, month: string) => `series|${TABLE}|${entity}|${grid}_${metric}|${month}-01T00:00:00Z`;

export function view(s: Snapshot, grid: Grid) {
  const g = s.grids[grid.slug];
  const rows: OwnerRow[] = [];
  for (const [entity, o] of Object.entries(s.owners)) {
    const m = o.grids[grid.slug];
    if (m) rows.push({ entity, name: o.name, ...m });
  }
  // operating: by the table's own rank (largest first; the builder breaks ties by name, so a rank is given once)
  const operating = rows.filter((r) => r.operating_rank !== undefined).sort((a, b) => a.operating_rank! - b.operating_rank!);
  // planned: by planned MW, then name
  const planned = rows.filter((r) => r.planned_mw !== undefined).sort((a, b) => b.planned_mw! - a.planned_mw! || a.name.localeCompare(b.name));
  return { grid: g, operating, planned, month: s.month };
}

/** A number as the page prints it. */
export function shown(v: number | undefined, digits = 0): string {
  return v === undefined ? "not held" : v.toLocaleString("en-US", { minimumFractionDigits: digits, maximumFractionDigits: digits });
}
export function monthName(m: string): string {
  return new Date(`${m}-15T12:00:00Z`).toLocaleString("en-US", { month: "long", year: "numeric", timeZone: "UTC" });
}
