// Session 411: the home page (the one page whose own file changed: its chart's size) at 1280 and 390 px, in the
// internal view of a local production build, the first screen and the chart. node shots-411.mjs <base> <before|after>
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
const here = path.dirname(fileURLToPath(import.meta.url));
const { withBrowser } = await import(pathToFileURL(path.join(here, "..", "..", "..", "site", "scripts", "browser.mjs")).href);
const [base = "http://localhost:3411", tag = "after"] = process.argv.slice(2);
for (const w of [1280, 390]) {
  const code = await withBrowser(async ({ go, evaluate, unlock, sleep, send }) => {
    await unlock(base);
    if (w === 390) await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
    await go(`${base}/`); await sleep(2500);
    const box = await evaluate(`(() => { const i = document.querySelector('#today img'); if (!i) return null; i.scrollIntoView({ block: 'start' }); const r = i.getBoundingClientRect(); return { y: Math.round(r.top + scrollY), w: Math.round(r.width), h: Math.round(r.height), nw: i.naturalWidth, nh: i.naturalHeight, aw: i.getAttribute('width'), ah: i.getAttribute('height') }; })()`);
    await sleep(500);
    const shot = await send("Page.captureScreenshot", { format: "png" });
    fs.writeFileSync(path.join(here, `home_today_${w}_${tag}.png`), Buffer.from(shot.data, "base64"));
    console.log(w, tag, JSON.stringify(box));
    return 0;
  }, { width: w === 390 ? 390 : 1280, height: w === 390 ? 844 : 900 });
  if (code !== 0) process.exit(1);
}
