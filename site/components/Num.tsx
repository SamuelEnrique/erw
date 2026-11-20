import { LICENSE_NEEDED, gridEntityOfKey, gridOfEntity, licenseGridTitle, licenseHeldGrid, licenseHeldRow, licenseTitle } from "@/lib/license";

// A number on the page, carrying where it came from: `check` names the Supabase
// table and key it was read from, and `raw` the value as read. scripts/check-values.mjs
// reads these attributes from the rendered pages and compares each one with a direct
// Supabase query. The text shown is the value rounded for display.
//
// Session 215: a number read from a table that is "license needed" today (lib/license.ts) is not shown. In its place,
// the catalogue's words, "license needed", with the publishers in the hover; no data-check, so the value checker and
// the snapshot's number list pass it by (data-license-held names the table). The table is read from the check key:
// the series keys name it second (series|<table>|...), the others by their first word (below); latest_prices is held
// by the grid of its entity, as the price board holds a grid (session 207).
const KEY_TABLE: Record<string, string> = {
  deals: "energy_deals", event: "", es: "event_window_daily", griddc: "datacenter_facilities", datacenters: "datacenter_facilities",
  bill: "cost_of_power_monthly", cop: "cost_of_power_monthly", mr: "merchant_revenue_monthly", ms: "merchant_revenue_monthly", projects: "energy_projects",
  gridnews: "news_index",
  // session 2248 (chain 156): the datacenter page's charts, grids view and timeline (dcchart|, dcgrid|, dctime|) count
  // the facilities of datacenter_facilities, so a figure of theirs is held as a datacenters| figure is
  dcchart: "datacenter_facilities", dcgrid: "datacenter_facilities", dctime: "datacenter_facilities",
  // session 264 added ms| (the generator page's month spans of merchant_revenue_monthly); the chain's landing of 14 October maps it as mr|
};

/** Session 7533: the grid of each bill's wholesale price on /learn/bill (site/data/bill_rules.json, `iso`). */
export const BILL_GRID: Record<string, string> = { CA: "caiso", SCE: "caiso", SDGE: "caiso", TX: "ercot", TXC: "ercot" };

/** The held table (and the row's entity) a check key names, or null when the key names no table or none that is held. */
export function heldBy(check: string): { table: string; title: string } | null {
  const p = check.split("|");
  const head = p[0];
  // session 382: or the grid an input names (mr| and ms| keys carry iso=<grid>), so a held grid's figures are held and
  // the others' shown, as the ruling of 12 October holds a table decided by grids row by row
  const entity = p.slice(1).find((x) => gridOfEntity(x) !== "") ?? gridEntityOfKey(p.slice(1));
  // session 315: a finding card's figure (finding|<card>|...|<grid>) is held by the grid its words name; the Digest's
  // chart of the day (digest_chart|<date>|<table>|<key>) by its table
  if (head === "finding") {
    const g = p[p.length - 1];
    return g && g !== "-" && licenseHeldGrid(g) ? { table: `finding ${p[1]}`, title: licenseGridTitle(g) } : null;
  }
  if (head === "digest_chart") return p[2] && licenseHeldRow(p[2], null) ? { table: p[2], title: licenseTitle(p[2]) } : null;
  // session 7533 (chain 304): a bill's figures (bill|<bill>|total, bill|<bill>|wholesale|<ts>, bill|<bill>|share|<ts>, on
  // /learn/bill and the problem sets) name no entity, so cost_of_power_monthly, held by grid since 21 October (ISO-NE,
  // MISO, NYISO), was asked about whole and every one of the five bills' totals, wholesale sums and shares printed
  // "license needed", though no bill is in a held grid and a total is tariff arithmetic that reads no table. A total is
  // never held; the other two are held by the grid of the bill's wholesale price (BILL_GRID, the `iso` of each bill in
  // site/data/bill_rules.json, held equal by tests/test_session7533_bill.py).
  if (head === "bill") {
    if (p[2] === "total") return null;
    const g = BILL_GRID[p[1]];
    return !g || licenseHeldRow("cost_of_power_monthly", `iso:${g}`) ? { table: "cost_of_power_monthly", title: licenseTitle("cost_of_power_monthly") } : null;
  }
  if (head === "latest_prices") {
    const g = gridOfEntity(p[1]);
    return g && licenseHeldGrid(g) ? { table: "latest_prices", title: licenseGridTitle(g) } : null;
  }
  let table = "";
  if (head.startsWith("series")) table = p[1] ?? "";
  else if (head === "event" || head === "entity") table = p[1] ?? "";   // session 329: entity|<table>|<id>|<field>
  // session 4005: the count of a table's rows (event_count|<table>|all or |since|<day>, the policy page and its week view)
  // names its table second as event| does; without this a held table's count printed the empty held rows' "0"
  else if (head === "event_count") table = p[1] ?? "";
  // chain 305 (session 7603, the datacenter tracker read as its reader): a grid's peak hour and capacity on the tracker's
  // "facilities against each grid" (dcgrid|peak_mw|<grid>, dcgrid|capacity_mw|<grid>) are grid_peak_vs_capacity's, and
  // ERCOT's reserve margin (dcgrid|reserve_margin|ERCOT) is ercot_cdr_reserve_margins': both public. Asked as
  // datacenter_facilities' (held whole) they printed "license needed" beside the facilities, against the component's
  // own rule that the grid's public figures stay
  else if (head === "dcgrid" && (p[1] === "peak_mw" || p[1] === "capacity_mw")) table = "grid_peak_vs_capacity";
  else if (head === "dcgrid" && p[1] === "reserve_margin") table = "ercot_cdr_reserve_margins";
  else if (head in KEY_TABLE) table = KEY_TABLE[head];
  if (!table) return null;
  return licenseHeldRow(table, entity ?? (head.startsWith("series") || head === "es" ? undefined : null)) ? { table, title: licenseTitle(table) } : null;
}

// Session 2200 (chain 086): `source`, when given, is the words of where the figure came from (the table, the entity,
// the variable, the period and the source report: lib/explore/source.ts reads them from the key), drawn as the span's
// title, so the figure's source is in its hover; the attribute is absent when the prop is, and no page without it
// changes. The snapshot's number list and check-values read data-check and data-raw as before.
export function Num({ check, raw, children, className, source }: { check: string; raw: number | string; children: React.ReactNode; className?: string; source?: string }) {
  const held = heldBy(check);
  if (held) {
    return (
      <span data-license-held={held.table} className={`text-muted ${className ?? ""}`.trim()} title={held.title}>
        {LICENSE_NEEDED}
      </span>
    );
  }
  return (
    <span data-check={check} data-raw={String(raw)} className={className} title={source}>
      {children}
    </span>
  );
}
