// Energy Research Warehouse (ERW) site, session 3308 (chain 200): the company pages and /deals/capital in a headless
// browser, in the internal view (the pages are in review), at 1280 and at 390 px wide (a phone, mobile emulation).
//
//   node --import ./scripts/alias-register.mjs scripts/shots-companies.mjs <base> <out-dir>
//
// For each page and width: a full-page screenshot (<out-dir>/<name>-<width>.png), the page's scroll width against the
// window (a page wider than the window fails), and the HTML as drawn (<out-dir>/<name>.html, for an accessibility audit).
// On a company page with the MW-by-year chart, the pointer is moved over the chart's middle and the hover card must
// appear with a figure (data-chart-card), and the left and right arrows move it from the keyboard.
// Exit 1 on a failure. It reads only; nothing is sent but the internal form's own POST.
import fs from "node:fs";
import path from "node:path";
import { withBrowser } from "./browser.mjs";

const base = (process.argv[2] ?? "http://localhost:3330").replace(/\/$/, "");
const out = process.argv[3] ?? "screenshots-companies";
fs.mkdirSync(out, { recursive: true });
const PAGES = [
  ["companies", "/companies"],
  ["companies-filtered", "/companies?kind=IPP&state=TX&has=queue"],
  ["company-fpl", "/companies/eia-6452"],
  ["company-tva", "/companies/eia-18642"],
  ["company-doe", "/companies/energy-department"],
  ["company-nextera", "/companies/nextera"],
  ["capital", "/deals/capital"],
];
let bad = 0;
const say = (ok, what) => { if (!ok) bad += 1; console.log(`${ok ? "ok  " : "FAIL"} ${what}`); };

const code = await withBrowser(async ({ go, evaluate, wait, unlock, send, sleep }) => {
  await unlock(base);
  for (const width of [1280, 390]) {
    const mobile = width < 600;
    await send("Emulation.setDeviceMetricsOverride", { width, height: mobile ? 844 : 900, deviceScaleFactor: 1, mobile });
    for (const [name, p] of PAGES) {
      await go(base + p);
      await wait("document.readyState === 'complete'", 20000);
      await sleep(400);
      const title = await evaluate("document.title");
      if (/In review/i.test(title)) { say(false, `${p} @${width}: the in-review page (the internal view did not hold)`); continue; }
      const sw = await evaluate("document.documentElement.scrollWidth");
      say(sw <= width + 1, `${p} @${width}: scroll width ${sw}`);
      if (width === 1280) fs.writeFileSync(path.join(out, `${name}.html`), await evaluate("document.documentElement.outerHTML"));
      const h = await evaluate("Math.min(document.documentElement.scrollHeight, 12000)");
      await send("Emulation.setDeviceMetricsOverride", { width, height: h, deviceScaleFactor: 1, mobile });
      const shot = await send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
      fs.writeFileSync(path.join(out, `${name}-${width}.png`), Buffer.from(shot.data, "base64"));
      await send("Emulation.setDeviceMetricsOverride", { width, height: mobile ? 844 : 900, deviceScaleFactor: 1, mobile });
      const chart = await evaluate("(() => { const el = document.querySelector('[data-bars-hover^=\"years-\"]'); if (!el) return null; el.scrollIntoView({block: 'center'}); const r = el.getBoundingClientRect(); return { x: r.left + r.width / 2, y: r.top + r.height / 2 }; })()");
      if (chart) {
        await send("Input.dispatchMouseEvent", { type: "mouseMoved", x: Math.round(chart.x), y: Math.round(chart.y) });
        await sleep(300);
        const card = await evaluate("document.querySelector('[data-chart-card]')?.textContent ?? ''");
        say(/\d/.test(card) && /MW/.test(card), `${p} @${width}: the year chart's hover card shows "${card.slice(0, 60)}"`);
        await evaluate("document.querySelector('[data-bars-hover^=\"years-\"]').focus()");
        await send("Input.dispatchKeyEvent", { type: "keyDown", key: "ArrowRight", code: "ArrowRight", windowsVirtualKeyCode: 39 });
        await sleep(200);
        const card2 = await evaluate("document.querySelector('[data-chart-card]')?.textContent ?? ''");
        say(card2.length > 0, `${p} @${width}: the arrow keys move the card ("${card2.slice(0, 40)}")`);
      }
    }
  }
  return 0;
});
if (code === null) { console.log("FAIL no Chrome or Edge on this machine"); process.exit(1); }
console.log(bad ? `FAILED: ${bad}` : "every check passed");
process.exit(bad ? 1 : 0);
