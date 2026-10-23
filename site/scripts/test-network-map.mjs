// Energy Research Warehouse (ERW) site, session 1156 (chain 077): the network map's pure parts (lib/networkMap.ts
// edgesAt, edgeHeld, edgeTip, mapWindowWords, mapPanelOf, regionSlug, carryMoment). On typed cases and on the committed
// snapshot (data/grid_network.json): an edge runs from the exporter to the importer by the tie's sign, a tie with no
// figure in the frame (or a zero) has no edge; a line's MW is written only where the panel under the map
// (lib/gridKeys.ts networkPanel, grid_network_<grid>) holds that same figure, and then it is that figure; one of the
// seven ISO grids clicked opens its row on the Grid tool, carrying the moment shown. Needs no build, no network and no
// node_modules.
//
//   node scripts/test-network-map.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as M from "../lib/networkMap.ts";
import * as K from "../lib/gridKeys.ts";
import * as V3 from "../lib/networkV3.ts";
import * as T from "../lib/gridtool.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const snap = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "grid_network.json"), "utf-8"));
const boundaries = JSON.parse(fs.readFileSync(path.join(here, "..", "public", "network", "ba_boundaries.json"), "utf-8"));
let n = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };
const complete = V3.completeHour(snap.hours, snap.links);
const hour = K.shownHour(snap, complete);
const h = snap.hours.indexOf(hour);
const fmt = (v) => (Number.isInteger(v) ? v.toLocaleString("en-US") : v.toFixed(2));
const live = { at: hour, refresh: snap.built, day: false };

test("the direction is the tie's sign: positive from a to b, negative from b to a; no figure or a zero, no edge", () => {
  const links = [{ a: "ERCO", b: "SWPP", mw: [120, -80, null, 0, undefined] }];
  assert.deepEqual(M.edgesAt(links, 0), [{ source: "ERCO", target: "SWPP", mw: 120, a: "ERCO", b: "SWPP" }]);
  assert.deepEqual(M.edgesAt(links, 1), [{ source: "SWPP", target: "ERCO", mw: 80, a: "ERCO", b: "SWPP" }]);
  assert.deepEqual(M.edgesAt(links, 2), [], "a null is no figure: not drawn");
  assert.deepEqual(M.edgesAt(links, 3), [], "a zero has no direction: not drawn, as the network has always done");
  assert.deepEqual(M.edgesAt(links, 4), []);
});

test("on the snapshot, every edge of the hour shown is a tie with a figure in it, and every such tie (but a zero) is an edge", () => {
  const edges = M.edgesAt(snap.links, h);
  const withFigure = snap.links.filter((l) => l.mw[h] !== null && l.mw[h] !== undefined && l.mw[h] !== 0);
  assert.equal(edges.length, withFigure.length);
  assert.ok(edges.length > 50, `the hour shown holds ${edges.length} edges`);
  for (const e of edges) {
    const l = snap.links.find((x) => x.a === e.a && x.b === e.b);
    assert.equal(e.mw, Math.abs(l.mw[h]));
    assert.equal(e.source, l.mw[h] > 0 ? l.a : l.b, "the exporter is the source, the arrowhead at the importer");
  }
});

test("the panel under the map: the page's grid from the query it keeps, the component's opening hour; the Lower 48 holds no tie", () => {
  assert.deepEqual(M.mapPanelOf("?grid=ercot&view=network", T.GRID_CHOICES, complete.hour, snap.hours), { ba: "ERCO", hour });
  assert.deepEqual(M.mapPanelOf(T.gridHref("pjm", "network").slice("/grid".length), T.GRID_CHOICES, complete.hour, snap.hours), { ba: "PJM", hour });
  assert.deepEqual(M.mapPanelOf("?grid=us48&view=network", T.GRID_CHOICES, complete.hour, snap.hours), { ba: null, hour });
  assert.deepEqual(M.mapPanelOf("?grid=ercot&view=network", T.GRID_CHOICES, null, ["2026-10-21T00:00:00Z", "2026-10-21T01:00:00Z"]), { ba: "ERCO", hour: "2026-10-21T01:00:00Z" });
  assert.equal(M.mapPanelOf("?view=network", T.GRID_CHOICES, complete.hour, snap.hours), null);
  assert.equal(hour, snap.hours[complete.index >= 0 ? complete.index : snap.hours.length - 1], "the hour NetworkFigures draws is the one the component opens on");
});

test("a line's MW is written only for the panel's figures, and is then the panel's own figure (every grid of the seven)", () => {
  const edges = M.edgesAt(snap.links, h);
  for (const g of T.GRID_CHOICES.filter((x) => x.slug !== "us48")) {
    const panel = M.mapPanelOf(T.gridHref(g.slug, "network").slice("/grid".length), T.GRID_CHOICES, complete.hour, snap.hours);
    const p = K.networkPanel(snap, g.ba, hour);
    const held = edges.filter((e) => M.edgeHeld(e, panel, live));
    // every held edge is one of the panel's ties, with the same MW (the panel signs it from the grid's side)
    for (const e of held) {
      const other = e.a === g.ba ? e.b : e.a;
      const t = p.ties.find((x) => x.other === other);
      assert.ok(t, `${g.ba} with ${other} is in the panel`);
      assert.equal(Math.abs(t.raw), e.mw);
      assert.equal(t.dir, e.source === g.ba ? "out" : "in");
      assert.equal(t.check, `net|tie|${g.ba}|${other}|${hour}`);
      const tip = M.edgeTip(e, (id) => id, panel, live, fmt);
      assert.equal(tip[1], `${fmt(e.mw)} MW, the figure checked in the panel under the map`);
    }
    // every edge not held writes no MW
    for (const e of edges.filter((x) => !held.includes(x))) {
      assert.ok(!(e.a === g.ba || e.b === g.ba), "an edge of the grid in view, in the panel's hour, is held");
      assert.ok(!/\d MW/.test(M.edgeTip(e, (id) => id, panel, live, fmt).join(" ")), "no MW for a tie the panel does not hold");
    }
    // the panel's ties with a nonzero figure are all edges (a zero is in the panel, not on the map)
    assert.equal(held.length, p.ties.filter((t) => t.raw !== 0).length);
  }
});

test("no MW for the Lower 48, another hour, a day of the replay or a story", () => {
  const edges = M.edgesAt(snap.links, h);
  const us48 = { ba: null, hour };
  assert.ok(edges.every((e) => !M.edgeHeld(e, us48, live)), "the Lower 48's panel holds no tie");
  const ercot = { ba: "ERCO", hour };
  const e = edges.find((x) => x.a === "ERCO" || x.b === "ERCO");
  assert.ok(e, "ERCOT has a tie in the hour shown");
  assert.equal(M.edgeHeld(e, ercot, live), true);
  assert.equal(M.edgeHeld(e, ercot, { ...live, at: snap.hours[0] }), false, "another hour of the week");
  assert.equal(M.edgeHeld(e, ercot, { at: hour.slice(0, 10), refresh: null, day: true }), false, "a day of the replay");
  assert.equal(M.edgeHeld(e, ercot, { at: hour, refresh: null, day: false }), false, "a story's hour");
  assert.equal(M.edgeHeld(e, null, live), false, "no panel");
  const other = M.edgeTip(e, (id) => id, ercot, { ...live, at: snap.hours[0] }, fmt);
  assert.equal(other[1], `Its MW is checked in the panel under the map for the hour from ${hour.slice(0, 10)} ${hour.slice(11, 13)}:00 UTC; here its width follows the flow`);
});

test("the hover words: direction, the window as the gravity shape writes it, the source", () => {
  const e = { source: "SWPP", target: "ERCO", mw: 312, a: "ERCO", b: "SWPP" };
  const names = { ERCO: "ERCOT", SWPP: "SPP" };
  const w = { at: "2026-10-21T23:00:00Z", refresh: "2026-10-23T14:36:57Z", day: false };
  assert.deepEqual(M.edgeTip(e, (id) => names[id], { ba: "ERCO", hour: "2026-10-21T23:00:00Z" }, w, fmt), [
    "From SPP to ERCOT", "312 MW, the figure checked in the panel under the map",
    "In the hour from 2026-10-21 23:00 UTC, snapshot refreshed 2026-10-23 14:36 UTC", "EIA-930's public interchange"]);
  assert.equal(M.mapWindowWords({ at: "2021-02-15T00:00:00Z", refresh: null, day: true }), "On 2021-02-15, EIA's Eastern day (the day's average MW)");
  assert.equal(M.mapWindowWords({ at: "2021-02-15T06:00:00Z", refresh: null, day: false }), "In the hour from 2021-02-15 06:00 UTC, as the story's file holds it");
  const tip = M.edgeTip(e, (id) => names[id], { ba: "CISO", hour: w.at }, w, fmt);
  assert.equal(tip[1], "Its MW is not written on the map: the panel under it holds the ties of the grid in view only; the width follows the flow");
});

test("a grid clicked: one of the seven ISO grids other than the grid in view opens its row; the rest open the panel", () => {
  assert.equal(M.regionSlug("CISO", T.GRID_CHOICES, "ERCO"), "caiso");
  assert.equal(M.regionSlug("ERCO", T.GRID_CHOICES, "ERCO"), null, "the grid in view opens its panel");
  assert.equal(M.regionSlug("BPAT", T.GRID_CHOICES, "ERCO"), null, "another balancing authority opens its panel");
  assert.equal(M.regionSlug("PJM", T.GRID_CHOICES, null), "pjm", "on the Lower 48 every one of the seven is a link");
  // the seven ISO grids are all regions of the boundary file, so each can be clicked
  const ids = new Set(boundaries.regions.map((r) => r.id));
  for (const g of T.GRID_CHOICES.filter((x) => x.slug !== "us48")) assert.ok(ids.has(g.ba), `${g.ba} has an area`);
});

test("the moment shown is carried onto the grid's address: the view as net and its t; the live week's opening hour adds nothing", () => {
  const base = T.gridHref("caiso", "network", { shape: "map" });
  assert.equal(base, "/grid?grid=caiso&view=network&shape=map");
  assert.equal(M.carryMoment(base, ""), base);
  assert.equal(M.carryMoment(base, "?grid=ERCO"), base, "the panel open is not carried: the new grid's own opens");
  assert.equal(M.carryMoment(base, "?view=day&t=2021-02-15&grid=ERCO"), "/grid?grid=caiso&view=network&shape=map&net=day&t=2021-02-15");
  assert.equal(M.carryMoment(base, "?t=2026-10-20T05%3A00%3A00Z"), "/grid?grid=caiso&view=network&shape=map&t=2026-10-20T05%3A00%3A00Z");
  // the page reads the carried words back as the network's own (lib/gridtool.ts netFromPage)
  const back = T.netFromPage(M.carryMoment(base, "?view=day&t=2021-02-15").split("?")[1], "CISO");
  assert.equal(back, "?view=day&t=2021-02-15&grid=CISO&shape=map");
});

test("the part of a line that takes the pointer is its middle: the ends, at the regions' points, stay the regions'", () => {
  assert.deepEqual(M.hitSegment([0, 0], [100, 50]), [[20, 10], [80, 40]]);
  assert.deepEqual(M.hitSegment([100, 50], [0, 0]), [[80, 40], [20, 10]], "from the exporter's side to the importer's");
  assert.deepEqual(M.hitSegment([10, 10], [10, 10]), [[10, 10], [10, 10]]);
  assert.deepEqual(M.hitSegment([0, 0], [10, 0], 0.5), [[5, 0], [5, 0]]);
});

console.log(`${n} tests passed`);
