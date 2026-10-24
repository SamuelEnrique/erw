// Energy Research Warehouse (ERW) site, session 1423 (chain 111): the network component's words against its server
// panels. The network component (app/network/Network.tsx, a client component) writes figures in the browser: its side
// panel for the picked grid (the ties, the net, the demand), the gravity shape's hover cards (generation, net import, the
// import as a percent of generation) and the map's line cards (a tie's MW). The server panels grid_network_<grid> and
// grid_gravity_<grid> (components/grid/NetworkFigures.tsx, lib/gridKeys.ts) key the same figures in the hour the
// component opens on. For each of the seven ISO grids and the Lower 48, on the committed snapshot
// (data/grid_network.json) with the live week's demand and generation of session 1165's fixture
// (scripts/fixtures/grid_balance.json, the same build), every MW the component's words would write, computed through its
// own functions (lib/networkSide.ts, lib/networkGravity.ts gravityTip, lib/networkMap.ts edgeTip), equals the panel's
// figure for the same tie and hour, as each writes it (lib/format.ts shown). Needs no build, no browser, no network and
// no node_modules.
//
//   node scripts/test-network-words.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as S from "../lib/networkSide.ts";
import * as K from "../lib/gridKeys.ts";
import * as G from "../lib/networkGravity.ts";
import * as M from "../lib/networkMap.ts";
import * as V3 from "../lib/networkV3.ts";
import * as T from "../lib/gridtool.ts";
import { shown } from "../lib/format.ts";

const here = path.dirname(fileURLToPath(import.meta.url));
const read = (...p) => fs.readFileSync(path.join(here, "..", ...p), "utf-8");
const snap = JSON.parse(read("data", "grid_network.json"));
const fx = JSON.parse(read("scripts", "fixtures", "grid_balance.json"));
let n = 0, compared = 0;
const test = (name, f) => { f(); n += 1; console.log(`ok   ${name}`); };
/** Network.tsx's own fmt (whole MW, never "-0"), the way a story or a replayed day is written */
const whole = (v) => (Math.round(v) === 0 ? 0 : Math.round(v)).toLocaleString("en-US");
/** a figure the panel writes signed ("-1,234"), without its sign: the component's words say which way */
const size = (s) => s.replace(/^-/, "");
const eq = (got, want, what) => { assert.equal(got, want, what); compared += 1; };

// the live week as the page reads it (app/network/data.ts liveExtras): the seven ISO grids' demand and generation,
// aligned to the snapshot's hours (lib/gridKeys.ts alignHours, the page's rounding to 0.1 MW)
const ISOS = T.GRID_CHOICES.filter((g) => g.slug !== "us48");
const live = { batteries: {}, batterySource: {}, prices: {}, priceKind: {},
  demand: Object.fromEntries(ISOS.map((g) => [g.ba, K.alignHours(fx.demand[g.ba] ?? [], snap.hours)])),
  generation: Object.fromEntries(ISOS.map((g) => [g.ba, K.alignHours(fx.generation[g.ba] ?? [], snap.hours)])) };
// two lines of the component stay where older tests pin them (sessions 124 and 54): the hour it opens on and the demand's
// check key. Their own text is run here, so the test follows the component as it stands
const comp = read("app", "network", "Network.tsx");
const openLine = /\n  const openHour = ([^;\n]+);/.exec(comp);
const keyLine = /const demandKey = [\s\S]*?const check = ([^;]+);/.exec(comp);
assert.ok(openLine && keyLine, "Network.tsx: the openHour line and demandKey's check line");
const openHourOf = new Function("v3", "snap", `return ${openLine[1]};`);
const demandCheck = new Function("n", "t", "v", `return ${keyLine[1]};`);
const complete = V3.completeHour(snap.hours, snap.links);
const h = openHourOf({ complete }, snap);
const hour = K.shownHour(snap, complete);
const panelFmt = S.sideFormat("live", shown, whole);

test("the fixture is the committed snapshot's week (the same build), so its rows are the page's for these hours", () => {
  assert.equal(fx.snapshot_built, snap.built, "regenerate the fixture with the snapshot (session 1165's read) if the snapshot is rebuilt");
  assert.deepEqual(fx.hours, snap.hours);
});

test("the component opens on the hour the server panels are drawn for", () => {
  assert.equal(snap.hours[h], hour, "Network.tsx openHour is lib/gridKeys.ts shownHour");
  const hours = snap.hours.slice(0, 3);
  assert.equal(openHourOf({ complete: { index: -1 } }, { hours }), 2, "no complete hour: the week's newest, as the panel's");
  assert.equal(K.shownHour({ hours }, { hour: null }), hours[2]);
  assert.equal(openHourOf(undefined, { hours }), 2);
  assert.equal(openHourOf({ complete: { index: 1 } }, { hours }), 1);
  assert.equal(K.shownHour({ hours }, { hour: hours[1] }), hours[1]);
});

test("each ISO grid's side panel in that hour writes the panel grid_network_<grid>'s ties, net and demand, as it writes them", () => {
  for (const g of ISOS) {
    const p = K.networkPanel(snap, g.ba, hour, live.demand[g.ba]);
    const ties = S.sideTies(snap.links, g.ba, h);
    const net = S.sideNet(ties);
    assert.deepEqual(ties.map((t) => t.other).sort(), p.ties.map((t) => t.other).sort(), `${g.ba}: the same ties`);
    for (const t of ties) {
      const k = p.ties.find((x) => x.other === t.other);
      const want = k.raw === 0 ? "0 MW" : `${size(shown(k.raw))} MW ${k.dir === "out" ? "out" : "in"}`;
      eq(S.sideTieWords(t.imp, panelFmt, true), want, `${g.ba} with ${t.other}: the panel writes ${shown(k.raw)} (${k.dir}), key ${k.check}`);
    }
    if (!p.net) { assert.equal(ties.length, 0, `${g.ba}: no net in the panel, no tie in the side panel`); continue; }
    eq(S.sideNetLabel(net, "hour"), `Net ${p.net.kind === "import" ? "imports" : "exports"} this hour`, `${g.ba}: the direction of ${p.net.check}`);
    eq(S.sideNetMw(net, panelFmt), `${shown(p.net.raw)} MW`, `${g.ba}: the net, ${p.net.check}`);
    const d = S.liveDemand(snap, live, g.ba, h);
    if (!p.demand) { assert.equal(d, null, `${g.ba}: no demand in the panel, none in the side panel`); continue; }
    eq(d === null ? null : shown(d), shown(p.demand.raw), `${g.ba}: the demand, ${p.demand.check}`);
    eq(demandCheck(snap.nodes.find((x) => x.id === g.ba), hour, d), p.demand.check, `${g.ba}: the demand's key`);
    console.log(`     ${g.ba}: ${ties.length} ties, ${S.sideNetLabel(net, "hour").toLowerCase()} ${S.sideNetMw(net, panelFmt)}, demand ${shown(d)} MW (panel: ${p.net.kind} ${shown(p.net.raw)}, demand ${shown(p.demand.raw)})`);
  }
});

test("the Lower 48: each of the seven grids, picked, writes its row's net export of grid_network_us48", () => {
  for (const r of K.lower48Panel(snap, ISOS.map((g) => g.ba), hour)) {
    const ties = S.sideTies(snap.links, r.ba, h);
    if (!r.net) { assert.equal(ties.length, 0, r.ba); continue; }
    const net = S.sideNet(ties);
    eq(S.sideNetLabel(net, "hour"), `Net ${r.net.raw < 0 ? "imports" : "exports"} this hour`, `${r.ba}: the direction of ${r.net.check} (${shown(r.net.raw)})`);
    eq(S.sideNetMw(net, panelFmt), `${size(shown(r.net.raw))} MW`, `${r.ba}: ${r.net.check}`);
  }
  assert.equal(T.GRID_CHOICES.find((g) => g.slug === "us48").ba, "US48");
  assert.ok(!snap.nodes.some((x) => x.id === "US48"), "the Lower 48 is no node: no side panel opens on it");
});

test("the gravity shape's cards write the panel grid_gravity_<grid>'s generation, net import and share, as it writes them", () => {
  const ids = G.GRAVITY_GRIDS.map((x) => x.id);
  const panel = K.gravityPanel(snap, ids, G.GRAVITY_CENTER, hour, live.generation);
  // what Network.tsx hands the shape in the live week: the hour's generation and the net import over the ties
  const gen = Object.fromEntries([...ids, G.GRAVITY_CENTER].map((id) => [id, live.generation?.[id]?.[h] ?? null]));
  const net = Object.fromEntries(ids.map((id) => [id, G.netImportAt(snap.links, id, h)]));
  const lay = G.gravityLayout(gen, net);
  const at = { hour: snap.hours[h], refresh: snap.built };
  for (const r of panel.rows) {
    const p = lay.places.find((x) => x.id === r.ba);
    const ties = !r.net ? "No tie reported in the hour"
      : `${r.net.raw > 0 ? `Net import ${shown(r.net.raw)} MW` : r.net.raw < 0 ? `Net export ${size(shown(r.net.raw))} MW` : "No net exchange (0 MW)"}, over its reporting ties (EIA-930 interchange)`;
    const share = r.share && r.net && r.net.raw !== 0 ? [`${size(shown(r.share.raw))} percent of its net generation`] : [];
    const window = `In the hour from ${hour.slice(0, 10)} ${hour.slice(11, 13)}:00 UTC, snapshot refreshed ${snap.built.slice(0, 16).replace("T", " ")} UTC`;
    const circle = G.gravityTip(p, at, "circle", shown);
    eq(circle[0], r.gen ? `Net generation ${shown(r.gen.raw)} MW (EIA-930)` : "Net generation not held for the hour", `${r.ba}: the generation, ${r.gen?.check}`);
    eq(circle[1], ties, `${r.ba}: the net import, ${r.net?.check}`);
    assert.deepEqual(circle.slice(2), [...share, window], `${r.ba}: the share (${r.share?.check}) and the window`);
    compared += share.length;
    assert.deepEqual(G.gravityTip(p, at, "edge", shown), [ties, ...share, window], `${r.ba}: the line's card`);
    console.log(`     ${r.ba}: ${circle.slice(0, 3).join("; ")} (panel: ${r.gen ? shown(r.gen.raw) : "not held"}, ${r.net ? shown(r.net.raw) : "no tie"}, ${r.share ? shown(r.share.raw) : "none"})`);
  }
  assert.ok(panel.rows.some((r) => r.share && !Number.isInteger(r.share.raw)), "a share that is not whole: the card's two decimals are tested");
});

test("the map's line cards: a MW only where grid_network_<grid> holds the tie, and then its figure as the panel writes it", () => {
  const edges = M.edgesAt(snap.links, h);
  const win = { at: hour, refresh: snap.built, day: false };
  for (const g of T.GRID_CHOICES) {
    const mp = M.mapPanelOf(`?grid=${g.slug}&view=network`, T.GRID_CHOICES, complete.hour, snap.hours);
    const p = g.slug === "us48" ? null : K.networkPanel(snap, g.ba, hour, live.demand[g.ba]);
    let held = 0;
    for (const e of edges) {
      const line = M.edgeTip(e, (id) => id, mp, win, shown)[1];
      if (!line.endsWith("MW, the figure checked in the panel under the map")) { assert.ok(!/^\d/.test(line), `${g.slug}: no MW on ${e.a}-${e.b}`); continue; }
      const t = p?.ties.find((x) => x.other === (e.a === g.ba ? e.b : e.a));
      assert.ok(t, `${g.slug}: ${e.a}-${e.b} is a tie of the panel`);
      eq(line, `${size(shown(t.raw))} MW, the figure checked in the panel under the map`, `${g.slug}: ${t.check}`);
      assert.equal(t.dir, e.source === g.ba ? "out" : "in");
      held += 1;
    }
    if (g.slug === "us48") assert.equal(held, 0, "the Lower 48's panel holds no tie: no line writes a MW");
    else assert.equal(held, p.ties.filter((t) => t.raw !== 0).length, `${g.slug}: every tie of the panel with a flow has its line's MW`);
  }
});

test("typed cases: the live week written as the panel writes it, a story and a replayed day as before", () => {
  const live1 = S.sideFormat("live", shown, whole), story = S.sideFormat("story", shown, whole);
  assert.equal(S.sideTieWords(1234, live1, true), "1,234 MW in");
  assert.equal(S.sideTieWords(-1234.5, live1, true), "1,234.50 MW out", "a figure that is not whole: two decimals, as shown writes it");
  assert.equal(S.sideTieWords(0.4, live1, true), "0.40 MW in", "the panel writes 0.40: so does the side panel");
  assert.equal(S.sideTieWords(0, live1, true), "0 MW");
  assert.equal(S.sideTieWords(0.4, story, false), "0 MW", "a story or a day: a figure that rounds to zero, as before");
  assert.equal(S.sideTieWords(-1234.5, story, false), "1,235 MW out", "whole MW, as before");
  assert.equal(S.sideNetLabel(0, "hour"), "Net exports this hour", "a zero net is an export, as the panel signs it");
  assert.equal(S.sideNetLabel(12, "day"), "Net imports this day");
  assert.equal(S.sideNetLabel(-12, "hour"), "Net exports this hour");
  assert.equal(S.sideNetMw(-2500.6, live1), "2,500.60 MW");
  assert.equal(S.sideNetMw(-2500.6, story), "2,501 MW");
  const lay = G.gravityLayout({ US48: 400000, CISO: 19800.5, ERCO: 50000 }, { CISO: 1234.4, ERCO: -2500 });
  const at = (id) => lay.places.find((p) => p.id === id);
  const W = { hour: "2026-10-21T23:00:00Z", refresh: "2026-10-23T14:36:57Z" };
  assert.deepEqual(G.gravityTip(at("CISO"), W, "circle", shown).slice(0, 3),
    ["Net generation 19,800.50 MW (EIA-930)", "Net import 1,234.40 MW, over its reporting ties (EIA-930 interchange)", `${shown((1234.4 / 19800.5) * 100)} percent of its net generation`]);
  assert.equal(G.gravityTip(at("ERCO"), W, "edge", shown)[1], "5 percent of its net generation", "a whole share is written whole, as shown writes it");
  assert.equal(G.gravityTip(at("ERCO"), W, "edge")[1], "5.0 percent of its net generation", "without a formatter, session 1153's words");
});

test("the component and the shape draw through these functions", () => {
  const net = read("app", "network", "Network.tsx"), grav = read("app", "network", "NetworkGravity.tsx"), map = read("app", "network", "NetworkMap.tsx");
  for (const s of [
    'const fmt = (v: number) => (Math.round(v) === 0 ? 0 : Math.round(v)).toLocaleString("en-US");',
    "demand: (id, h) => liveDemand(snap, live, id, h),",
    "const ties = useMemo(() => (pick ? sideTies(view.links, pick.id, hour) : []), [pick, hour, view]);",
    "const netImport = sideNet(ties);",
    "const mwOf = sideFormat(view.kind, shown, fmt);",
    "{sideNetLabel(netImport, unit)}",
    "{sideNetMw(netImport, mwOf)}",
    'sideTieWords(t.imp, mwOf, view.kind === "live")',
    "<Num check={check} raw={v}>{shown(v)}</Num>",
    "for (const g of GRAVITY_GRIDS) net[g.id] = netImportAt(view.links, g.id, hour);",
    'gen[id] = view.kind === "live" ? live.generation?.[id]?.[hour] ?? null : null;',
  ]) assert.ok(net.includes(s), `Network.tsx: ${s}`);
  assert.ok(grav.includes("gravityTip(hovered, at, hover.kind, shown)"), "NetworkGravity.tsx passes shown");
  assert.ok(map.includes("edgeTip(hoveredEdge, nameOf, panel, win, shown)"), "NetworkMap.tsx passes shown");
});

console.log(`${n} tests passed, ${compared} figures compared with the server panels in the hour ${hour}`);
