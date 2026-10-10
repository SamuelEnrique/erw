// Energy Research Warehouse (ERW) site, session 180: the network as a map, in a real browser.
//
//   npm run build && npx next start -p 3180
//   node scripts/check-network-map.mjs [base-url] [phone-screenshot.png]      (default http://localhost:3180)
//   node scripts/check-network-map.mjs capture <base-url> <out.json>          the default view, for a before and after
//   node scripts/check-network-map.mjs compare <before.json> <after.json>     exit 1 when the default view differs
//
// The page is in review, so every check is made in the internal view. No model call; the only requests are to the site
// under test. What is checked:
//   pure      the address's word for the shape (lib/networkMap.ts): "network" is never written, "map" comes after the
//             view's own query, and version 3's addresses read exactly as they did
//   default   /network opens as the network, as before: a bare address, the 3D canvas, the toggle at the top with
//             "Network" pressed, no map in the page
//   toggle    "Map" shows the map's frame in place of the canvas and writes shape=map to the address; "Network" brings
//             the canvas back and takes it off; a shared address of version 3 with shape=map restores its view, its day
//             and its grid on the map; without it, on the network; a word it does not know is the network
//   held      what the map draws is what the boundary file holds: when the site has no file
//             (public/network/ba_boundaries.json) the frame says so and draws no region; when it has one, the regions
//             drawn are the file's matched grids, one each
//   drawing   with the test's own file of made-up squares (tests/fixtures/session180, handed to the page in place of the
//             boundary file; never shipped, never on a page a person opens): a region per matched grid and no other, the
//             smaller on top of the larger it sits inside, each tie that has both ends drawn from its exporter to its
//             importer; hovering a region names it; clicking it opens the same panel the network opens for that grid,
//             word for word; a day of the replay with another carbon intensity changes the region's color, and a grid
//             with no intensity that day is grey
//   phone     at 390 px: the toggle is reachable, nothing is wider than the screen, the panel is under the map
// Exit 1 on a failure; "not proven" (exit 0) without a browser.
import fs from "node:fs";
import { withBrowser } from "./browser.mjs";
import { parseShape, withShape } from "../lib/networkMap.ts";
import { parseShared, sharedQuery } from "../lib/networkV3.ts";

const args = process.argv.slice(2);
const READY = `!!document.querySelector('[data-network-view][data-restored="1"]')`;

// ------------------------------------------------------------------ capture and compare: the default view, before and after
const CAPTURE = `(() => {
  const root = document.querySelector('[data-network-view]').parentElement;
  const page = root.parentElement.cloneNode(true);
  page.querySelectorAll('[data-shape-toggle], script').forEach((e) => e.remove());
  const g = document.querySelector('[aria-label^="A 3D network"]').__erwGraph;
  const gd = g.graphData();
  const end = (v) => (v && typeof v === 'object' ? v.id : v);
  return {
    address: window.location.pathname + window.location.search,
    html: page.outerHTML,
    scene: { nodes: gd.nodes.map((n) => [n.id, n.x, n.y, n.z]), links: gd.links.map((l) => [l.a, l.b, end(l.source), end(l.target), l.mw]) },
    spheres: gd.nodes.map((n) => { const o = n.__threeObj; const m = o && o.children[0] && o.children[0].material; return [n.id, m ? m.color.getHexString() : null, m ? m.opacity : null, o ? o.children.length : null]; }),
    built: document.querySelector('[data-network-source]')?.innerText ?? null,
  };
})()`;
if (args[0] === "capture") {
  const base = args[1].replace(/\/$/, "");
  const code = await withBrowser(async ({ go, evaluate, wait, unlock, sleep }) => {
    await unlock(base);
    await go(`${base}/network`);
    await wait(READY, 30000, "the page to be ready");
    await wait(`!!document.querySelector('canvas') && !!document.querySelector('[aria-label^="A 3D network"]').__erwGraph`, 30000, "the network's canvas");
    await sleep(3000);
    const c = await evaluate(CAPTURE);
    fs.writeFileSync(args[2], JSON.stringify(c, null, 1));
    console.log(`${args[2]}: ${c.html.length} characters of the page, ${c.scene.nodes.length} spheres, ${c.scene.links.length} ties; ${c.built}`);
    return 0;
  });
  process.exit(code === 0 ? 0 : 1);
}
if (args[0] === "compare") {
  const [a, b] = [args[1], args[2]].map((f) => JSON.parse(fs.readFileSync(f, "utf-8")));
  let diff = 0;
  for (const k of ["address", "html", "scene", "spheres"]) {
    const x = typeof a[k] === "string" ? a[k] : JSON.stringify(a[k]), y = typeof b[k] === "string" ? b[k] : JSON.stringify(b[k]);
    if (x === y) { console.log(`same  ${k} (${x.length} characters)`); continue; }
    diff += 1;
    let i = 0;
    while (i < x.length && x[i] === y[i]) i += 1;
    console.log(`DIFF  ${k}: ${x.length} against ${y.length} characters; first difference at ${i}\n      before: ${x.slice(Math.max(0, i - 80), i + 120)}\n      after:  ${y.slice(Math.max(0, i - 80), i + 120)}`);
  }
  console.log(`the data: before "${a.built}"\n          after  "${b.built}"`);
  console.log(diff ? `${diff} part(s) of the default view DIFFER` : "the default view is the same, before and after (the toggle left out of the comparison)");
  process.exit(diff ? 1 : 0);
}

// ------------------------------------------------------------------ the check
const base = (args[0] ?? "http://localhost:3180").replace(/\/$/, "");
const shotFile = args[1] ?? null;
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const read = (p) => JSON.parse(fs.readFileSync(new URL(p, import.meta.url), "utf-8"));

// pure
check(parseShape("") === "network" && parseShape("?view=day&t=2021-02-15") === "network" && parseShape("?shape=map") === "map" && parseShape("?shape=globe") === "network", "an address names the map only by shape=map; anything else is the network");
const v3q = sharedQuery({ view: "day", t: "2021-02-15", grid: "ERCO", batteries: false, prices: true, trace: true });
check(withShape(v3q, "network") === v3q && withShape("", "network") === "" && withShape("", "map") === "?shape=map" && withShape(v3q, "map") === `${v3q}&shape=map`, `the network adds nothing to an address; the map adds shape=map after the view's own query (${withShape(v3q, "map")})`);
check(JSON.stringify(parseShared(withShape(v3q, "map"))) === JSON.stringify(parseShared(v3q)), "version 3 reads a view from an address with shape=map exactly as it does without");

const fixture = read("../../tests/fixtures/session180/ba_boundaries_fixture.json");
const snap = read("../data/grid_network.json");
const y21 = read("../public/network/daily_2021.json");
const heldFile = fs.existsSync(new URL("../public/network/ba_boundaries.json", import.meta.url)) ? read("../public/network/ba_boundaries.json") : null;
const MAP = `(() => { const m = document.querySelector('[data-map-state]'); const t = document.querySelector('[data-shape-toggle]'); const d = document.querySelector('[data-network-view]');
  return { shape: t?.getAttribute('data-shape-toggle') ?? null, pressed: [...(t?.querySelectorAll('button[aria-pressed="true"]') ?? [])].map((b) => b.innerText.trim()).join(','),
    buttons: [...(t?.querySelectorAll('button') ?? [])].map((b) => b.innerText.trim()).join(','), state: m?.getAttribute('data-map-state') ?? null, regions: document.querySelectorAll('[data-region]').length,
    said: Number(m?.getAttribute('data-map-regions') ?? -1), matched: Number(m?.getAttribute('data-map-matched') ?? -1), flows: document.querySelectorAll('[data-flow]').length, canvas: !!document.querySelector('canvas'),
    view: d?.getAttribute('data-network-view'), t: d?.getAttribute('data-t'), panel: document.querySelector('[data-panel]')?.getAttribute('data-panel') ?? null, search: window.location.search,
    text: m?.innerText ?? '' }; })()`;
const press = (k) => `(() => { const b = document.querySelector('[data-shape-toggle] button[data-shape="${k}"]'); if (!b) return false; b.click(); return true; })()`;
const setDate = (v) => `(() => { const el = document.querySelector('#replay-day'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(el, '${v}');
  el.dispatchEvent(new Event('input', { bubbles: true })); el.dispatchEvent(new Event('change', { bubbles: true })); return true; })()`;
const centre = (id) => `(() => { const e = document.querySelector('[data-region="${id}"]'); if (!e) return null; e.scrollIntoView({ block: 'center' }); const b = e.getBoundingClientRect(); return { x: b.left + b.width / 2, y: b.top + b.height / 2 }; })()`;

const code = await withBrowser(async ({ go, evaluate, wait, unlock, sleep, errors, send }) => {
  await unlock(base);

  // default: the network, as before
  await go(`${base}/network`);
  await wait(READY, 30000, "the page to be ready");
  const gl = !(await evaluate(`document.body.innerText.includes('This browser cannot draw 3D')`));
  if (gl) await wait(`!!document.querySelector('canvas')`, 30000, "the network's canvas");
  let s = await evaluate(MAP);
  check(s.buttons === "Map,Network" && s.pressed === "Network" && s.shape === "network", `the toggle is at the top, "Map" and "Network", with Network pressed (${s.buttons}; pressed ${s.pressed})`);
  check(s.search === "" && s.state === null && s.regions === 0 && (s.canvas || !gl), `the page opens as the network: a bare address, ${gl ? "the 3D canvas" : "no 3D in this browser"}, no map in the page`);
  check(await evaluate(`(() => { const t = document.querySelector('[data-shape-toggle]'); const w = document.querySelector('[role="group"][aria-label="Watch"]'); return !!t && !!w && (t.compareDocumentPosition(w) & Node.DOCUMENT_POSITION_FOLLOWING) !== 0; })()`), "the toggle stands above the Watch buttons");

  // toggle: the map, and back
  await evaluate(press("map"));
  s = await wait(`(() => { const s = ${MAP}; return s.state && s.state !== 'loading' ? s : null; })()`, 20000, "the map's frame");
  check(s.shape === "map" && s.pressed === "Map" && !s.canvas && s.search === "?shape=map", `"Map" shows the map in place of the canvas and the address holds it (${s.search}; canvas ${s.canvas})`);
  // held: the page draws what the site's boundary file holds, and says so when there is none
  if (!heldFile) {
    check(s.state === "absent" && s.regions === 0 && s.said === 0 && s.matched === 0 && s.text.includes("The boundary file is not yet held") && s.text.includes("no region is drawn"),
      `the site holds no boundary file, and the map says so and draws no region (state ${s.state}, ${s.regions} regions): "${s.text.slice(0, 60)}..."`);
  } else {
    const want = heldFile.regions.filter((r) => snap.nodes.some((x) => x.id === r.id)).length;
    check(s.state === "held" && s.regions === want && s.said === want && want === heldFile.matched && s.matched === heldFile.matched, `the regions drawn (${s.regions}) are the boundary file's matched grids (${heldFile.matched}), one each`);
  }
  check(await evaluate(`!!document.querySelector('[data-map-key]') && document.body.innerText.includes('Carbon intensity of generation:') && !document.body.innerText.includes('Drag to rotate')`), "the key keeps the carbon scale and reads for a map, not for a 3D scene");
  await evaluate(press("network"));
  s = await wait(`(() => { const s = ${MAP}; return s.shape === 'network' && s.search === '' && (s.canvas || ${!gl}) ? s : null; })()`, 30000, "the network to come back");
  check(s.state === null && s.pressed === "Network" && s.search === "", `"Network" brings the canvas back and takes shape=map off the address`);

  // a shared address of version 3, with the shape and without
  await go(`${base}/network?view=day&t=2021-02-15&grid=ERCO&shape=map`);
  await wait(READY, 30000, "the shared view to be restored");
  s = await wait(`(() => { const s = ${MAP}; return s.view === 'day' && s.t === '2021-02-15' && s.panel === 'ERCO' && s.state && s.state !== 'loading' ? s : null; })()`, 30000, "the shared day, grid and map");
  check(s.shape === "map" && !s.canvas && s.search === "?view=day&t=2021-02-15&grid=ERCO&shape=map", `a shared address with shape=map restores its day and grid on the map, and the address stays as it was (${s.search})`);
  await evaluate(press("network"));
  s = await wait(`(() => { const s = ${MAP}; return s.shape === 'network' && s.search === '?view=day&t=2021-02-15&grid=ERCO' ? s : null; })()`, 30000, "the same view as the network");
  check(s.view === "day" && s.t === "2021-02-15" && s.panel === "ERCO", "back on the network the view, the day and the grid are the same, and the address is version 3's own");
  await go(`${base}/network?view=day&t=2021-02-15&grid=ERCO`);
  await wait(READY, 30000, "the shared view to be restored");
  s = await wait(`(() => { const s = ${MAP}; return s.view === 'day' && s.panel === 'ERCO' ? s : null; })()`, 30000, "the shared day and grid");
  check(s.shape === "network" && s.state === null && s.search === "?view=day&t=2021-02-15&grid=ERCO", "version 3's shared address without the shape opens on the network, the address unchanged");
  const netPanel = await evaluate(`document.querySelector('[data-panel]').innerText`);
  await go(`${base}/network?shape=globe`);
  await wait(READY, 30000, "the page to be ready");
  s = await evaluate(MAP);
  check(s.shape === "network" && s.state === null, "a shape the page does not know is the network");

  // drawing: the test's own made-up squares in place of the boundary file
  const inject = await send("Page.addScriptToEvaluateOnNewDocument", { source: `(() => { const real = window.fetch; const f = ${JSON.stringify(fixture)};
    window.fetch = (u, o) => (String(u).includes('/network/ba_boundaries.json') ? Promise.resolve(new Response(JSON.stringify(f), { status: 200, headers: { 'content-type': 'application/json' } })) : real(u, o)); })()` });
  await go(`${base}/network?view=day&t=2021-02-15&shape=map`);
  await wait(READY, 30000, "the page to be ready");
  s = await wait(`(() => { const s = ${MAP}; return s.state === 'held' && s.view === 'day' && s.t === '2021-02-15' ? s : null; })()`, 30000, "the fixture's map");
  const ids = fixture.regions.map((r) => r.id);
  const drawn = await evaluate(`[...document.querySelectorAll('[data-region]')].map((e) => e.getAttribute('data-region'))`);
  check(drawn.join(",") === ids.join(",") && s.said === ids.length && s.matched === fixture.matched, `a region for each matched grid of the file and no other, in the file's order (${drawn.length} drawn, ${fixture.matched} matched): ${drawn.join(" ")}`);
  const i15 = y21.days.indexOf("2021-02-15");
  const moving = y21.links.filter((l) => l.mw[i15] !== null && l.mw[i15] !== 0 && ids.includes(l.a) && ids.includes(l.b));
  const wantFlows = moving.map((l) => (l.mw[i15] > 0 ? `${l.a}>${l.b}` : `${l.b}>${l.a}`)).sort();
  const flows = (await evaluate(`[...document.querySelectorAll('[data-flow]')].map((e) => e.getAttribute('data-flow'))`)).sort();
  check(wantFlows.length > 0 && flows.join(",") === wantFlows.join(","), `each tie with both ends on the map is drawn from its exporter to its importer, as the day's file has it (${flows.join(" ")})`);
  check(await evaluate(`[...document.querySelectorAll('[data-flow]')].every((g) => g.querySelector('line[marker-end]') && g.querySelector('line.erw-flow-dash'))`), "every tie has an arrowhead at its importer and a moving dash");
  // the smaller inside the larger: BANC's square is inside CISO's, and is the one under the pointer
  let c = await evaluate(centre("BANC"));
  check(await evaluate(`document.elementFromPoint(${c.x}, ${c.y})?.getAttribute('data-region')`) === "BANC", "a balancing authority inside another is drawn on top of it (BANC over CISO in the fixture)");
  // hover names the region, as hovering a sphere names it
  c = await evaluate(centre("SWPP"));
  await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: c.x, y: c.y });
  const hov = await wait(`(() => { const h = document.querySelector('[data-map-hover]'); return h ? { id: h.getAttribute('data-map-hover'), text: h.innerText } : null; })()`, 5000, "the hover");
  check(hov.id === "SWPP" && hov.text === snap.nodes.find((x) => x.id === "SWPP").name, `hovering a region names the grid (${hov.text})`);
  // a click opens the same panel
  c = await evaluate(centre("ERCO"));
  for (const type of ["mousePressed", "mouseReleased"]) await send("Input.dispatchMouseEvent", { type, x: c.x, y: c.y, button: "left", clickCount: 1 });
  await wait(`document.querySelector('[data-panel]')?.getAttribute('data-panel') === 'ERCO'`, 10000, "ERCOT's panel from a click on its region");
  const mapPanel = await evaluate(`document.querySelector('[data-panel]').innerText`);
  check(mapPanel === netPanel, `clicking a region opens the same panel the network opens for that grid and day, word for word (${mapPanel.length} characters)`);
  const dims = await evaluate(`Object.fromEntries([...document.querySelectorAll('[data-region]')].map((e) => [e.getAttribute('data-region'), e.getAttribute('data-dim')]))`);
  const near = new Set(y21.links.filter((l) => l.a === "ERCO" || l.b === "ERCO").map((l) => (l.a === "ERCO" ? l.b : l.a)));
  check(ids.every((id) => dims[id] === (id === "ERCO" || near.has(id) ? "0" : "1")), "with a grid selected, it and its neighbours stay as they are and the rest is dimmed, as in the network");
  check((await evaluate(MAP)).search === "?view=day&t=2021-02-15&grid=ERCO&shape=map", "the address holds the grid chosen on the map");
  // the replay drives the colors: two days on which a grid's carbon intensity differs
  const fills = () => evaluate(`Object.fromEntries([...document.querySelectorAll('[data-region]')].map((e) => [e.getAttribute('data-region'), e.getAttribute('data-fill')]))`);
  const f1 = await fills();
  const other = y21.days.findIndex((d, i) => i > i15 + 20 && ids.some((id) => (y21.intensity[id]?.[i] ?? null) !== null && (y21.intensity[id]?.[i15] ?? null) !== null && Math.abs(y21.intensity[id][i] - y21.intensity[id][i15]) > 40));
  await evaluate(setDate(y21.days[other]));
  await wait(`document.querySelector('[data-network-view]')?.getAttribute('data-t') === '${y21.days[other]}'`, 20000, "the other day");
  const f2 = await fills();
  const moved = ids.filter((id) => f1[id] !== f2[id]);
  const differ = ids.filter((id) => (y21.intensity[id]?.[i15] ?? null) !== (y21.intensity[id]?.[other] ?? null));
  check(other > 0 && moved.length > 0 && moved.every((id) => differ.includes(id)), `the replay's day drives the colors: from 2021-02-15 to ${y21.days[other]}, ${moved.length} of ${ids.length} regions change color, each a grid whose carbon intensity differs between the two days`);
  const grey = ids.filter((id) => (y21.intensity[id]?.[other] ?? null) === null);
  check(ids.every((id) => (f2[id] === "#9a958c") === grey.includes(id)), `a region is grey exactly when its carbon intensity is not held for the day (${grey.length ? grey.join(" ") : "none that day"}); the others carry a color of the scale`);
  // playing moves the day on the map
  await evaluate(`(() => { const b = [...document.querySelectorAll('button')].find((x) => x.innerText.trim() === 'Play'); b.click(); return true; })()`);
  await sleep(1500);
  await evaluate(`(() => { const b = [...document.querySelectorAll('button')].find((x) => x.innerText.trim() === 'Pause'); if (b) b.click(); return true; })()`);
  const tNow = await evaluate(`document.querySelector('[data-network-view]').getAttribute('data-t')`);
  check(tNow > y21.days[other], `Play moves the map through the days (${y21.days[other]} to ${tNow})`);
  // a story on the map
  await evaluate(`(() => { const b = [...document.querySelectorAll('button')].find((x) => x.innerText.trim().startsWith('Texas during Uri')); b.click(); return true; })()`);
  s = await wait(`(() => { const s = ${MAP}; return s.view === 'uri_2021' && s.panel === 'ERCO' ? s : null; })()`, 30000, "the Uri story on the map");
  await evaluate(`(() => { const b = [...document.querySelectorAll('button')].find((x) => x.innerText.trim() === 'Pause'); if (b) b.click(); return true; })()`);
  check(s.state === "held" && s.regions === ids.length && s.shape === "map", "a story plays on the map: Texas during Uri opens ERCOT's panel with the map still shown");
  if (shotFile) {
    await evaluate(`window.scrollTo(0, Math.max(0, document.querySelector('[data-shape-toggle]').getBoundingClientRect().top + window.scrollY - 8))`);
    await sleep(600);
    const wide = shotFile.replace(/\.png$/, "_desktop.png");
    fs.writeFileSync(wide, Buffer.from((await send("Page.captureScreenshot", { format: "png" })).data, "base64"));
    console.log(`     ${wide}: the Uri story on the map at 1280 px, drawn from the test's made-up squares (not boundaries)`);
  }

  // phone
  await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
  await go(`${base}/network?grid=CISO&shape=map`);
  await wait(READY, 30000, "the page at a phone's width");
  await wait(`document.querySelector('[data-map-state]')?.getAttribute('data-map-state') === 'held' && !!document.querySelector('[data-panel]')`, 30000, "the map and the panel at a phone's width");
  const ph = await evaluate(`(() => { const r = (e) => e.getBoundingClientRect(); const t = [...document.querySelectorAll('[data-shape-toggle] button')].map(r); const m = r(document.querySelector('[data-map-state]')); const p = r(document.querySelector('[data-panel]'));
    return { scroll: document.documentElement.scrollWidth, client: document.documentElement.clientWidth, toggle: t.map((b) => [Math.round(b.left), Math.round(b.right), Math.round(b.height)]), mapW: Math.round(m.width), mapH: Math.round(m.height),
      mapBottom: Math.round(m.bottom), panelTop: Math.round(p.top), panelW: Math.round(p.width) }; })()`);
  check(ph.scroll <= ph.client + 1 && ph.toggle.every((b) => b[0] >= 0 && b[1] <= 390 && b[2] >= 30), `at 390 px nothing is wider than the screen (${ph.scroll} of ${ph.client}) and both toggle buttons are on it, ${ph.toggle.map((b) => b[2]).join(" and ")} px tall`);
  check(ph.mapW <= 390 && ph.mapW >= 320 && ph.mapH >= 190 && Math.abs(ph.mapW / ph.mapH - 975 / 610) < 0.06 && ph.panelTop >= ph.mapBottom && ph.panelW <= 390, `the map is ${ph.mapW} by ${ph.mapH} px, the whole country with no empty band, and the panel is under it, ${ph.panelW} px wide`);
  if (shotFile) {
    await evaluate(`window.scrollTo(0, Math.max(0, document.querySelector('[data-shape-toggle]').getBoundingClientRect().top + window.scrollY - 8))`);
    await sleep(600);
    const shot = await send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(shotFile, Buffer.from(shot.data, "base64"));
    console.log(`     ${shotFile}: the map at 390 px, drawn from the test's made-up squares (not boundaries)`);
  }
  await send("Page.removeScriptToEvaluateOnNewDocument", { identifier: inject.identifier });
  await send("Emulation.clearDeviceMetricsOverride");
  check(errors.length === 0, `no error in the page through all of it${errors.length ? `: ${errors.join(" | ").slice(0, 300)}` : ""}`);
  return bad ? 1 : 0;
});
if (code === null) { console.log("check-network-map: NOT PROVEN on this machine (no Chrome or Edge)"); process.exit(0); }
console.log(bad ? `${bad} of ${n} checks FAILED` : `the network as a map, in a browser: ${n} checks pass`);
process.exit(code);
