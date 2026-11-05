// Energy Research Warehouse (ERW), session 401: the five tool pages in the internal view (every page is in review), at
// 1280 and at 390 px wide, before and after the session's fixes. For each page and width: a shot of the window at the
// top into this folder (<name>_<width>_<stage>.png), a full-page shot (JPEG, capped) into the run folder for the
// critiques, and one JSON of what the page carried: every checked figure (data-check, data-raw, the text shown), and
// the measurements the tools' findings are read against (text under 12 px, targets under 24 px, a page wider than the
// window, the heading outline, fields with no name, cardinal used outside a link or a control, round corners).
//
//   cd site && npx next start -p 3401
//   node docs/brand/review-401/shots-401.mjs http://localhost:3401 <stage: before|after> <run-dir>
//
// The internal view is opened by unlock(base) from site/scripts/browser.mjs: the token is posted by the form, never in
// an address, and never printed. Exit 1 when a page could not be read.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3401").replace(/\/$/, "");
const stage = process.argv[3] ?? "before";
const runDir = process.argv[4] ?? here;
fs.mkdirSync(runDir, { recursive: true });
const WIDTHS = [[1280, 900, false], [390, 844, true]];
const PAGES = [
  ["battery", "/cost-of-power/battery"],
  ["seller", "/cost-of-power/seller"],
  ["cost-of-power", "/cost-of-power"],
  ["cost-of-power-grids", "/cost-of-power?view=grids"],
  ["research", "/analysis"],
  ["grid", "/grid"],
];
const FULL_CAP = 9000;

const MEASURE = `(() => {
  const vis = (e) => { const r = e.getBoundingClientRect(); const s = getComputedStyle(e); return r.width > 0 && r.height > 0 && s.visibility !== "hidden" && s.display !== "none"; };
  const where = (e) => { const p = []; let x = e; for (let i = 0; x && i < 4; i += 1, x = x.parentElement) { let t = x.tagName.toLowerCase(); const d = [...x.attributes].find((a) => a.name.startsWith("data-")); if (x.id) t += "#" + x.id; else if (d) t += "[" + d.name + "]"; p.unshift(t); } return p.join(" > "); };
  const own = (e) => [...e.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
  const txt = (e) => e.textContent.replace(/\\s+/g, " ").trim().slice(0, 80);
  const all = [...document.querySelectorAll("body *")];
  const small = all.filter((e) => own(e) && vis(e) && parseFloat(getComputedStyle(e).fontSize) < 12 && !e.closest("svg"));
  const svgSmall = [...document.querySelectorAll("svg text")].filter((e) => vis(e) && parseFloat(getComputedStyle(e).fontSize) < 12);
  const ctl = [...document.querySelectorAll("a[href], button, input:not([type=hidden]), select, textarea, summary")].filter(vis);
  const inText = (e) => e.tagName === "A" && e.parentElement && ["P", "LI", "TD", "SPAN", "DIV"].includes(e.parentElement.tagName) && e.parentElement.textContent.trim().length > e.textContent.trim().length + 2;
  const targetOf = (e) => { const l = (e.tagName === "INPUT" && (e.type === "radio" || e.type === "checkbox")) ? e.closest("label") : null; return (l || e).getBoundingClientRect(); };
  const smallTargets = ctl.filter((e) => !inText(e)).filter((e) => { const r = targetOf(e); return r.width < 24 || r.height < 24; });
  const nameOf = (e) => (e.getAttribute("aria-label") || (e.labels && e.labels[0] && e.labels[0].textContent) || e.getAttribute("title") || e.getAttribute("aria-labelledby") || "").trim();
  const unnamed = [...document.querySelectorAll("input:not([type=hidden]), select, textarea")].filter((e) => vis(e) && !nameOf(e));
  const btnNames = {}; for (const b of [...document.querySelectorAll("button, a[href]")].filter(vis)) { const n = (b.getAttribute("aria-label") || b.textContent).replace(/\\s+/g, " ").trim(); if (n) btnNames[n] = (btnNames[n] || 0) + 1; }
  const dupes = Object.entries(btnNames).filter(([n, c]) => c > 1 && /^(reset|show|more|here|csv|method|download)/i.test(n));
  const CARD = "rgb(140, 21, 21)";
  const cardText = all.filter((e) => own(e) && vis(e) && getComputedStyle(e).color === CARD && !e.closest("a, button, summary, label, svg, [aria-pressed]"));
  const cardBg = all.filter((e) => vis(e) && getComputedStyle(e).backgroundColor === CARD && !e.closest("a, button, [aria-pressed], svg") && e.tagName !== "SPAN");
  const round = all.filter((e) => vis(e) && !e.closest("svg") && parseFloat(getComputedStyle(e).borderTopLeftRadius) > 0 && !["INPUT", "SELECT", "TEXTAREA"].includes(e.tagName));
  const heads = [...document.querySelectorAll("h1, h2, h3, h4, h5, h6")].filter(vis).map((h) => Number(h.tagName[1]));
  const skips = []; for (let i = 1; i < heads.length; i += 1) if (heads[i] > heads[i - 1] + 1) skips.push(heads[i - 1] + ">" + heads[i]);
  const pos = [...document.querySelectorAll("[tabindex]")].filter((e) => Number(e.getAttribute("tabindex")) > 0).length;
  const sample = (l, f) => l.slice(0, 12).map(f);
  return {
    url: location.pathname + location.search,
    inReview: !!document.querySelector("[data-in-review]"),
    unreadable: (document.body.innerText.match(/[^\\n]*could not be read[^\\n]*/g) || []).slice(0, 5),
    title: document.title,
    height: document.documentElement.scrollHeight,
    scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
    checks: [...document.querySelectorAll("[data-check]")].map((e) => [e.getAttribute("data-check"), e.getAttribute("data-raw"), e.textContent.replace(/\\s+/g, " ").trim()]),
    smallText: { n: small.length, sizes: [...new Set(small.map((e) => getComputedStyle(e).fontSize))], at: sample(small, (e) => [getComputedStyle(e).fontSize, where(e), txt(e)]) },
    svgSmall: { n: svgSmall.length, sizes: [...new Set(svgSmall.map((e) => getComputedStyle(e).fontSize))] },
    smallTargets: { n: smallTargets.length, of: ctl.length, at: sample(smallTargets, (e) => { const r = targetOf(e); return [Math.round(r.width) + "x" + Math.round(r.height), where(e), txt(e) || e.getAttribute("aria-label") || e.type]; }) },
    unnamed: { n: unnamed.length, at: sample(unnamed, (e) => [where(e), e.outerHTML.slice(0, 140)]) },
    dupeNames: dupes,
    cardinalText: { n: cardText.length, at: sample(cardText, (e) => [e.tagName.toLowerCase(), where(e), txt(e)]) },
    cardinalBg: { n: cardBg.length, at: sample(cardBg, (e) => [e.tagName.toLowerCase(), where(e), txt(e)]) },
    round: { n: round.length, at: sample(round, (e) => [getComputedStyle(e).borderTopLeftRadius, where(e), txt(e)]) },
    headings: heads.join(""), headingSkips: skips,
    positiveTabindex: pos,
    focusable: ctl.length,
  };
})()`;

let failed = 0;
for (const [width, height, mobile] of WIDTHS) {
  const res = await withBrowser(async ({ go, evaluate, wait, unlock, send, sleep, errors }) => {
    await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile });
    await unlock(base);
    const out = [];
    for (const [name, page] of PAGES) {
      const rec = { name, page, width };
      try {
        await go(base + page);
        await wait("document.readyState === 'complete'", 60000, page);
        await sleep(3500);   // the charts draw after hydration
        Object.assign(rec, await evaluate(MEASURE));
        await evaluate("window.scrollTo(0, 0)");
        await sleep(400);
        const shot = await send("Page.captureScreenshot", { format: "png" });
        fs.writeFileSync(path.join(here, `${name}_${width}_${stage}.png`), Buffer.from(shot.data, "base64"));
        const h = Math.min(rec.height, FULL_CAP);
        const full = await send("Page.captureScreenshot", { format: "jpeg", quality: 55, captureBeyondViewport: true, clip: { x: 0, y: 0, width, height: h, scale: width > 600 ? 0.6 : 1 } });
        fs.writeFileSync(path.join(runDir, `full_${name}_${width}_${stage}.jpg`), Buffer.from(full.data, "base64"));
        console.log(`ok   ${name} ${width}: ${rec.url}, ${rec.checks.length} checked figures, height ${rec.height}${rec.unreadable.length ? ", UNREADABLE: " + rec.unreadable[0] : ""}${rec.inReview ? ", IN REVIEW (not unlocked)" : ""}`);
      } catch (e) {
        failed += 1; rec.error = String(e.message ?? e);
        console.log(`FAIL ${name} ${width}: ${rec.error}`);
      }
      out.push(rec);
    }
    return { pages: out, pageErrors: errors };
  }, { width, height });
  if (!res) { console.log("no browser on this machine"); process.exit(1); }
  fs.writeFileSync(path.join(runDir, `measure-${width}-${stage}.json`), JSON.stringify(res, null, 1));
}
process.exit(failed ? 1 : 0);
