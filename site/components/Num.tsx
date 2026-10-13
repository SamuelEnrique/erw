import { LICENSE_NEEDED, gridOfEntity, licenseGridTitle, licenseHeldGrid, licenseHeldRow, licenseTitle } from "@/lib/license";

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
  bill: "cost_of_power_monthly", cop: "cost_of_power_monthly", mr: "merchant_revenue_monthly", projects: "energy_projects",
  gridnews: "news_index",
};

/** The held table (and the row's entity) a check key names, or null when the key names no table or none that is held. */
export function heldBy(check: string): { table: string; title: string } | null {
  const p = check.split("|");
  const head = p[0];
  const entity = p.slice(1).find((x) => gridOfEntity(x) !== "");
  if (head === "latest_prices") {
    const g = gridOfEntity(p[1]);
    return g && licenseHeldGrid(g) ? { table: "latest_prices", title: licenseGridTitle(g) } : null;
  }
  let table = "";
  if (head.startsWith("series")) table = p[1] ?? "";
  else if (head === "event") table = p[1] ?? "";
  else if (head in KEY_TABLE) table = KEY_TABLE[head];
  if (!table) return null;
  return licenseHeldRow(table, entity ?? (head.startsWith("series") || head === "es" ? undefined : null)) ? { table, title: licenseTitle(table) } : null;
}

export function Num({ check, raw, children, className }: { check: string; raw: number | string; children: React.ReactNode; className?: string }) {
  const held = heldBy(check);
  if (held) {
    return (
      <span data-license-held={held.table} className={`text-muted ${className ?? ""}`.trim()} title={held.title}>
        {LICENSE_NEEDED}
      </span>
    );
  }
  return (
    <span data-check={check} data-raw={String(raw)} className={className}>
      {children}
    </span>
  );
}
