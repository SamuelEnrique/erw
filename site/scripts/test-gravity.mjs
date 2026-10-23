// Energy Research Warehouse (ERW) site, session 1153 (chain 077): the gravity shape's edges and hover words
// (lib/networkGravity.ts gravityEdges, netWords, gravityTip, windowWords) and the picker's carried day (lib/carry.ts).
// On typed cases and on the committed snapshot (data/grid_network.json): a net importer sits nearer the center than the
// middle ring and a net exporter farther out (the rule, its sign and its square-root scale, unchanged); an edge is drawn
// only for a grid with a net figure in the window, and its words give the MW, the share and the window. Needs no build,
// no network and no node_modules.
//
//   node scripts/test-gravity.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as G from "../lib/networkGravity.ts";
import * as C from "../lib/carry.ts";
import * as V3 from "../lib/networkV3.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const snap = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "grid_network.json"), "utf-8"));
let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };
const W = { hour: "2026-10-21T23:00:00Z", refresh: "2026-10-23T14:36:57Z" };

test("the rule stands: an importer nearer the center, an exporter farther out, square root, full at a quarter", () => {
  const gen = { US48: 400000, CISO: 20000, ERCO: 50000, PJM: 90000, MISO: 70000, NYIS: 15000, ISNE: 12000, SWPP: 30000 };
  const net = { CISO: 5000, ERCO: -2000, PJM: 0, MISO: 70000 / 16, NYIS: null, ISNE: 12000, SWPP: -30000 };
  const l = G.gravityLayout(gen, net);
  const at = (id) => l.places.find((p) => p.id === id);
  const { D_MID, D_SPAN } = G.GRAVITY;
  assert.ok(at("CISO").d < D_MID, "a net importer is pulled in");
  assert.ok(at("ERCO").d > D_MID, "a net exporter is pushed out");
  assert.equal(at("PJM").d, D_MID, "no net exchange: the middle ring");
  assert.equal(at("NYIS").d, D_MID, "no tie reported: the middle ring");
  assert.equal(at("NYIS").state, "no-ties");
  // a sixteenth of generation is half the full pull (ruling 2c)
  assert.ok(Math.abs(at("MISO").d - (D_MID - D_SPAN * 0.5)) < 1e-9);
  // CAISO imports a quarter: the full pull (unless the frame's limits hold it), ISO-NE all of it: the full pull too
  assert.equal(at("CISO").share, 0.25);
  assert.ok(Math.abs(at("ISNE").d - Math.max(D_MID - D_SPAN, G.GRAVITY.R_CENTER + at("ISNE").r + G.GRAVITY.GAP)) < 1e-9);
});

test("an edge is drawn only for a grid with a net figure in the window", () => {
  const l = G.gravityLayout({ US48: 400000, CISO: 20000, ERCO: 50000 }, { CISO: 100, ERCO: null, PJM: -50 });
  const ids = G.gravityEdges(l).map((p) => p.id);
  assert.deepEqual(ids, ["CISO", "PJM"]);   // the order of GRAVITY_GRIDS: CISO, SWPP, MISO, ISNE, NYIS, PJM, ERCO
  assert.ok(!ids.includes("ERCO") && !ids.includes("MISO"));
});

test("the edge's words: MW with its direction, the share, the window", () => {
  const l = G.gravityLayout({ US48: 400000, CISO: 20000, ERCO: 50000, PJM: 90000 }, { CISO: 1234.4, ERCO: -2500.6, PJM: 0.3 });
  const at = (id) => l.places.find((p) => p.id === id);
  assert.equal(G.netWords(at("CISO")), "Net import 1,234 MW");
  assert.equal(G.netWords(at("ERCO")), "Net export 2,501 MW");
  assert.equal(G.netWords(at("PJM")), "No net exchange (0 MW)");
  assert.equal(G.netWords(at("MISO")), null);
  assert.deepEqual(G.gravityTip(at("CISO"), W, "edge"), [
    "Net import 1,234 MW, over its reporting ties (EIA-930 interchange)",
    "6.2 percent of its net generation",
    "In the hour from 2026-10-21 23:00 UTC, snapshot refreshed 2026-10-23 14:36 UTC",
  ]);
  assert.deepEqual(G.gravityTip(at("ERCO"), W, "edge"), [
    "Net export 2,501 MW, over its reporting ties (EIA-930 interchange)",
    "5.0 percent of its net generation",
    "In the hour from 2026-10-21 23:00 UTC, snapshot refreshed 2026-10-23 14:36 UTC",
  ]);
  assert.equal(G.gravityTip(at("PJM"), W, "edge").length, 2, "no share for no net exchange");
});

test("the circle's words: generation, the exchange, the window; nothing stands in for what is not held", () => {
  const l = G.gravityLayout({ US48: 400000, CISO: 20000 }, { CISO: 1000, SWPP: -10 });
  const at = (id) => l.places.find((p) => p.id === id);
  assert.deepEqual(G.gravityTip(at("CISO"), W, "circle"), [
    "Net generation 20,000 MW (EIA-930)",
    "Net import 1,000 MW, over its reporting ties (EIA-930 interchange)",
    "5.0 percent of its net generation",
    "In the hour from 2026-10-21 23:00 UTC, snapshot refreshed 2026-10-23 14:36 UTC",
  ]);
  assert.deepEqual(G.gravityTip(at("SWPP"), W, "circle").slice(0, 2), ["Net generation not held for the hour", "Net export 10 MW, over its reporting ties (EIA-930 interchange)"]);
  assert.equal(G.gravityTip(at("ERCO"), W, "circle")[1], "No tie reported in the hour");
});

test("on the committed snapshot, in the hour the component opens on: one edge per grid with a reporting tie, its MW the ties' sum", () => {
  const c = V3.completeHour(snap.hours, snap.links);
  const h = c.index >= 0 ? c.index : snap.hours.length - 1;
  const net = Object.fromEntries(G.GRAVITY_GRIDS.map((g) => [g.id, G.netImportAt(snap.links, g.id, h)]));
  const l = G.gravityLayout({}, net);
  const edges = G.gravityEdges(l);
  assert.equal(edges.length, G.GRAVITY_GRIDS.filter((g) => net[g.id] !== null).length);
  assert.ok(edges.length >= 1);
  for (const e of edges) {
    const ties = snap.links.filter((x) => (x.a === e.id || x.b === e.id) && x.mw[h] !== null && x.mw[h] !== undefined);
    assert.ok(ties.length > 0, e.id);
    const sum = ties.reduce((a, x) => a + (x.a === e.id ? -x.mw[h] : x.mw[h]), 0);
    assert.equal(e.net, sum, e.id);
    assert.ok(G.gravityTip(e, { hour: snap.hours[h], refresh: snap.built }, "edge").at(-1).includes(snap.hours[h].slice(0, 10)));
  }
});

test("the picker carries the replay's day, and nothing else", () => {
  const href = "/grid?grid=caiso&view=gravity&shape=gravity";
  assert.equal(C.carryWords(href, "?grid=ercot&view=gravity&net=day&t=2025-07-01&node=ERCO&shape=gravity", C.KEEP_DAY),
    "/grid?grid=caiso&view=gravity&shape=gravity&net=day&t=2025-07-01");
  assert.equal(C.carryWords(href, "grid=ercot&view=gravity&net=day&t=2025-07-01", C.KEEP_DAY), "/grid?grid=caiso&view=gravity&shape=gravity&net=day&t=2025-07-01");
  // the live week's hour, a story, or no day: the link is as the page wrote it
  assert.equal(C.carryWords(href, "?grid=ercot&view=gravity&net=live&t=2026-10-21T23:00:00Z", C.KEEP_DAY), href);
  assert.equal(C.carryWords(href, "?grid=ercot&view=gravity&net=uri_2021", C.KEEP_DAY), href);
  assert.equal(C.carryWords(href, "", C.KEEP_DAY), href);
  assert.equal(C.carryWords("/grid", "?net=day&t=2021-02-15", C.KEEP_DAY), "/grid?net=day&t=2021-02-15");
  // the restored address reads the day back as the component's own: view=day, t
  const page = C.carryWords(href, "?net=day&t=2021-02-15", C.KEEP_DAY);
  const q = new URLSearchParams(page.split("?")[1]);
  assert.equal(q.get("net"), "day");
  assert.equal(q.get("t"), "2021-02-15");
  assert.equal(q.get("grid"), "caiso");
});

console.log(`${n} of ${n} passed`);
