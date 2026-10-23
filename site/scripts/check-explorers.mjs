// Energy Research Warehouse (ERW) site, session 2200 (chain 086): the signature explorers, read in a real browser.
//
//   node scripts/check-explorers.mjs <base> [--pages /a,/b] [--out runs/check-explorers.json] [--no-unlock]
//
// For each explorer view of check-values' list (`node scripts/check-values.mjs --list`: the addresses under /explore/
// and the ERCOT tab of /prices), in the internal view (every page is in review), it reads:
//   tips     every figure ([data-check]) has its source in its hover: a title (components/Num.tsx, `source`), or a Tip
//            it sits in or that follows it ([data-tip]); a figure with neither is a finding ("tip"), with its key
//   hover    every chart ([data-svg-chart], [data-time-chart], [data-series-chart], [data-bars]) shows a hover card
//            ([data-chart-card]) with at least one figure when the pointer moves over the middle of its plot; a chart
//            that shows none is a finding ("hover"), with the chart's id and kind
//   width    at 390 by 844, as a phone, the page's scroll width is at most 390; wider is a finding ("width")
// Each finding is one line: `<kind> | <page> | <what> | <why>`. Exit 0 when every page was read and none has a finding,
// 1 when a page has one, 2 on bad input, no browser, or a page not read. It reads only; nothing is written but the JSON.
// --no-unlock reads a site that needs no internal view (the test's fixture). The judging is `judge()`, a pure function
// of what the page gave, so scripts/test-check-explorers.mjs can hold it to fixtures without a browser.
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
export const CHART = "[data-svg-chart], [data-time-chart], [data-series-chart], [data-bars]";
export const CARD = "[data-chart-card]";
export const PHONE = { width: 390, height: 844 };

/** The explorers' views among check-values' pages: /explore/<name> and the ERCOT tab of /prices. */
export function explorerPages() {
  const j = JSON.parse(execFileSync(process.execPath, [path.join(here, "check-values.mjs"), "--list"], { encoding: "utf-8" }));
  return [...j.pages, ...j.internal].filter((p) => p.startsWith("/explore/") || p === "/prices?tab=ercot");
}

/** Run in the page: every figure's key and whether its source is in its hover, and every chart's place. */
export const READ = String.raw`(() => {
  const tips = Array.from(document.querySelectorAll("[data-check]")).map((el) => ({
    key: el.getAttribute("data-check"),
    title: el.getAttribute("title") || "",
    tip: !!(el.closest("[data-tip]") || (el.nextElementSibling && el.nextElementSibling.matches("[data-tip]"))),
  }));
  const charts = Array.from(document.querySelectorAll(${JSON.stringify(CHART)})).map((el, i) => {
    const kind = el.hasAttribute("data-svg-chart") ? "svg:" + el.getAttribute("data-svg-chart") : el.hasAttribute("data-time-chart") ? "time:" + el.getAttribute("data-time-chart") : el.hasAttribute("data-series-chart") ? "series" : "bars";
    const id = el.getAttribute("data-chart") || el.getAttribute("data-series-chart") || el.getAttribute("data-bars") || el.getAttribute("aria-label") || String(i);
    return { i, kind, id };
  });
  return { tips, charts, scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth };
})()`;

/** The findings of one page, from what the browser read. `hovers` is, by chart index, whether a card with a figure
 *  appeared; `phone` the scroll and client widths at 390. */
export function judge(page, reading, hovers, phone) {
  const out = [];
  for (const t of reading.tips) {
    if (!t.title && !t.tip) out.push({ kind: "tip", page, what: t.key, why: "the figure has no title and no tip beside it: its source is not in its hover" });
  }
  reading.charts.forEach((c, i) => {
    const h = hovers[i];
    if (!h || !h.card) out.push({ kind: "hover", page, what: `${c.kind} ${c.id}`, why: "no hover card appeared when the pointer moved over the plot" });
    else if (!h.figure) out.push({ kind: "hover", page, what: `${c.kind} ${c.id}`, why: "the hover card names no figure" });
  });
  if (phone && phone.scrollWidth > PHONE.width) out.push({ kind: "width", page, what: `${phone.scrollWidth} px`, why: `the page scrolls sideways at ${PHONE.width} px` });
  return out;
}

/** One page read in the browser: the reading, the hover of each chart, and the widths as a phone. */
export async function readPage(h, base, page) {
  await h.send("Emulation.setDeviceMetricsOverride", { width: 1280, height: 900, deviceScaleFactor: 1, mobile: false });
  await h.go(base + page);
  await h.sleep(1200);
  const reading = await h.evaluate(READ);
  const hovers = [];
  for (const c of reading.charts) {
    // the chart's plot into view, the pointer to its middle, the card read inside the chart's own box
    const rect = await h.evaluate(`(() => { const el = document.querySelectorAll(${JSON.stringify(CHART)})[${c.i}]; el.scrollIntoView({ block: "center" }); const r = el.getBoundingClientRect(); return { x: r.left + r.width * 0.55, y: r.top + r.height * 0.5 }; })()`);
    await h.send("Input.dispatchMouseEvent", { type: "mouseMoved", x: Math.round(rect.x), y: Math.round(rect.y) });
    await h.sleep(250);
    await h.send("Input.dispatchMouseEvent", { type: "mouseMoved", x: Math.round(rect.x) + 3, y: Math.round(rect.y) + 1 });
    await h.sleep(250);
    // the card is looked for inside the chart's own box only (a bar chart's SVG has its wrapper for a box)
    const card = await h.evaluate(`(() => { const el = document.querySelectorAll(${JSON.stringify(CHART)})[${c.i}]; const box = el.matches("[data-bars]") ? (el.parentElement || el) : el; const card = box.querySelector(${JSON.stringify(CARD)}); return card ? { card: true, figure: /[0-9]/.test(card.textContent || "") } : { card: false, figure: false }; })()`);
    hovers.push(card);
    await h.send("Input.dispatchMouseEvent", { type: "mouseMoved", x: 2, y: 2 });
  }
  await h.send("Emulation.setDeviceMetricsOverride", { width: PHONE.width, height: PHONE.height, deviceScaleFactor: 1, mobile: true });
  await h.go(base + page);
  await h.sleep(1200);
  const phone = await h.evaluate("({ scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth })");
  return { reading, hovers, phone };
}

export async function run(base, pages, { unlock = true } = {}) {
  const results = [];
  const code = await withBrowser(async (h) => {
    if (unlock) await h.unlock(base);
    for (const page of pages) {
      try {
        const r = await readPage(h, base, page);
        results.push({ page, read: true, figures: r.reading.tips.length, charts: r.reading.charts.length, phone: r.phone, findings: judge(page, r.reading, r.hovers, r.phone) });
      } catch (e) {
        results.push({ page, read: false, error: String(e.message || e), findings: [] });
      }
    }
    return 0;
  });
  if (code === null) return { code: 2, results, why: "no browser on this machine" };
  const unread = results.filter((r) => !r.read);
  const findings = results.flatMap((r) => r.findings);
  return { code: unread.length ? 2 : findings.length ? 1 : 0, results };
}

const isMain = process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url);
if (isMain) {
  const args = process.argv.slice(2);
  const take = (f) => { const i = args.indexOf(f); return i >= 0 ? args.splice(i, 2)[1] : undefined; };
  const only = take("--pages");
  const out = take("--out") ?? path.join(here, "..", "..", "runs", "check-explorers.json");
  const noUnlock = args.includes("--no-unlock"); if (noUnlock) args.splice(args.indexOf("--no-unlock"), 1);
  const base = args[0];
  if (!base) { console.error("usage: node scripts/check-explorers.mjs <base> [--pages /a,/b] [--out file.json] [--no-unlock]"); process.exit(2); }
  const pages = only ? only.split(",") : explorerPages();
  const r = await run(base, pages, { unlock: !noUnlock });
  for (const p of r.results) {
    console.log(p.read ? `read  ${p.page}: ${p.figures} figures, ${p.charts} charts, ${p.phone.scrollWidth} px wide as a phone, ${p.findings.length} findings` : `UNREAD ${p.page}: ${p.error}`);
    for (const f of p.findings) console.log(`  ${f.kind} | ${f.page} | ${f.what} | ${f.why}`);
  }
  if (r.why) console.log(r.why);
  fs.mkdirSync(path.dirname(out), { recursive: true });
  fs.writeFileSync(out, JSON.stringify({ at: new Date().toISOString(), base, results: r.results }, null, 1));
  console.log(`exit ${r.code}: ${r.results.filter((p) => p.read).length} of ${pages.length} pages read, ${r.results.flatMap((p) => p.findings).length} findings; ${out}`);
  process.exit(r.code);
}
