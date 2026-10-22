// Energy Research Warehouse (ERW), session 588: the render frames of the cards named, photographed as
// scripts/render-cards.mjs photographs them (/research/card/<id>?render=1 at 1600 x 900 and 1080 x 1350), with the
// bottom of the lowest SVG text on the picture written beside each shot.
//   node docs/brand/review-588/shot-588.mjs <base> <out dir> <id>...       (from the repository root; site/node_modules present)
import fs from "node:fs";
import path from "node:path";
import { withBrowser } from "../../../site/scripts/browser.mjs";
const [base, out, ...ids] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const lines = [];
const code = await withBrowser(async ({ go, wait, unlock, send, sleep }) => {
  const js = async (expression) => (await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true })).result?.value;
  await unlock(base);
  for (const id of ids) {
    for (const [w, h] of [[1600, 900], [1080, 1350]]) {
      await send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile: false });
      await go(`${base}/research/card/${id}?render=1`);
      await wait('!!document.querySelector("[data-render=\\"1\\"] [data-finding-chart] svg")', 30000, "the render frame's chart");
      await sleep(800);
      await js("document.fonts.ready.then(() => true)");  // session 506: the fonts drawn before the measure and the shot
      const m = await js("({ h: document.documentElement.scrollHeight, foot: Math.round(document.querySelector('.finding-render-foot').getBoundingClientRect().bottom), text: Math.round(Math.max(0, ...[...document.querySelectorAll('[data-finding-chart] svg text')].map((t) => t.getBoundingClientRect().bottom))), panels: document.querySelectorAll('[data-finding-chart=\"multiples\"] [data-panel]').length, callouts: Math.round((document.querySelector('.finding-callouts') ?? document.querySelector('.finding-why')).getBoundingClientRect().top) })");
      lines.push(`${id} ${w}x${h}: page ${m.h} px, last line ${m.foot} px, lowest chart text ${m.text} px, panels ${m.panels}, callouts top ${m.callouts} px`);
      const s = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: w, height: Math.max(h, m.h), scale: 1 }, captureBeyondViewport: true });
      fs.writeFileSync(path.join(out, `${id}_${w}x${h}.png`), Buffer.from(s.data, "base64"));
    }
  }
  return 0;
}, { width: 1600, height: 900 });
fs.writeFileSync(path.join(out, "measures-588.txt"), lines.join("\n") + "\n");
console.log(lines.join("\n"));
process.exit(code);
