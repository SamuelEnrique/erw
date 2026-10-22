// Energy Research Warehouse (ERW), session 724 (chain 062): the trader's failed steps of session 723's walk
// (docs/reviews/siting-trader-path.md, steps 4, 7, 8, 9 and 13), walked again on a build of wip/724-allgrids in the
// internal view, at 1280 and 390 px, with the fixes in place: the shared line's tip, the status line's words, the panel's
// Close and its "Set as A" and "Set as B" links, two nodes as A and B beside the node list, the basis spread column, and
// the transmission sort's words. Shots and records as walk-723.mjs writes them, into this folder.
//
//   cd site && npx next start -p 3724
//   node docs/brand/review-724/walk-724.mjs http://localhost:3724 docs/brand/review-724
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3724").replace(/\/$/, "");
const jsonDir = process.argv[3] ?? here;
const WIDTHS = [[1280, 900, false], [390, 844, true]];
const TAB = "/cost-of-power?view=allgrids";
const js = (s) => JSON.stringify(s);
const HELPERS = `(() => {
  window.__h = {
    click(el) { if (!el) throw new Error("nothing to click"); el.scrollIntoView({ block: "center" }); el.click(); return true; },
    set(sel, value) { const e = document.querySelector(sel); if (!e) throw new Error("no field " + sel); e.value = value; e.dispatchEvent(new Event("input", { bubbles: true })); e.dispatchEvent(new Event("change", { bubbles: true })); return true; },
    submit() { const f = document.querySelector("form[data-allgrids-form]"); if (!f) throw new Error("no form"); f.requestSubmit(); return true; },
    nodeSort() { const e = document.querySelector("[data-node-sort]"); return e ? e.getAttribute("data-node-sort") : null; },
  };
  return true;
})()`;
const state = { nodes: [] };
const STEPS = [
  { id: "04-nodes", page: `${TAB}&rows=nodes&sort=energy&dir=asc&grid=ercot`, focus: "[data-node-shared]", does: "the node view (step 4): the shared line's tips" },
  { id: "05-nodes-energy-cheapest", act: `(() => { __h.click(document.querySelector('button[data-node-head="energy"]')); return true; })()`,
    then: `__h.click(document.querySelector('button[data-node-head="energy"]'))`, until2: "__h.nodeSort() === 'energy|asc'", settle: 1500, focus: "[data-allgrids-nodes]", does: "Energy twice (step 5)", keepNodes: true },
  { id: "06b-nodes-spread-widest", act: `__h.click(document.querySelector('button[data-node-head="spread"]'))`, until: "__h.nodeSort() === 'spread|desc'", settle: 1500, focus: "[data-allgrids-nodes]",
    does: "clicks the new heading Basis spread: widest first" },
  { id: "07-nodes-basis-lowest", act: `(() => { __h.click(document.querySelector('button[data-node-head="basis"]')); return true; })()`,
    then: `__h.click(document.querySelector('button[data-node-head="basis"]'))`, until2: "__h.nodeSort() === 'basis|asc'", settle: 1500, focus: "[data-allgrids-nodes]", does: "Basis twice (step 7): the status line" },
  { id: "08-node-panel", act: `(() => { const b = [...document.querySelectorAll('button[data-node-open]')].find((e) => e.getBoundingClientRect().height > 0); return __h.click(b); })()`,
    until: "location.search.includes('node=')", settle: 3500, focus: "[data-node-panel]", does: "the first node's panel (step 8)" },
  { id: "08b-set-as-a", act: `__h.click(document.querySelector('a[data-node-set="a"]'))`, until: "location.search.includes('a=ercot') && !!document.querySelector('[data-allgrids-headline=\"1\"]')", settle: 3000, focus: "[data-allgrids-headline]", block: "start",
    does: "clicks Set as A in the panel: the headline above the list" },
  { id: "08c-close", act: `__h.click(document.querySelector('a[data-node-close]'))`, until: "!location.search.includes('node=') && !!document.querySelector('[data-allgrids-nodes]')", settle: 3000, focus: "[data-node-sort]",
    does: "clicks Close: the sort, the filter and A kept" },
  { id: "09-two-nodes-ab", page: () => `${TAB}&rows=nodes&nsort=basis&ndir=asc&a=${encodeURIComponent(state.nodes[0] ?? "ercot:BBREEZE_1_2")}&b=${encodeURIComponent(state.nodes[1] ?? "ercot:ELSAUZ_ALL")}`,
    focus: "[data-allgrids-abpanel]", block: "start", does: "two nodes as A and B, in the node view (step 9): the box's lists, the headline, the panel" },
  { id: "13-four-peak", page: `${TAB}&profile=flexible&strike=100&sort=transmission&grid=ercot&a=ercot%3AHB_HUBAVG&b=ercot%3AHB_WEST`, focus: "p[data-allgrids-sort]", block: "start",
    does: "the transmission sort under the flexible profile (step 13): the sort line's words" },
];
const LOOK = (focus) => `(() => {
  const f = ${js(focus)};
  const el = document.querySelector(f);
  const vis = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight; };
  const text = (e) => (e ? e.textContent.replace(/\\s+/g, " ").trim() : null);
  const tipOf = (b) => { const id = b.getAttribute("aria-describedby"); const t = id ? document.getElementById(id) : null; return t ? text(t) : null; };
  return {
    url: location.pathname + location.search, found: !!el,
    errorText: (document.body.innerText.match(/[^\\n]*(Application error|could not be read)[^\\n]*/) || [""])[0],
    checksInView: [...document.querySelectorAll("[data-check]")].filter(vis).map((e) => ({ k: e.getAttribute("data-check"), raw: e.getAttribute("data-raw"), text: e.textContent.trim() })).slice(0, 160),
    tipsInView: [...document.querySelectorAll("[data-tip-trigger],[aria-describedby]")].filter(vis).map((b) => ({ on: text(b).slice(0, 60), tip: tipOf(b) })).filter((t) => t.tip).slice(0, 80),
    nChecks: document.querySelectorAll("[data-check]").length,
    sortLine: text(document.querySelector("p[data-allgrids-sort]")) || text(document.querySelector("[data-node-sort]")),
    headline: text(document.querySelector("[data-allgrids-headline]")),
    abPanel: text(document.querySelector("[data-allgrids-abpanel]")),
    shared: text(document.querySelector("[data-node-shared]")),
    panel: text(document.querySelector("[data-node-panel]")),
    selects: [...document.querySelectorAll("select[data-allgrids-pick]")].map((s) => ({ k: s.getAttribute("data-allgrids-pick"), value: s.value, chosen: s.options[s.selectedIndex]?.text ?? null, n: s.options.length })),
    rows: [...document.querySelectorAll("[data-allgrids-row]")].slice(0, 6).map((r) => ({ id: r.getAttribute("data-allgrids-row"), text: text(r).slice(0, 240) })),
    nodeIds: [...document.querySelectorAll("button[data-node-open]")].slice(0, 3).map((b) => b.getAttribute("data-node-open")),
    heads: [...document.querySelectorAll("[data-node-head]")].map((h) => h.getAttribute("data-node-head")),
    scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth, totalH: document.documentElement.scrollHeight,
  };
})()`;
let failed = 0;
for (const [width, height, mobile] of WIDTHS) {
  const res = await withBrowser(async ({ go, evaluate, wait, unlock, send, sleep, errors }) => {
    await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile });
    await unlock(base);
    const out = [];
    for (const s of STEPS) {
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
        await evaluate(`(() => { const el = document.querySelector(${js(s.focus)}); if (el) el.scrollIntoView({ block: ${js(s.block ?? "start")} }); return !!el; })()`);
        await sleep(800);
        Object.assign(rec, await evaluate(LOOK(s.focus)));
        if (s.keepNodes && rec.nodeIds?.length >= 2 && width === 1280) state.nodes = rec.nodeIds.slice(0, 2);
        const shot = await send("Page.captureScreenshot", { format: "png" });
        fs.writeFileSync(path.join(here, `${s.id}_${width}.png`), Buffer.from(shot.data, "base64"));
        rec.shot = `${s.id}_${width}.png`;
        console.log(`${rec.found ? "ok  " : "MISS"} ${s.id} ${width}: ${rec.url}`);
      } catch (e) { failed += 1; rec.error = String(e.message ?? e); console.log(`FAIL ${s.id} ${width}: ${rec.error}`); }
      out.push(rec);
    }
    return { steps: out, pageErrors: errors };
  }, { width, height });
  if (!res) { console.log("no browser on this machine"); process.exit(1); }
  fs.writeFileSync(path.join(jsonDir, `walk-${width}.json`), JSON.stringify(res, null, 1));
}
process.exit(failed ? 1 : 0);
