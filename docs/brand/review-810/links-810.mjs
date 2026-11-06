// Energy Research Warehouse (ERW), session 810: which links sit outside a 390 px viewport on a page, and whether each
// is inside a scroll container (reachable by scrolling it) or not.
//   node docs/brand/review-810/links-810.mjs <url>...     (the internal view is opened first)
import { withBrowser } from "../../../site/scripts/browser.mjs";
const urls = process.argv.slice(2);
const JS = `(() => {
  const vw = document.documentElement.clientWidth;
  const inScroll = (el) => { for (let p = el.parentElement; p; p = p.parentElement) { const o = getComputedStyle(p).overflowX; if (o === "auto" || o === "scroll") return true; } return false; };
  const out = [];
  for (const a of document.querySelectorAll("a[href]")) {
    const r = a.getBoundingClientRect();
    if (r.width > 0 && (r.right > vw + 1 || r.left < -1)) out.push({ text: (a.textContent || "").trim().slice(0, 40), href: a.getAttribute("href").slice(0, 60), right: Math.round(r.right), scroll: inScroll(a) });
  }
  return { vw, out };
})()`;
const code = await withBrowser(async ({ go, unlock, send, sleep }) => {
  const js = async (expression) => (await send("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true })).result?.value;
  let unlocked = "";
  for (const url of urls) {
    const base = new URL(url).origin;
    if (base !== unlocked) { await unlock(base); unlocked = base; }
    await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
    await go(url);
    await sleep(1200);
    const m = await js(JS);
    const unreachable = m.out.filter((x) => !x.scroll);
    console.log(`${url}: ${m.out.length} links beyond ${m.vw} px, ${unreachable.length} of them not in a scroll container`);
    for (const x of m.out.slice(0, 12)) console.log(`  ${x.scroll ? "in a scroll container" : "NOT in one"} | right ${x.right} | ${x.text} | ${x.href}`);
  }
  return 0;
}, { width: 390, height: 844 });
process.exit(code ?? 2);
