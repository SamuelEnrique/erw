// Energy Research Warehouse (ERW) site, session 146: "Where the resources are" (/resources), on the built site.
//
//   npm run build && npx next start -p 3146
//   node scripts/check-resources.mjs [base-url]                (default http://localhost:3146)
//
// As HTML, in the internal view (the page is in review):
//   opens      200, its title, one sentence, the toggles in the owner's groups, then "What is built or planned"; no
//              "undefined", no NaN, no em dash; the Method note is there and closed; no hub or zone is named
//   face       the face holds none of the Method note's sentences and no method words
//   held       every layer of the manifest is a toggle; every expected layer not held is a greyed placeholder with a
//              reason on hover
//   files      a layer's file as the site serves it is the file the data side wrote, byte for byte
//   visitor    without the cookie the page, a layer's file and an overlay each answer the in-review page
// In a real browser:
//   draws      every toggle, switched on alone, changes the drawing, reports what it drew, and shows a legend that
//              carries the manifest's unit
//   grids      for every grid layer held, at four zooms (the address, the mouse wheel, the buttons, zoomed out): the level drawn is
//              the finest whose cells are 0.75 of a pixel wide or more, and the value on hover equals the file's value
//              at the pointer's longitude and latitude, decoded here with Buffer and placed with this file's own copy of
//              the plane; the hover carries the unit, the cell size, the vintage and the publisher; an empty cell reads
//              "no value in the source here"
//   shapes     a shape's hover names the feature under the pointer, with the vintage
//   overlays   the counts on the page equal the tables' own; a plant, a queue county ("a county, not a site") and a
//              datacenter each answer the pointer
//   address    an address restores the layers, the fuels, the zoom and the centre; a change is written to the address;
//              a bare address opens the contiguous states with one layer on
//   requests   the page asks nothing of any other site
// Exit 1 on a failure.
import { createHash } from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { env, withBrowser } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3146").replace(/\/$/, "");
let bad = 0, n = 0;
const check = (ok, what) => { n += 1; if (!ok) { bad += 1; console.log(`FAIL ${what}`); } else console.log(`ok   ${what}`); };
const DASH = String.fromCharCode(0x2014);

// the data side's files, read here from the disk
const manifestPath = path.join(here, "..", "data", "resources", "manifest.json");
if (!fs.existsSync(manifestPath)) { console.log("FAILED: site/data/resources/manifest.json is not on this machine: there is no layer to check"); process.exit(1); }
const MANIFEST = JSON.parse(fs.readFileSync(manifestPath, "utf-8"));
const DIRS = [path.join(here, "..", "data", "resources", "layers"), path.join(here, "..", "public", "resources-data")];
const diskPath = (f) => DIRS.map((d) => path.join(d, f)).find((p) => fs.existsSync(p)) ?? null;
const filesOf = (l) => [...(l.levels ?? []).map((v) => v.file), ...(l.other_extents ?? []).flatMap((x) => (x.levels ?? []).map((v) => v.file)), ...(typeof l.file === "string" ? [l.file] : [])];
const stem = (f) => f.replace(/\.[A-Za-z0-9]+$/, "");
const LAYERS = (MANIFEST.layers ?? []).filter((l) => filesOf(l).some((f) => diskPath(f)));
const MAPFILE = JSON.parse(fs.readFileSync(path.join(here, "..", "data", "map_v2.json"), "utf-8"));

// this file's own copy of the plane (lib/resources.ts is not imported: the check computes on its own)
const KX = Math.cos((37.5 * Math.PI) / 180), SPAN_LON = 60, SPAN_LAT = 27.5, MIN_CELL_PX = 0.75;
const scaleOf = (box, z) => Math.min(box.w / (SPAN_LON * KX), box.h / SPAN_LAT) * z;
const pixelOf = (box, view, lon, lat) => { const k = scaleOf(box, view.z); return [box.left + (lon - view.lon) * KX * k + box.w / 2, box.top + (view.lat - lat) * k + box.h / 2]; };
const levelAt = (levels, k) => { const s = [...levels].sort((a, b) => b.cell_deg - a.cell_deg); let pick = s[0]; for (const l of s) if (l.cell_deg * KX * k >= MIN_CELL_PX) pick = l; return pick; };
// a grid file, decoded with Buffer
const gridCache = new Map();
function gridOf(file) {
  if (!gridCache.has(file)) { const f = JSON.parse(fs.readFileSync(diskPath(file), "utf-8")); gridCache.set(file, { ...f, dlon: Math.abs(f.dlon), dlat: Math.abs(f.dlat), buf: Buffer.from(f.values, "base64") }); }
  return gridCache.get(file);
}
function storedAt(g, lon, lat) {
  const col = Math.floor((lon - g.lon0) / g.dlon), row = Math.floor((g.lat0 - lat) / g.dlat);
  if (col < 0 || row < 0 || col >= g.ncols || row >= g.nrows) return null;
  const s = g.buf.readUInt16LE(2 * (row * g.ncols + col));
  return s === (g.nodata ?? 65535) ? null : s;
}
const valueOf = (g, lon, lat) => { const s = storedAt(g, lon, lat); return s === null ? null : s * g.scale + (g.offset ?? 0); };
function inside(geom, lon, lat) {
  const rings = (rs) => { let inn = false; for (const r of rs) for (let i = 0, j = r.length - 1; i < r.length; j = i++) { if (r[i][1] > lat !== r[j][1] > lat && lon < ((r[j][0] - r[i][0]) * (lat - r[i][1])) / (r[j][1] - r[i][1]) + r[i][0]) inn = !inn; } return inn; };
  return geom.type === "Polygon" ? rings(geom.coordinates) : geom.type === "MultiPolygon" ? geom.coordinates.some(rings) : false;
}
/** A place well inside a shape: the middle of its widest run along the latitude where that run is widest. */
function placeIn(geom) {
  const polys = geom.type === "Polygon" ? [geom.coordinates] : geom.type === "MultiPolygon" ? geom.coordinates : [];
  let best = null;
  for (const poly of polys) {
    const ys = poly[0].map((c) => c[1]), lo = Math.min(...ys), hi = Math.max(...ys);
    for (let s = 1; s < 8; s++) {
      const lat = lo + ((hi - lo) * s) / 8, xs = [];
      for (const r of poly) for (let i = 0, j = r.length - 1; i < r.length; j = i++) if (r[i][1] > lat !== r[j][1] > lat) xs.push(((r[j][0] - r[i][0]) * (lat - r[i][1])) / (r[j][1] - r[i][1]) + r[i][0]);
      xs.sort((a, b) => a - b);
      for (let i = 0; i + 1 < xs.length; i += 2) if (!best || xs[i + 1] - xs[i] > best.w) best = { w: xs[i + 1] - xs[i], lon: (xs[i] + xs[i + 1]) / 2, lat };
    }
  }
  return best && inside(geom, best.lon, best.lat) ? best : null;
}

const unlock = await fetch(`${base}/internal/unlock?token=${encodeURIComponent(env("INTERNAL_COSTS_TOKEN") ?? "")}`, { redirect: "manual" });
const cookie = (unlock.headers.getSetCookie?.() ?? []).map((c) => c.split(";")[0]).join("; ");
if (!cookie) { console.log(`FAILED: ${base}/internal/unlock gave no cookie (INTERNAL_COSTS_TOKEN missing or not the server's)`); process.exit(1); }
const get = async (p, withCookie = true) => { const r = await fetch(base + p, { headers: withCookie ? { Cookie: cookie } : {}, redirect: "manual" }); return { status: r.status, type: r.headers.get("content-type") ?? "", buf: Buffer.from(await r.arrayBuffer()) }; };
const plain = (html) => html.replace(/<script[\s\S]*?<\/script>/gi, " ").replace(/<style[\s\S]*?<\/style>/gi, " ").replace(/<!--.*?-->/g, "").replace(/<[^>]+>/g, " ").replace(/&#x27;/g, "'").replace(/&quot;/g, '"').replace(/&amp;/g, "&").replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/\s+/g, " ");

// ---------------------------------------------------------------------------------------------------------------------
// As HTML
const page = await get("/resources");
const html = page.buf.toString("utf-8");
const from = html.indexOf("<h1"), noteAt = html.search(/<details[^>]*data-method-note="1"/), noteEnd = html.lastIndexOf("</details>");   // the menu has details of its own, above the page
const noteHtml = noteAt >= 0 && noteEnd > noteAt ? html.slice(noteAt, noteEnd) : "";
const faceHtml = from < 0 ? "" : html.slice(from, noteAt >= 0 ? noteAt : undefined) + (noteEnd > 0 ? html.slice(noteEnd) : "");
const face = plain(faceHtml.split(/<footer/)[0]), note = plain(noteHtml);
check(page.status === 200 && /<h1[^>]*>Where the resources are<\/h1>/.test(html) && !/\bundefined\b|NaN/.test(face + note) && !html.includes(DASH), '/resources opens as "Where the resources are", with no "undefined", no NaN and no em dash');
check(face.includes("The project map shows what is built; this shows the natural resource itself"), "one sentence under the title: what is built against the resource itself");
{
  const groups = [...faceHtml.matchAll(/data-group="([a-z_]+)"/g)].map((m) => m[1]);
  const want = ["wind", "solar", "geothermal", "oil_gas", "hydropower", "biomass", "offshore_wind"];
  check(want.every((g, i) => groups[i] === g) && faceHtml.indexOf('data-group="offshore_wind"') < faceHtml.indexOf("What is built or planned") && ["plants_operating", "plants_planned", "queue", "datacenters"].every((o) => faceHtml.includes(`data-toggle="${o}"`)),
    `the toggles are in the owner's groups and order (${groups.join(", ")}), then "What is built or planned": plants, queue, datacenters`);
}
check(/<details[^>]*data-method-note="1"/.test(html) && !/<details[^>]*\sopen/.test(html.slice(noteAt, noteAt + 300)) && note.includes("Method note") && LAYERS.every((l) => noteHtml.includes(`data-method-layer="${l.id}"`)),
  `the Method note is there, closed, with a section for each of the ${LAYERS.length} layers held`);
check(LAYERS.every((l) => !l.terms_quote || note.includes(plain(l.terms_quote).trim().slice(0, 60))) && LAYERS.every((l) => !l.publisher || note.includes(plain(l.publisher).trim())), "the Method note quotes each layer's terms and names its publisher");
{
  const sentences = note.split(/(?<=[.;:])\s+/).map((s) => s.trim()).filter((s) => s.split(" ").length >= 6);
  const found = sentences.filter((s) => face.includes(s));
  const WORDS = /siting study|before losses|limitation|assum|interpolat|simplified|smooth|reduced|squeezed|cosine|terms of use|not a plant|census of/i;
  check(sentences.length > 10 && found.length === 0 && !WORDS.test(face), `no method prose on the face: none of the Method note's ${sentences.length} sentences is on it${found.length ? ` (found "${found[0].slice(0, 80)}")` : ""}${WORDS.test(face) ? ` (found the word "${WORDS.exec(face)[0]}")` : ""}`);
}
check(!/\bhubs?\b|\bzones?\b/i.test(face), "no hub or zone is named on the face");
check(!/MISO|PJM/.test(face + note) || (/paused while terms are reviewed/.test(face + note) && /licensed source needed/.test(face + note)), "MISO and PJM are not named (or only with their two fixed phrases)");
{
  const toggles = [...faceHtml.matchAll(/data-toggle="([A-Za-z0-9_]+)"/g)].map((m) => m[1]);
  check(LAYERS.length > 0 && LAYERS.every((l) => toggles.includes(l.id)), `each of the ${LAYERS.length} layers of the manifest is a toggle (${LAYERS.map((l) => l.id).join(", ")})`);
  const missing = [...faceHtml.matchAll(/<label[^>]*title="([^"]*)"[^>]*data-missing="([^"]+)"[^>]*>([\s\S]*?)<\/label>/g)].map((m) => ({ title: m[1], key: m[2], inner: m[3] }));
  const named = (MANIFEST.missing ?? []).filter((x) => !LAYERS.some((l) => l.id === x.id));
  check(missing.every((m) => m.title.trim().length > 5 && /disabled=""/.test(m.inner) && plain(m.inner).includes("not held")) && named.every((x) => !x.reason || missing.some((m) => m.title === x.reason.replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/'/g, "&#x27;") || plain(m.title) === x.reason)),
    `each of the ${missing.length} layers not held is a greyed toggle that reads "not held", cannot be switched, and carries its reason on hover${named.length ? `; the manifest's ${named.length} reasons are shown as written` : ""}`);
}
{
  let files = 0, same = 0, first = "";
  for (const l of LAYERS) for (const f of filesOf(l)) {
    if (!diskPath(f)) continue;
    files += 1;
    const r = await get(`/resources/layer/${stem(f)}`);
    const a = createHash("sha256").update(r.buf).digest("hex"), b = createHash("sha256").update(fs.readFileSync(diskPath(f))).digest("hex");
    if (r.status === 200 && /json/.test(r.type) && a === b) same += 1; else first ||= `${f}: status ${r.status}, ${r.type}, ${a === b ? "same bytes" : "other bytes (the site was built before the data side's last write: build again)"}`;
  }
  check(files > 0 && same === files, `each of the ${files} files of the layers, as the site serves it in the internal view, is the file on the disk byte for byte${first ? ` (${first})` : ""}`);
}
{
  const v = await get("/resources", false), vh = v.buf.toString("utf-8");
  check(v.status === 200 && vh.includes('data-in-review="1"') && !vh.includes('data-map="1"') && !/data-toggle=/.test(vh), "without the cookie a visitor gets the in-review page, and nothing of the map");
  const f0 = filesOf(LAYERS[0])[0];
  const lf = await get(`/resources/layer/${stem(f0)}`, false), ov = await get("/resources/overlay/plants", false), oq = await get("/resources/overlay/queue", false);
  check([lf, ov, oq].every((r) => !/json/.test(r.type) && r.buf.toString("utf-8").includes('data-in-review="1"')), "a visitor who asks for a layer's file or an overlay gets the in-review page, not the data");
  const pub = await get(`/resources-data/${f0}`, false);
  console.log(`note: /resources-data/${f0} asked as a visitor answers ${pub.status}${pub.status === 200 ? ": the folder the data side writes is under public/, which is open to every visitor whatever the page's status (the page itself reads through the gate; the report says what to move)" : ""}`);
  const nf = await get("/resources/layer/no_such_layer");
  check(nf.status === 404, "a name that is no file of a layer answers 404");
}

// ---------------------------------------------------------------------------------------------------------------------
// In a real browser
const code = await withBrowser(async ({ go, evaluate, wait, unlock: open, send, requests, errors, sleep }) => {
  await open(base);
  // the unlock lands on the home page, whose charts load their library from its CDN: leave it before counting requests
  await go("about:blank");
  await sleep(800);
  const start = requests.length;
  const mapData = () => evaluate(`(() => { const el = document.querySelector('[data-map]'); const c = el.querySelector('canvas'); c.scrollIntoView({ block: 'center' }); const r = c.getBoundingClientRect(); return { z: Number(el.dataset.z), lon: Number(el.dataset.lon), lat: Number(el.dataset.lat), settled: Number(el.dataset.settled || 0), drawn: JSON.parse(el.dataset.drawn || '{}'), box: { left: r.left, top: r.top, w: r.width, h: r.height } }; })()`);
  const stateOf = (id) => evaluate(`(() => { const el = document.querySelector('[data-layer="${id}"]'); return el ? { state: el.dataset.state, level: el.dataset.level === '' || el.dataset.level === undefined ? null : Number(el.dataset.level), on: el.querySelector('input').checked } : null; })()`);
  const ready = async (ids, ms = 60000) => {
    await wait(`${JSON.stringify(ids)}.every((id) => { const el = document.querySelector('[data-layer="' + id + '"]'); return el && (el.dataset.state === 'ready' || el.dataset.state.startsWith('not read')); })`, ms, `the layers ${ids.join(", ")} to be read`);
    await sleep(450);
  };
  const settledAfter = async (t) => { await wait(`Number(document.querySelector('[data-map]').dataset.settled || 0) > ${t}`, 15000, "the view to come to rest"); await sleep(250); };
  const hash = () => evaluate(`(() => { const c = document.querySelector('[data-map] canvas'); const d = c.getContext('2d').getImageData(0, 0, c.width, c.height).data; let h = 0; for (let i = 0; i < d.length; i += 4) h = (Math.imul(h, 31) + d[i] + d[i + 1] * 3 + d[i + 2] * 7) | 0; return h; })()`);
  const hoverAt = async (x, y) => {
    await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: x + 30, y: y + 30 });
    await sleep(60);
    await send("Input.dispatchMouseEvent", { type: "mouseMoved", x, y });
    for (let i = 0; i < 25; i++) {
      await sleep(120);
      const h = await evaluate(`(() => { const h = document.querySelector('[data-hover]'); if (!h) return null; return { lon: Number(h.dataset.hoverLon), lat: Number(h.dataset.hoverLat), rows: [...h.querySelectorAll('[data-hover-layer]')].map((r) => ({ id: r.dataset.hoverLayer, value: r.dataset.hoverValue, feature: r.dataset.hoverFeature, empty: r.dataset.hoverEmpty, text: r.querySelector('[data-hover-text]').innerText, sub: r.querySelector('[data-hover-sub]').innerText })) }; })()`);
      if (h) return h;
    }
    return null;
  };
  const awayFromMap = () => send("Input.dispatchMouseEvent", { type: "mouseMoved", x: 5, y: 5 });
  const click = (sel) => evaluate(`(() => { const el = document.querySelector(${JSON.stringify(sel)}); if (!el) return false; el.click(); return true; })()`);

  // the bare address
  await go(`${base}/resources`);
  await wait(`!!document.querySelector('[data-map] canvas') && Number(document.querySelector('[data-map]').dataset.settled || 0) > 0`, 30000, "the map");
  const firstWant = (LAYERS.find((l) => /wind/.test(l.group) && !/offshore/.test(l.group) && /speed/i.test(`${l.id} ${l.title}`)) ?? LAYERS[0]).id;
  await ready([firstWant]);
  {
    const m = await mapData(), onNow = await evaluate(`[...document.querySelectorAll('[data-toggle]')].filter((e) => e.checked).map((e) => e.dataset.toggle)`);
    check(m.z === 1 && m.lon === -95.75 && m.lat === 37.25 && onNow.length === 1 && onNow[0] === firstWant && (await evaluate("location.search")) === "" && (m.drawn[firstWant] ?? 0) > 0,
      `/resources alone opens the contiguous states with one layer on (${onNow.join(", ")}), and leaves the address as it was`);
  }

  // every toggle, alone
  await go(`${base}/resources?on=`);
  await wait(`Number(document.querySelector('[data-map]').dataset.settled || 0) > 0`, 30000, "the map with every layer off");
  await sleep(500);
  // reading a canvas's pixels a few times moves it to the browser's other way of drawing, whose edges differ by a
  // shade: read three times, draw once more (a toggle on and off), and only then take the drawing with nothing on
  await hash(); await hash(); await hash();
  await click(`[data-toggle="${LAYERS[0].id}"]`);
  await ready([LAYERS[0].id]);
  await click(`[data-toggle="${LAYERS[0].id}"]`);
  await sleep(500);
  const empty = await hash();
  const overlays = ["plants_operating", "plants_planned", "queue", "datacenters"], left = [], offs = [];
  for (const id of [...LAYERS.map((l) => l.id), ...overlays]) {
    const l = LAYERS.find((x) => x.id === id);
    const t0 = (await mapData()).settled;
    await click(`[data-toggle="${id}"]`);
    await ready([id]);
    await settledAfter(t0);
    const st = await stateOf(id), m = await mapData(), h = await hash();
    const legendKey = l ? id : id.startsWith("plants") ? "plants" : id;
    const legend = await evaluate(`(() => { const el = document.querySelector('[data-legend="${legendKey}"]'); return el ? { unit: el.dataset.unit, text: el.innerText } : null; })()`);
    const unitOk = l ? legend && legend.unit === (l.unit ?? "") && (!l.unit || legend.text.includes(l.unit)) : !!legend;
    check(st?.state === "ready" && h !== empty && (m.drawn[id] ?? 0) > 0 && unitOk, `${id}: switched on alone it is read, changes the drawing (${m.drawn[id] ?? 0} ${l?.kind === "grid" ? "cells" : "marks"} in view) and shows its legend${l ? ` in the manifest's unit (${l.unit || "no unit"})` : ""}${st?.state !== "ready" ? ` (state: ${st?.state})` : ""}${!unitOk ? ` (legend: ${JSON.stringify(legend)})` : ""}`);
    await click(`[data-toggle="${id}"]`);
    await sleep(500);
    const off = await hash();
    offs.push(off);
    if (h === off) left.push(id);
  }
  check(left.length === 0 && new Set(offs).size === 1, `each toggle, switched off again, takes its marks off the map, and the map with nothing on is the same picture after each (${new Set(offs).size} ${new Set(offs).size === 1 ? "picture" : "pictures"} over ${offs.length} toggles)${left.length ? ` (still drawn: ${left.join(", ")})` : ""}`);

  // grids: the value under the pointer, at three zooms
  for (const l of LAYERS.filter((x) => x.kind === "grid")) {
    const levels = (l.levels ?? []).filter((v) => diskPath(v.file));
    const fine = gridOf([...levels].sort((a, b) => a.cell_deg - b.cell_deg)[0].file);
    // the cell of the finest level that holds a value, nearest the middle of the grid, valid at every level
    const midLon = fine.lon0 + (fine.ncols * fine.dlon) / 2, midLat = fine.lat0 - (fine.nrows * fine.dlat) / 2;
    let target = null, bestD = Infinity;
    for (let row = 0; row < fine.nrows; row += 1) for (let col = 0; col < fine.ncols; col += 1) {
      if (fine.buf.readUInt16LE(2 * (row * fine.ncols + col)) === (fine.nodata ?? 65535)) continue;
      const lon = fine.lon0 + (col + 0.5) * fine.dlon, lat = fine.lat0 - (row + 0.5) * fine.dlat, d = Math.hypot((lon - midLon) * KX, lat - midLat);
      if (d < bestD && levels.every((v) => storedAt(gridOf(v.file), lon, lat) !== null)) { bestD = d; target = { lon, lat }; }
    }
    // an empty place inside the grid, empty at every level
    const coarse = gridOf([...levels].sort((a, b) => b.cell_deg - a.cell_deg)[0].file);
    let hole = null; bestD = Infinity;
    for (let row = 1; row < coarse.nrows - 1; row += 1) for (let col = 1; col < coarse.ncols - 1; col += 1) {
      const lon = coarse.lon0 + (col + 0.3) * coarse.dlon, lat = coarse.lat0 - (row + 0.3) * coarse.dlat, d = Math.hypot((lon - target.lon) * KX, lat - target.lat);
      if (d < bestD && d > 1.5 && levels.every((v) => storedAt(gridOf(v.file), lon, lat) === null && storedAt(gridOf(v.file), lon + 0.21, lat) === null && storedAt(gridOf(v.file), lon - 0.21, lat - 0.21) === null)) { bestD = d; hole = { lon, lat }; }
    }
    const view0 = { z: 1, lon: Number((target.lon + 4.3).toFixed(4)), lat: Number((target.lat - 2.1).toFixed(4)) };
    await go(`${base}/resources?on=${l.id}&z=${view0.z}&c=${view0.lon},${view0.lat}`);
    await wait(`!!document.querySelector('[data-map] canvas') && Number(document.querySelector('[data-map]').dataset.settled || 0) > 0`, 30000, "the map");
    await ready([l.id]);
    const probe = async (label, place, wantEmpty) => {
      const m = await mapData(), k = scaleOf(m.box, m.z), want = levelAt(levels, k);
      await wait(`Number(document.querySelector('[data-layer="${l.id}"]').dataset.level) === ${want.cell_deg}`, 60000, `${l.id} to draw its ${want.cell_deg} degree level at zoom ${m.z.toFixed(2)}`).catch(() => {});
      await sleep(300);
      const st = await stateOf(l.id), g = gridOf(want.file);
      const [x, y] = pixelOf(m.box, m, place.lon, place.lat);
      const h = await hoverAt(x, y), row = h?.rows.find((r) => r.id === l.id);
      const file = valueOf(g, place.lon, place.lat), shown = row && row.value !== "" ? Number(row.value) : null;
      const where = h ? Math.hypot((h.lon - place.lon) * KX * k, (h.lat - place.lat) * k) : Infinity;
      const dec = Math.min(4, Math.max(0, Math.ceil(-Math.log10(g.scale) - 1e-9)));
      const okLevel = st?.level === want.cell_deg, okPlace = where <= 1.5;
      if (wantEmpty) {
        check(okLevel && okPlace && row && file === null && shown === null && row.empty === "1" && row.text === "no value in the source here", `${l.id}, ${label}: an empty cell reads "no value in the source here"${row ? "" : " (no hover row)"}${okLevel ? "" : ` (level ${st?.level}, wanted ${want.cell_deg})`}`);
        return;
      }
      const okValue = file !== null && shown !== null && Math.abs(shown - file) <= g.scale / 2 + 1e-9 && row.text === `${file.toLocaleString("en-US", { minimumFractionDigits: dec, maximumFractionDigits: dec })} ${l.unit ?? ""}`.trim();
      const okWords = row && row.sub.includes(`Cell of ${want.cell_deg} degrees`) && (!l.vintage || row.sub.includes(l.vintage)) && (!l.publisher || row.sub.includes(l.publisher));
      check(okLevel && okPlace && okValue && okWords, `${l.id}, ${label}: zoom ${m.z.toFixed(2)}, cells of ${want.cell_deg} degrees (${(want.cell_deg * KX * k).toFixed(2)} px); at ${place.lat.toFixed(4)} N ${(-place.lon).toFixed(4)} W the hover reads ${row?.text ?? "nothing"} and the file holds ${file === null ? "no value" : file.toFixed(dec)}; with the cell size, the vintage and the publisher`
        + `${okLevel ? "" : ` (level drawn ${st?.level})`}${okPlace ? "" : ` (the hover is ${where.toFixed(1)} px from the place)`}${okWords ? "" : ` (sub: ${row?.sub})`}`);
    };
    await probe("by the address", target, false);
    if (hole) await probe("by the address", hole, true); else console.log(`note: ${l.id}: no place inside the grid is empty at every level; the empty cell was not probed`);
    // the mouse wheel, at the target: the place stays under the pointer
    {
      const m = await mapData(), [x, y] = pixelOf(m.box, m, target.lon, target.lat);
      await send("Input.dispatchMouseEvent", { type: "mouseMoved", x, y });
      await send("Input.dispatchMouseEvent", { type: "mouseWheel", x, y, deltaX: 0, deltaY: -700 });
      await settledAfter(m.settled);
      const m2 = await mapData(), [x2, y2] = pixelOf(m2.box, m2, target.lon, target.lat);
      check(m2.z > m.z * 2 && Math.hypot(x2 - x, y2 - y) < 1.5, `${l.id}: the mouse wheel zooms from ${m.z.toFixed(2)} to ${m2.z.toFixed(2)} and keeps the place under the pointer`);
      await probe("after the mouse wheel", target, false);
    }
    // the buttons: in twice, east once
    {
      const m = await mapData();
      await awayFromMap();
      await click('[data-map-button="in"]'); await sleep(120); await click('[data-map-button="in"]'); await sleep(120); await click('[data-map-button="east"]');
      await settledAfter(m.settled);
      const m2 = await mapData();
      check(Math.abs(m2.z - m.z * 1.6 * 1.6) < 1e-6 * m2.z && m2.lon > m.lon && Math.abs(m2.lat - m.lat) < 1e-9, `${l.id}: the buttons zoom in twice (to ${m2.z.toFixed(2)}) and move east`);
      // the target may now be off the box: move back to it with the address the page wrote, then probe
      const [x, y] = pixelOf(m2.box, m2, target.lon, target.lat);
      if (x < m2.box.left + 20 || x > m2.box.left + m2.box.w - 20 || y < m2.box.top + 20 || y > m2.box.top + m2.box.h - 20) { await click('[data-map-button="west"]'); await settledAfter(m2.settled); }
      await probe("after the buttons", target, false);
      const m3 = await mapData(), search = await evaluate("location.search"), q = new URLSearchParams(search);
      check(q.get("on") === l.id && Math.abs(Number(q.get("z")) - m3.z) < 0.001 && Math.abs(Number((q.get("c") ?? "").split(",")[0]) - m3.lon) < 0.0001 && Math.abs(Number((q.get("c") ?? "").split(",")[1]) - m3.lat) < 0.0001, `${l.id}: the address holds the view after the zoom (${search})`);
      // zoomed out, by the address: the coarsest level, and still the cell under the pointer
      await go(`${base}/resources?on=${l.id}&z=0.5&c=${view0.lon},${view0.lat}`);
      await wait(`!!document.querySelector('[data-map] canvas') && Number(document.querySelector('[data-map]').dataset.settled || 0) > 0`, 30000, "the map");
      await ready([l.id]);
      await probe("zoomed out, by the address", target, false);
    }
  }

  // a part of a grid kept in files of its own (Alaska, Hawaii): read when the map shows it, and the same hover
  for (const l of LAYERS.filter((x) => x.kind === "grid")) for (const part of l.other_extents ?? []) {
    const levels = (part.levels ?? []).filter((v) => diskPath(v.file));
    if (!levels.length) continue;
    const fine = gridOf([...levels].sort((a, b) => a.cell_deg - b.cell_deg)[0].file);
    const midLon = fine.lon0 + (fine.ncols * fine.dlon) / 2, midLat = fine.lat0 - (fine.nrows * fine.dlat) / 2;
    let target = null, bestD = Infinity;
    for (let row = 0; row < fine.nrows; row += 1) for (let col = 0; col < fine.ncols; col += 1) {
      if (fine.buf.readUInt16LE(2 * (row * fine.ncols + col)) === (fine.nodata ?? 65535)) continue;
      const lon = fine.lon0 + (col + 0.5) * fine.dlon, lat = fine.lat0 - (row + 0.5) * fine.dlat, d = Math.hypot((lon - midLon) * KX, lat - midLat);
      if (d < bestD && levels.every((v) => storedAt(gridOf(v.file), lon, lat) !== null)) { bestD = d; target = { lon, lat }; }
    }
    if (!target) { console.log(`note: ${l.id}, ${part.extent}: no cell holds a value at every level; it was not probed`); continue; }
    await go(`${base}/resources?on=${l.id}&z=6&c=${(target.lon + 0.7).toFixed(4)},${(target.lat - 0.4).toFixed(4)}`);
    await wait(`!!document.querySelector('[data-map] canvas') && Number(document.querySelector('[data-map]').dataset.settled || 0) > 0`, 30000, "the map");
    const m0 = await mapData(), k = scaleOf(m0.box, m0.z), want = levelAt(levels, k), key = `${l.id}:${part.extent}`;
    await wait(`JSON.parse(document.querySelector('[data-map]').dataset.levels || '{}')[${JSON.stringify(key)}] === ${want.cell_deg}`, 60000, `${key} to draw its ${want.cell_deg} degree level`).catch(() => {});
    await sleep(300);
    const m = await mapData(), [x, y] = pixelOf(m.box, m, target.lon, target.lat), g = gridOf(want.file);
    const h = await hoverAt(x, y), row = h?.rows.find((r) => r.id === l.id);
    const file = valueOf(g, target.lon, target.lat), shown = row && row.value !== "" ? Number(row.value) : null;
    // the page's own record of the pyramids it holds a level of (the grid reader works off the page's thread, so
    // its requests are not among the page's own): this part, and no other part the map does not show
    const held = Object.keys(JSON.parse(await evaluate(`document.querySelector('[data-map]').dataset.levels || '{}'`)));
    const others = (l.other_extents ?? []).filter((o) => o !== part).map((o) => `${l.id}:${o.extent}`);
    check(row && file !== null && shown !== null && Math.abs(shown - file) <= g.scale / 2 + 1e-9 && row.sub.includes(`Cell of ${want.cell_deg} degrees`) && held.includes(key) && !held.some((a) => others.includes(a)),
      `${l.id}, ${part.extent}: its own files are read when the map shows it, and no other part's (${held.join(", ")}); at ${target.lat.toFixed(4)} N ${(-target.lon).toFixed(4)} W the hover reads ${row?.text ?? "nothing"} and the file holds ${file === null ? "no value" : file}`);
  }

  // shapes: the feature under the pointer
  for (const l of LAYERS.filter((x) => x.kind === "shapes")) {
    const fc = JSON.parse(fs.readFileSync(diskPath(filesOf(l)[0]), "utf-8"));
    const cands = fc.features.map((f) => ({ f, at: placeIn(f.geometry) })).filter((x) => x.at && x.at.w > 0.05).sort((a, b) => b.at.w - a.at.w);
    if (!cands.length) { console.log(`note: ${l.id}: no polygon wide enough to point at; its hover was not probed`); continue; }
    const pick = cands[Math.floor(cands.length / 2)];   // a feature of middling size, not the easiest
    const z = Math.min(40, Math.max(2, 6 / pick.at.w));
    const view = { z: Number(z.toFixed(3)), lon: Number((pick.at.lon + 0.6 / z).toFixed(4)), lat: Number((pick.at.lat - 0.4 / z).toFixed(4)) };
    await go(`${base}/resources?on=${l.id}&z=${view.z}&c=${view.lon},${view.lat}`);
    await wait(`!!document.querySelector('[data-map] canvas') && Number(document.querySelector('[data-map]').dataset.settled || 0) > 0`, 30000, "the map");
    await ready([l.id]);
    const m = await mapData(), [x, y] = pixelOf(m.box, m, pick.at.lon, pick.at.lat);
    const h = await hoverAt(x, y), rows = (h?.rows ?? []).filter((r) => r.id === l.id);
    const under = fc.features.filter((f) => inside(f.geometry, pick.at.lon, pick.at.lat)).map((f) => f.properties.name);
    const named = rows.some((r) => r.feature === pick.f.properties.name && r.text.includes(pick.f.properties.name));
    check(named && rows.every((r) => under.includes(r.feature)) && rows.every((r) => !l.vintage || r.sub.includes(l.vintage)) && rows.every((r) => !l.publisher || r.sub.includes(l.publisher)),
      `${l.id}: at ${pick.at.lat.toFixed(3)} N ${(-pick.at.lon).toFixed(3)} W the hover names the feature under the pointer, "${pick.f.properties.name}" (${rows.map((r) => r.text).join(" | ") || "no row"}), with the vintage and the publisher`);
  }

  // points: the row under the pointer
  for (const l of LAYERS.filter((x) => x.kind === "points")) {
    const f = JSON.parse(fs.readFileSync(diskPath(filesOf(l)[0]), "utf-8"));
    const iName = Math.max(0, (f.columns ?? []).findIndex((c) => /^name$/i.test(c))) || 2;
    const r = f.rows[Math.floor(f.rows.length / 2)];
    await go(`${base}/resources?on=${l.id}&z=24&c=${(r[0] + 0.05).toFixed(4)},${(r[1] - 0.03).toFixed(4)}`);
    await wait(`!!document.querySelector('[data-map] canvas') && Number(document.querySelector('[data-map]').dataset.settled || 0) > 0`, 30000, "the map");
    await ready([l.id]);
    const m = await mapData(), [x, y] = pixelOf(m.box, m, r[0], r[1]);
    const h = await hoverAt(x, y), row = (h?.rows ?? []).find((q) => q.id === l.id);
    const k = scaleOf(m.box, m.z), near = f.rows.filter((q) => Math.hypot((q[0] - r[0]) * KX * k, (q[1] - r[1]) * k) <= 12).map((q) => String(q[iName]));
    check(row && near.includes(row.feature) && (!l.vintage || row.sub.includes(l.vintage)), `${l.id}: the hover names the row of the source under the pointer (${row?.text ?? "no row"}), with the vintage`);
  }

  // the overlays: the counts are the tables' own, and each answers the pointer
  {
    const ov = async (name) => JSON.parse((await get(`/resources/overlay/${name}`)).buf.toString("utf-8"));
    const queue = await ov("queue"), centers = await ov("datacenters");
    const op = MAPFILE.st.filter((s) => s === 0).length, pl = MAPFILE.st.length - op;
    const big = 0;   // the file's first unit is its largest
    const plantAt = { lon: MAPFILE.lo[big], lat: MAPFILE.la[big] };
    const county = queue.ok ? queue.shapes.features.map((f) => ({ f, at: placeIn(f.geometry) })).filter((x) => x.at).sort((a, b) => b.f.properties.mw - a.f.properties.mw)[0] : null;
    await go(`${base}/resources?on=plants_operating,plants_planned&z=20&c=${(plantAt.lon + 0.1).toFixed(4)},${(plantAt.lat - 0.05).toFixed(4)}`);
    await wait(`!!document.querySelector('[data-map] canvas') && Number(document.querySelector('[data-map]').dataset.settled || 0) > 0`, 30000, "the map");
    await ready(["plants_operating"]);
    const counts = await evaluate(`Object.fromEntries([...document.querySelectorAll('[data-count-value]')].map((e) => [e.dataset.countValue, Number(e.innerText.replace(/,/g, ''))]))`);
    check(counts.plants_operating === op && counts.plants_planned === pl && op === MAPFILE.counts.operating && pl === MAPFILE.counts.under_construction + MAPFILE.counts.planned,
      `plants: ${op.toLocaleString("en-US")} operating units and ${pl.toLocaleString("en-US")} planned or under construction on the page, as EIA-860M's inventory of ${MAPFILE.vintage} holds them (the page says ${counts.plants_operating} and ${counts.plants_planned})`);
    {
      const m = await mapData(), [x, y] = pixelOf(m.box, m, plantAt.lon, plantAt.lat);
      const h = await hoverAt(x, y), row = (h?.rows ?? []).find((r) => r.id.startsWith("plants"));
      const here2 = MAPFILE.n.filter((_, i) => MAPFILE.lo[i] !== null && Math.hypot((MAPFILE.lo[i] - plantAt.lon) * KX, MAPFILE.la[i] - plantAt.lat) * scaleOf(m.box, m.z) <= 12).map((ni) => MAPFILE.names[ni]);
      check(row && here2.includes(row.feature) && / MW$/.test(row.text) && row.sub.includes(`EIA-860M, ${MAPFILE.vintage}`), `plants: the hover names a unit at the pointer (${row?.text ?? "no row"}) with its status, its state and the inventory's vintage`);
      // one fuel hidden: the count and the address follow
      const slug = MAPFILE.techs[MAPFILE.t[big]].slug;
      await click(`[data-fuel="${slug}"]`);
      await sleep(700);
      const c2 = await evaluate(`Number(document.querySelector('[data-count-value="plants_operating"]').innerText.replace(/,/g, ''))`);
      const opWithout = MAPFILE.st.filter((s, i) => s === 0 && MAPFILE.t[i] !== MAPFILE.t[big]).length;
      const fuels = new URLSearchParams(await evaluate("location.search")).get("fuel") ?? "";
      check(c2 === opWithout && fuels.length > 0 && !fuels.split(",").includes(slug), `plants: with ${slug} switched off in the legend ${c2.toLocaleString("en-US")} operating units are counted, and the address holds the fuels shown`);
    }
    if (queue.ok && county) {
      const z = Math.min(40, Math.max(3, 5 / county.at.w));
      await go(`${base}/resources?on=queue&z=${z.toFixed(3)}&c=${(county.at.lon + 0.5 / z).toFixed(4)},${(county.at.lat - 0.3 / z).toFixed(4)}`);
      await wait(`!!document.querySelector('[data-map] canvas') && Number(document.querySelector('[data-map]').dataset.settled || 0) > 0`, 30000, "the map");
      await ready(["queue"]);
      const c = await evaluate(`Object.fromEntries([...document.querySelectorAll('[data-count-value]')].map((e) => [e.dataset.countValue, Number(e.innerText.replace(/,/g, ''))]))`);
      const title = await evaluate(`document.querySelector('[data-count="queue"] [title]')?.title ?? ''`);
      check(c.queue_drawn === queue.drawn && c.queue_counties === queue.counties && c.queue_not_drawn === queue.not_placed + queue.no_shape && queue.drawn + queue.not_placed + queue.no_shape === queue.rows && title.length > 20,
        `the queue: ${queue.drawn.toLocaleString("en-US")} rows drawn in ${queue.counties} counties and ${queue.not_placed + queue.no_shape} not drawn, counted in a short line with a hover; together the ${queue.rows.toLocaleString("en-US")} rows the live set holds`);
      const m = await mapData(), [x, y] = pixelOf(m.box, m, county.at.lon, county.at.lat);
      const h = await hoverAt(x, y), row = (h?.rows ?? []).find((r) => r.id === "queue");
      check(row && row.feature === county.f.properties.name && row.text.includes(`${county.f.properties.requests.toLocaleString("en-US")} request`) && /A county, not a site/.test(row.sub),
        `the queue: the hover names the county under the pointer and says it is a county, not a site (${row ? `${row.text}; ${row.sub}` : "no row"})`);
    } else check(false, `the queue overlay was not read: ${queue.reason ?? "no county"}`);
    if (centers.ok && centers.points.length) {
      const d = centers.points[Math.floor(centers.points.length / 2)];
      await go(`${base}/resources?on=datacenters&z=30&c=${(d.lon + 0.05).toFixed(4)},${(d.lat - 0.03).toFixed(4)}`);
      await wait(`!!document.querySelector('[data-map] canvas') && Number(document.querySelector('[data-map]').dataset.settled || 0) > 0`, 30000, "the map");
      await ready(["datacenters"]);
      const c = await evaluate(`Object.fromEntries([...document.querySelectorAll('[data-count-value]')].map((e) => [e.dataset.countValue, Number(e.innerText.replace(/,/g, ''))]))`);
      const m = await mapData(), [x, y] = pixelOf(m.box, m, d.lon, d.lat);
      const h = await hoverAt(x, y), row = (h?.rows ?? []).find((r) => r.id === "datacenters");
      check(c.datacenters_drawn === centers.drawn && c.datacenters_not_drawn === centers.not_placed && centers.drawn + centers.not_placed === centers.rows && row && /MW/.test(row.text) && /coordinates|not the site/.test(row.sub),
        `datacenters: ${centers.drawn} facilities drawn and ${centers.not_placed} not drawn, of the ${centers.rows} the live set holds; the hover answers at a facility (${row ? `${row.text}; ${row.sub}` : "no row"})`);
    } else check(false, `the datacenter overlay was not read: ${centers.reason ?? "no facility placed"}`);
  }

  // where two layers are on, the hover lists each; and an address restores a view
  {
    const two = LAYERS.filter((l) => l.kind === "shapes").slice(0, 1).concat(LAYERS.filter((l) => l.kind === "grid").slice(0, 1));
    const ids = [...two.map((l) => l.id), "plants_operating"];
    const addr = `?on=${ids.join(",")}&z=3.5&c=-101.25,31.5&fuel=solar,wind`;
    await go(`${base}/resources${addr}`);
    await wait(`!!document.querySelector('[data-map] canvas') && Number(document.querySelector('[data-map]').dataset.settled || 0) > 0`, 30000, "the map");
    await ready(ids);
    const m = await mapData();
    const onNow = await evaluate(`[...document.querySelectorAll('[data-toggle]')].filter((e) => e.checked).map((e) => e.dataset.toggle)`);
    const fuels = await evaluate(`[...document.querySelectorAll('[data-fuel]')].filter((e) => e.getAttribute('aria-pressed') === 'true').map((e) => e.dataset.fuel)`);
    check(m.z === 3.5 && m.lon === -101.25 && m.lat === 31.5 && JSON.stringify([...onNow].sort()) === JSON.stringify([...ids].sort()) && JSON.stringify(fuels.sort()) === '["solar","wind"]' && (await evaluate("location.search")) === addr,
      `an address restores the view: the layers (${onNow.join(", ")}), the fuels (${fuels.join(", ")}), the zoom ${m.z} and the centre ${m.lat} N ${-m.lon} W`);
    if (two.length === 2) {
      const fc = JSON.parse(fs.readFileSync(diskPath(filesOf(two[0])[0]), "utf-8"));
      const grid = two[1], levels = (grid.levels ?? []).filter((v) => diskPath(v.file));
      const spot = fc.features.map((f) => placeIn(f.geometry)).filter((at) => at && at.w > 0.3 && levels.every((v) => storedAt(gridOf(v.file), at.lon, at.lat) !== null))[0];
      if (spot) {
        await go(`${base}/resources?on=${two.map((l) => l.id).join(",")}&z=5&c=${(spot.lon + 0.4).toFixed(4)},${(spot.lat + 0.2).toFixed(4)}`);
        await wait(`!!document.querySelector('[data-map] canvas') && Number(document.querySelector('[data-map]').dataset.settled || 0) > 0`, 30000, "the map");
        await ready(two.map((l) => l.id));
        const m2 = await mapData(), [x, y] = pixelOf(m2.box, m2, spot.lon, spot.lat), h = await hoverAt(x, y);
        check(h && two.every((l) => h.rows.some((r) => r.id === l.id)), `where two layers are on the hover lists each (${(h?.rows ?? []).map((r) => `${r.id}: ${r.text}`).join(" | ")})`);
      }
    }
  }

  const made = requests.slice(start), off = made.filter((r) => !r.url.startsWith(`${base}/`) && !/^(data|blob|about|chrome|devtools):/.test(r.url));
  check(made.length > 20 && off.length === 0, `the page asks nothing of any other site: ${made.length} requests of its own while it was open, all to this one${off.length ? ` but ${off.length} (${off[0].url.slice(0, 120)})` : ""} (its grid reader, off the page's thread, asks only for the address the page hands it, which tests/test_session146_page.py holds to this site)`);
  check(errors.length === 0, `no script error on the page${errors.length ? `: ${errors[0].slice(0, 200)}` : ""}`);
  return 0;
}, { width: 1400, height: 1000 });
if (code === null) console.log("note: no Chrome or Edge on this machine; the browser checks were not run");
console.log(bad ? `${bad} of ${n} failed` : `all ${n} passed`);
process.exit(bad ? 1 : 0);
