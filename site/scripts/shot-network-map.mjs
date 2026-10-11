// Energy Research Warehouse (ERW) site, session 193: pictures of the Map view as the site's own boundary file draws it
// (not the check's made-up squares), for a person's eye. In the internal view; nothing is sent but requests to the
// site under test.
//
//   node scripts/shot-network-map.mjs <base-url> <out-prefix>
//
// Writes <out-prefix>_1280.png (the map at 1280 px), <out-prefix>_1280_uri.png (15 February 2021 with ERCOT chosen)
// and <out-prefix>_390.png (a phone), and prints what the frame holds in each. Exit 1 when the map is not held.
import fs from "node:fs";
import { sleep, withBrowser } from "./browser.mjs";

const [base, prefix] = process.argv.slice(2);
if (!base || !prefix) { console.log("usage: shot-network-map.mjs <base-url> <out-prefix>"); process.exit(2); }
const READY = `!!document.querySelector('[data-network-view][data-restored="1"]')`;
const FRAME = `(() => { const m = document.querySelector('[data-map-state]'); const p = document.querySelector('[data-map-derived-label]');
  return { state: m?.getAttribute('data-map-state') ?? null, regions: document.querySelectorAll('[data-region]').length, flows: document.querySelectorAll('[data-flow]').length,
    derived: m?.getAttribute('data-map-derived') ?? null, label: p?.innerText ?? '', noShape: (m?.getAttribute('data-map-no-shape') ?? '').split(',').filter(Boolean).length,
    w: Math.round(m?.getBoundingClientRect().width ?? 0), h: Math.round(m?.getBoundingClientRect().height ?? 0), labelH: Math.round(p?.getBoundingClientRect().height ?? 0) }; })()`;

const code = await withBrowser(async ({ go, evaluate, wait, unlock, send }) => {
  await unlock(base);
  const shot = async (url, file, width, height, mobile) => {
    await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: mobile ? 2 : 1, mobile });
    await go(url);
    await wait(READY, 30000, "the page to be ready");
    const s = await wait(`(() => { const s = ${FRAME}; return s.state && s.state !== 'loading' ? s : null; })()`, 30000, "the map's frame");
    await evaluate(`window.scrollTo(0, Math.max(0, document.querySelector('[data-shape-toggle]').getBoundingClientRect().top + window.scrollY - 8))`);
    await sleep(800);
    fs.writeFileSync(file, Buffer.from((await send("Page.captureScreenshot", { format: "png" })).data, "base64"));
    console.log(`${file}: ${s.state}, ${s.regions} regions, ${s.flows} ties drawn, ${s.noShape} grids with no area, frame ${s.w} by ${s.h} px, derived ${s.derived}, label ${s.labelH} px high: "${s.label}"`);
    return s;
  };
  const a = await shot(`${base}/network?shape=map`, `${prefix}_1280.png`, 1280, 900, false);
  await shot(`${base}/network?view=day&t=2021-02-15&grid=ERCO&shape=map`, `${prefix}_1280_uri.png`, 1280, 900, false);
  await shot(`${base}/network?shape=map`, `${prefix}_390.png`, 390, 844, true);
  return a.state === "held" ? 0 : 1;
});
if (code === null) { console.log("not proven here: no browser on this machine"); process.exit(0); }
process.exit(code);
