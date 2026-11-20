// ERW, the Grid tool's map (the Map shape of /grid?view=network): the figures the map draws, read from the page
// (session 8606, chain 504).
//
// It opens the map on a built site, in the internal view, and writes down what a reader sees: the hour the week
// opens on, the snapshot's refresh, how many regions and ties are drawn, the authorities listed under the map, every
// tie drawn with its megawatts and its direction, the width key, and the hover of every region the pointer can
// reach (its carbon intensity, its demand, its net exchange and its count of ties). It also keeps the snapshot the
// page drew (the hourly copy in public Storage, or the repository's copy), so replicate_map.py can compute the same
// figures from the snapshot and the boundary file without the page's code.
//
//   node replication/grid/map_figures.mjs <base-url> [out.json] [snapshot.json]
//
// It reads the page only, and one public object of the ERW's own Storage. INTERNAL_COSTS_TOKEN opens the internal
// view, as for the site's own browser checks. Exit 2 when the snapshot read is not the one the page drew.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const [base, out = path.join(here, "map_page_figures.json"), snapOut = path.join(here, "map_snapshot.json")] = process.argv.slice(2);
if (!base) { console.error("usage: node replication/grid/map_figures.mjs <base-url> [out.json] [snapshot.json]"); process.exit(2); }
const OBJECT = "storage/v1/object/public/erw-public/network/grid_network.json";   // site/lib/network.ts NETWORK_OBJECT

async function snapshot() {
  const host = process.env.NEXT_PUBLIC_SUPABASE_URL || process.env.SUPABASE_URL;
  if (host) {
    try {
      const r = await fetch(`${new URL(host).origin}/${OBJECT}`, { cache: "no-store" });   // the address the site itself reads (site/lib/network.ts)
      if (r.ok) return { from: "the hourly copy in public Storage (erw-public/network/grid_network.json)", snap: await r.json() };
      console.log(`the hourly copy answered HTTP ${r.status}; the repository's copy is read`);
    } catch (e) { console.log(`the hourly copy was not reachable (${e.message}); the repository's copy is read`); }
  }
  return { from: "the repository's copy (site/data/grid_network.json)", snap: JSON.parse(fs.readFileSync(path.join(here, "..", "..", "site", "data", "grid_network.json"), "utf-8")) };
}

const code = await withBrowser(async ({ go, evaluate, unlock, sleep, send, errors }) => {
  await unlock(base);
  await send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 1000, deviceScaleFactor: 1, mobile: false });
  await go(`${base}/grid?view=network&shape=map`);
  for (let i = 0; i < 60; i += 1) { if (await evaluate(`document.querySelector('[data-map-state]')?.getAttribute('data-map-state') === 'held'`)) break; await sleep(500); }
  await evaluate(`window.scrollTo(0, Math.max(0, document.querySelector('[data-shape-toggle]').getBoundingClientRect().top + window.scrollY - 8))`);
  await sleep(600);
  const page = await evaluate(`(() => { const m = document.querySelector('[data-map-state="held"]'); if (!m) return null; const t = (e) => (e ? e.innerText.replace(/\\s+/g, ' ').trim() : null);
    const body = document.body.innerText;
    return { address: window.location.search, complete_hour: document.querySelector('[data-complete-hour]')?.getAttribute('data-complete-hour') ?? null, opens_line: t(document.querySelector('[data-complete-hour]')),
      refreshed: (body.match(/refreshed (\\d{4}-\\d{2}-\\d{2} \\d{2}:\\d{2}) UTC/) || [])[1] ?? null, slider: t(document.querySelector('input[type=range]')?.parentElement)?.slice(0, 120) ?? null,
      regions: Number(m.getAttribute('data-map-regions')), matched: Number(m.getAttribute('data-map-matched')), flows: Number(m.getAttribute('data-map-flows')), flows_all: Number(m.getAttribute('data-map-flows-all')),
      no_shape: (m.getAttribute('data-map-no-shape') || '').split(',').filter(Boolean), boundary_sha256: m.getAttribute('data-map-sha'),
      listed: [...document.querySelectorAll('[data-listed]')].map((e) => e.getAttribute('data-listed')), listed_count: Number(document.querySelector('[data-map-listed]')?.getAttribute('data-map-listed') ?? -1),
      width_key: Number(document.querySelector('[data-map-width-key]')?.getAttribute('data-map-width-key') ?? NaN), width_key_text: t(document.querySelector('[data-map-width-key]')),
      ties: [...m.querySelectorAll('[data-flow]')].map((g) => ({ flow: g.getAttribute('data-flow'), mw: Number(g.getAttribute('data-mw')) })),
      region_codes: [...m.querySelectorAll('[data-region]')].map((e) => e.getAttribute('data-region')) }; })()`);
  if (!page) { console.error("the map did not draw"); return 1; }
  // the hover of every region the pointer can reach
  const hovers = {};
  for (const ba of page.region_codes) {
    // points of the screen where the region is the top shape, spread over its box; a point near a tie's line gives the
    // tie's card (the map reads the nearest line), so points are tried until the card is the region's own
    const pts = await evaluate(`(() => { const e = document.querySelector('[data-region="${ba}"]'); if (!e) return []; const b = e.getBoundingClientRect(); const out = [];
      for (let i = 1; i < 40; i += 1) for (let j = 1; j < 40; j += 1) { const x = b.left + (b.width * i) / 40, y = b.top + (b.height * j) / 40; if (x > 0 && y > 0 && y < window.innerHeight && document.elementFromPoint(x, y) === e) out.push({ x, y }); }
      const step = Math.max(1, Math.floor(out.length / 24)); return out.filter((_, k) => k % step === 0).slice(0, 24); })()`);
    hovers[ba] = null;
    for (const pt of pts) {
      await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: pt.x, y: pt.y });
      await sleep(120);
      const card = await evaluate(`(() => { const n = document.querySelector('[data-map-hover-name]'); if (!n) return null; const box = n.parentElement; return [...box.children].map((c) => c.innerText.replace(/\\s+/g, ' ').trim()); })()`);
      if (card && !hovers[ba]) hovers[ba] = card;                                   // a tie's card is kept only if no point gives the region's
      if (card && card.some((l) => l.startsWith("Carbon intensity of generation"))) { hovers[ba] = card; break; }
    }
  }
  await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: 3, y: 3 });
  const { from, snap } = await snapshot();
  const built = String(snap.built ?? "").slice(0, 16).replace("T", " ");
  if (page.refreshed && built !== page.refreshed) {
    console.error(`the page drew the snapshot refreshed ${page.refreshed} UTC; the snapshot read now was built ${built} UTC. The hour rolled between the two: run again.`);
    return 2;
  }
  fs.writeFileSync(snapOut, `${JSON.stringify(snap)}\n`);
  fs.writeFileSync(out, `${JSON.stringify({ what: "the figures the Grid tool's map draws, read from the page", base: base.replace(/^https?:\/\/localhost:\d+/, "a local build"), taken: new Date().toISOString().replace(/\.\d+Z$/, "Z"),
    snapshot_from: from, snapshot_built: snap.built, page, hovers }, null, 1)}\n`);
  const reached = Object.values(hovers).filter(Boolean).length;
  console.log(`the map: ${page.regions} regions, ${page.flows} of ${page.flows_all} ties drawn, ${page.listed.length} authorities listed; hover read for ${reached} of ${page.region_codes.length} regions; the week opens on ${page.complete_hour}; refreshed ${page.refreshed} UTC`);
  console.log(`written: ${path.relative(process.cwd(), out)} and ${path.relative(process.cwd(), snapOut)} (${from}); errors in the page: ${JSON.stringify(errors.slice(0, 4))}`);
  return errors.length ? 1 : 0;
});
process.exitCode = typeof code === "number" ? code : 0;
