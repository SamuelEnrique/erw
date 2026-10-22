// Energy Research Warehouse (ERW), session 723 (chain 062): the trader's path through the All grids tab of
// /cost-of-power, walked click by click in a real browser, in the internal view (every page is in review), at 1280 and
// at 390 px wide. One shot a step and a width into this folder, named by the step (01-open_1280.png), and one JSON a
// width of what each step showed: its address, the checked figures in view (data-check and data-raw), every tip in
// view (the trigger's words and the tip's words: the source and the window of each figure), the sort line, the headline,
// the A and B panel and the first rows. docs/reviews/siting-trader-path.md is written from these files.
//
//   node docs/brand/review-723/walk-723.mjs https://erw-flame.vercel.app <json-dir> [only-steps]
//
// The internal view is opened by unlock(base) from site/scripts/browser.mjs: the token is posted by the form, never in
// an address, and never printed. Exit 1 when a step could not be made. The walk is session 585's walk-585.mjs in its
// shape (the same helpers), with the tab's own clicks.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3723").replace(/\/$/, "");
const jsonDir = process.argv[3] ?? here;
const only = (process.argv[4] ?? "").split(",").filter(Boolean);
const WIDTHS = [[1280, 900, false], [390, 844, true]];
const TAB = "/cost-of-power?view=allgrids";

const js = (s) => JSON.stringify(s);
const HELPERS = `(() => {
  window.__h = {
    byText(sel, start) { return [...document.querySelectorAll(sel)].find((e) => e.textContent.replace(/\\s+/g, " ").trim().startsWith(start)) || null; },
    click(el) { if (!el) throw new Error("nothing to click"); el.scrollIntoView({ block: "center" }); el.click(); return true; },
    // the box's selects and fields: set, then the form's own submit (the box may be folded on a phone; the form is still there)
    set(sel, value) { const e = document.querySelector(sel); if (!e) throw new Error("no field " + sel); e.value = value; e.dispatchEvent(new Event("input", { bubbles: true })); e.dispatchEvent(new Event("change", { bubbles: true })); return true; },
    tick(sel, on) { const e = document.querySelector(sel); if (!e) throw new Error("no box " + sel); if (e.checked !== on) e.click(); return e.checked; },
    submit() { const f = document.querySelector("form[data-allgrids-form]"); if (!f) throw new Error("no form"); f.requestSubmit(); return true; },
    nodeSort() { const e = document.querySelector("[data-node-sort]"); return e ? e.getAttribute("data-node-sort") : null; },
  };
  return true;
})()`;

// what the previous steps found (the first two nodes of the cheapest sort), for the steps that need an id
const state = { nodes: [] };

/** Each step: what the trader does (act, in the page), what is shown (focus: a selector or a heading's first words). */
const STEPS = [
  { id: "01-open", page: TAB, focus: "h1",
    does: "opens the tab: Economics menu, What a datacenter pays, the view All grids" },
  { id: "02-energy-cheapest", act: `(() => { __h.set('select[data-allgrids-sort]', 'energy'); __h.set('select[data-allgrids-dir]', 'asc'); return __h.submit(); })()`,
    until: "location.search.includes('sort=energy') && location.search.includes('dir=asc')", focus: "p[data-allgrids-sort]",
    does: "Sort and filter: Sort by energy, Order smallest first, Show" },
  { id: "03-ercot-only", act: `(() => { __h.tick('input[name="grid"][value="ercot"]', true); return __h.submit(); })()`,
    until: "location.search.includes('grid=ercot')", focus: "p[data-allgrids-sort]",
    does: "Grids shown: ticks ERCOT, Show" },
  { id: "04-nodes", act: `__h.click(document.querySelector('a[data-allgrids-rows="nodes"]'))`,
    until: "location.search.includes('rows=nodes') && !!document.querySelector('[data-allgrids-nodes]')", settle: 3500, focus: "[data-node-shared]",
    does: "clicks ERCOT nodes above the table" },
  { id: "05-nodes-energy-cheapest", act: `(() => { __h.click(document.querySelector('button[data-node-head="energy"]')); return true; })()`,
    then: `__h.click(document.querySelector('button[data-node-head="energy"]'))`, until2: "__h.nodeSort() === 'energy|asc'", settle: 1500, focus: "[data-allgrids-nodes]",
    does: "clicks the heading Energy twice: largest first, then smallest first", keepNodes: true },
  { id: "06-nodes-basis-widest", act: `__h.click(document.querySelector('button[data-node-head="basis"]'))`,
    until: "__h.nodeSort() === 'basis|desc'", settle: 1500, focus: "[data-allgrids-nodes]",
    does: "clicks the heading Basis to HB_HUBAVG: largest first" },
  { id: "07-nodes-basis-lowest", act: `__h.click(document.querySelector('button[data-node-head="basis"]'))`,
    until: "__h.nodeSort() === 'basis|asc'", settle: 1500, focus: "[data-allgrids-nodes]",
    does: "clicks it again: smallest first (the most negative basis)" },
  { id: "08-node-panel", act: `(() => { const b = [...document.querySelectorAll('button[data-node-open]')].find((e) => e.getBoundingClientRect().height > 0); window.__picked = b ? b.getAttribute('data-node-open') : null; return __h.click(b); })()`,
    until: "location.search.includes('node=')", settle: 3500, focus: "[data-node-panel]", block: "start",
    does: "clicks the first node's name: its panel opens above the list" },
  { id: "09-two-nodes-ab", page: () => `${TAB}&a=${encodeURIComponent(state.nodes[0] ?? "ercot:HB_HUBAVG")}&b=${encodeURIComponent(state.nodes[1] ?? "ercot:HB_WEST")}`,
    focus: "[data-allgrids-headline]", block: "start",
    does: "writes the two cheapest nodes into the address as A and B (the box's A and B lists hubs and zones only)" },
  { id: "10-hub-vs-nodes", page: `${TAB}&grid=ercot&sort=energy&dir=asc&a=ercot%3AHB_HUBAVG&b=ercot%3AHB_WEST`, focus: "[data-allgrids-abpanel]", block: "start",
    does: "A ERCOT HB_HUBAVG, B ERCOT HB_WEST, Show: the hub average against a hub; the nodes' basis is to HB_HUBAVG only" },
  { id: "11-flexible", act: `__h.set('select[data-allgrids-profile]', 'flexible')`,
    until: "location.search.includes('profile=flexible')", settle: 3500, focus: "[data-allgrids-table]", block: "start",
    does: "Profile: Flexible compute (the page opens the new address at once)" },
  { id: "12-flexible-strike-100", act: `(() => { __h.set('input[data-allgrids-strike]', '100'); return __h.submit(); })()`,
    until: "location.search.includes('strike=100')", settle: 3500, focus: "[data-allgrids-table]", block: "start",
    does: "Strike, USD per MWh: 100, Show" },
  { id: "13-four-peak", act: `(() => { __h.set('select[data-allgrids-sort]', 'transmission'); __h.set('select[data-allgrids-dir]', 'desc'); return __h.submit(); })()`,
    until: "location.search.includes('sort=transmission')", settle: 3500, focus: "[data-allgrids-table]", block: "start",
    does: "Sort by transmission and the four peaks, largest first, Show" },
  { id: "14-send", page: () => state.last ?? TAB, focus: "h1",
    does: "opens the last address in a new tab, as a colleague would" },
];

const LOOK = (focus) => `(() => {
  const f = ${js(focus)};
  let el = null;
  if (f.startsWith("text:")) { const [, sel, start] = f.match(/^text:([^:]+):(.*)$/); el = __h.byText(sel, start); }
  else el = document.querySelector(f);
  const vis = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight; };
  const text = (e) => (e ? e.textContent.replace(/\\s+/g, " ").trim() : null);
  const tipOf = (b) => { const id = b.getAttribute("aria-describedby"); const t = id ? document.getElementById(id) : null; return t ? text(t) : null; };
  return {
    url: location.pathname + location.search,
    found: !!el,
    unreadable: document.body.innerText.includes("could not be read"),
    errorText: (document.body.innerText.match(/[^\\n]*(Application error|could not be read)[^\\n]*/) || [""])[0],
    checksInView: [...document.querySelectorAll("[data-check]")].filter(vis).map((e) => ({ k: e.getAttribute("data-check"), raw: e.getAttribute("data-raw"), text: e.textContent.trim() })).slice(0, 160),
    tipsInView: [...document.querySelectorAll("[data-tip-trigger],[aria-describedby]")].filter(vis).map((b) => ({ on: text(b).slice(0, 60), tip: tipOf(b) })).filter((t) => t.tip).slice(0, 80),
    nChecks: document.querySelectorAll("[data-check]").length,
    sortLine: text(document.querySelector("p[data-allgrids-sort]")) || text(document.querySelector("[data-node-sort]")),
    countLine: text(document.querySelector("[data-allgrids-count]")),
    headline: text(document.querySelector("[data-allgrids-headline]")),
    abPanel: text(document.querySelector("[data-allgrids-abpanel]")),
    shared: text(document.querySelector("[data-node-shared]")),
    panel: text(document.querySelector("[data-node-panel]")),
    rows: [...document.querySelectorAll("[data-allgrids-row]")].slice(0, 8).map((r) => ({ id: r.getAttribute("data-allgrids-row"), text: text(r).slice(0, 320) })),
    nodeIds: [...document.querySelectorAll("button[data-node-open]")].slice(0, 3).map((b) => b.getAttribute("data-node-open")),
    heads: [...document.querySelectorAll("th[data-col]")].map((h) => h.getAttribute("data-col")),
    boxOpen: (() => { const d = document.querySelector("details[data-allgrids-box]"); return d ? d.open : null; })(),
    focusText: el ? (el.closest("section") || el).innerText.replace(/\\n{2,}/g, "\\n").slice(0, 1800) : null,
    scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
    nHeldText: (document.body.innerText.match(/license needed/gi) || []).length,
    nNotHeld: (document.body.innerText.match(/not held/gi) || []).length,
    totalH: document.documentElement.scrollHeight,
    firstCheckY: (() => { const c = document.querySelector("[data-check]"); return c ? Math.round(c.getBoundingClientRect().top + scrollY) : null; })(),
  };
})()`;

let failed = 0;
for (const [width, height, mobile] of WIDTHS) {
  const res = await withBrowser(async ({ go, evaluate, wait, unlock, send, sleep, errors }) => {
    await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile });
    await unlock(base);
    const out = [];
    for (const s of STEPS) {
      const keep = !only.length || only.includes(s.id);
      const rec = { step: s.id, width, does: s.does };
      try {
        const page = typeof s.page === "function" ? s.page() : s.page;
        if (page) await go(base + page);
        await evaluate(HELPERS);
        if (s.act) rec.act = await evaluate(s.act);
        if (s.until) await wait(s.until, 60000, `${s.id}: ${s.until}`);
        if (s.then) { await sleep(1500); await evaluate(HELPERS); rec.then = await evaluate(s.then); }
        if (s.until2) await wait(s.until2, 60000, `${s.id}: ${s.until2}`);
        await sleep(s.settle ?? 2500);
        await evaluate(HELPERS);
        await evaluate(`(() => { const f = ${js(s.focus)}; let el; if (f.startsWith("text:")) { const [, sel, start] = f.match(/^text:([^:]+):(.*)$/); el = __h.byText(sel, start); } else el = document.querySelector(f);
          if (el) { if (f === "h1") window.scrollTo(0, 0); else el.scrollIntoView({ block: ${js(s.block ?? "start")} }); } return !!el; })()`);
        await sleep(800);
        Object.assign(rec, await evaluate(LOOK(s.focus)));
        if (s.keepNodes && rec.nodeIds?.length >= 2 && width === 1280) state.nodes = rec.nodeIds.slice(0, 2);
        state.last = rec.url;
        if (!keep) continue;
        const shot = await send("Page.captureScreenshot", { format: "png" });
        fs.writeFileSync(path.join(here, `${s.id}_${width}.png`), Buffer.from(shot.data, "base64"));
        rec.shot = `${s.id}_${width}.png`;
        console.log(`${rec.found ? "ok  " : "MISS"} ${s.id} ${width}: ${rec.url}${rec.unreadable ? " (the live set could not be read)" : ""}`);
      } catch (e) {
        failed += 1; rec.error = String(e.message ?? e);
        console.log(`FAIL ${s.id} ${width}: ${rec.error}`);
      }
      if (keep) out.push(rec);
    }
    return { steps: out, pageErrors: errors };
  }, { width, height });
  if (!res) { console.log("no browser on this machine"); process.exit(1); }
  fs.writeFileSync(path.join(jsonDir, `walk-${width}${only.length ? "-" + only.join("+") : ""}.json`), JSON.stringify(res, null, 1));
}
process.exit(failed ? 1 : 0);
