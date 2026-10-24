// Energy Research Warehouse (ERW) site, session 1172 (chain 078): every old address of the Grid tool, tested. Every
// address that redirects to /grid (next.config.ts, read here as Next reads it: the rules' own list, their `has`
// conditions and named groups, and the query carried over under the destination's, as Next 16 merges them in
// prepareDestination: the request's words first, the destination's on top), the in-page redirect of /ask
// (app/ask/page.tsx), and every old view word the page reads (lib/gridtool.ts OLD_VIEWS, mix=clean, shape=gravity,
// grid=ERCO, ba=erco, grids=pjm,miso, node=BPAT) opens the tab that holds its blocks with the grid it named, and the
// view's own words (net, t, node, mix, mixp, shape, q) are kept. Then the round trips: an address written by gridHref,
// by the picker's carry (lib/carry.ts), by the map's region link (lib/networkMap.ts carryMoment) or by the network
// component (netToPage) reads back through gridPick to the same grid and tab. Needs no build, no server, no database.
//
//   node --import ./scripts/alias-register.mjs scripts/test-grid-addresses.mjs
//
// The cases are written from the code and from the method notes (docs/methods/grid_network.md "One page, four tabs, and
// the Ask panel", docs/methods/generation_mix_hourly.md "Session 133: the one energy mix page" and "mixp in the
// address"). The route check (scripts/check-routes.mjs) lists every case marked `route`: the test asserts it.
import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as T from "../lib/gridtool.ts";
import { carryWords, KEEP_DAY } from "../lib/carry.ts";
import { carryMoment } from "../lib/networkMap.ts";
import { choiceOf } from "../lib/mixpage.ts";
import nextConfig from "../next.config.ts";
import { GRID_ANCHOR, PANEL_ANCHORS, anchorOf, panelAddress } from "../lib/gridAnchors.ts";   // session 1183

const here = path.dirname(fileURLToPath(import.meta.url));
const SITE = path.join(here, "..");
const src = (...p) => fs.readFileSync(path.join(SITE, ...p), "utf-8");
let n = 0;
const test = async (name, f) => { await f(); n += 1; console.log(`ok   ${name}`); };
const one = (v) => (Array.isArray(v) ? v[0] : v);

// ------------------------------------------------------------------ the redirects, as Next applies them
const RULES = await nextConfig.redirects();
const toGrid = (d) => d === "/grid" || d.startsWith("/grid?");
const GRID_RULES = RULES.filter((r) => toGrid(r.destination));

/** A query as Next parses a request's: each word once, a repeated word an array. */
function queryOf(search) {
  const q = {};
  for (const [k, v] of new URLSearchParams(search)) q[k] = k in q ? [].concat(q[k], v) : v;
  return q;
}
/** next/dist/shared/lib/router/utils/prepare-destination.js matchHas: a query condition matches the word's last value,
 *  anchored; its named groups become params; no value asks only that the word is there. */
function matchHas(rule, query) {
  const params = {};
  const hit = (h) => {
    assert.equal(h.type, "query", `a Grid redirect's condition is on the query (${rule.source})`);
    const value = query[h.key];
    if (!h.value && value) { params[h.key] = value; return true; }
    if (!value) return false;
    const m = (Array.isArray(value) ? value.slice(-1)[0] : value).match(new RegExp(`^${h.value}$`));
    if (!m) return false;
    Object.assign(params, m.groups ?? {});
    return true;
  };
  return (rule.has ?? []).every(hit) && !(rule.missing ?? []).some(hit) ? params : null;
}
/** The address a request is sent to, or null when no rule of the list matches (the first rule that matches wins). */
function redirectOf(address) {
  const at = address.indexOf("?");
  const pathname = at < 0 ? address : address.slice(0, at);
  const query = queryOf(at < 0 ? "" : address.slice(at + 1));
  for (const [i, rule] of RULES.entries()) {
    if (rule.source !== pathname) continue;
    const params = matchHas(rule, query);
    if (!params) continue;
    const [destPath, destSearch = ""] = rule.destination.split("?");
    const dest = queryOf(destSearch);
    for (const [k, v] of Object.entries(dest)) dest[k] = v.replace(/:([a-z_][a-z0-9_]*)/gi, (_, name) => { assert.ok(name in params, `:${name} is captured`); return params[name]; });
    return { rule: i, pathname: destPath, query: { ...query, ...dest } };   // the request's words, the destination's on top
  }
  return null;
}
/** app/ask/page.tsx: /ask is the Ask panel of the Grid tool, its own redirect (a 307), so its query is not carried whole:
 *  the grid by any of its words (else the Lower 48), ask=1, and the question. */
function askRedirect(address) {
  const q = queryOf(address.split("?")[1] ?? "");
  const grid = one(q.grid), question = one(q.q);
  const base = T.gridHref(T.gridBy(grid)?.slug ?? "us48");
  const to = `${base}${base.includes("?") ? "&" : "?"}ask=1${question ? `&q=${encodeURIComponent(question.slice(0, 500))}` : ""}`;
  return { rule: "ask", pathname: to.split("?")[0], query: queryOf(to.split("?")[1]) };
}
/** Where an address lands: through its redirect when it has one, else as it is. */
function land(address) {
  if (address === "/ask" || address.startsWith("/ask?")) return askRedirect(address);
  const r = redirectOf(address);
  if (r) {
    assert.equal(redirectOf(`${r.pathname}?${new URLSearchParams(Object.entries(r.query).flatMap(([k, v]) => [].concat(v).map((x) => [k, x])))}`), null, `${address} arrives in one step`);
    return r;
  }
  return { rule: null, pathname: address.split("?")[0], query: queryOf(address.split("?")[1] ?? "") };
}
/** What the page draws from a query (app/grid/page.tsx: the pick, then the mix page's own choice on the Mix and Clean tabs). */
function pageOf(sp) {
  const p = T.gridPick(sp);
  const { grid, view } = p;
  let mix = null;
  if (view === "mix" || view === "clean") {
    const mixQuery = { ...sp, view: view === "clean" ? "clean" : one(sp.mix), grid: undefined };
    if (grid.slug === "us48") { if (!one(sp.ba)) mixQuery.ba = "us48"; } else if (!one(sp.grids)) mixQuery.grids = grid.slug;
    mix = choiceOf(mixQuery).view;
  }
  return { p, mix };
}

// ------------------------------------------------------------------ the cases
// from: the old address; tab, grid: where it lands; node, day, ask, mix: what the page then opens (mix: the energy mix's
// own view on the Mix or Clean tab); keep: words the landed query must hold, with their values; route: listed in the
// route check. Every word of `from` other than view is carried over unchanged (asserted for every redirect case).
const DAY = "2021-02-15";
const CASES = [
  // /network and /network/v3: the network's view is written as net, its grid (an EIA-930 code) chooses the grid or opens its panel
  { from: "/network", tab: "network", grid: "us48", node: null, route: true },
  { from: `/network?view=day&t=${DAY}&grid=ERCO&prices=1&trace=1`, tab: "network", grid: "ercot", node: "ERCO", day: DAY, keep: { net: "day", t: DAY, prices: "1", trace: "1" }, route: true },
  { from: "/network?view=live&grid=BPAT", tab: "network", grid: "us48", node: "BPAT", keep: { net: "live" }, route: true },
  { from: "/network?view=uri_2021&grid=CISO", tab: "network", grid: "caiso", node: "CISO", keep: { net: "uri_2021" } },
  { from: "/network?view=east_heat_2025&grid=PJM&batteries=1", tab: "network", grid: "pjm", node: "PJM", keep: { net: "east_heat_2025", batteries: "1" } },
  { from: "/network?shape=gravity&grid=ERCO", tab: "gravity", grid: "ercot", node: "ERCO", keep: { shape: "gravity" }, route: true },
  { from: `/network?view=day&t=${DAY}&shape=gravity&grid=SWPP`, tab: "gravity", grid: "spp", node: "SWPP", day: DAY, keep: { net: "day", t: DAY, shape: "gravity" } },
  { from: "/network?shape=map&grid=NYIS", tab: "network", grid: "nyiso", node: "NYIS", keep: { shape: "map" }, route: true },
  { from: "/network/v3", tab: "network", grid: "us48", node: null, route: true },
  { from: `/network/v3?view=day&t=${DAY}&grid=ERCO&prices=1&trace=1`, tab: "network", grid: "ercot", node: "ERCO", day: DAY, keep: { net: "day", t: DAY }, route: true },
  { from: "/network/v3?view=evening&grid=ISNE", tab: "network", grid: "isone", node: "ISNE", keep: { net: "evening" } },
  // /mix: its view is written as mix (How clean, and when is the Clean tab), its ba and grids choose the grid
  { from: "/mix", tab: "mix", grid: "us48", mix: "now", route: true },
  { from: "/mix?ba=erco&state=TX", tab: "mix", grid: "ercot", mix: "now", keep: { ba: "erco", state: "TX" }, route: true },
  { from: "/mix?ba=ciso&state=CA", tab: "mix", grid: "caiso", mix: "now", keep: { ba: "ciso", state: "CA" }, route: true },
  { from: "/mix?view=clean", tab: "clean", grid: "us48", mix: "clean", route: true },
  { from: "/mix?view=clean&grids=pjm&year=2024", tab: "clean", grid: "pjm", mix: "clean", keep: { grids: "pjm", year: "2024" } },
  { from: "/mix?view=now&ba=erco&mixp=month", tab: "mix", grid: "ercot", mix: "now", keep: { mix: "now", mixp: "month" }, route: true },
  { from: "/mix?view=day&grids=pjm,miso&period=2026-04", tab: "mix", grid: "pjm", mix: "day", keep: { mix: "day", grids: "pjm,miso", period: "2026-04" }, route: true },
  { from: "/mix?view=stress&grids=nyiso&year=2025", tab: "mix", grid: "nyiso", mix: "stress", keep: { mix: "stress" } },
  { from: "/mix?view=history&states=TX", tab: "mix", grid: "us48", mix: "history", keep: { mix: "history", states: "TX" } },
  { from: "/mix?view=forecast&grids=caiso&src=solar", tab: "mix", grid: "caiso", mix: "forecast", keep: { mix: "forecast", src: "solar" } },
  { from: "/mix?view=duck&grids=spp&cal=07", tab: "mix", grid: "spp", mix: "duck", keep: { mix: "duck", cal: "07" } },
  // /mix/v2, /mix/clean, /mix/stress (session 133's views; session 237's one step) and /emissions
  { from: "/mix/v2", tab: "mix", grid: "us48", mix: "day", keep: { mix: "day" }, route: true },
  { from: "/mix/v2?grid=caiso&period=2026-04&vs=ercot", tab: "mix", grid: "caiso", mix: "day", keep: { period: "2026-04", vs: "ercot" }, route: true },
  { from: "/mix/clean", tab: "clean", grid: "us48", mix: "clean", route: true },
  { from: "/mix/clean?grid=caiso&year=2026", tab: "clean", grid: "caiso", mix: "clean", keep: { year: "2026" }, route: true },
  { from: "/mix/stress", tab: "mix", grid: "us48", mix: "stress", keep: { mix: "stress" }, route: true },
  { from: "/mix/stress?grid=nyiso&year=2025", tab: "mix", grid: "nyiso", mix: "stress", keep: { year: "2025" }, route: true },
  { from: "/emissions", tab: "clean", grid: "us48", mix: "clean", route: true },
  // the seven grid pages: the grid on the opening tab (Mix, which holds the Now view's blocks); a word after is carried
  ...T.GRID_CHOICES.filter((g) => g.slug !== "us48").map((g) => ({ from: `/grid/${g.slug}`, tab: "mix", grid: g.slug, node: g.ba, mix: "now", route: true })),
  { from: "/grid/ercot?view=network", tab: "network", grid: "ercot", node: "ERCO", route: true },
  { from: "/grid/caiso?view=clean", tab: "clean", grid: "caiso", mix: "clean" },
  // /ask: the Ask panel beside the grid named (else the Lower 48), on the opening tab, the question placed in the box
  { from: "/ask", tab: "mix", grid: "us48", ask: true, route: true },
  { from: "/ask?grid=ercot&q=What+was+the+peak%3F", tab: "mix", grid: "ercot", ask: true, keep: { q: "What was the peak?" }, route: true },
  { from: "/ask?grid=CISO", tab: "mix", grid: "caiso", ask: true },
  // the old view words, on /grid itself (OLD_VIEWS: now, exchange, ask; mix=clean; shape=gravity)
  { from: "/grid?grid=ercot&view=now", tab: "mix", grid: "ercot", mix: "now", route: true },
  { from: "/grid?grid=caiso&view=now&mixp=month", tab: "mix", grid: "caiso", mix: "now", keep: { mixp: "month" }, route: true },
  { from: "/grid?grid=ercot&view=exchange", tab: "gravity", grid: "ercot", route: true },
  { from: "/grid?grid=us48&view=exchange", tab: "gravity", grid: "us48", node: null, route: true },
  { from: "/grid?grid=ercot&view=ask", tab: "mix", grid: "ercot", ask: true, route: true },
  { from: "/grid?grid=nyiso&view=ask&q=What+was+the+highest+demand+this+week%3F", tab: "mix", grid: "nyiso", ask: true, keep: { q: "What was the highest demand this week?" }, route: true },
  { from: "/grid?grid=caiso&ask=1", tab: "mix", grid: "caiso", ask: true, route: true },
  { from: "/grid?grid=nyiso&view=mix&mix=clean", tab: "clean", grid: "nyiso", mix: "clean", route: true },
  { from: "/grid?grid=ercot&view=network&shape=gravity", tab: "gravity", grid: "ercot", keep: { shape: "gravity" }, route: true },
  { from: `/grid?grid=ercot&view=network&shape=gravity&net=day&t=${DAY}`, tab: "gravity", grid: "ercot", day: DAY, keep: { net: "day", t: DAY } },
  // the old grid words: the network's EIA-930 code, the mix's ba, the first of the mix's grids, a node of none of the eight
  { from: "/grid?grid=ERCO&view=network", tab: "network", grid: "ercot", node: "ERCO", route: true },
  { from: "/grid?grid=SWPP", tab: "mix", grid: "spp", node: "SWPP", mix: "now" },
  { from: "/grid?view=mix&ba=erco", tab: "mix", grid: "ercot", mix: "now", keep: { ba: "erco" }, route: true },
  { from: "/grid?view=mix&ba=ciso&state=CA", tab: "mix", grid: "caiso", mix: "now", route: true },
  { from: "/grid?view=mix&mix=day&grids=pjm,miso", tab: "mix", grid: "pjm", mix: "day", keep: { grids: "pjm,miso" }, route: true },
  { from: "/grid?view=network&grid=BPAT", tab: "network", grid: "us48", node: "BPAT", route: true },
  { from: `/grid?grid=ercot&view=network&net=day&t=${DAY}&node=BPAT`, tab: "network", grid: "ercot", node: "BPAT", day: DAY, keep: { node: "BPAT" }, route: true },
  { from: "/grid?view=network&node=ERCO", tab: "network", grid: "ercot", node: "ERCO" },
  { from: "/grid?grid=ercot&view=network&net=day&t=2021-02-15T05:00", tab: "network", grid: "ercot", day: null },   // t not a date: no day
  { from: "/grid?grid=nowhere&view=nothing", tab: "mix", grid: "us48", node: null, mix: "now", route: true },          // an address it does not understand
];

// ------------------------------------------------------------------ the tests
await test("the redirects are read from next.config.ts and every rule to /grid has a plain source this test can match", () => {
  assert.ok(GRID_RULES.length >= 18, `${GRID_RULES.length} rules to /grid`);
  for (const r of GRID_RULES) {
    assert.match(r.source, /^\/[a-z0-9/]+$/, `${r.source}: a plain address (no :param), so this test matches it as Next does`);
    assert.equal(r.permanent, true, `${r.source} is permanent`);
    for (const h of r.has ?? []) assert.equal(h.type, "query", `${r.source}: its condition is on the query`);
  }
  // a rule with a condition stands before the rule without one for the same source, or it would never be reached
  for (const [i, r] of RULES.entries()) if (r.has) assert.ok(RULES.slice(i + 1).some((x) => x.source === r.source && !x.has), `${r.source} has a fallback after it`);
  // and every address the Grid tool came from is one of them
  for (const s of ["/network", "/network/v3", "/mix", "/mix/v2", "/mix/clean", "/mix/stress", "/emissions", "/grid/ercot", "/grid/caiso", "/grid/pjm", "/grid/miso", "/grid/nyiso", "/grid/isone", "/grid/spp"])
    assert.ok(GRID_RULES.some((r) => r.source === s), `${s} redirects to /grid`);
  // /grid/caiso/alerts (the Flex Alert scorecard) is its own page
  assert.equal(redirectOf("/grid/caiso/alerts"), null);
});

await test("the Next merge this test models: the destination's words over the request's (prepareDestination), and /ask's own redirect", () => {
  // read against the installed Next where there is one (site/node_modules; a worktree without it skips this part)
  const file = path.join(SITE, "node_modules", "next", "dist", "shared", "lib", "router", "utils", "prepare-destination.js");
  if (fs.existsSync(file)) {
    const nx = fs.readFileSync(file, "utf-8");
    assert.match(nx, /parsedDestination\.query = \{\s*\.\.\.args\.query,\s*\.\.\.parsedDestination\.query\s*\}/, "Next merges the request's query under the destination's");
    assert.ok(nx.includes("new RegExp(`^${hasItem.value}$`)"), "a query condition is anchored");
    assert.ok(nx.includes("value.slice(-1)[0].match(matcher)"), "a repeated word is matched on its last value");
  } else console.log("     (no site/node_modules: the Next source is not read here)");
  const ask = src("app", "ask", "page.tsx");
  assert.ok(ask.includes('const base = gridHref(gridBy(grid)?.slug ?? "us48");'));
  assert.ok(ask.includes('redirect(`${base}${base.includes("?") ? "&" : "?"}ask=1${q ? `&q=${encodeURIComponent(q.slice(0, 500))}` : ""}`);'));
  const page = src("app", "grid", "page.tsx");
  for (const line of ["const p = gridPick(sp);",
    'const mixQuery: Query = { ...sp, view: view === "clean" ? "clean" : one(sp.mix), grid: undefined };',
    'if (grid.slug === "us48") { if (!one(sp.ba)) mixQuery.ba = "us48"; } else if (!one(sp.grids)) mixQuery.grids = grid.slug;',
    "const mix = { ...choiceOf(mixQuery),"]) assert.ok(page.includes(line), `app/grid/page.tsx: ${line}`);
});

await test("every old address opens the tab that holds its blocks, with the grid it named, and keeps the view's own words", () => {
  const failed = [];
  for (const c of CASES) {
    const l = land(c.from);
    assert.equal(l.pathname, "/grid", `${c.from} lands on /grid`);
    const { p, mix } = pageOf(l.query);
    const got = { tab: p.view, grid: p.grid.slug, node: p.node, day: p.day, ask: p.ask, mix };
    // a case that names no node accepts the page's; every case that asks for a day names it; mix is named on the Mix and Clean tabs
    const want = { tab: c.tab, grid: c.grid, node: "node" in c ? c.node : got.node, day: c.day ?? null, ask: c.ask ?? false, mix: "mix" in c ? c.mix : got.mix };
    if ((c.tab === "mix" || c.tab === "clean") && !("mix" in c) && !c.ask) failed.push(`${c.from}: the case names no mix view`);
    try { assert.deepEqual(got, want); } catch { failed.push(`${c.from}: got ${JSON.stringify(got)}, want ${JSON.stringify(want)}`); }
    for (const [k, v] of Object.entries(c.keep ?? {})) if (one(l.query[k]) !== v) failed.push(`${c.from}: ${k}=${one(l.query[k])}, want ${v}`);
    // Next carries every word of the old address; only view is the tool's own and is rewritten (as net or mix, or the tab)
    if (l.rule !== null && l.rule !== "ask")
      for (const [k, v] of Object.entries(queryOf(c.from.split("?")[1] ?? ""))) if (k !== "view" && one(l.query[k]) !== one(v)) failed.push(`${c.from}: ${k} not carried`);
    // the network's own view word reaches the network as its view (netFromPage), and its grid word as its node
    if (got.tab === "network" || got.tab === "gravity") {
      const own = new URLSearchParams(T.netFromPage(`?${new URLSearchParams(Object.entries(l.query).map(([k, v]) => [k, one(v)]))}`, p.node).slice(1));
      if ((one(l.query.net) ?? null) !== own.get("view")) failed.push(`${c.from}: the network reads view=${own.get("view")}`);
      if (p.node !== own.get("grid")) failed.push(`${c.from}: the network opens ${own.get("grid")}, the page ${p.node}`);
    }
  }
  assert.deepEqual(failed, []);
});

await test("every rule to /grid, every old view word and every grid of the eight is reached by a case", () => {
  const hit = new Set(CASES.map((c) => land(c.from).rule));
  for (const [i, r] of RULES.entries()) if (toGrid(r.destination)) assert.ok(hit.has(i), `${r.source}${r.has ? ` (${JSON.stringify(r.has)})` : ""} has a case`);
  for (const w of Object.keys(T.OLD_VIEWS)) assert.ok(CASES.some((c) => c.from.includes(`view=${w}`)), `view=${w} has a case`);
  for (const w of ["mix=clean", "shape=gravity", "grid=ERCO", "ba=erco", "grids=pjm,miso", "node=BPAT", "mixp=month", "net=day", "shape=map", "q="])
    assert.ok(CASES.some((c) => c.from.includes(w)), `${w} has a case`);
  for (const g of T.GRID_CHOICES) assert.ok(CASES.some((c) => c.grid === g.slug), `${g.slug} is landed on`);
  for (const [v] of T.GRID_VIEWS) assert.ok(CASES.some((c) => c.tab === v), `the ${v} tab is landed on`);
});

await test("a repeated word: the destination's value stands whatever the request held, and the page reads the first", () => {
  // Next keeps one value for a word the destination writes; a host that appended the request's after it would still be read by one(), the first
  const l = land("/network?view=day&view=live&grid=ERCO");
  assert.equal(l.query.view, "network");
  assert.equal(l.query.net, "live", "the condition reads the last value of a repeated word");
  assert.deepEqual([T.gridPick({ view: ["network", "day"], grid: "ERCO" }).view, T.gridPick({ view: ["clean", "mix"] }).view], ["network", "clean"]);
});

await test("gridHref round trips: an address written by gridHref reads back to the same grid and tab, its words kept", () => {
  for (const g of T.GRID_CHOICES) for (const [v] of T.GRID_VIEWS) {
    const href = T.gridHref(g.slug, v);
    const p = T.gridPick(queryOf(href.split("?")[1]));
    assert.deepEqual([p.grid.slug, p.view, p.named, p.ask, p.day], [g.slug, v, true, false, null], href);
    assert.equal(p.node, g.slug === "us48" ? null : g.ba, href);
    // the view's own words ride on the address and read back
    const more = v === "mix" ? { mixp: "month", q: "peak?" } : v === "clean" ? { year: "2024" } : { net: "day", t: DAY, node: "BPAT" };
    const h2 = T.gridHref(g.slug, v, more);
    const q2 = queryOf(h2.split("?")[1]);
    const p2 = T.gridPick(q2);
    assert.deepEqual([p2.grid.slug, p2.view], [g.slug, v], h2);
    for (const [k, val] of Object.entries(more)) assert.equal(q2[k], val, `${h2}: ${k}`);
    if (more.net) assert.deepEqual([p2.day, p2.node], [DAY, "BPAT"], h2);
    // the tabs and the picker the page draws (gridHref(grid, k), gridHref(slug, view))
    for (const [k] of T.GRID_VIEWS) assert.equal(T.gridPick(queryOf(T.gridHref(g.slug, k).split("?")[1])).view, k);
  }
  // the opening tab writes no view, the Gravity tab its shape word; gridHref with an empty word writes none
  assert.equal(T.gridHref("ercot"), "/grid?grid=ercot");
  assert.equal(T.gridHref("ercot", "gravity"), "/grid?grid=ercot&view=gravity&shape=gravity");
  assert.equal(T.gridHref("ercot", "network", { net: "", t: undefined }), "/grid?grid=ercot&view=network");
});

await test("the links the tool writes read back: the picker's carried day, the map's region link, the network's own writes", () => {
  const at = `?grid=ercot&view=gravity&shape=gravity&net=day&t=${DAY}`;
  for (const g of T.GRID_CHOICES) {
    for (const v of ["gravity", "network"]) {
      // session 1153: the picker carries the replay's day on the Gravity and Network tabs (lib/carry.ts KEEP_DAY)
      const href = carryWords(T.gridHref(g.slug, v), at, KEEP_DAY);
      const p = T.gridPick(queryOf(href.split("?")[1]));
      assert.deepEqual([p.grid.slug, p.view, p.day], [g.slug, v, DAY], href);
    }
    // session 1156: a grid clicked on the map opens its row on the Network tab, in the Map shape, the moment carried
    const link = carryMoment(T.gridHref(g.slug, "network", { shape: "map" }), `?view=day&t=${DAY}&grid=ERCO`);
    const q = queryOf(link.split("?")[1]);
    const p = T.gridPick(q);
    assert.deepEqual([p.grid.slug, p.view, p.day, q.shape], [g.slug, "network", DAY, "map"], link);
    // the network component writes through netToPage on the page's keep (app/grid/page.tsx), and the page reads it back
    const keepNet = T.gridHref(g.slug, "network").slice("/grid".length);
    const keepGravity = `?grid=${g.slug}&view=gravity`;
    for (const [keep, tab, own] of [[keepNet, "network", `?view=day&t=${DAY}&grid=BPAT&shape=map&prices=1`], [keepGravity, "gravity", `?view=day&t=${DAY}&shape=gravity`]]) {
      const page = T.netToPage(keep, own);
      const back = T.gridPick(queryOf(page.slice(1)));
      assert.deepEqual([back.grid.slug, back.view, back.day], [g.slug, tab, DAY], page);
      // and the network reads its own words back as it wrote them (its grid, on the Gravity tab, the page's node)
      const read = new URLSearchParams(T.netFromPage(page, back.node).slice(1));
      for (const [k, v] of new URLSearchParams(own.slice(1))) assert.equal(read.get(k), v, `${page}: ${k}`);
      if (tab === "network") assert.equal(back.node, "BPAT", page);
      else assert.equal(read.get("grid"), g.slug === "us48" ? null : g.ba, page);
    }
  }
  assert.equal(carryWords(T.gridHref("pjm", "mix"), "?grid=ercot&view=mix", KEEP_DAY), "/grid?grid=pjm", "no day, nothing carried");
});

await test("the route check lists every old address marked route", () => {
  const routes = src("scripts", "check-routes.mjs");
  const missing = CASES.filter((c) => c.route && !routes.includes(`"${c.from}"`)).map((c) => c.from);
  assert.deepEqual(missing, []);
});

// ------------------------------------------------------------------ session 1183: every panel in the address
// Each panel chains 077, 078 and 091 added has an anchor (lib/gridAnchors.ts) and an address that opens it with its own
// state: the address is the one the tool writes (gridHref), it opens the panel's tab and grid, each word of the panel's
// state is read back by the page as the panel reads it, and the route check lists the address with its anchor.
await test("every panel's address opens its tab and grid, written as gridHref writes it, its state read back", () => {
  const failed = [];
  for (const a of PANEL_ANCHORS) {
    const q = queryOf(a.address.split("?")[1] ?? "");
    const more = Object.fromEntries(Object.entries(q).filter(([k]) => k !== "grid" && k !== "view"));
    if (T.gridHref(a.grid, a.tab, more) !== a.address) failed.push(`${a.key}: ${a.address} is not gridHref's ${T.gridHref(a.grid, a.tab, more)}`);
    const l = land(a.address);
    if (l.rule !== null) failed.push(`${a.key}: ${a.address} is redirected`);
    const { p, mix } = pageOf(l.query);
    if (p.view !== a.tab || p.grid.slug !== a.grid) failed.push(`${a.key}: opens ${p.view}/${p.grid.slug}, want ${a.tab}/${a.grid}`);
    for (const w of a.state) {
      if (!(w in q)) { failed.push(`${a.key}: the address carries no ${w}`); continue; }
      if (w === "shape" && (q.shape === "gravity") !== (p.view === "gravity")) failed.push(`${a.key}: shape=${q.shape} on the ${p.view} tab`);
      if (w === "t" && p.day !== q.t) failed.push(`${a.key}: the day read is ${p.day}, the address ${q.t}`);
      if (w === "node" && p.node !== q.node) failed.push(`${a.key}: the node read is ${p.node}, the address ${q.node}`);
      if (w === "ask" && !p.ask) failed.push(`${a.key}: ask=1 does not open the Ask panel`);
      if (w === "mix" && mix !== q.mix) failed.push(`${a.key}: the mix view read is ${mix}, the address ${q.mix}`);
      if (w === "mixp" || w === "year") {
        const mq = { ...l.query, view: one(l.query.mix), grid: undefined };
        if (!one(l.query.grids)) mq.grids = p.grid.slug;
        const c = choiceOf(mq);
        if (w === "mixp" && c.mixp !== "month") failed.push(`${a.key}: mixp=month is not read (${c.mixp})`);
        if (w === "year" && c.year !== q.year) failed.push(`${a.key}: the year read is ${c.year}, the address ${q.year}`);
      }
      if (w === "net" && (p.view === "network" || p.view === "gravity")) {
        const own = new URLSearchParams(T.netFromPage(`?${new URLSearchParams(Object.entries(l.query).map(([k, v]) => [k, one(v)]))}`, p.node).slice(1));
        if (own.get("view") !== q.net) failed.push(`${a.key}: the network reads view=${own.get("view")}, the address net=${q.net}`);
      }
    }
  }
  assert.deepEqual(failed, []);
});

await test("each anchor is one id, never two panels', and every anchor has a panel's address", () => {
  const ids = Object.values(GRID_ANCHOR);
  assert.equal(new Set(ids).size, ids.length, "two panels share an anchor");
  for (const id of ids) assert.match(id, /^[a-z][a-z0-9-]*$/, `${id}: a plain id`);
  assert.deepEqual([...new Set(PANEL_ANCHORS.map((a) => a.key))].sort(), Object.keys(GRID_ANCHOR).sort());
  assert.deepEqual([anchorOf("mix", 0, "pjm"), anchorOf("mix", 1, "miso"), anchorOf("stressRamp", 2, "caiso")], ["mix-panel", "mix-panel-miso", "stress-ramp-caiso"]);
  assert.equal(panelAddress(PANEL_ANCHORS.find((a) => a.key === "mix")), "/grid?grid=ercot&mixp=month#mix-panel");
  // no anchor is an id the page already draws for something else (the older sections and controls of /grid)
  const older = ["ask", "ask-box", "today", "hourly", "monthly", "mix-table", "now-mix", "reliability", "day", "together", "years", "clean", "stress", "stress-netload", "supply", "history", "replay-day"];
  for (const id of ids) assert.ok(!older.includes(id), `${id} is an older id of the page`);
});

await test("the route check lists every panel's address with its anchor, and checks the anchor is on the page", () => {
  const routes = src("scripts", "check-routes.mjs");
  const missing = PANEL_ANCHORS.filter((a) => !routes.includes(`"${panelAddress(a)}"`)).map(panelAddress);
  assert.deepEqual(missing, []);
  assert.ok(routes.includes("GRID_ANCHORS") && routes.includes("id=\"${anchor}\""), "check-routes.mjs looks for the anchor's id in the page");
});

await test("the method note names each anchor with its panel", () => {
  const note = fs.readFileSync(path.join(SITE, "..", "docs", "methods", "grid_network.md"), "utf-8");
  for (const a of PANEL_ANCHORS) assert.ok(note.includes(`\`#${GRID_ANCHOR[a.key]}\``), `docs/methods/grid_network.md names #${GRID_ANCHOR[a.key]}`);
});

console.log(`${n} tests passed, ${CASES.length} addresses, ${PANEL_ANCHORS.length} panels`);
