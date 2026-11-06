// ERW, the Grid tool (/grid): the Network and Gravity tabs' keyed figures as the page's own code computes them
// (session 3703, chain 208). It imports the page's pure functions (site/lib/gridKeys.ts, networkV3.ts, network.ts,
// networkGravity.ts: type imports only, so node runs them without a build or node_modules) and runs them on a network
// snapshot, the file the page draws (the hourly copy in public Storage, erw-public/network/grid_network.json, or the
// committed site/data/grid_network.json). It prints one JSON object on stdout: the hour shown, the snapshot's refresh,
// and every figure with its check key and value. figures_of_the_page.py writes them into page_figures.json; replicate.py
// recomputes each without this code.
//
//   node replication/grid/network_figures.mjs [snapshot.json] [generation.json]
//
// generation.json, optional: {"<BA>": [MW per hour of the snapshot, or null]} for the seven grids and US48, as the page's
// live read of eia930_all_generation gives them; without it the Gravity tab's generation and share are not written.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as K from "../../site/lib/gridKeys.ts";
import * as N from "../../site/lib/network.ts";
import * as V3 from "../../site/lib/networkV3.ts";
import * as G from "../../site/lib/networkGravity.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const snapPath = process.argv[2] ?? path.join(here, "..", "..", "site", "data", "grid_network.json");
const snap = JSON.parse(fs.readFileSync(snapPath, "utf-8"));
const generation = process.argv[3] ? JSON.parse(fs.readFileSync(process.argv[3], "utf-8")) : undefined;
// the seven ISO grids, in the order of the page's grid picker (lib/gridtool.ts GRID_CHOICES)
const ISOS = ["ERCO", "CISO", "PJM", "MISO", "NYIS", "ISNE", "SWPP"];

const complete = V3.completeHour(snap.hours, snap.links);
const hour = K.shownHour(snap, complete);
const out = { built: snap.built, hour, pairs: complete.pairs, reporting: complete.reporting, figures: [] };
const add = (tab, name, check, raw) => out.figures.push({ tab, name, check, raw });

add("network", "hours from the hour shown to the snapshot's refresh", `net|lag|${hour}|${snap.built}`, N.netValue(snap, `net|lag|${hour}|${snap.built}`));
for (const r of K.lower48Panel(snap, ISOS, hour)) {
  if (r.net) add("network", `${r.ba}: net export over its reporting ties, MW (negative: a net import)`, r.net.check, r.net.raw);
  add("network", `${r.ba}: ties reporting`, r.count.check, r.count.raw);
}
const top = N.topExporter(snap, hour);
if (top) add("gravity", `the largest net export of any balancing authority, MW (${top.id})`, `net|topexport|${hour}`, top.mw);
for (const ba of ISOS) {
  const p = K.networkPanel(snap, ba, hour);
  for (const t of p.ties) add("network", `${ba}: its tie with ${t.other}, MW signed from ${ba}'s side`, t.check, t.raw);
  if (p.net) add("network", `${ba}: net ${p.net.kind} over its reporting ties, MW`, p.net.check, p.net.raw);
  if (p.demand) add("network", `${ba}: demand in the hour, MW (the snapshot's)`, p.demand.check, p.demand.raw);
  const mx = N.netValue(snap, `net|maxflow|${ba}|${hour}`);
  if (mx !== undefined) add("gravity", `${ba}: the largest flow on its ties, MW, either way`, `net|maxflow|${ba}|${hour}`, mx);
}
const g = K.gravityPanel(snap, G.GRAVITY_GRIDS.map((x) => x.id), G.GRAVITY_CENTER, hour, generation);
if (g.center) add("gravity", "US48: net generation, MW (the shape's scale)", g.center.check, g.center.raw);
for (const r of g.rows) {
  if (r.gen) add("gravity", `${r.ba}: net generation, MW`, r.gen.check, r.gen.raw);
  if (r.net) add("gravity", `${r.ba}: net import over its reporting ties, MW (negative: a net export)`, r.net.check, r.net.raw);
  if (r.share) add("gravity", `${r.ba}: net import, percent of its net generation`, r.share.check, r.share.raw);
}
// the network's sphere color for the seven grids: the node's carbon intensity and its hour, as the snapshot holds them
for (const ba of ISOS) {
  const n = snap.nodes.find((x) => x.id === ba);
  if (n && n.intensity !== null && n.intensity !== undefined && n.intensity_ts) {
    add("carbon", `${ba}: carbon intensity of its generation, kg CO2 per MWh (the network's sphere color)`,
      `series|carbon_intensity_hourly|eia930:${ba}|intensity_generation|${n.intensity_ts}`, n.intensity);
  }
}
process.stdout.write(JSON.stringify(out) + "\n");
