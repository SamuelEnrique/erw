// Energy Research Warehouse (ERW) site, session 132: one screenshot of one page in the internal view, so a session can
// look at a page that is in review (scripts/screenshots.mjs reads pages as a visitor).
//
//   node scripts/shot.mjs <url> <out.png> [width] [height] [wait-for-selector]
//
// Opens the internal view (INTERNAL_COSTS_TOKEN), loads the address, waits for the selector when one is given and for
// the charts to draw, and writes a PNG of the window (not of the whole page). Exit 1 when it cannot.
import fs from "node:fs";
import { withBrowser } from "./browser.mjs";

const [url, out, w = "1600", h = "1000", selector] = process.argv.slice(2);
if (!url || !out) { console.error("usage: node scripts/shot.mjs <url> <out.png> [width] [height] [wait-for-selector]"); process.exit(2); }
const code = await withBrowser(async ({ go, wait, unlock, send, sleep }) => {
  await unlock(new URL(url).origin);
  await send("Emulation.setDeviceMetricsOverride", { width: Number(w), height: Number(h), deviceScaleFactor: 1, mobile: false });
  await go(url);
  if (selector) await wait(`!!document.querySelector(${JSON.stringify(selector)})`, 30000, selector);
  await sleep(1500);
  const shot = await send("Page.captureScreenshot", { format: "png" });
  fs.writeFileSync(out, Buffer.from(shot.data, "base64"));
  console.log(`${out}: ${w} x ${h}, ${url}`);
  return 0;
});
process.exitCode = code === 0 ? 0 : 1;
