// Energy Research Warehouse (ERW) site, ruling alternatives of /events (session 7712, 17 November 2026; wip/alt-events-*
// branches, not a default on main). The site's own code run on the replication's file of the ten event pages' figures
// (replication/events/page_figures.json: every figure the pages draw, with its check key), so that what the other choice
// draws is pinned with the site's code. On wip/alt-events-1: how many of those figures the hold leaves "license needed"
// (components/Num.tsx heldBy, lib/license.ts gridOfEntity), by the kind of row, and the index card's CAISO peak.
//   node --import ./scripts/tsx-register.mjs scripts/alt-events-figures.mjs
import fs from "node:fs";

const { heldBy } = await import("../components/Num.tsx");
const fig = JSON.parse(fs.readFileSync(new URL("../../replication/events/page_figures.json", import.meta.url), "utf8"));
const HELD = new Set(["ISNE", "MISO", "NYIS"]);
const out = { figures: 0, held: 0, drawn: 0, byKind: {} };
let caiso = null;
for (const v of Object.values(fig.pages)) {
  for (const f of v.figures) {
    const ent = f.check.split("|")[2] ?? "";
    const [head, code] = ent.split(":");
    const kind = head === "eia930" ? (HELD.has(code) ? "eia930_held_grid" : "eia930_other") : `${head}_own`;
    const h = heldBy(f.check) !== null;
    out.figures += 1;
    out[h ? "held" : "drawn"] += 1;
    out.byKind[kind] = out.byKind[kind] ?? { held: 0, drawn: 0 };
    out.byKind[kind][h ? "held" : "drawn"] += 1;
    if (f.check.includes("eia930:CISO|demand_max_mw|2022-09-06")) caiso = { shown: f.shown, held: h };
  }
}
out.caiso = caiso;
process.stdout.write(JSON.stringify(out));
