// Energy Research Warehouse (ERW), session 402: the Digest's pages at 1280 and 390 px, whole page, in the internal view.
//
//   node docs/brand/review-402/shots-402.mjs http://localhost:3402      (from the repository root; site/node_modules not needed)
//
// Writes <page>-<width>.png beside this file, and pages-402.json: each page's held figures, checked figures and the
// line a day without a Digest shows.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = process.argv[2] ?? "http://localhost:3402";
const PAGES = [["digest", "/digest"], ["digest-2026-10-20", "/digest/2026-10-20"], ["digest-2026-10-19", "/digest/2026-10-19"],
  ["digest-2026-09-25", "/digest/2026-09-25"], ["digest-2026-10-13", "/digest/2026-10-13"]];
const record = {};
const code = await withBrowser(async ({ go, unlock, send, sleep, evaluate }) => {
  await unlock(base);
  for (const width of [1280, 390]) {
    for (const [name, url] of PAGES) {
      await send("Emulation.setDeviceMetricsOverride", { width, height: 900, deviceScaleFactor: 1, mobile: width < 600 });
      await go(base + url);
      await sleep(1200);
      const m = await send("Page.getLayoutMetrics");
      const h = Math.min(Math.ceil(m.cssContentSize?.height ?? m.contentSize.height), 12000);
      const shot = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip: { x: 0, y: 0, width, height: h, scale: 1 } });
      fs.writeFileSync(path.join(here, `${name}-${width}.png`), Buffer.from(shot.data, "base64"));
      record[`${url} @${width}`] = await evaluate(`({
        held: [...document.querySelectorAll('[data-license-held]')].map((e) => e.getAttribute('data-license-held')),
        checked: [...document.querySelectorAll('[data-check]')].map((e) => [e.getAttribute('data-check'), e.textContent]),
        none: document.querySelector('[data-digest-none]')?.textContent ?? null,
        archive: [...document.querySelectorAll('[data-archive-day]')].map((e) => e.getAttribute('data-archive-day') + ' ' + e.textContent).slice(0, 8),
        overflow: document.documentElement.scrollWidth > window.innerWidth,
        height: ${h} })`);
      console.log(`${name}-${width}.png ${h} px`);
    }
  }
  return 0;
});
fs.writeFileSync(path.join(here, "pages-402.json"), JSON.stringify(record, null, 1) + "\n");
process.exitCode = code === 0 ? 0 : 1;
