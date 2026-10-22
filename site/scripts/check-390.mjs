// Energy Research Warehouse (ERW) site, session 584: every page of check-values' list at 390 by 844, measured.
//
//   node scripts/check-390.mjs <base> <out.json> [shots-dir] [--pages a,b,c]
//
// Opens the internal view (every page is in review), sets the window to 390 by 844 as a phone (mobile emulation, the
// page's own viewport tag), loads each page of `node scripts/check-values.mjs --list` (pages and internal), and lists:
//   wide    each element or run of text that reaches past the window's right edge with no ancestor that clips or
//           scrolls it sideways (the outermost of each nest; the inside of a closed <details> is not drawn and is
//           left out), and the page's own scroll width
//   tables  each table with no ancestor that scrolls it sideways (overflow-x auto or scroll), and whether it is wider
//           than its frame
//   labels  each SVG text cut by its own SVG (overflow not visible) or by an ancestor that clips, or past the window's
//           left or right edge (1.5 px at a side; 3.5 px at the top or the bottom, past its em box's empty margin). Labels drawn on a canvas (ECharts) cannot be read from the page and are not judged.
// With a shots directory, a picture of the window for each page that has a finding, scrolled to its first one.
// Exit 0 when every page was read and none has a finding, 1 when a page has one, 2 on bad input or a page not read.
// It reads only; nothing is written but the JSON and the pictures.
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { withBrowser } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const flag = args.indexOf("--pages");
const only = flag >= 0 ? args.splice(flag, 2)[1].split(",") : null;
const [base, out, shots] = args;
if (!base || !out) { console.error("usage: node scripts/check-390.mjs <base> <out.json> [shots-dir] [--pages a,b,c]"); process.exit(2); }

function pageList() {
  if (only) return only;
  const j = JSON.parse(execFileSync(process.execPath, [path.join(here, "check-values.mjs"), "--list"], { encoding: "utf-8" }));
  return [...j.pages, ...j.internal];
}

/** The measure, run in the page. Kept as a string so the browser runs exactly this text. */
export const MEASURE = String.raw`(() => {
  const W = document.documentElement.clientWidth;
  const sel = (el) => {
    const parts = [];
    for (let e = el, i = 0; e && e !== document.body && i < 4; e = e.parentElement, i += 1) {
      let s = e.tagName.toLowerCase();
      if (e.id) { s += "#" + e.id; parts.unshift(s); break; }
      const cls = typeof e.className === "string" ? e.className.trim().split(/\s+/).filter(Boolean).slice(0, 3) : [];
      if (cls.length) s += "." + cls.join(".");
      parts.unshift(s);
    }
    return parts.join(" > ");
  };
  const hidden = (el) => { for (let e = el; e; e = e.parentElement) { if (e.parentElement && e.parentElement.tagName === "DETAILS" && !e.parentElement.open && e.tagName !== "SUMMARY") return true; const cs = getComputedStyle(e); if (cs.display === "none" || cs.visibility === "hidden") return true; if (cs.position === "fixed") return "fixed"; } return false; };
  const clipAncestor = (el, stopAt) => {
    for (let p = el.parentElement; p && p !== document.body && p !== document.documentElement; p = p.parentElement) {
      if (p === stopAt) return null;
      const ox = getComputedStyle(p).overflowX;
      if (ox !== "visible") return p;
    }
    return null;
  };
  // 1. wide: elements past the right edge, not clipped or scrolled by an ancestor (the outermost of a nest)
  const over = new Set();
  for (const el of document.body.querySelectorAll("*")) {
    if (el.closest("svg") && el.tagName.toLowerCase() !== "svg") continue;
    const r = el.getBoundingClientRect();
    if (r.width === 0 || r.height === 0 || r.right <= W + 1) continue;
    if (clipAncestor(el)) continue;
    if (hidden(el)) continue;
    over.add(el);
  }
  const wide = [];
  for (const el of over) if (!over.has(el.parentElement)) { const r = el.getBoundingClientRect(); wide.push({ sel: sel(el), right: Math.round(r.right + scrollX), width: Math.round(r.width), text: (el.textContent || "").trim().slice(0, 60) }); }
  // runs of text past the edge whose element is not already listed
  const tw = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  const textOver = new Set();
  for (let n = tw.nextNode(); n; n = tw.nextNode()) {
    if (!n.textContent.trim()) continue;
    const el = n.parentElement;
    if (!el || el.closest("svg") || el.closest("script,style,noscript")) continue;
    const rg = document.createRange(); rg.selectNodeContents(n);
    let right = 0; for (const rr of rg.getClientRects()) right = Math.max(right, rr.right);
    if (right <= W + 1) continue;
    if (clipAncestor(n.parentElement ? { parentElement: n.parentElement } : el)) continue;
    if (hidden(el)) continue;
    let listed = false; for (let e = el; e; e = e.parentElement) if (over.has(e)) { listed = true; break; }
    if (listed || textOver.has(el)) continue;
    textOver.add(el);
    wide.push({ sel: sel(el), right: Math.round(right + scrollX), width: null, text: n.textContent.trim().slice(0, 60), kind: "text" });
  }
  // 2. tables with no sideways scroll container
  const tables = [];
  for (const t of document.querySelectorAll("table")) {
    const r = t.getBoundingClientRect();
    if (r.width === 0 || hidden(t)) continue;
    let scroller = null;
    for (let p = t.parentElement; p && p !== document.body; p = p.parentElement) { const ox = getComputedStyle(p).overflowX; if (ox === "auto" || ox === "scroll") { scroller = p; break; } }
    if (!scroller) { const ox = getComputedStyle(t).overflowX; if ((ox === "auto" || ox === "scroll") && getComputedStyle(t).display === "block") scroller = t; }
    if (scroller) continue;
    const frame = t.parentElement.getBoundingClientRect();
    tables.push({ sel: sel(t), width: Math.round(Math.max(r.width, t.scrollWidth)), frame: Math.round(frame.width), wider: r.right > W + 1 || t.scrollWidth > frame.width + 1, caption: (t.querySelector("caption,th")?.textContent || "").trim().slice(0, 50) });
  }
  // 3. SVG labels cut
  const labels = [];
  for (const svg of document.querySelectorAll("svg")) {
    const sr = svg.getBoundingClientRect();
    if (sr.width < 40 || sr.height < 20 || hidden(svg)) continue;
    if (svg.parentElement && svg.parentElement.closest("svg")) continue;
    const svgClips = getComputedStyle(svg).overflow !== "visible";
    let box = svgClips ? { l: sr.left, r: sr.right, t: sr.top, b: sr.bottom } : { l: -1e9, r: 1e9, t: -1e9, b: 1e9 };
    let scrolls = false;
    for (let p = svg.parentElement; p && p !== document.body; p = p.parentElement) {
      const cs = getComputedStyle(p);
      if (cs.overflowX === "auto" || cs.overflowX === "scroll") { scrolls = true; break; }
      if (cs.overflowX !== "visible" || cs.overflowY !== "visible") { const pr = p.getBoundingClientRect(); box = { l: Math.max(box.l, pr.left), r: Math.min(box.r, pr.right), t: Math.max(box.t, pr.top), b: Math.min(box.b, pr.bottom) }; }
    }
    if (!scrolls) { box.l = Math.max(box.l, 0); box.r = Math.min(box.r, W); }
    const cut = [];
    for (const tx of svg.querySelectorAll("text")) {
      if (!tx.textContent.trim()) continue;
      const cs = getComputedStyle(tx);
      if (cs.display === "none" || cs.visibility === "hidden" || cs.opacity === "0") continue;
      if (tx.closest("[clip-path]")) continue;
      const r = tx.getBoundingClientRect();
      if (r.width === 0) continue;
      // a text's box is its font's em box: above and below it holds 3 px or so where no glyph is drawn, so a text is cut
      // at the top or the bottom only past that; at the sides its box is its advance, and 1.5 px is a cut
      const sides = { left: box.l - r.left, right: r.right - box.r }, ends = { top: box.t - r.top, bottom: r.bottom - box.b };
      const hit = Object.entries(sides).find(([, v]) => v > 1.5) ?? Object.entries(ends).find(([, v]) => v > 3.5);
      if (hit) cut.push({ text: tx.textContent.trim().slice(0, 40), by: Math.round(hit[1]), side: hit[0] });
    }
    if (cut.length) labels.push({ sel: sel(svg), label: (svg.getAttribute("aria-label") || svg.querySelector("title")?.textContent || "").slice(0, 60), cut: cut.slice(0, 6), count: cut.length });
  }
  return { W, scrollWidth: document.documentElement.scrollWidth, wide: wide.slice(0, 12), wideCount: wide.length, tables, labels };
})()`;

const pages = pageList();
const results = [];
let failed = 0;
const code = await withBrowser(async ({ go, evaluate, unlock, send, sleep }) => {
  await unlock(base);
  await send("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
  if (shots) fs.mkdirSync(shots, { recursive: true });
  for (const p of pages) {
    const url = base + p;
    try {
      await go(url);
      await sleep(1800);
      const m = await evaluate(MEASURE);
      const findings = m.wide.length + m.tables.length + m.labels.length;
      results.push({ page: p, ...m, findings });
      console.log(`${findings ? "FIND" : "ok  "} ${p}  scroll ${m.scrollWidth}/${m.W}  wide ${m.wideCount}  tables ${m.tables.length}  labels ${m.labels.length}`);
      if (shots && findings) {
        const target = m.wide[0]?.sel ?? m.tables[0]?.sel ?? m.labels[0]?.sel;
        if (target) await evaluate(`(() => { const e = document.querySelector(${JSON.stringify(target.replace(/ > /g, " "))}); if (e) e.scrollIntoView({ block: "center" }); })()`).catch(() => {});
        await sleep(500);
        const shot = await send("Page.captureScreenshot", { format: "png" });
        const name = (p.replace(/^\//, "") || "home").replace(/[^a-z0-9]+/gi, "_").replace(/_+$/, "") + ".png";
        fs.writeFileSync(path.join(shots, name), Buffer.from(shot.data, "base64"));
        await evaluate("scrollTo(0, 0)").catch(() => {});
      }
    } catch (e) {
      failed += 1;
      results.push({ page: p, error: String(e.message || e) });
      console.log(`ERR  ${p}  ${e.message || e}`);
    }
  }
  return 0;
}, { width: 390, height: 844 });
fs.writeFileSync(out, JSON.stringify({ base, at: new Date().toISOString(), pages: results }, null, 1));
if (code === null) { console.error("no browser on this machine: not proven here"); process.exit(2); }
const withFindings = results.filter((r) => r.findings).length;
console.log(`${results.length} pages read, ${failed} not read, ${withFindings} with a finding`);
process.exit(failed ? 2 : withFindings ? 1 : 0);
