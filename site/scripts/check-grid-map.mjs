// Energy Research Warehouse (ERW) site, session 8601 (chain 504, 19 November 2026): the Grid tool's map of the
// balancing authorities, made whole, in a real browser.
//
//   npm run build && npx next start -p 3504
//   node scripts/check-grid-map.mjs [base-url] [screenshot-folder]        (default http://localhost:3504)
//
// The page is in review, so every check is made in the internal view. No model call; the only requests are to the site
// under test. scripts/check-network-map.mjs (session 180) holds what the map has always done (the toggle, the address,
// the file it draws, the panel); this file holds what session 8601 added:
//   pure      the reader of the whole country's boundary file (the contract's form, on the tests' own made-up squares),
//             the point inside a shape, the words of a tie's hover, the batteries' ring and the zoom's arithmetic
//   unopened  the network opens as before and has asked for no boundary file: the map loads only when it is chosen
//   speed     from the click on "Map" to the regions drawn and answering: under three seconds; the time is printed
//   same MW   every tie the map draws carries the megawatts and the direction the network's own scene holds for that
//             pair in that hour, and the map says how many ties it could not draw
//   one scale every region has exactly the color its sphere has
//   hovers    a region's hover gives its name and its figures, the same figures its panel gives; a tie's hover gives
//             both names, the megawatts, the hour and which side reported it
//   batteries the switch draws a ring on the map for each grid whose batteries are reported, and the key says so
//   a story   switched from the network to the map and back in the middle of a story, the hour is the same
//   zoom      the buttons, the wheel and a drag move and zoom the map; a drag opens no panel; Reset shows it whole
//   listed    every grid with no boundary in the file is named under the map, and a click on its name opens its panel
//   phone     at 390 px nothing scrolls sideways; two fingers zoom the map and one finger moves it
// Exit 1 on a failure; "not proven" (exit 0) without a browser.
import fs from "node:fs";
import path from "node:path";
import { withBrowser } from "./browser.mjs";
import { MAP_HOME, arcPath, batteryFill, clampMapView, derivedLabel, flowTip, insidePoint, insideRings, nearestLine, onTheLine, readGeoBoundaries, reportedBy, whole, zoomMapAt } from "../lib/networkMap.ts";

const base = (process.argv[2] ?? "http://localhost:3504").replace(/\/$/, "");
const shots = process.argv[3] ?? null;
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const read = (p) => JSON.parse(fs.readFileSync(new URL(p, import.meta.url), "utf-8"));
const same = (a, b) => JSON.stringify(a) === JSON.stringify(b);

// ------------------------------------------------------------------ pure
const fixture = read("../../tests/fixtures/session8601/ba_boundaries_contract_fixture.json");
const held = readGeoBoundaries(fixture);
check(held.state === "held" && same(held.file.regions.map((r) => r.id), ["MISO", "SWPP", "CISO", "PJM", "ERCO", "ZZZZ", "BANC"]), "the contract's file is read into one region a balancing authority, the largest first");
check(held.state === "held" && held.file.regions.every((r) => insideRings(r.point, r.rings)), "every region has a point inside its own shape");
const swpp = held.state === "held" ? held.file.regions.find((r) => r.id === "SWPP") : null;
check(!!swpp && !(swpp.point[0] > -100 && swpp.point[0] < -97 && swpp.point[1] >= 35.5 && swpp.point[1] <= 38.5), `a shape with a hole in its middle has its point outside the hole (${swpp?.point.join(", ")})`);
const pjm = held.state === "held" ? held.file.regions.find((r) => r.id === "PJM") : null;
check(!!pjm && pjm.rings.length === 2 && same(pjm.point, [-80, 39]), "a shape in two parts keeps both and has its point in the larger");
check(held.state === "held" && derivedLabel(held.file) === null && held.file.provenance.source === fixture.source && held.file.provenance.retrieved_utc === fixture.retrieved_at
  && same(held.file.nodes_without_shape.map((x) => x.id), ["NYIS", "ISNE"]) && held.file.shapes_without_node.length === 1, "the file keeps its source, its retrieval time and its two lists, and carries no derived label");
check(readGeoBoundaries({ ...fixture, source: "" }).state === "error" && readGeoBoundaries({ ...fixture, features: [{ properties: {}, geometry: null }] }).state === "error"
  && readGeoBoundaries({ held: false }).state === "error" && readGeoBoundaries(null).state === "error", "a file with no source, a feature with no code, or anything that is not the file is an error, never a partial drawing");
check(insidePoint([[[0, 0], [4, 0], [4, 4], [0, 4], [0, 0]]])?.join() === "2,2" && insidePoint([[[0, 0], [1, 0]]]) === null, "the point inside a plain square is its middle; a ring of two points has none");
const tip = (side, unit = "hour") => flowTip({ from: "ERCO", to: "SWPP", fromName: "ERCOT", toName: "Southwest Power Pool", mw: 219.6, when: "2026-11-17 04:00 UTC", unit, a: "ERCO", b: "SWPP", aName: "ERCOT", bName: "Southwest Power Pool", side });
check(tip(null).head === "ERCOT (ERCO) to Southwest Power Pool (SWPP)" && tip(null).lines[0] === "220 MW" && tip(null).lines[1] === "2026-11-17 04:00 UTC" && /The file does not mark which\.$/.test(tip(null).lines[2]),
  "a tie's hover: both names, the megawatts, the hour, and the rule when the file does not mark the side");
check(tip("first").lines[2] === "Reported by ERCOT (ERCO)." && tip("second").lines[2] === "Reported by Southwest Power Pool (SWPP): ERCOT (ERCO) filed nothing for this hour." && tip(null, "day").lines[0] === "220 MW on average over the day",
  "a tie's hover names the side that reported it when the file marks it, and a day's megawatts are an average");
check(reportedBy(undefined, 3) === null && reportedBy([3], 3) === "second" && reportedBy([2], 3) === "first", "which side reported: unknown without the file's mark, the second side in a marked frame, the first otherwise");
const lines = [{ from: [0, 0], to: [100, 0] }, { from: [40, 1], to: [60, 1] }, { from: [0, 50], to: [0, 60] }];
check(nearestLine([50, 0], lines)?.index === 0 && nearestLine([50, 0.9], lines)?.index === 1 && nearestLine([50, 0.9], lines)?.distance < 0.11 && nearestLine([-5, 0], lines)?.distance === 5 && nearestLine([1, 1], []) === null,
  "the hover takes the nearest line: of two ties that run together, each is reached on its own side, and a short one is not hidden under a long one");
check(onTheLine({ along: 0.5, length: 100 }, 8) && !onTheLine({ along: 0.05, length: 100 }, 8) && !onTheLine({ along: 0.97, length: 100 }, 8) && onTheLine({ along: 0.5, length: 6 }, 8) && !onTheLine({ along: 0.1, length: 6 }, 8),
  "a tie does not take the hover at its two ends, where a grid's ties meet and the grid answers; a short tie keeps its middle");
check(batteryFill(100, 100) === 1 && batteryFill(-100, 100) === 0.02 && batteryFill(0, 100) === 0.5 && batteryFill(50, 0) === 1, "the batteries' ring is full when discharging at the period's most, half at rest, nearly empty when charging at its most");
check(arcPath(10, 10, 5, 0.25) === "M10,5A5,5 0 0 1 15,10" && arcPath(10, 10, 5, 0.75) === "M10,5A5,5 0 1 1 5,10" && arcPath(10, 10, 5, 1).split("A").length === 3, "the ring's arc starts at the top and runs clockwise; a whole ring is two halves");
check(same(zoomMapAt(MAP_HOME, 2, 100, 100, 975, 610), { k: 2, x: -100, y: -100 }) && same(zoomMapAt({ k: 2, x: -100, y: -100 }, 0.25, 100, 100, 975, 610), MAP_HOME)
  && same(clampMapView({ k: 2, x: 500, y: -5000 }, 975, 610), { k: 2, x: 0, y: -610 }) && zoomMapAt(MAP_HOME, 100, 0, 0, 975, 610).k === 12,
  "the zoom keeps the point under the pointer, never zooms out past the whole map or in past twelve times, and never pulls the map off its frame");

// ------------------------------------------------------------------ the browser
const READY = `!!document.querySelector('[data-network-view][data-restored="1"]')`;
const press = (k) => `(() => { const b = document.querySelector('[data-shape-toggle] button[data-shape="${k}"]'); if (!b) return false; b.click(); return true; })()`;
const clickText = (t) => `(() => { const b = [...document.querySelectorAll('button')].find((x) => x.innerText.trim().startsWith(${JSON.stringify(t)})); if (!b) return false; b.click(); return true; })()`;
const T = `document.querySelector('[data-network-view]')?.getAttribute('data-t')`;
const FRAME = `(() => { const m = document.querySelector('[data-map-state]'); return m ? { state: m.getAttribute('data-map-state'), regions: document.querySelectorAll('[data-region]').length, flows: Number(m.getAttribute('data-map-flows')),
  all: Number(m.getAttribute('data-map-flows-all')), noShape: (m.getAttribute('data-map-no-shape') || '').split(',').filter(Boolean), zoom: Number(m.getAttribute('data-map-zoom')), derived: m.getAttribute('data-map-derived'),
  moved: document.querySelector('[data-map-moved]')?.getAttribute('transform') ?? '' } : null; })()`;
const SCENE = `(() => { const g = document.querySelector('[aria-label^="A 3D network"]').__erwGraph; const gd = g.graphData(); const end = (v) => (v && typeof v === 'object' ? v.id : v);
  return { links: gd.links.map((l) => [end(l.source), end(l.target), l.mw]), spheres: Object.fromEntries(gd.nodes.map((x) => { const m = x.__threeObj && x.__threeObj.children[0] && x.__threeObj.children[0].material; return [x.id, m ? m.color.getHexString() : null]; })) }; })()`;
// a point of the screen that the element itself answers at (a region can lie under a tie, or under a smaller region)
const TOP = `window.scrollTo(0, Math.max(0, document.querySelector('[data-shape-toggle]').getBoundingClientRect().top + window.scrollY - 8))`;
const pointOn = (sel) => `(() => { const e = document.querySelector(${JSON.stringify(sel)}); if (!e) return null; const b = e.getBoundingClientRect();
  for (let i = 1; i < 24; i += 1) for (let j = 1; j < 24; j += 1) { const x = b.left + (b.width * i) / 24, y = b.top + (b.height * j) / 24; if (document.elementFromPoint(x, y) === e) return { x, y }; } return null; })()`;
// a point of the screen on a tie's own line, a share of the way along it
const pointOnLine = (sel, share) => `(() => { const e = document.querySelector(${JSON.stringify(sel)}); if (!e) return null; const m = e.getScreenCTM();
  const q = new DOMPoint(Number(e.getAttribute('x1')) + (Number(e.getAttribute('x2')) - Number(e.getAttribute('x1'))) * ${share}, Number(e.getAttribute('y1')) + (Number(e.getAttribute('y2')) - Number(e.getAttribute('y1'))) * ${share}).matrixTransform(m); return { x: q.x, y: q.y }; })()`;
const hex = `((c) => { const s = document.createElement('span'); s.style.color = c; document.body.appendChild(s); const v = getComputedStyle(s).color.match(/\\d+/g).slice(0, 3).map((x) => Number(x).toString(16).padStart(2, '0')).join(''); s.remove(); return v; })`;
const WIDE = `document.documentElement.scrollWidth <= window.innerWidth`;

const code = await withBrowser(async ({ go, evaluate, wait, unlock, sleep, send, requests, errors }) => {
  const shot = async (name) => {
    // the page stands with the toggle at the top of the window through every check, so a point found stays where it was
    await evaluate(TOP);
    await sleep(300);
    if (!shots) return;
    fs.mkdirSync(shots, { recursive: true });
    fs.writeFileSync(path.join(shots, name), Buffer.from((await send("Page.captureScreenshot", { format: "png" })).data, "base64"));
    console.log(`     ${path.join(shots, name)}`);
  };
  const mouse = (type, p, more = {}) => send("Input.dispatchMouseEvent", { type, x: p.x, y: p.y, ...more });
  await unlock(base);

  // unopened: the network, and nothing asked of the map
  await go(`${base}/grid?view=network`);
  await wait(READY, 30000, "the page to be ready");
  const gl = !(await evaluate(`document.body.innerText.includes('This browser cannot draw 3D')`));
  if (!gl) { console.log("not proven here: this browser cannot draw the 3D network, so the two views cannot be set side by side"); return 0; }
  await wait(`!!document.querySelector('canvas') && !!document.querySelector('[aria-label^="A 3D network"]').__erwGraph`, 30000, "the network's canvas");
  await sleep(2500);
  const asked = () => requests.filter((r) => /\/grid\/boundaries|ba_boundaries\.json/.test(r.url)).map((r) => new URL(r.url).pathname);
  check(asked().length === 0 && (await evaluate(FRAME)) === null && (await evaluate(`document.querySelector('[data-shape-toggle]').getAttribute('data-shape-toggle')`)) === "network",
    "the tool opens on the network, and no boundary file has been asked for: the map loads only when it is chosen");
  const t0 = await evaluate(T);
  const scene = await evaluate(SCENE);
  await shot("network_1280.png");

  // speed: from the click to the regions drawn and answering
  const ms = await evaluate(`new Promise((done) => { const t = performance.now(); document.querySelector('[data-shape-toggle] button[data-shape="map"]').click();
    const look = () => { if (document.querySelectorAll('[data-region]').length) requestAnimationFrame(() => requestAnimationFrame(() => done(Math.round(performance.now() - t)))); else requestAnimationFrame(look); }; look(); })`);
  let f = await wait(`(() => { const s = ${FRAME}; return s && s.state === 'held' ? s : null; })()`, 20000, "the map");
  check(ms < 3000, `the map is drawn and answers ${ms} ms after "Map" is chosen (under 3,000)`);
  check(asked().includes("/grid/boundaries"), `the map asks for the whole country's boundary file when it is chosen (${asked().join(", ")})`);
  console.log(`     the file drawn: ${f.derived === "1" ? "the derived county file (the whole country's file is not held yet)" : "the whole country's boundary file"}; ${f.regions} regions, ${f.noShape.length} grids with no boundary`);
  check((await evaluate(T)) === t0, `the map shows the hour the network showed (${t0})`);
  await shot("map_1280.png");

  // same megawatts, same direction, as the network's own scene
  const drawn = await evaluate(`[...document.querySelectorAll('[data-flow]')].map((e) => [e.getAttribute('data-flow'), Number(e.getAttribute('data-mw'))])`);
  const regionIds = new Set(await evaluate(`[...document.querySelectorAll('[data-region]')].map((e) => e.getAttribute('data-region'))`));
  const want = scene.links.filter((l) => regionIds.has(l[0]) && regionIds.has(l[1])).map((l) => [`${l[0]}>${l[1]}`, l[2]]);
  const key = (x) => x.map((y) => `${y[0]}=${y[1]}`).sort().join(";");
  check(want.length > 0 && key(drawn) === key(want), `the ${drawn.length} ties on the map carry the megawatts and the direction of the network's scene for the same pair and hour (${scene.links.length} in the scene, ${want.length} with both ends on the map)`);
  check(f.all === scene.links.length && f.flows === drawn.length, `the map says how many ties it draws of how many (${f.flows} of ${f.all})`);

  // one scale: a region has its sphere's color
  const fills = await evaluate(`Object.fromEntries([...document.querySelectorAll('[data-region]')].map((e) => [e.getAttribute('data-region'), ${hex}(e.getAttribute('data-fill'))]))`);
  const off = Object.keys(fills).filter((id) => fills[id] !== scene.spheres[id]);
  check(Object.keys(fills).length === regionIds.size && off.length === 0, `every one of the ${regionIds.size} regions has exactly the color of its sphere${off.length ? ` (not: ${off.map((id) => `${id} ${fills[id]} against ${scene.spheres[id]}`).join(", ")})` : ""}`);
  check(await evaluate(`document.body.innerText.includes('Carbon intensity of generation:') && document.querySelectorAll('[data-map-key]').length === 1`), "one carbon scale under the map, the network's own");

  // hovers: a region
  const grid = regionIds.has("ERCO") ? "ERCO" : [...regionIds][0];
  await evaluate(TOP);
  await sleep(300);
  let p = await evaluate(pointOn(`[data-region="${grid}"]`));
  await mouse("mouseMoved", p);
  const hov = await wait(`(() => { const h = document.querySelector('[data-map-hover]'); return h ? { id: h.getAttribute('data-map-hover'), name: h.querySelector('[data-map-hover-name]').innerText, text: h.innerText, box: h.getBoundingClientRect().toJSON(), frame: document.querySelector('[data-map-state]').getBoundingClientRect().toJSON() } : null; })()`, 5000, "a region's hover");
  check(hov.id === grid && /Carbon intensity of generation: /.test(hov.text) && /Demand: /.test(hov.text) && /(Net (imports|exports): [\d,]+ MW over \d+ ties?|No tie reported this hour)/.test(hov.text) && /UTC/.test(hov.text) && /Tables: eia930_all_interchange/.test(hov.text),
    `a region's hover gives its name and its figures (${hov.text.replace(/\n/g, " | ")})`);
  check(hov.box.left >= hov.frame.left && hov.box.right <= hov.frame.right + 1, "the hover stands inside the map's frame");
  await shot("map_1280_hover_region.png");
  for (const type of ["mousePressed", "mouseReleased"]) await mouse(type, p, { button: "left", clickCount: 1 });
  await wait(`document.querySelector('[data-panel]')?.getAttribute('data-panel') === '${grid}'`, 10000, "the panel from a click on a region");
  const panel = await evaluate(`document.querySelector('[data-panel]').innerText`);
  const net = hov.text.match(/Net (imports|exports): ([\d,]+) MW/);
  const ci = hov.text.match(/Carbon intensity of generation: ([\d,.]+) kg/);
  check((!net || new RegExp(`Net ${net[1]} this hour\\s*${net[2]} MW`).test(panel)) && (!ci || panel.includes(`${ci[1]} kg CO2/MWh`)), `the hover's figures are the panel's (${net ? `net ${net[1]} ${net[2]} MW` : "no tie"}; ${ci ? `${ci[1]} kg CO2/MWh` : "intensity not held"})`);
  await evaluate(clickText("Close"));
  await wait(`!document.querySelector('[data-panel]')`, 5000, "the panel to close");

  // hovers: a tie (the largest the map draws)
  await evaluate(TOP);
  await sleep(300);
  // every tie answers somewhere along its own line: the hover takes the nearest line, so a short tie is not hidden under a long one
  const reach = [];
  for (const [pair] of drawn) {
    let ok = false;
    for (const share of [0.5, 0.3, 0.7, 0.15, 0.85]) {
      const q = await evaluate(pointOnLine(`[data-flow="${pair}"] line`, share));
      await mouse("mouseMoved", q);
      await sleep(30);
      if ((await evaluate(`document.querySelector('[data-map-flow-hover]')?.getAttribute('data-map-flow-hover') ?? null`)) === pair) { ok = true; break; }
    }
    if (!ok) reach.push(pair);
  }
  check(reach.length === 0, `every one of the ${drawn.length} ties can be reached by the mouse somewhere along its line${reach.length ? ` (not: ${reach.join(", ")})` : ""}`);
  const big = drawn.slice().sort((a, b) => b[1] - a[1])[0];
  p = await evaluate(pointOnLine(`[data-flow="${big[0]}"] line`, 0.5));
  await mouse("mouseMoved", { x: 5, y: 5 });
  await mouse("mouseMoved", p);
  const fh = await wait(`(() => { const h = document.querySelector('[data-map-flow-hover]'); return h ? { id: h.getAttribute('data-map-flow-hover'), mw: Number(h.getAttribute('data-mw')), text: h.innerText } : null; })()`, 5000, "a tie's hover");
  const [from, to] = big[0].split(">");
  const nameOf = await evaluate(`Object.fromEntries([...document.querySelectorAll('[data-region]')].map((e) => [e.getAttribute('data-region'), e.getAttribute('aria-label')]))`);
  check(fh.id === big[0] && fh.mw === big[1] && fh.text.includes(`${nameOf[from]} (${from}) to ${nameOf[to]} (${to})`) && fh.text.includes(`${whole(big[1])} MW`) && fh.text.includes(t0.slice(0, 13).replace("T", " ")) && /Reported by /.test(fh.text),
    `a tie's hover gives both names, the megawatts, the hour and who reported it (${fh.text.replace(/\n/g, " | ")})`);
  await shot("map_1280_hover_flow.png");
  await mouse("mouseMoved", { x: 5, y: 5 });

  // batteries on the map: "California's evening" turns the switch on over a whole Pacific day; the hours are stepped until one reports a battery
  await evaluate(clickText("California's evening"));
  await wait(`document.querySelector('[data-network-view]')?.getAttribute('data-network-view') === 'evening'`, 15000, "California's evening");
  await sleep(500);
  await evaluate(clickText("Pause"));
  const RINGS = `(() => { const r = [...document.querySelectorAll('[data-battery-ring]')]; return r.length ? r.map((e) => [e.getAttribute('data-battery-ring'), Number(e.getAttribute('data-battery-mw')), Number(e.getAttribute('data-battery-fill'))]) : null; })()`;
  let rings = null;
  for (let i = 0; i < 26 && !rings; i += 1) {
    rings = await evaluate(RINGS);
    if (!rings) { await evaluate(`(() => { const el = document.querySelector('input[type="range"]'); if (Number(el.value) >= Number(el.max)) return false; Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(el, String(Number(el.value) + 1)); el.dispatchEvent(new Event('input', { bubbles: true })); return true; })()`); await sleep(120); }
  }
  const sw = await evaluate(`(() => { const b = [...document.querySelectorAll('button[role="switch"]')].find((x) => x.innerText.startsWith('Batteries')); const s = getComputedStyle(b); return { text: b.innerText.trim(), color: s.color, ground: s.backgroundColor, on: b.getAttribute('aria-checked') }; })()`);
  check(sw.on === "true" && sw.text === "Batteries: on" && sw.color !== sw.ground, `the switch that is on can be read: its label is ${sw.color} on ${sw.ground} (it was ink on ink under the brand's button rule)`);
  const switchOn = await evaluate(`document.querySelector('button[role="switch"]').getAttribute('aria-checked') === 'true' && !!document.querySelector('[data-map-batteries]')`);
  if (!rings) console.log(`     not proven here: the live week holds no hour of that day with a battery reported (the switch is ${switchOn ? "on and the map's layer is there" : "off"})`);
  else {
    check(switchOn && rings.every((r) => regionIds.has(r[0]) && r[2] >= 0.02 && r[2] <= 1) && (await evaluate(`document.querySelector('[data-map-key]').innerText.includes('Ring: batteries reported')`)),
      `the Batteries switch draws a ring on the map for each grid whose batteries are reported in the hour (${rings.map((r) => `${r[0]} ${whole(r[1])} MW, ring ${Math.round(r[2] * 100)} percent full`).join(", ")}), and the key says what the ring is`);
    await evaluate(TOP);
    await sleep(300);
    p = await evaluate(pointOn(`[data-region="${rings[0][0]}"]`));
    await mouse("mouseMoved", { x: 5, y: 5 });
    await mouse("mouseMoved", p);
    const bh = await wait(`document.querySelector('[data-map-hover="${rings[0][0]}"]')?.innerText ?? null`, 5000, "the hover of a grid with a ring");
    check(new RegExp(`Batteries: (discharging|charging) ${whole(Math.abs(rings[0][1]))} MW`).test(bh), `the hover of a grid with a ring gives its batteries' megawatts (${bh.split("\n").find((l) => l.startsWith("Batteries"))})`);
    await shot("map_1280_batteries.png");
    await mouse("mouseMoved", { x: 5, y: 5 });
  }
  await evaluate(clickText("Close"));
  await evaluate(clickText("Batteries: on"));

  // a story, switched in its middle
  await evaluate(press("network"));
  await wait(`!!document.querySelector('canvas')`, 30000, "the network to come back");
  await evaluate(clickText("Texas during Uri"));
  await wait(`document.querySelector('[data-network-view]')?.getAttribute('data-network-view') === 'uri_2021'`, 30000, "the Uri story");
  await sleep(1600);
  await evaluate(clickText("Pause"));
  await evaluate(`(() => { const el = document.querySelector('input[type="range"]'); Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(el, String(Number(el.min) + 40)); el.dispatchEvent(new Event('input', { bubbles: true })); return true; })()`);
  await sleep(400);
  const mid = await evaluate(T);
  await evaluate(press("map"));
  await wait(`(() => { const s = ${FRAME}; return s && s.state === 'held'; })()`, 20000, "the map in the story");
  const onMap = await evaluate(T);
  const storyFlows = await evaluate(`document.querySelectorAll('[data-flow]').length`);
  await shot("map_1280_story_uri.png");
  await evaluate(press("network"));
  await wait(`!!document.querySelector('canvas')`, 30000, "the network again");
  check(mid === onMap && (await evaluate(T)) === mid && mid !== t0, `switched to the map in the middle of a story and back, the hour is the same (${mid}; ${storyFlows} ties on the map in that hour)`);

  // zoom and move, with the mouse
  await go(`${base}/grid?view=network&shape=map`);
  await wait(READY, 30000, "the page to be ready");
  await wait(`(() => { const s = ${FRAME}; return s && s.state === 'held'; })()`, 20000, "the map");
  await evaluate(TOP);
  await sleep(300);
  await evaluate(`document.querySelector('[data-zoom="in"]').click()`);
  f = await wait(`(() => { const s = ${FRAME}; return s.zoom > 1 ? s : null; })()`, 5000, "the zoom");
  check(f.zoom === 1.6, `"+" zooms the map (${f.zoom} times)`);
  p = await evaluate(`(() => { const b = document.querySelector('[data-map-state] svg').getBoundingClientRect(); return { x: b.left + b.width * 0.3, y: b.top + b.height * 0.5 }; })()`);
  await mouse("mouseWheel", p, { deltaX: 0, deltaY: -120 });
  f = await wait(`(() => { const s = ${FRAME}; return s.zoom > 1.6 ? s : null; })()`, 5000, "the wheel's zoom");
  const before = f.moved;
  await mouse("mousePressed", p, { button: "left", clickCount: 1 });
  for (let i = 1; i <= 6; i += 1) await mouse("mouseMoved", { x: p.x + 12 * i, y: p.y + 8 * i }, { button: "left", buttons: 1 });
  await mouse("mouseReleased", { x: p.x + 72, y: p.y + 48 }, { button: "left", clickCount: 1 });
  await sleep(300);
  f = await evaluate(FRAME);
  check(f.zoom === 2 && f.moved !== before && !(await evaluate(`!!document.querySelector('[data-panel]')`)), `the wheel zooms about the pointer (${f.zoom} times) and a drag moves the map without opening a panel (${before} to ${f.moved})`);
  await shot("map_1280_zoomed.png");
  await evaluate(`document.querySelector('[data-zoom="reset"]').click()`);
  f = await wait(`(() => { const s = ${FRAME}; return s.zoom === 1 ? s : null; })()`, 5000, "the reset");
  check(f.moved === "translate(0,0) scale(1)", "Reset shows the whole map again");

  // listed: the grids with no boundary
  const listed = await evaluate(`[...document.querySelectorAll('[data-listed]')].map((e) => [e.getAttribute('data-listed'), e.innerText.trim()])`);
  check(same(listed.map((x) => x[0]).sort(), f.noShape.slice().sort()) && listed.every((x) => x[1].length > 0), `every grid with no boundary in the file is named under the map (${listed.length}: ${listed.slice(0, 4).map((x) => x[1]).join("; ")}${listed.length > 4 ? "; ..." : ""})`);
  if (listed.length) {
    await evaluate(`document.querySelector('[data-listed="${listed[0][0]}"]').click()`);
    await wait(`document.querySelector('[data-panel]')?.getAttribute('data-panel') === '${listed[0][0]}'`, 8000, "the panel of a listed grid");
    check(true, `a click on a listed name opens its panel (${listed[0][1]})`);
  }
  check(errors.length === 0, `no error in the page${errors.length ? `: ${errors.slice(0, 2).join("; ")}` : ""}`);

  // phone: 390 px, fingers
  await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
  await send("Emulation.setTouchEmulationEnabled", { enabled: true, maxTouchPoints: 2 });
  await go(`${base}/grid?view=network&shape=map`);
  await wait(READY, 30000, "the page to be ready");
  await wait(`(() => { const s = ${FRAME}; return s && s.state === 'held'; })()`, 20000, "the map on a phone");
  check(await evaluate(WIDE), `at 390 px nothing is wider than the screen (${await evaluate(`document.documentElement.scrollWidth`)} px)`);
  await shot("map_390.png");
  const c = await evaluate(`(() => { const e = document.querySelector('[data-map-state] svg'); e.scrollIntoView({ block: 'center' }); const b = e.getBoundingClientRect(); return { x: b.left + b.width / 2, y: b.top + b.height / 2 }; })()`);
  const touch = (type, pts) => send("Input.dispatchTouchEvent", { type, touchPoints: pts.map((q, i) => ({ x: q.x, y: q.y, id: i + 1, radiusX: 2, radiusY: 2, force: 1 })) });
  // a finger has no hover: a tap on a tie shows the tie's figures
  const tie = await evaluate(`[...document.querySelectorAll('[data-flow]')].sort((a, b) => Number(b.getAttribute('data-mw')) - Number(a.getAttribute('data-mw')))[0].getAttribute('data-flow')`);
  const tp = await evaluate(pointOnLine(`[data-flow="${tie}"] line`, 0.5));
  await touch("touchStart", [tp]);
  await touch("touchEnd", []);
  const tapped = await wait(`document.querySelector('[data-map-flow-hover]')?.innerText ?? null`, 5000, "a tie's figures under a finger").catch(() => null);
  check(!!tapped && / MW/.test(tapped) && /Reported by /.test(tapped) && !(await evaluate(`!!document.querySelector('[data-panel]')`)) && (await evaluate(WIDE)), `a tap on a tie shows its figures and opens no panel (${(tapped ?? "nothing shown").split("\n").slice(0, 2).join(" | ")})`);
  await shot("map_390_tie.png");
  await evaluate(`document.querySelector('[data-map-state] svg').scrollIntoView({ block: 'center' })`);
  await touch("touchStart", [{ x: c.x - 20, y: c.y }, { x: c.x + 20, y: c.y }]);
  for (let i = 1; i <= 8; i += 1) await touch("touchMove", [{ x: c.x - 20 - 8 * i, y: c.y }, { x: c.x + 20 + 8 * i, y: c.y }]);
  await touch("touchEnd", []);
  await sleep(300);
  f = await evaluate(FRAME);
  check(f.zoom > 1.5, `two fingers moved apart zoom the map (${Math.round(f.zoom * 100) / 100} times)`);
  const was = f.moved;
  await touch("touchStart", [{ x: c.x, y: c.y }]);
  for (let i = 1; i <= 8; i += 1) await touch("touchMove", [{ x: c.x + 7 * i, y: c.y + 5 * i }]);
  await touch("touchEnd", []);
  await sleep(300);
  f = await evaluate(FRAME);
  check(f.moved !== was && (await evaluate(WIDE)), `one finger moves the zoomed map (${was} to ${f.moved}), and still nothing scrolls sideways`);
  await shot("map_390_zoomed.png");
  const sizes = await evaluate(`[...document.querySelectorAll('[data-map-zoom-buttons] button')].map((b) => { const r = b.getBoundingClientRect(); return [Math.round(r.width), Math.round(r.height)]; })`);
  check(sizes.length === 3 && sizes.every((s) => s[0] >= 32 && s[1] >= 32), `the three zoom buttons can be pressed with a finger (${sizes.map((s) => s.join(" by ")).join(", ")} px)`);
  return bad ? 1 : 0;
});
if (code === null) { console.log("not proven here: no browser on this machine (the pure checks above stand)"); process.exit(bad ? 1 : 0); }
console.log(`${n} checks, ${bad} failed`);
process.exit(code === 0 && !bad ? 0 : 1);
