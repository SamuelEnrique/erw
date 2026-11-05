// Session 406: the three charts of the newsletter's issue 1, cut from pages of a local build by a browser screenshot
// of each chart's own element (the site's shared chart components, as the pages draw them). Kept beside the PNGs so
// the charts can be made again on the next build.
//
//   cd site && npm run build && npx next start -p 3406
//   node ../docs/reviews/newsletter/issue-001/shots-406.mjs http://localhost:3406
//
// The pages are in review: the internal view is opened by the form (unlock, the token posted, never in an address).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = process.argv[2] ?? "http://localhost:3406";

// Each chart: the page, a script that returns its element, and the file.
const CHARTS = [
  { file: "chart-1-ercot-revenue-by-year.png", page: "/cost-of-power/battery",
    find: `document.querySelector('[data-series-chart="years"]')` },
  { file: "chart-2-ercot-fleet-mw.png", page: "/storage?tab=buildout&grid=ercot",
    find: `[...document.querySelectorAll("figure")].find((f) => /MW at each year's end/.test(f.querySelector("figcaption")?.textContent ?? "") && !/solar/.test(f.querySelector("figcaption")?.textContent ?? ""))` },
  { file: "chart-3-caiso-revenue-by-year.png", page: "/cost-of-power/battery?grid=caiso&dur=4&strat=foresight",
    find: `document.querySelector('[data-series-chart="years"]')` },
];

const code = await withBrowser(async ({ go, evaluate, wait, unlock, send, sleep }) => {
  await unlock(base);
  let failed = 0;
  for (const c of CHARTS) {
    try {
      await go(base + c.page);
      await wait(`(() => { const e = ${c.find}; return !!(e && e.querySelector("svg")); })()`, 30000, `the chart of ${c.page}`);
      if (await evaluate(`/could not be read/i.test(document.body.innerText)`)) console.log(`note ${c.page}: the page says the live set could not be read`);
      await evaluate(`(${c.find}).scrollIntoView({ block: "center" })`);
      await sleep(1200);
      const r = await evaluate(`(() => { const b = (${c.find}).getBoundingClientRect(); return { x: b.left + scrollX, y: b.top + scrollY, w: b.width, h: b.height, title: (${c.find}).querySelector("figcaption, h3, h4")?.textContent?.trim() ?? "" }; })()`);
      const pad = 12;
      const shot = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true,
        clip: { x: Math.max(0, r.x - pad), y: Math.max(0, r.y - pad), width: r.w + 2 * pad, height: r.h + 2 * pad, scale: 2 } });
      fs.writeFileSync(path.join(here, c.file), Buffer.from(shot.data, "base64"));
      console.log(`ok   ${c.file}: ${c.page}, ${Math.round(r.w)} by ${Math.round(r.h)} CSS px at 2x; "${r.title.slice(0, 80)}"`);
    } catch (e) {
      failed += 1;
      console.log(`FAIL ${c.file}: ${c.page}: ${e.message ?? e}`);
    }
  }
  return failed ? 1 : 0;
}, { width: 1280, height: 900 });
if (code === null) { console.log("no browser on this machine: not proven here"); process.exit(1); }
process.exit(code);
