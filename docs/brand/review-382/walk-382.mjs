// Energy Research Warehouse (ERW), session 382: the trader path, walked click by click in a real browser, in the internal
// view (every page is in review), at 1280 and at 390 px wide. One shot a step and a width into this folder, named by
// the step (01-seller_1280.png), and one JSON a width of what each step showed: its address, whether the live set
// could be read, the checked figures in view (data-check and data-raw; the board's data-n), the text of the part in view.
// The 1280 pass also asks every same-origin link of the three pages for its status (never /internal/, which would lock
// the view, and never another host). docs/reviews/trader-path.md is written from these files.
//
//   cd site && npx next start -p 3382
//   node docs/brand/review-382/walk-382.mjs http://localhost:3382 <json-dir> [only-steps]
//
// The internal view is opened by unlock(base) from site/scripts/browser.mjs: the token is posted by the form, never in
// an address, and never printed. Exit 1 when a step could not be made.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3382").replace(/\/$/, "");
const jsonDir = process.argv[3] ?? here;
const only = (process.argv[4] ?? "").split(",").filter(Boolean);
const WIDTHS = [[1280, 900, false], [390, 844, true]];

const js = (s) => JSON.stringify(s);
// in-page helpers, put on window once a page is loaded
const HELPERS = `(() => {
  window.__h = {
    byText(sel, start) { return [...document.querySelectorAll(sel)].find((e) => e.textContent.replace(/\\s+/g, " ").trim().startsWith(start)) || null; },
    click(el) { if (!el) throw new Error("nothing to click"); el.scrollIntoView({ block: "center" }); el.click(); return true; },
  };
  return true;
})()`;

/** Each step: what the reader does (act, in the page), what is shown (focus: a CSS selector, or a heading's first words). */
const STEPS = [
  { id: "01-seller", page: "/cost-of-power/seller", focus: "h1" },
  { id: "02-seller-wind", act: `__h.click(document.querySelector('[data-asset="wind"] input'))`, until: "location.search.includes('asset=wind')", focus: "h1" },
  { id: "03-seller-west", act: `(() => { const s = document.querySelector('select[data-hub]'); s.value = 'HB_WEST'; s.dispatchEvent(new Event('change', { bubbles: true })); __h.click(__h.byText('form[data-seller-form] button', 'Show')); return true; })()`,
    until: "location.search.includes('hub=HB_WEST')", focus: "h1" },
  { id: "04-seller-capture", focus: "text:h3:What it earned per MWh against the hub average" },
  { id: "05-seller-caiso", act: `__h.click(document.querySelector('[data-grid="caiso"] input'))`, until: "location.search.includes('iso=caiso')", focus: "h1" },
  { id: "06-seller-ppa", act: `__h.click(__h.byText('button', 'Make B a PPA'))`, settle: 2500, focus: "text:td,th:Breakeven PPA price", block: "center" },
  { id: "07-battery", act: `__h.click(__h.byText('nav[aria-label="Cost of power"] a', 'What a battery earns'))`, until: "location.pathname === '/cost-of-power/battery'", focus: "h1" },
  { id: "08-battery-awards", focus: "[data-awards-beside]", block: "center" },
  { id: "09-battery-2h", act: `__h.click(document.querySelector('a[data-duration="2"]'))`, until: "location.search.includes('dur=2')", focus: "h1" },
  { id: "10-battery-4h-dayahead", act: `__h.click(document.querySelector('a[data-duration="4"]'))`, until: "location.search.includes('dur=4')",
    then: `(() => { __h.click(document.querySelector('input[name="strat"][value="dayahead"]')); __h.click(__h.byText('form[action="/cost-of-power/battery"] button', 'Show')); return true; })()`,
    until2: "location.search.includes('strat=dayahead')", focus: "h1" },
  { id: "11-battery-caiso", act: `(() => { __h.click(document.querySelector('input[name="grid"][value="caiso"]')); __h.click(__h.byText('form[action="/cost-of-power/battery"] button', 'Show')); return true; })()`,
    until: "location.search.includes('grid=caiso')", focus: "h1" },
  { id: "12-battery-income", focus: "text:h3:Income by stream" },
  { id: "13-board", act: `(() => { const a = [...document.querySelectorAll('a[href="/board"]')][0]; a.click(); return true; })()`, until: "location.pathname === '/board' && !!document.querySelector('[data-board][data-ready]')", focus: "h1" },
  { id: "14-board-workbench", act: `__h.click(__h.byText('[data-top-twelve] button', 'ERCOT Hub averageday-ahead'))`, settle: 3000, focus: "aside[aria-label=\"Markets workbench\"]" },
  { id: "15-board-ercot-hubs", act: `(() => { const pick = (f) => { const x = document.querySelector('[data-filter="' + f + '"]'); if (x) x.click(); return !!x; }; return [pick('power.grid.ERCOT'), pick('power.scope.all')]; })()`,
    settle: 2000, focus: "#power" },
  { id: "16-board-week", act: `(() => { const d = document.querySelector('#week details'); if (d && !d.open) d.querySelector('summary').click(); return !!d; })()`, settle: 2000, focus: "#week" },
];

const LOOK = (focus) => `(() => {
  const f = ${js(focus)};
  let el = null;
  if (f.startsWith("text:")) { const [, sel, start] = f.match(/^text:([^:]+):(.*)$/); el = __h.byText(sel, start); }
  else el = document.querySelector(f);
  const scope = el ? (el.closest("section") || el.parentElement || el) : document.body;
  const vis = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight; };
  return {
    url: location.pathname + location.search,
    found: !!el,
    unreadable: document.body.innerText.includes("could not be read"),
    inReview: !!document.querySelector("[data-in-review]"),
    errorText: (document.body.innerText.match(/[^\\n]*(Application error|could not be read)[^\\n]*/) || [""])[0],
    checksInView: [...document.querySelectorAll("[data-check]")].filter(vis).map((e) => ({ k: e.getAttribute("data-check"), raw: e.getAttribute("data-raw"), text: e.textContent.trim() })).slice(0, 120),
    nsInView: [...document.querySelectorAll("[data-n]")].filter(vis).map((e) => ({ k: e.getAttribute("data-n"), text: e.textContent.trim() })).slice(0, 120),
    nChecks: document.querySelectorAll("[data-check]").length,
    focusText: el ? (el.closest("section") || el).innerText.replace(/\\n{2,}/g, "\\n").slice(0, 1800) : null,
    viewText: [...document.querySelectorAll("h1,h2,h3,p,td,th,li,button,label,span")].filter((e) => vis(e) && e.children.length === 0).map((e) => e.textContent.replace(/\\s+/g, " ").trim()).filter(Boolean).slice(0, 120).join(" | "),
    scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
  };
})()`;

let failed = 0;
const linkSet = new Set();
for (const [width, height, mobile] of WIDTHS) {
  const res = await withBrowser(async ({ go, evaluate, wait, unlock, send, sleep, errors }) => {
    await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile });
    await unlock(base);
    const out = [];
    for (const s of STEPS) {
      // with a list of steps, every step is still made (the later ones start where the earlier left the page), and only
      // the listed ones are shot and recorded
      const keep = !only.length || only.includes(s.id);
      const rec = { step: s.id, width };
      try {
        if (s.page) await go(base + s.page);
        await evaluate(HELPERS);
        if (s.act) rec.act = await evaluate(s.act);
        if (s.until) await wait(s.until, 45000, `${s.id}: ${s.until}`);
        if (s.then) { await sleep(2500); await evaluate(HELPERS); rec.then = await evaluate(s.then); }
        if (s.until2) await wait(s.until2, 45000, `${s.id}: ${s.until2}`);
        await sleep(s.settle ?? 2500);
        await evaluate(HELPERS);
        // the part in view: the focus scrolled to the top (or the centre) of the window
        await evaluate(`(() => { const f = ${js(s.focus)}; let el; if (f.startsWith("text:")) { const [, sel, start] = f.match(/^text:([^:]+):(.*)$/); el = __h.byText(sel, start); } else el = document.querySelector(f);
          if (el) { if (f === "h1") window.scrollTo(0, 0); else el.scrollIntoView({ block: ${js(s.block ?? "start")} }); } return !!el; })()`);
        await sleep(800);
        Object.assign(rec, await evaluate(LOOK(s.focus)));
        if (!keep) continue;
        const shot = await send("Page.captureScreenshot", { format: "png" });
        fs.writeFileSync(path.join(here, `${s.id}_${width}.png`), Buffer.from(shot.data, "base64"));
        rec.shot = `${s.id}_${width}.png`;
        if (width === 1280) for (const h of await evaluate(`[...document.querySelectorAll("a[href]")].map((a) => a.getAttribute("href"))`)) linkSet.add(h);
        console.log(`${rec.found ? "ok  " : "MISS"} ${s.id} ${width}: ${rec.url}${rec.unreadable ? " (the live set could not be read)" : ""}`);
      } catch (e) {
        failed += 1; rec.error = String(e.message ?? e);
        console.log(`FAIL ${s.id} ${width}: ${rec.error}`);
      }
      if (keep) out.push(rec);
    }
    let links = null;
    if (width === 1280 && !only.length) {
      const same = [...linkSet].filter((h) => h.startsWith("/") && !h.startsWith("//") && !h.startsWith("/internal/"));
      // one at a time: the first run asked for all of them at once and met the live set's statement timeouts
      links = await evaluate(`(async () => { const out = []; for (const h of ${js(same)}) { try { const r = await fetch(h, { credentials: "include" }); try { await r.body?.cancel(); } catch {} out.push([h, r.status, r.url.replace(location.origin, "")]); } catch (e) { out.push([h, 0, String(e)]); } } return out; })()`);
      const bad = links.filter(([, st]) => st !== 200);
      console.log(`links: ${links.length} same-origin, ${bad.length} not 200${bad.length ? ": " + bad.map((b) => b.join(" ")).join("; ") : ""}`);
    }
    return { steps: out, links, pageErrors: errors };
  }, { width, height });
  if (!res) { console.log("no browser on this machine"); process.exit(1); }
  fs.writeFileSync(path.join(jsonDir, `walk-${width}${only.length ? "-" + only.join("+") : ""}.json`), JSON.stringify(res, null, 1));
}
process.exit(failed ? 1 : 0);
