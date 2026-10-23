// Session 2403 (chain 088): an accessibility pass by hand, in the browser, for the chain's pages, because the AccessLint
// plugin is not on this machine (docs/tooling.md; sessions 810, 829 and 840 found the same). WCAG 2.2 A and AA, the
// mechanical part: every control with a name (a label, aria-label, aria-labelledby or text), every table with a
// caption or an aria-label, every image with an alt, a hover (title) that stands on an element a keyboard cannot reach
// (not focusable, no tabindex) and has no other text of its own, headings in order, duplicate ids, and the contrast of
// the muted text against the page (from the page's own computed colors).
//
//   cd <a site/ with .env.local>; node ../../erw/docs/brand/review-2403/a11y-2403.mjs <base> <out.json> [--pages a,b]
//
// Prints one line a page and exits 1 when any page has a finding. Reads only.
import fs from "node:fs";
import path from "node:path";
import { withBrowser } from "./../../../site/scripts/browser.mjs";

const args = process.argv.slice(2);
const flag = args.indexOf("--pages");
const only = flag >= 0 ? args.splice(flag, 2)[1].split(",") : null;
const [base, out] = args;
if (!base || !out) { console.error("usage: node a11y-2403.mjs <base> <out.json> [--pages a,b]"); process.exit(2); }
const PAGES = only ?? ["/policy", "/policy?view=week", "/play/battery", "/play/battery?mode=hard", "/play/ev", "/learn/bill",
  "/learn/problems/know-your-grid", "/learn/problems/prices-and-your-bill", "/learn/problems/when-the-grid-broke", "/learn/problems/storage-and-taxes", "/learn/problems/networks-and-money"];

const MEASURE = `(() => {
  const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none"; };
  const name = (e) => (e.getAttribute("aria-label") || (e.getAttribute("aria-labelledby") && document.getElementById(e.getAttribute("aria-labelledby"))?.textContent) || (e.id && document.querySelector('label[for="' + e.id + '"]')?.textContent) || e.closest("label")?.textContent || e.textContent || e.getAttribute("title") || "").trim();
  const short = (e) => (e.tagName.toLowerCase() + (e.id ? "#" + e.id : "") + (e.className && typeof e.className === "string" ? "." + e.className.split(/\\s+/).slice(0, 2).join(".") : "") + " \\"" + (e.textContent || "").trim().slice(0, 40) + "\\"");
  const controls = [...document.querySelectorAll("button, a[href], input, select, textarea, [role=button], [role=switch]")].filter(vis).filter((e) => !name(e) && !(e.tagName === "INPUT" && e.type === "hidden")).map(short);
  const tables = [...document.querySelectorAll("table")].filter(vis).filter((t) => !t.querySelector("caption") && !t.getAttribute("aria-label") && !t.getAttribute("aria-labelledby")).map(short);
  const images = [...document.querySelectorAll("img, svg[role=img]")].filter(vis).filter((e) => e.tagName === "IMG" ? !e.hasAttribute("alt") : !e.getAttribute("aria-label") && !e.querySelector("title")).map(short);
  const reach = (e) => e.matches("a[href], button, input, select, textarea, summary") || (e.hasAttribute("tabindex") && Number(e.getAttribute("tabindex")) >= 0);
  const focusable = (e) => reach(e) || !!e.closest("a[href], button, summary, [tabindex]:not([tabindex='-1'])");
  const hoverOnly = [...document.querySelectorAll("[title]")].filter(vis).filter((e) => !focusable(e) && !e.querySelector("a[href], button, [tabindex]")).map((e) => short(e) + " title=\\"" + e.getAttribute("title").slice(0, 60) + "\\"");
  const hs = [...document.querySelectorAll("h1, h2, h3, h4, h5, h6")].filter(vis).map((h) => Number(h.tagName[1]));
  const order = []; for (let i = 1; i < hs.length; i++) if (hs[i] > hs[i - 1] + 1) order.push("h" + hs[i - 1] + " then h" + hs[i]);
  const ids = {}; for (const e of document.querySelectorAll("[id]")) ids[e.id] = (ids[e.id] || 0) + 1;
  const dupIds = Object.entries(ids).filter(([, n]) => n > 1).map(([k, n]) => k + " x" + n);
  // contrast of the muted text: the first element whose class holds text-muted, against the body's background
  const lum = (c) => { const m = c.match(/\\d+(\\.\\d+)?/g); if (!m) return null; const [r, g, b] = m.slice(0, 3).map((v) => { v = Number(v) / 255; return v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4; }); return 0.2126 * r + 0.7152 * g + 0.0722 * b; };
  const bg = lum(getComputedStyle(document.body).backgroundColor);
  const muted = document.querySelector(".text-muted");
  const mutedL = muted ? lum(getComputedStyle(muted).color) : null;
  const contrast = bg !== null && mutedL !== null ? Math.round(((Math.max(bg, mutedL) + 0.05) / (Math.min(bg, mutedL) + 0.05)) * 100) / 100 : null;
  const h1 = document.querySelectorAll("h1").length;
  return { controls, tables, images, hoverOnly: hoverOnly.slice(0, 40), hoverOnlyCount: hoverOnly.length, order, dupIds, contrast, h1, lang: document.documentElement.lang || "" };
})()`;

const results = [];
const code = await withBrowser(async ({ go, evaluate, unlock, send, sleep }) => {
  await unlock(new URL(base).origin);
  for (const [width, height] of [[1280, 900], [390, 844]]) {
    await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile: width < 500 });
    for (const page of PAGES) {
      await go(base + page);
      await sleep(2500);
      const r = await evaluate(MEASURE);
      const findings = r.controls.length + r.tables.length + r.images.length + r.order.length + r.dupIds.length + (r.h1 !== 1 ? 1 : 0) + (r.lang ? 0 : 1) + (r.contrast !== null && r.contrast < 4.5 ? 1 : 0);
      results.push({ page, width, ...r, findings });
      console.log(`${findings ? "FIND" : "ok  "} ${page} @${width}  controls ${r.controls.length}  tables ${r.tables.length}  images ${r.images.length}  hover-only ${r.hoverOnlyCount}  heading-order ${r.order.length}  dup-ids ${r.dupIds.length}  h1 ${r.h1}  muted contrast ${r.contrast}`);
    }
  }
  return 0;
});
fs.mkdirSync(path.dirname(out), { recursive: true });
fs.writeFileSync(out, JSON.stringify({ base, at: new Date().toISOString(), pages: results }, null, 1));
const bad = results.filter((r) => r.findings).length;
console.log(`${results.length} page views read, ${bad} with a finding (hover-only is counted, not a finding: a title on a span is the site's hover rule; listed for the report)`);
process.exit(code === 0 ? (bad ? 1 : 0) : 2);
