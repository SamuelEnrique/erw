// Energy Research Warehouse (ERW), session 726 (chain 062): the utility planner's failed steps of session 725's walk
// (docs/reviews/siting-utility-path.md, steps 2, 3, 6, 7 and 9), walked again on a build of wip/726-allgrids in the
// internal view, at 1280 and 390 px, with the fixes in place: the basis words under each utility figure, the sort line's
// sentence, the rule's document link, and the A and B panel's utility row tip. Shots and records as walk-725.mjs writes
// them, into this folder.
//
//   cd site && npx next start -p 3726
//   node docs/brand/review-726/walk-726.mjs http://localhost:3726 docs/brand/review-726
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3726").replace(/\/$/, "");
const jsonDir = process.argv[3] ?? here;
const WIDTHS = [[1280, 900, false], [390, 844, true]];
const TAB = "/cost-of-power?view=allgrids&mw=1000";
const js = (s) => JSON.stringify(s);
const STEPS = [
  { id: "02-utility-dearest", page: `${TAB}&sort=utility`, focus: "p[data-allgrids-sort]", does: "the utility sort (step 2): the sort line and the basis under each figure" },
  { id: "03-utility-ercot", page: `${TAB}&sort=utility&grid=ercot`, focus: "p[data-allgrids-sort]", does: "ERCOT only (step 3)" },
  { id: "06-connect", page: `${TAB}&sort=connect&dir=asc`, focus: "p[data-allgrids-sort]", does: "the connect sort (step 6): the document link beside each rule" },
  { id: "07-rule-doc", act: `(() => { const a = document.querySelector('a[data-rule-doc]'); if (!a) throw new Error('no document link'); a.scrollIntoView({ block: 'center' }); a.focus(); window.__doc = { href: a.getAttribute('href'), target: a.getAttribute('target'), label: a.getAttribute('aria-label'), text: a.textContent.trim() }; return window.__doc; })()`,
    settle: 1000, focus: "a[data-rule-doc]", does: "puts the keyboard on the first row's document link (step 7)" },
  { id: "09-ab-zones", page: `${TAB}&sort=utility&grid=ercot&a=ercot%3ALZ_HOUSTON&b=ercot%3ALZ_NORTH`, focus: "[data-allgrids-abpanel]", block: "start", does: "A LZ_HOUSTON, B LZ_NORTH (step 9): the utility row's tip" },
];
const LOOK = (focus) => `(() => {
  const el = document.querySelector(${js(focus)});
  const vis = (e) => { const r = e.getBoundingClientRect(); return r.width > 0 && r.height > 0 && r.bottom > 0 && r.top < innerHeight; };
  const text = (e) => (e ? e.textContent.replace(/\\s+/g, " ").trim() : null);
  const tipOf = (b) => { const id = b.getAttribute("aria-describedby"); const t = id ? document.getElementById(id) : null; return t ? text(t) : null; };
  const ab = document.querySelector("[data-ab-utility-basis] button");
  return {
    url: location.pathname + location.search, found: !!el,
    errorText: (document.body.innerText.match(/[^\\n]*(Application error|could not be read)[^\\n]*/) || [""])[0],
    checksInView: [...document.querySelectorAll("[data-check]")].filter(vis).map((e) => ({ k: e.getAttribute("data-check"), raw: e.getAttribute("data-raw"), text: e.textContent.trim() })).slice(0, 160),
    nChecks: document.querySelectorAll("[data-check]").length,
    sortLine: text(document.querySelector("p[data-allgrids-sort]")),
    headline: text(document.querySelector("[data-allgrids-headline]")),
    abUtilityTip: ab ? tipOf(ab) : null,
    basisWords: [...document.querySelectorAll("[data-util-basis]")].slice(0, 10).map((e) => text(e)),
    nBasis: document.querySelectorAll("[data-util-basis]").length,
    docLinks: [...document.querySelectorAll("a[data-rule-doc]")].slice(0, 8).map((a) => ({ href: a.getAttribute("href"), text: text(a) })),
    nDocLinks: document.querySelectorAll("a[data-rule-doc]").length,
    doc: window.__doc ?? null,
    rows: [...document.querySelectorAll("[data-allgrids-row]")].slice(0, 6).map((r) => ({ id: r.getAttribute("data-allgrids-row"), text: text(r).slice(0, 200) })),
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
        if (s.page) await go(base + s.page);
        if (s.act) rec.act = await evaluate(s.act);
        await sleep(s.settle ?? 2500);
        if (s.id !== "07-rule-doc") await evaluate(`(() => { const el = document.querySelector(${js(s.focus)}); if (el) el.scrollIntoView({ block: ${js(s.block ?? "start")} }); return !!el; })()`);
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
