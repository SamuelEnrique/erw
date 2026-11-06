// Energy Research Warehouse (ERW), session 810: the Digest and Roundup pages and the email's HTML at 1280 x 800 and
// 390 x 844, photographed over the DevTools protocol (site/scripts/browser.mjs), with the measures a reader at 390 px
// cares about written beside each shot: whether the page is wider than the viewport, how many tables sit in a scroll
// container, the widest table's overflow, the chart image's drawn width, and the links reachable (inside the viewport's
// width).
//   node docs/brand/review-810/shot-810.mjs <out dir> <label>=<url> ...     (from the repository root; site/node_modules present)
// A url that starts with http is a page (the internal view is opened first); a file:// url is an email's HTML.
import fs from "node:fs";
import path from "node:path";
import { withBrowser } from "../../../site/scripts/browser.mjs";
const [out, ...targets] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const lines = [];
const MEASURE = `(() => {
  const vw = document.documentElement.clientWidth;
  const tables = [...document.querySelectorAll("table")];
  const scrolls = tables.filter((t) => { const p = t.parentElement; const own = getComputedStyle(t).overflowX; const par = p ? getComputedStyle(p).overflowX : ""; return ["auto", "scroll"].includes(own) || ["auto", "scroll"].includes(par); }).length;
  const widest = Math.max(0, ...tables.map((t) => t.scrollWidth));
  const img = document.querySelector("img[src*='chart'], img[alt*='MWh'], img[alt*='USD'], img[src*='.png']");
  const links = [...document.querySelectorAll("a[href]")];
  const outside = links.filter((a) => { const r = a.getBoundingClientRect(); return r.width > 0 && (r.right > vw + 1 || r.left < -1); }).length;
  return { vw, pageW: document.documentElement.scrollWidth, pageH: document.documentElement.scrollHeight, tables: tables.length, scrolls, widest,
           img: img ? Math.round(img.getBoundingClientRect().width) : null, links: links.length, outside };
})()`;
const code = await withBrowser(async ({ go, unlock, send, sleep }) => {
  const js = async (expression) => (await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true })).result?.value;
  let unlocked = "";
  for (const t of targets) {
    const i = t.indexOf("=");
    const label = t.slice(0, i), url = t.slice(i + 1);
    const base = url.startsWith("http") ? new URL(url).origin : "";
    if (base && base !== unlocked) { await unlock(base); unlocked = base; }
    for (const [w, h, mobile] of [[1280, 800, false], [390, 844, true]]) {
      await send("Emulation.setDeviceMetricsOverride", { width: w, height: h, deviceScaleFactor: 1, mobile });
      await go(url);
      await sleep(1200);
      await js("document.fonts.ready.then(() => true)");
      const m = await js(MEASURE);
      lines.push(`${label} ${w}x${h}: page ${m.pageW}x${m.pageH} px (viewport ${m.vw}); tables ${m.tables}, in a scroll container ${m.scrolls}, widest ${m.widest} px; `
        + `chart image ${m.img === null ? "none" : m.img + " px wide"}; links ${m.links}, outside the viewport ${m.outside}`);
      const s = await send("Page.captureScreenshot", { format: "png", clip: { x: 0, y: 0, width: w, height: Math.min(Math.max(h, m.pageH), 6000), scale: 1 }, captureBeyondViewport: true });
      fs.writeFileSync(path.join(out, `${label}_${w}x${h}.png`), Buffer.from(s.data, "base64"));
    }
  }
  return 0;
}, { width: 1280, height: 800 });
fs.writeFileSync(path.join(out, "measures-810.txt"), lines.join("\n") + "\n");
console.log(lines.join("\n"));
process.exit(code ?? 2);
