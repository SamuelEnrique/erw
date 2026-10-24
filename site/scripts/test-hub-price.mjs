// Energy Research Warehouse (ERW) site, session 1402 (chain 100): the hub's real-time price beside the Grid tool's
// hourly mix (lib/hubPriceHourly.ts, components/grid/HubPricePanel.tsx, the `strip` series of components/TimeChart.tsx).
// On a committed fixture of real rows (scripts/fixtures/hub_price.json: iso_rtm_hub_prices at ERCOT's, SPP's and CAISO's
// hubs, read with the anon key on 24 October 2026; tests/fixtures/session1152/mix_hourly_erco.json for ERCOT's hourly
// mix of the same days): every key the panel writes is recomputed here the way scripts/check-values.mjs recomputes it
// (the table's rows of the key's entity, variable and range, then hubHourStat), and again by plain arithmetic. Needs no
// build, no server and no database.
//
//   node --import ./scripts/alias-register.mjs --import ./scripts/tsx-register.mjs scripts/test-hub-price.mjs
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import os from "node:os";
import { createRequire } from "node:module";
import { fileURLToPath, pathToFileURL } from "node:url";
import { createElement } from "react";
import { renderToStaticMarkup } from "react-dom/server";
import * as P from "../lib/hubPriceHourly.ts";
import { licenseHeldRow } from "../lib/license.ts";
import { heldBy } from "../components/Num.tsx";
import { Hourly } from "../components/mix/Now.tsx";
import { StackedArea } from "../components/StackedArea.tsx";
import { HubPricePanel, hubPriceWhy, hubStrip } from "../components/grid/HubPricePanel.tsx";
import { HUB_PRICE_ANCHOR, METHOD_HUB_PRICE, hubPriceAnchor } from "../lib/gridAnchors.ts";
import { render } from "../lib/markdown.ts";
import { transpile } from "./tsx-loader.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.join(here, "..", "..");
const FIX = JSON.parse(fs.readFileSync(path.join(here, "fixtures", "hub_price.json"), "utf-8"));
const MIX = JSON.parse(fs.readFileSync(path.join(ROOT, "tests", "fixtures", "session1152", "mix_hourly_erco.json"), "utf-8"));
const H = 3_600_000, DAY = 24 * H;
const AT = new Date(FIX.read_at);
/** The fixture's rows as the live set's series rows. */
const ROWS = Object.entries(FIX.rows).flatMap(([k, rs]) => { const [entity, variable] = k.split("|"); return rs.map(([ts_utc, value]) => ({ entity, variable, ts_utc, value })); });
const rowsOf = (hub) => ROWS.filter((r) => r.entity === hub.entity && r.variable === hub.variable);
const text = (h) => h.replace(/<!-- -->/g, "").replace(/<[^>]+>/g, "").replace(/&#x27;/g, "'").replace(/&amp;/g, "&");

/** Every href of a tree of React elements (a function component that is not a client stub called with its props). */
function linksOf(node, out = []) {
  if (!node || typeof node !== "object") return out;
  if (Array.isArray(node)) { for (const x of node) linksOf(x, out); return out; }
  const p = node.props ?? {};
  if (typeof p.href === "string") out.push(p.href);
  if (typeof node.type === "function" && !node.type.__erwClient) return linksOf(node.type(p), out);
  return linksOf(p.children, out);
}

/** The client components a tree draws (the tsx loader's stubs), each with its props. */
function clientsOf(node, out = []) {
  if (!node || typeof node !== "object") return out;
  if (Array.isArray(node)) { for (const x of node) clientsOf(x, out); return out; }
  const p = node.props ?? {};
  if (typeof node.type === "function" && node.type.__erwClient) { out.push({ name: node.type.__erwClient.split("#").pop(), props: p }); return clientsOf(p.children, out); }
  if (typeof node.type === "function") return clientsOf(node.type(p), out);
  return clientsOf(p.children, out);
}

/** A key recomputed as scripts/check-values.mjs does: the rows of its entity, variable and [start, end), then hubHourStat. */
function truth(check) {
  const [kind, table, variable, start, end, entity] = check.split("|");
  assert.equal(table, "iso_rtm_hub_prices");
  const rows = ROWS.filter((r) => r.entity === entity && r.variable === variable && Date.parse(r.ts_utc) >= Date.parse(start) && Date.parse(r.ts_utc) < Date.parse(end));
  return P.hubHourStat(rows.map((r) => ({ ts_utc: r.ts_utc, value: r.value })), kind.slice("series_h".length), start, end);
}
/** The same by plain arithmetic, by hour: the hours with four rows, each the sum of the four over four. */
function plain(rows, start, end) {
  const by = new Map();
  for (const r of rows) { const t = Date.parse(r.ts_utc); if (t < start || t >= end) continue; const h = Math.floor(t / H) * H; by.set(h, [...(by.get(h) ?? []), r.value]); }
  return [...by].filter(([, v]) => v.length === 4).map(([t, v]) => ({ t, mean: (v[0] + v[1] + v[2] + v[3]) / 4 })).sort((a, b) => a.t - b.t);
}

test("the three hubs are the site's own (docs/grids/grids.json) and public; MISO's is held, PJM has none", () => {
  const grids = Object.fromEntries(JSON.parse(fs.readFileSync(path.join(ROOT, "docs", "grids", "grids.json"), "utf-8")).grids.map((g) => [g.slug, g]));
  assert.deepEqual(Object.keys(P.HUB_PRICE).sort(), ["caiso", "ercot", "spp"]);
  for (const [g, hub] of Object.entries(P.HUB_PRICE)) {
    const want = grids[g].hub;
    assert.equal(hub.entity, want.entity, g);
    assert.equal(hub.label, want.label, g);
    assert.equal(licenseHeldRow(P.RT_HUB_TABLE, hub.entity, AT), false, `${g}'s hub is public on ${FIX.read_at}`);
    assert.ok(rowsOf(hub).length > 0, `${g}: the fixture holds rows of ${hub.entity} ${hub.variable}`);
  }
  assert.equal(grids.pjm.hub, null);
  assert.equal(licenseHeldRow(P.RT_HUB_TABLE, grids.miso.hub.entity, AT), true, "MISO's rows of the table are held");
  // the scarcity strip reads the same hubs and variables (lib/scarcityStrip.ts, session 1154)
  const strip = fs.readFileSync(path.join(here, "..", "lib", "scarcityStrip.ts"), "utf-8");
  for (const g of ["ercot", "caiso"]) assert.ok(strip.includes(`price: { entity: "${P.HUB_PRICE[g].entity}", variable: "${P.HUB_PRICE[g].variable}" }`), g);
});

test("an hour's price is the mean of its four 15-minute prices, and an hour missing one is not held", () => {
  const rows = rowsOf(P.HUB_PRICE.ercot);
  const hs = P.hourMeans(rows);
  assert.equal(hs.length, 72);
  assert.deepEqual(hs, plain(rows, -Infinity, Infinity));
  // taken out inside this test only: one interval of 2026-10-21 18:00 UTC (the fixture holds all four)
  const less = rows.filter((r) => r.ts_utc !== "2026-10-21T18:30:00+00:00");
  const h2 = P.hourMeans(less);
  assert.equal(h2.length, 71);
  assert.ok(!h2.some((h) => h.t === Date.parse("2026-10-21T18:00:00Z")), "the hour with three intervals has no price");
  // an interval written twice is held once (its last row): made inside this test only
  const twice = [...rows, { ...rows[0], value: rows[0].value }];
  assert.deepEqual(P.hourMeans(twice), hs);
});

test("the chart's window is the hourly chart's own (components/mix/Now.tsx Hourly), on ERCOT's real rows", () => {
  const gen = MIX.generation;
  const w = P.chartWindow(gen);
  const el = Hourly({ rows: gen, table: "eia930_all_generation", label: "ERCOT" });
  const area = el.props.children;
  assert.equal(area.type, StackedArea);
  const x = area.props.x;
  assert.equal(w.t0, x[0]);
  assert.equal(w.t1, x[x.length - 1] + H);
  assert.equal(w.t0, Date.parse("2026-10-20T00:00:00Z"));
  assert.equal(w.t1, Date.parse("2026-10-23T00:00:00Z"));
  // through a later newest hour, as the panel passes it
  const t = Date.parse("2026-10-23T05:00:00Z");
  const x2 = Hourly({ rows: gen, table: "t", label: "ERCOT", through: t }).props.children.props.x;
  assert.equal(P.chartWindow(gen, t).t1, x2[x2.length - 1] + H);
  assert.equal(P.chartWindow([]), null);
});

test("ERCOT over the chart's 3 days: every key recomputed as check-values does, and by plain arithmetic", () => {
  const hub = P.HUB_PRICE.ercot;
  const w = P.chartWindow(MIX.generation);
  const hp = P.hubPrice(ROWS, hub, w);
  assert.equal(hp.of, 72);
  assert.equal(hp.points.length, 72);
  assert.equal(hp.n.raw, 72);
  const ps = plain(rowsOf(hub), w.t0, w.t1);
  const mean = ps.reduce((a, h) => a + h.mean, 0) / ps.length;
  assert.ok(Math.abs(hp.mean.raw - mean) < 1e-9);
  const top = ps.reduce((a, h) => (h.mean > a.mean ? h : a));
  assert.equal(hp.max.t, top.t);
  assert.equal(hp.max.fig.raw, top.mean);
  assert.equal(hp.latest.t, Date.parse("2026-10-22T23:00:00Z"));
  for (const f of [hp.n, hp.mean, hp.max.fig, hp.latest.fig]) assert.equal(truth(f.check), f.raw, f.check);
  assert.equal(hp.n.check, "series_hn|iso_rtm_hub_prices|spp_rtm|2026-10-20T00:00:00Z|2026-10-23T00:00:00Z|ercot:HB_HUBAVG");
  assert.equal(hp.latest.fig.check, "series_hmean|iso_rtm_hub_prices|spp_rtm|2026-10-22T23:00:00Z|2026-10-23T00:00:00Z|ercot:HB_HUBAVG");
  assert.match(hp.max.fig.check, /^series_hmax\|iso_rtm_hub_prices\|spp_rtm\|2026-10-20T00:00:00Z\|2026-10-23T00:00:00Z\|ercot:HB_HUBAVG$/);
  // each key names a public table and grid: drawn, not held (components/Num.tsx heldBy)
  for (const f of [hp.n, hp.mean, hp.max.fig, hp.latest.fig]) assert.equal(heldBy(f.check), null, f.check);
  // a MISO hub's key of the same kind would be held (the table is held for MISO)
  if (licenseHeldRow(P.RT_HUB_TABLE, "miso:INDIANA.HUB")) assert.equal(heldBy("series_hmean|iso_rtm_hub_prices|lmp_rtm_15m_mean|2026-10-20T00:00:00Z|2026-10-23T00:00:00Z|miso:INDIANA.HUB")?.table, "iso_rtm_hub_prices");
});

test("SPP's real gap (2026-10-19 05:00 to 2026-10-20 05:00 UTC not held) is a gap in the strip, never filled", () => {
  const hub = P.HUB_PRICE.spp;
  const w = { t0: Date.parse("2026-10-19T00:00:00Z"), t1: Date.parse("2026-10-22T00:00:00Z") };
  const hp = P.hubPrice(ROWS, hub, w);
  assert.equal(hp.of, 72);
  assert.equal(hp.n.raw, 29);
  const held = new Map(hp.points);
  assert.equal(held.get(Date.parse("2026-10-19T04:00:00Z")) !== null, true);
  for (let t = Date.parse("2026-10-19T05:00:00Z"); t < Date.parse("2026-10-20T05:00:00Z"); t += H) assert.equal(held.get(t), null, new Date(t).toISOString());
  for (let t = Date.parse("2026-10-21T05:00:00Z"); t < w.t1; t += H) assert.equal(held.get(t), null, "after the newest row");
  assert.equal(hp.latest.t, Date.parse("2026-10-21T04:00:00Z"));
  for (const f of [hp.n, hp.mean, hp.max.fig, hp.latest.fig]) assert.equal(truth(f.check), f.raw, f.check);
  assert.ok(Number.isFinite(hp.mean.raw) && hp.max.fig.raw >= hp.mean.raw);
  // no hour held in a window: the count is 0, and no mean, highest or last hour is written
  const none = P.hubPrice(ROWS, hub, { t0: Date.parse("2026-10-19T06:00:00Z"), t1: Date.parse("2026-10-19T12:00:00Z") });
  assert.equal(none.n.raw, 0);
  assert.equal(truth(none.n.check), 0);
  assert.equal(none.mean, null);
  assert.equal(none.max, null);
  assert.equal(none.latest, null);
  assert.equal(hubStrip(none), undefined);
});

test("where no chart is drawn (CAISO): the 7 days to the newest day held whole", () => {
  const hub = P.HUB_PRICE.caiso;
  const w = P.priceWindow(rowsOf(hub));
  assert.equal(w.t1, Date.parse("2026-10-23T00:00:00Z"), "2026-10-23 is held only to 06:45 UTC");
  assert.equal(w.t1 - w.t0, 7 * DAY);
  const hp = P.hubPrice(ROWS, hub, w);
  assert.equal(hp.n.raw, 48);
  assert.equal(hp.of, 168);
  for (const f of [hp.n, hp.mean, hp.max.fig, hp.latest.fig]) assert.equal(truth(f.check), f.raw, f.check);
  assert.equal(P.priceWindow([]), null);
});

test("the grids without a price say why, in the tool's words", () => {
  for (const g of ["ercot", "caiso", "spp"]) assert.equal(hubPriceWhy(g, g.toUpperCase(), AT), null, g);
  assert.equal(hubPriceWhy("pjm", "PJM", AT).words, "license needed");
  assert.equal(hubPriceWhy("miso", "MISO", AT).words, "paused");
  for (const [g, l] of [["nyiso", "NYISO"], ["isone", "ISO-NE"]]) {
    const w = hubPriceWhy(g, l, AT);
    assert.equal(w.words, "license needed", g);
    assert.match(w.why, new RegExp(`^${l}'s prices need a license from 2026-10-2`));
  }
  assert.equal(hubPriceWhy("us48", "Lower 48", AT).words, "no hub of its own");
});

test("the panel: its figures keyed, its anchor, its file, its method; a failed read says so and draws no figure", () => {
  const hub = P.HUB_PRICE.ercot;
  const hp = P.hubPrice(ROWS, hub, P.chartWindow(MIX.generation));
  const html = renderToStaticMarkup(createElement(HubPricePanel, { grid: "ercot", label: "ERCOT", i: 0, read: { ok: true, data: ROWS }, hp, alone: false }));
  assert.ok(html.includes(`id="${HUB_PRICE_ANCHOR}"`) && html.includes('data-grid-panel="grid_hubprice_ercot"'));
  const keys = [...html.matchAll(/data-check="([^"]+)" data-raw="([^"]+)"/g)].map((m) => [m[1], Number(m[2])]);
  const distinct = new Map(keys);
  assert.equal(distinct.size, 4);
  for (const [k, v] of distinct) assert.equal(truth(k), v, k);
  assert.ok(html.includes('data-grid-file="grid_hubprice_ercot"'), "the panel's file");
  // the method link: a SiteLink (a client component, drawn by the browser), found in the panel's tree with its address
  assert.ok(linksOf(HubPricePanel({ grid: "ercot", label: "ERCOT", i: 0, read: { ok: true, data: ROWS }, hp, alone: false })).includes(METHOD_HUB_PRICE), "the method link");
  assert.ok(!clientsOf(HubPricePanel({ grid: "ercot", label: "ERCOT", i: 0, read: { ok: true, data: ROWS }, hp, alone: false })).some((c) => c.name === "TimeChart"), "under the mix chart, the panel draws no chart of its own");
  assert.match(text(html), /Under the chart, ERCOT Hub Average \(HB_HUBAVG\)'s real-time price by hour, the same hours: 2026-10-20 00:00 UTC to 2026-10-22 24:00 UTC \(72 of 72 hours held whole\)/);
  // alone (CAISO): the price drawn by itself
  const c = P.hubPrice(ROWS, P.HUB_PRICE.caiso, P.priceWindow(rowsOf(P.HUB_PRICE.caiso)));
  const alone = renderToStaticMarkup(createElement(HubPricePanel, { grid: "caiso", label: "CAISO", i: 1, read: { ok: true, data: ROWS }, hp: c, alone: true }));
  assert.ok(alone.includes(`id="${hubPriceAnchor(1, "caiso")}"`) && alone.includes('id="hub-price-caiso"'));
  const charts = clientsOf(HubPricePanel({ grid: "caiso", label: "CAISO", i: 1, read: { ok: true, data: ROWS }, hp: c, alone: true })).filter((x) => x.name === "TimeChart");
  assert.equal(charts.length, 1);
  assert.equal(charts[0].props.series.length, 1);
  assert.deepEqual(charts[0].props.series[0].points, c.points);
  assert.match(text(alone), /California's hourly mix is withheld \(session 118\), so the price is drawn alone\./);
  // a failed read: "could not be read", no figure, the method kept
  const failed = renderToStaticMarkup(createElement(HubPricePanel, { grid: "spp", label: "SPP", i: 0, read: { ok: false, reason: "statement timeout" }, hp: null, alone: false }));
  assert.ok(!failed.includes("data-check"));
  assert.match(text(failed), /SPP North Hub \(SPPNORTH_HUB\), real-time price by hour: could not be read \(iso_rtm_hub_prices\)\./);
  assert.ok(failed.includes("iso_rtm_hub_prices could not be read just now: statement timeout"));
  // held, paused and hubless grids: one line, no figure, no read made
  for (const [g, l, w] of [["pjm", "PJM", "license needed"], ["miso", "MISO", "paused"], ["nyiso", "NYISO", "license needed"], ["isone", "ISO-NE", "license needed"], ["us48", "Lower 48", "no hub of its own"]]) {
    const h = renderToStaticMarkup(createElement(HubPricePanel, { grid: g, label: l, i: 0, read: null, hp: null, alone: false }));
    assert.ok(h.includes(`data-hubprice-held="${w}"`) && !h.includes("data-check") && h.includes(`data-grid-panel="grid_hubprice_${g}"`), g);
  }
});

// components/TimeChart.tsx is a client component, which the tsx loader stubs; here its own source is transpiled as the
// loader transpiles a server file and loaded from a temporary file, so it draws (React's hooks run in a static render)
const require_ = createRequire(path.join(here, "..", "package.json"));
async function realTimeChart() {
  const src = fs.readFileSync(path.join(here, "..", "components", "TimeChart.tsx"), "utf-8").replace(/^"use client";/, "");
  const js = transpile(src, "TimeChart.tsx").replace(/from "react\/jsx-runtime"/g, `from "${pathToFileURL(require_.resolve("react/jsx-runtime")).href}"`)
    .replace(/from "react"/g, `from "${pathToFileURL(require_.resolve("react")).href}"`);
  const f = path.join(os.tmpdir(), `erw-s1402-timechart-${process.pid}.mjs`);
  fs.writeFileSync(f, js);
  try { return (await import(pathToFileURL(f).href)).TimeChart; } finally { fs.rmSync(f, { force: true }); }
}

test("the strip of TimeChart: off by default (the chart as before), drawn under the chart on its time axis when given", async () => {
  const TimeChart = await realTimeChart();
  const x = [0, 1, 2].map((i) => Date.parse("2026-10-20T00:00:00Z") + i * H);
  const gas = { name: "Natural gas", color: "var(--color-fuel-gas)", points: x.map((t, i) => [t, 10 * (i + 1)]) };
  const before = renderToStaticMarkup(createElement(TimeChart, { series: [gas], stack: true, share: true, unit: "MW", ariaLabel: "a", height: 320 }));
  assert.ok(!before.includes("data-chart-strip"));
  assert.match(before, /viewBox="0 0 760 320" width="760" height="320"/);
  // a name no longer than the stack's ("Natural gas"), so the right gutter (the widest name's, the strip's included) is the same
  const strip = { name: "Hub price", color: "ink", unit: "USD/MWh", points: x.map((t, i) => [t, i === 1 ? null : 25 + i]), strip: true };
  const after = renderToStaticMarkup(createElement(TimeChart, { series: [gas, strip], stack: true, share: true, unit: "MW", ariaLabel: "a", height: 320 }));
  assert.ok(after.includes('data-chart-strip="Hub price"'));
  assert.match(after, /viewBox="0 0 760 412" width="760" height="412"/);
  // the stack is the other series alone: the strip is not stacked, not among data-points, not in the direct labels
  const pts = JSON.parse(after.match(/data-points="([^"]+)"/)[1].replace(/&quot;/g, '"'));
  assert.equal(pts.length, 1);
  assert.equal(after.split("<g data-chart-strip")[0], before.split("</svg>")[0].replace(/viewBox="0 0 760 320" width="760" height="320"/, 'viewBox="0 0 760 412" width="760" height="412"').replace('aria-label="a"', 'aria-label="a; under it, Hub price in USD/MWh"').replace(/<\/g>(?![\s\S]*<\/g>)/, "</g>"),
    "everything drawn before the strip is the chart without it (the frame's height and its label aside)");
  assert.match(after, /aria-label="a; under it, Hub price in USD\/MWh"/);
  // the gap at the hour not held: the line breaks (two moves)
  const d = after.match(/<g data-chart-strip[^>]*>.*?<path d="([^"]+)"/)[1];
  assert.equal((d.match(/M/g) ?? []).length, 2);
  // StackedArea hands the strip on as the last series, marked
  const el = StackedArea({ x, layers: [{ key: "gas", label: "Natural gas", color: "var(--color-fuel-gas)", values: [10, 20, 30] }], unit: "MW", ariaLabel: "a", strip: { name: strip.name, color: "ink", unit: "USD/MWh", points: strip.points } });
  const ser = el.props.series;
  assert.equal(ser.length, 2);
  assert.equal(ser[1].strip, true);
  assert.equal(StackedArea({ x, layers: [{ key: "gas", label: "g", color: "c", values: [1, 2, 3] }], unit: "MW", ariaLabel: "a" }).props.series.length, 1);
});

test("check-values and check-methods know the three kinds; the method note names the figures and its heading is the link's", () => {
  const cv = fs.readFileSync(path.join(here, "check-values.mjs"), "utf-8");
  assert.ok(cv.includes('if (p[0] === "series_hn" || p[0] === "series_hmean" || p[0] === "series_hmax") {'));
  assert.ok(cv.includes('return P.hubHourStat(rows, p[0].slice("series_h".length), start, end);'));
  const cm = fs.readFileSync(path.join(here, "check-methods.mjs"), "utf-8");
  assert.ok(cm.includes("series_hn: [1, 2], series_hmean: [1, 2], series_hmax: [1, 2],"));
  const note = fs.readFileSync(path.join(ROOT, "docs", "methods", "generation_mix_hourly.md"), "utf-8");
  const html = render(note, "docs/methods/generation_mix_hourly.md");
  const id = METHOD_HUB_PRICE.split("#")[1];
  assert.ok(html.includes(`id="${id}"`), `the note has the heading ${id}`);
  const sec = note.split("## The hub's price beside the hourly mix (chain 100, 24 October 2026)")[1].split("\n## ")[0];
  for (const w of ["iso_rtm_hub_prices", "spp_rtm", "lmp_rtm_15m_mean", "series_hn|", "series_hmean|", "series_hmax|", "grid_hubprice_<grid>", "Decisions (chain 100"]) assert.ok(sec.includes(w), w);
});
