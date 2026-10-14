// Energy Research Warehouse (ERW) site, session 266: the figures the Grid tool's Network view shows (/grid?view=network),
// exported from the same reads the page makes, for Samuel's Stata run (public/grid/erw_2026_grid_replication.do) and its
// Python mirror (erw_2026_grid_replication.py).
//
//   node scripts/write-grid-replication.mjs [out.csv]      (default: public/grid/erw_2026_grid_replication.csv)
//
// The reads, as the page makes them: the network's hourly snapshot in public Storage (lib/network.ts fetchHourly and
// pickSnapshot: the Storage object when it is whole and not older than the committed data/grid_network.json, else the
// committed one); the hour shown (lib/networkV3.ts completeHour); demand of the seven ISO grids (eia930_all_demand) and
// net generation of the seven and the Lower 48 (eia930_all_generation) at that hour, through the public (anon) key.
// Nothing is computed here: every row is a value as read. Exit 1 when a read fails; no file is written then.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const N = await import("../lib/network.ts");
const V3 = await import("../lib/networkV3.ts");

function env(name) {
  if (process.env[name]) return process.env[name];
  const f = path.join(here, "..", ".env.local");
  if (fs.existsSync(f)) for (const line of fs.readFileSync(f, "utf-8").split(/\r?\n/)) { const m = line.match(/^([A-Z_]+)=(.*)$/); if (m && m[1] === name) return m[2].trim().replace(/^"|"$/g, ""); }
  throw new Error(`${name} is not set`);
}
const origin = new URL(env("SUPABASE_URL")).origin;
const key = env("SUPABASE_ANON_KEY");
const ISO = ["CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP"];
const out = process.argv[2] ?? path.join(here, "..", "public", "grid", "erw_2026_grid_replication.csv");

async function q(params) {
  const r = await fetch(`${origin}/rest/v1/series?${new URLSearchParams(params)}`, { headers: { apikey: key, Authorization: `Bearer ${key}` } });
  if (!r.ok) throw new Error(`series: HTTP ${r.status} ${(await r.text()).slice(0, 200)}`);
  return r.json();
}

try {
  const retrieved = new Date().toISOString().replace(/\.\d+Z$/, "Z");
  const committed = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "grid_network.json"), "utf-8"));
  const res = await fetch(`${origin}/${N.NETWORK_OBJECT}`, { cache: "no-store" });
  const fetched = res.ok ? await res.json() : null;
  const { snap, from } = N.pickSnapshot(fetched, committed);
  const complete = V3.completeHour(snap.hours, snap.links);
  const hour = complete.hour ?? snap.hours[snap.hours.length - 1];
  const h = snap.hours.indexOf(hour);
  const at = { ts_utc: `eq.${hour}` };
  const dem = await q({ select: "entity,value", table_name: "eq.eia930_all_demand", variable: "eq.demand_mw", entity: `in.(${ISO.map((b) => `"eia930:${b}"`).join(",")})`, ...at });
  const gen = await q({ select: "entity,value", table_name: "eq.eia930_all_generation", variable: "eq.net_generation_mw", entity: `in.(${[...ISO, "US48"].map((b) => `"eia930:${b}"`).join(",")})`, ...at });
  const rows = [];
  for (const n of snap.nodes) rows.push(["node", n.id, "", hour, 1, "count"]);
  for (const l of snap.links) if (l.mw[h] !== null && l.mw[h] !== undefined) rows.push(["tie", l.a, l.b, hour, l.mw[h], "MW"]);
  for (const r of dem) rows.push(["demand", r.entity.split(":")[1], "", hour, r.value, "MW"]);
  for (const r of gen) rows.push(["generation", r.entity.split(":")[1], "", hour, r.value, "MW"]);
  const head = [
    "# Energy Research Warehouse (ERW): the figures of the Grid tool's Network view (/grid?view=network), session 266",
    `# The hour shown: ${hour} (its start, UTC): the newest hour every reporting pair holds (lib/networkV3.ts completeHour); ${complete.reporting} of the week's ${complete.pairs} pairs report`,
    `# The network's snapshot: ${from === "storage" ? "the hourly one in public Storage (network/grid_network.json)" : "the committed one (site/data/grid_network.json)"}, refreshed ${snap.built}`,
    "# kind node: one row per balancing authority drawn (value 1); kind tie: one pair's flow in the hour, MW, as stored: positive, id exports to other (EIA-930, eia930_all_interchange through the snapshot)",
    "# kind demand: eia930_all_demand, demand_mw, the seven ISO grids; kind generation: eia930_all_generation, net_generation_mw, the seven and US48 (the Lower 48), at the hour shown",
    `# Read with the public key at ${retrieved}. A value not reported is not a row: nothing is filled. Public domain (EIA, Form EIA-930)`,
    `# snapshot_built,${snap.built}`,
    `# hour_shown,${hour}`,
  ];
  const csv = [...head, "kind,id,other,ts_utc,value,unit", ...rows.map((r) => r.join(","))].join("\n") + "\n";
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, csv);
  console.log(`${out}: ${rows.length} rows (${snap.nodes.length} nodes, ${rows.filter((r) => r[0] === "tie").length} ties, ${dem.length} demand, ${gen.length} generation); hour ${hour}; snapshot ${from}, built ${snap.built}`);
} catch (e) {
  console.error(`not written: ${e.message}`);
  process.exit(1);
}
