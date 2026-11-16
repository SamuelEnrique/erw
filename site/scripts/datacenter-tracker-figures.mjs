// Energy Research Warehouse (ERW) site, session 7400 (chain 303): every figure of the datacenter tracker (/datacenters
// and /datacenters?view=grids), as the page computes it, by its check key.
//
//   node scripts/datacenter-tracker-figures.mjs <rows dir> [today YYYY-MM-DD]
//
// <rows dir> holds what replication/datacenter_tracker/fetch_rows.py wrote from the live set: datacenter_facilities.json,
// queue_sites.json, queue_active.json. The page's own functions are run on those rows (lib/dctop.ts, lib/largeload.ts,
// lib/dcrollups.ts, lib/datacenter/bygrid.ts, lib/datacenter.ts) and on the site's own files (data/large_load_status.json,
// data/siting/headroom.json, data/datacenter/). The facilities are held (license needed), so the built page draws none
// of their figures: this is what it draws once the hold allows, and what scripts/check-values.mjs would read there.
// Prints one JSON object: { today, figures: {key: value}, words: {key: text} }. replication/datacenter_tracker/replicate.py
// compares it with its own computation. No network, nothing written.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { INDEX, yearFiles } from "./datacenter-ways.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const T = await import("../lib/dctop.ts");
const L = await import("../lib/largeload.ts");
const R = await import("../lib/dcrollups.ts");
const B = await import("../lib/datacenter/bygrid.ts");
const D = await import("../lib/datacenter.ts");

const dir = process.argv[2];
const today = process.argv[3] ?? new Date().toISOString().slice(0, 10);
const read = (name) => JSON.parse(fs.readFileSync(path.join(dir, name), "utf-8"));
const site = (...p) => JSON.parse(fs.readFileSync(path.join(here, "..", ...p), "utf-8"));
const rows = read("datacenter_facilities.json"), sites = read("queue_sites.json"), active = read("queue_active.json");
const out = {}, words = {};

// 1. the top block and the list's group lines (app/datacenters/Body.tsx, DatacentersTable.tsx: lib/dctop.ts)
Object.assign(out, T.topFigures(rows.map(T.topRowOf), today));

// 2. ERCOT's large loads (app/datacenters/LargeLoad.tsx): each stated figure by its series key, and the summary's share
const f = site("data", "large_load_status.json");
const VARIABLE = { approved: "approved_to_energize_mw", nonsimultaneous: "observed_nonsimultaneous_peak_mw", simultaneous: "observed_simultaneous_peak_mw",
  new_count: "new_submissions_count", new_mw: "new_submissions_mw" };
for (const r of f.reports) for (const [k, v] of Object.entries(VARIABLE)) if (r[k] !== undefined) out[`series|${f.table}|ercot:large_load|${v}|${r.day}T00:00:00Z`] = r[k];
words["ercot|summary"] = L.summary(f);
const s = L.span(f);
if (s) out["ercot|observed_share_pct"] = Number(((100 * s.last.nonsimultaneous) / s.last.approved).toFixed(0));
out["ercot|reports"] = f.reports.length;
out["ercot|impossible_reports"] = L.impossible(f).length;
out["ercot|month_mismatch_reports"] = f.reports.filter(L.monthMismatch).length;

// 3. beside it, the facilities the ERW holds (LargeLoad.tsx's own mapping of a row, then lib/largeload.ts facilityCounts)
const fac = rows.map((r) => ({ name: r.name, operator: r.operator, status: r.status, capacity_mw: r.capacity_mw, state: r.extra?.state ?? "", kind: r.extra?.kind ?? "",
  country: L.countryOf(r.extra?.country, r.extra?.state) }));
const c = L.facilityCounts(fac);
Object.assign(out, { "datacenters|sites_us": c.us, "datacenters|sites_texas": c.texas, "datacenters|sites_n_with_mw": c.withMw, "datacenters|sites_mw": c.mw,
  "datacenters|texas_n_with_mw": c.texasWithMw });
if (c.texasWithMw) out["datacenters|texas_mw"] = c.texasMw;
for (const [k, n] of Object.entries(c.byKind)) out[`datacenters|kind_count|${k}`] = n;

// 4. the rollups by grid and by operator (Rollups.tsx: the groups with a counted facility)
for (const dim of ["grid", "operator"]) {
  for (const r of R.rollups(rows, dim).filter((x) => x.counted > 0)) {
    out[R.rollupKey("facilities", dim, r.value)] = r.counted;
    if (r.mw !== null) out[R.rollupKey("mw", dim, r.value)] = r.mw;
    out[R.rollupKey("with_mw", dim, r.value)] = r.withMw;
    out[R.rollupKey("without", dim, r.value)] = r.without;
  }
}

// 5. the timeline (Timeline.tsx)
const t = R.timeline(rows);
out["dctime|rows"] = t.length;
for (const dim of ["grid", "year"]) {
  for (const cell of R.timelineCells(t, dim)) {
    out[R.timeKey("count", dim, cell.value)] = cell.count;
    if (cell.median !== null) out[R.timeKey("median", dim, cell.value)] = cell.median;
  }
}

// 6. the three charts (DcCharts.tsx: lib/dcrollups.ts dcFigures)
Object.assign(out, R.dcFigures(rows));

// 7. the facilities against each grid (FacilitiesVsGrid.tsx), with the site's copy of grid_peak_vs_capacity and ERCOT's margin
const h = site("data", "siting", "headroom.json");
const GRID_ID = { ERCOT: "ercot", CAISO: "caiso", PJM: "pjm", MISO: "miso", SPP: "spp", NYISO: "nyiso", "ISO-NE": "isone" };
const loads = new Map(R.gridLoads(rows).map((l) => [l.grid, l]));
for (const [g, id] of Object.entries(GRID_ID)) {
  const pc = h?.peak_capacity?.[id], l = loads.get(g) ?? null, rm = h?.reserve?.grids?.[id];
  if (l) {
    out[R.gridKey("facilities", g)] = l.facilities;
    out[R.gridKey("with_mw", g)] = l.withMw;
    for (const [stat, v] of [["planned", l.planned], ["under_construction", l.underConstruction], ["operating", l.operating]]) if (v !== null) out[R.gridKey(stat, g)] = v;
    const share = pc ? R.shareOfPeak(l, pc.peak_mw) : null;
    if (share !== null) out[R.gridKey("share_of_peak", g)] = share;
  }
  if (pc) { out[R.gridKey("peak_mw", g)] = pc.peak_mw; out[R.gridKey("capacity_mw", g)] = pc.capacity_mw; }
  if (rm) out[R.gridKey("reserve_margin", g)] = rm.peak.pct;
}

// 8. the power side and the view by grid: the queue sites (PowerSide.tsx, GridsView.tsx) and what a flat load paid
for (const r of sites) if (r.capacity_mw !== null) out[`entity|${r.table_name}|${r.entity_id}|capacity_mw`] = Number(r.capacity_mw);
const qrows = sites.map((r) => ({ table_name: r.table_name, capacity_mw: r.capacity_mw, status: r.status, zone: r.extra?.zone ?? null }));
const gs = B.groups(qrows, active);
for (const g of gs) for (const stat of ["sites", "sites_with_mw", "mw_asked", "active_positions", "active_mw"]) out[`dcq|${g.grid}|${g.zone}|${stat}`] = B.groupStat(gs, g.grid, g.zone, stat);
for (const g of [...new Set(gs.map((x) => x.grid))].filter((x) => INDEX.grids[x])) {
  const cs = D.regionCosts(yearFiles(g), INDEX.grids[g], ["zone"]);
  const main = cs.find((x) => x.main) ?? cs[0];
  const ys = [...new Set(cs.flatMap((x) => x.years.map((y) => y.y)))].sort().slice(-8);   // GridsView.tsx: at most the last eight years held
  for (const x of cs) {
    out[`dcpow|${g}|${x.id}|per`] = x.per;
    words[`dcpow|${g}|${x.id}|span`] = `${x.buy} ${x.from} to ${x.to}`;
    // the fold under the chart shows, for each year, the cheapest zone, the default zone and the dearest: every zone's year is emitted
    for (const y of x.years) if (ys.includes(y.y)) out[`dcpow|${g}|${x.id}|year|${y.y}`] = y.per;
  }
  if (main) words[`dcpow|${g}|main`] = main.id;
}

console.log(JSON.stringify({ today, figures: out, words }));
