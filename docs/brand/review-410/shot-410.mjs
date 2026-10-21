// Energy Research Warehouse (ERW), session 410: /data in the internal view at 1280 and 390 px wide. One shot of the
// page's top and one of the coverage table a width into this folder, and data-410.json: every row of the coverage table
// as the page drew it (table, refreshed, rows, license, download), for the comparison with coverage.csv.
//
//   cd site && npx next start -p 3410
//   node docs/brand/review-410/shot-410.mjs http://localhost:3410
//
// The internal view is opened by unlock(base) from site/scripts/browser.mjs (the token is posted, never in an address).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3410").replace(/\/$/, "");
const WIDTHS = [[1280, 900, false], [390, 844, true]];

const ROWS = `(() => {
  const t = document.querySelector('#coverage table');
  if (!t) return null;
  const head = [...t.querySelectorAll('thead th')].map((th) => th.textContent.trim());
  const rows = [...t.querySelectorAll('tbody tr')].map((tr) => {
    const c = [...tr.children].map((td) => td.textContent.replace(/\\s+/g, ' ').trim());
    const a = tr.querySelector('td:last-child a');
    return { id: tr.id, cells: c, link: a ? a.getAttribute('href') : null };
  });
  return { head, rows, aside: document.querySelector('#coverage')?.textContent.match(/([0-9,]+) public tables/)?.[1] ?? null,
           noData: document.body.innerText.includes('could not be read') };
})()`;

let code = 0;
const out = {};
for (const [w, h, mobile] of WIDTHS) {
  const r = await withBrowser(async ({ go, evaluate, wait, unlock, send }) => {
    await send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile });
    await unlock(base);
    await go(`${base}/data`);
    await wait("document.querySelector('h1') !== null", 30000, "the page's heading");
    const shot = async (name) => {
      const s = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: w, height: h, scale: 1 }, captureBeyondViewport: false });
      fs.writeFileSync(path.join(here, `${name}_${w}.png`), Buffer.from(s.data, "base64"));
    };
    await evaluate("window.scrollTo(0, 0)");
    await shot("01-data-top");
    await evaluate("(() => { const t = document.querySelector('#coverage table'); if (t) { t.scrollIntoView({ block: 'start' }); } return true; })()");
    await evaluate("new Promise((r) => setTimeout(r, 300))");
    await shot("02-data-coverage");
    // the table's Refreshed column in view at a phone width: scroll its box sideways to the column
    if (mobile) {
      await evaluate(`(() => { const b = document.querySelector('#coverage .overflow-x-auto'); const th = [...b.querySelectorAll('th')].find((x) => x.textContent.trim() === 'Refreshed (UTC)'); if (b && th) b.scrollLeft = th.offsetLeft - 8; return true; })()`);
      await evaluate("new Promise((r) => setTimeout(r, 300))");
      await shot("03-data-refreshed");
    }
    return await evaluate(ROWS);
  }, { width: w, height: h });
  if (!r) { console.log(`${w}: no browser on this machine`); code = 1; continue; }
  out[w] = r;
  console.log(`${w}: ${r.rows.length} rows; heading ${JSON.stringify(r.head)}; aside ${r.aside}; live set unreadable: ${r.noData}`);
}
fs.writeFileSync(path.join(here, "data-410.json"), JSON.stringify(out[1280] ?? out[390] ?? null, null, 1) + "\n");
process.exit(code);
