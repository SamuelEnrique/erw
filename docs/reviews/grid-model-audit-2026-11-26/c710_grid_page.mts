// Session 10205: the Gravity tab's Lower 48 figures as the page's own code computes them (site/lib/network.ts and
// site/lib/networkV3.ts), from the committed snapshot, to set beside the independent restatement (runs/c710_grid_audit.py).
//   cd site && node --import ./scripts/tsx-register.mjs ../runs/c710_grid_page.mts
import { readFileSync } from "node:fs";
import { netExports, tiesAt, topExporter } from "../site/lib/network.ts";
import { completeHour } from "../site/lib/networkV3.ts";

const snap = JSON.parse(readFileSync(new URL("../site/data/grid_network.json", import.meta.url), "utf-8"));
const c = completeHour(snap.hours, snap.links);
const hour = c.hour ?? snap.hours[snap.hours.length - 1];
const net = netExports(snap, hour);
const out: Record<string, unknown> = { hour, reporting: c.reporting, newestPairs: c.newestPairs, top: topExporter(snap, hour),
  lag: Math.round((Date.parse(snap.built) - Date.parse(hour)) / 3_600_000) };
for (const ba of ["CISO", "ERCO", "ISNE", "MISO", "NYIS", "PJM", "SWPP"]) {
  const ties = tiesAt(snap, ba, hour);
  out[ba] = { net: net.get(ba), ties: ties.length, maxflow: Math.max(...ties.map((t) => Math.abs(t.mw))) };
}
console.log(JSON.stringify(out));
process.exitCode = 0;
