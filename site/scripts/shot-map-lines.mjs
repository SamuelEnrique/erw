// Energy Research Warehouse (ERW) site, session 8014 (chain 581, part D): one screenshot of the project map with its
// line layers turned on, in the internal view, so a session can see the switches work before a landing.
//
//   node scripts/shot-map-lines.mjs <base> <out.png> [width] [height]
//
// Opens <base>/map, turns on every switch under "Lines on the map", waits for the files and the drawing, writes a PNG
// of the window and prints how many line switches are on and whether any layer says it was not read. Exit 1 when it cannot.
import fs from "node:fs";
import { withBrowser } from "./browser.mjs";

const [base, out, w = "1280", h = "1400"] = process.argv.slice(2);
if (!base || !out) { console.error("usage: node scripts/shot-map-lines.mjs <base> <out.png> [width] [height]"); process.exit(2); }
const code = await withBrowser(async ({ go, wait, unlock, send, sleep }) => {
  await unlock(base);
  await send("Emulation.setDeviceMetricsOverride", { width: Number(w), height: Number(h), deviceScaleFactor: 1, mobile: false });
  await go(`${base}/map`);
  await wait("!!document.querySelector('[data-map-line]')", 30000, "the line switches");
  await send("Runtime.evaluate", { expression: "document.querySelectorAll('[data-map-line]').forEach((b) => b.click())" });
  await sleep(6000);
  const r = await send("Runtime.evaluate", { expression: "JSON.stringify({ on: [...document.querySelectorAll('[data-map-line]')].filter((b) => b.checked).length, text: document.querySelector('[data-map-lines]').innerText })", returnByValue: true });
  await send("Runtime.evaluate", { expression: "document.querySelector('[data-map-drawn]').scrollIntoView({ block: 'center' })" });
  await sleep(1500);
  const shot = await send("Page.captureScreenshot", { format: "png" });
  fs.writeFileSync(out, Buffer.from(shot.data, "base64"));
  console.log(`${out}: ${w} x ${h}; ${r.result.value}`);
  return 0;
});
process.exitCode = code === 0 ? 0 : 1;
