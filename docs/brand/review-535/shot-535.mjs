// Energy Research Warehouse (ERW), session 535: the downloads line (components/tool/TableDownloads.tsx) with its new R
// link, shot in the internal view at 1280 and at 390 px wide, on the pages the session's check read. The line is at the
// foot of each page, so the shot scrolls it into the middle of the window before it is taken. One PNG a page and a width
// into this folder (storage_1280.png), named by the page.
//
//   cd site && npx next start -p 3535
//   node ../docs/brand/review-535/shot-535.mjs http://localhost:3535 [/page ...]     (default /board /storage /curtailment)
//
// The internal view is opened by unlock(base) from site/scripts/browser.mjs: the token is posted, never in an address.
// Exit 1 when a page has no downloads line or a shot could not be made.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3535").replace(/\/$/, "");
const pages = process.argv.length > 3 ? process.argv.slice(3) : ["/board", "/storage", "/curtailment"];

let bad = 0;
for (const width of [1280, 390]) {
  const code = await withBrowser(async ({ go, wait, unlock, send, sleep, evaluate }) => {
    await unlock(base);
    await send("Emulation.setDeviceMetricsOverride", { width, height: width === 390 ? 844 : 900, deviceScaleFactor: 1, mobile: width === 390 });
    for (const page of pages) {
      await go(base + page);
      const ok = await wait("!!document.querySelector('[data-downloads]')", 30000, `${page}: the downloads line`).catch(() => false);
      if (!ok) { console.log(`FAIL ${page} at ${width}: no downloads line`); bad += 1; continue; }
      await evaluate("document.querySelector('[data-downloads]').scrollIntoView({ block: 'center' })");
      await sleep(1500);
      const rLinks = await evaluate("document.querySelectorAll('[data-download=\"r\"]').length");
      const shot = await send("Page.captureScreenshot", { format: "png" });
      const out = path.join(here, `${page.replace(/^\//, "").replace(/\//g, "-") || "home"}_${width}.png`);
      fs.writeFileSync(out, Buffer.from(shot.data, "base64"));
      console.log(`${out}: ${width} px, ${rLinks} R links`);
    }
    return 0;
  }, { width, height: 900 });
  if (code !== 0) bad += 1;
}
process.exitCode = bad ? 1 : 0;
