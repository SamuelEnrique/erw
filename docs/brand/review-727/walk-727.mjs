// Energy Research Warehouse (ERW), session 727 (chain 062): the lab's path of session 717 (docs/reviews/siting-path.md),
// walked again, step by step, on a build of wip/727-allgrids (chain 050's 718 to 721 and this chain's 722 to 726 in
// place) in the internal view, at 1280 and 390 px, with two steps added for 719's tracker link and 720's card. One shot
// a step and a width into this folder, and one JSON a width of what each step showed (the headline, the sort line, the
// first rows with their figures, the node panel, the card's figures). The path file's "Now" column is written from it.
//
//   cd site && npx next start -p 3727
//   node docs/brand/review-727/walk-727.mjs http://localhost:3727 docs/brand/review-727
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3727").replace(/\/$/, "");
const jsonDir = process.argv[3] ?? here;
const WIDTHS = [[1280, 900, false], [390, 844, true]];
const TAB = "/cost-of-power?view=allgrids&mw=1000";
const js = (s) => JSON.stringify(s);
const STEPS = [
  { id: "q1_allin_cheapest", page: `${TAB}&sort=allin&dir=asc`, focus: "p[data-allgrids-sort]" },
  { id: "q1_energy_cheapest", page: `${TAB}&sort=energy&dir=asc`, focus: "p[data-allgrids-sort]" },
  { id: "q2_a_b", page: `${TAB}&sort=allin&dir=asc&a=ercot%3AHB_WEST&b=ercot%3ALZ_NORTH`, focus: "[data-allgrids-headline]" },
  { id: "q3_connect", page: `${TAB}&sort=connect&dir=asc`, focus: "p[data-allgrids-sort]" },
  { id: "q4_headroom", page: `${TAB}&sort=headroom`, focus: "p[data-allgrids-sort]" },
  { id: "q5_carbon_electrolyzer", page: `${TAB}&profile=electrolyzer&sort=carbon&dir=asc`, focus: "p[data-allgrids-sort]" },
  { id: "q6_flexible", page: `${TAB}&profile=flexible&sort=allin&dir=asc&a=ercot%3AHB_WEST&b=ercot%3ALZ_NORTH`, focus: "[data-allgrids-headline]" },
  { id: "q7_nodes_cheapest", page: `${TAB}&rows=nodes&nsort=energy&ndir=asc`, focus: "[data-allgrids-nodes]" },
  { id: "q7_node_panel", page: `${TAB}&rows=nodes&nsort=energy&ndir=asc&node=ercot%3ABBREEZE_1_2`, focus: "[data-node-panel]" },
  { id: "q8_utility", page: `${TAB}&sort=utility&dir=asc`, focus: "p[data-allgrids-sort]" },
  { id: "q9_gaps", page: "/internal/siting-gaps", focus: "h1" },
  { id: "q10_send", page: `${TAB}&sort=allin&dir=asc&a=ercot%3AHB_WEST&b=ercot%3ALZ_NORTH`, focus: "h1" },
  { id: "q11_tracker", page: "/datacenters", focus: "h1" },
  { id: "q12_card", page: "/research/card/siting_gigawatt", focus: "h1" },
];
const LOOK = (focus) => `(() => {
  const el = document.querySelector(${js(focus)});
  const vis = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight; };
  const text = (e) => (e ? e.textContent.replace(/\\s+/g, " ").trim() : null);
  const checks = (root) => [...root.querySelectorAll("[data-check]")].map((e) => ({ k: e.getAttribute("data-check"), raw: e.getAttribute("data-raw"), text: e.textContent.trim() }));
  return {
    url: location.pathname + location.search, found: !!el,
    errorText: (document.body.innerText.match(/[^\\n]*(Application error|could not be read)[^\\n]*/) || [""])[0],
    nChecks: document.querySelectorAll("[data-check]").length,
    sortLine: text(document.querySelector("p[data-allgrids-sort]")) || text(document.querySelector("[data-node-sort]")),
    countLine: text(document.querySelector("[data-allgrids-count]")),
    headline: text(document.querySelector("[data-allgrids-headline]")),
    abPanel: text(document.querySelector("[data-allgrids-abpanel]")),
    shared: text(document.querySelector("[data-node-shared]")),
    panel: text(document.querySelector("[data-node-panel]")),
    rows: [...document.querySelectorAll("[data-allgrids-row]")].slice(0, 8).map((r) => ({ id: r.getAttribute("data-allgrids-row"), checks: checks(r).slice(0, 14), text: text(r).slice(0, 160) })),
    heads: [...document.querySelectorAll("th[data-col]")].map((h) => h.getAttribute("data-col")),
    gaps: document.querySelector("[data-siting-gaps]")?.getAttribute("data-siting-gaps") ?? null,
    tracker: location.pathname === "/datacenters" ? { links: document.querySelectorAll("[data-facility-siting]").length, held: /license needed/.test(document.body.innerText) } : null,
    card: location.pathname.startsWith("/research/card/") ? { title: text(document.querySelector("h1")), checks: checks(document).slice(0, 20), text: text(document.querySelector("main") || document.body).slice(0, 1400) } : null,
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
      const rec = { step: s.id, width };
      try {
        await go(base + s.page);
        await sleep(2500);
        await evaluate(`(() => { const f = ${js(s.focus)}; const el = document.querySelector(f); if (el) { if (f === "h1") window.scrollTo(0, 0); else el.scrollIntoView({ block: "start" }); } return !!el; })()`);
        await sleep(800);
        Object.assign(rec, await evaluate(LOOK(s.focus)));
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
