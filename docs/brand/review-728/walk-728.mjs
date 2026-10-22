// Energy Research Warehouse (ERW), session 728 (chain 062): the headroom column with a zone's own demand growth under the
// grid's, on a build of wip/728-allgrids in the internal view at 1280 and 390 px: the tab sorted by demand growth, and
// the load zones only. Shots and a record of the zone lines into this folder.
//
//   cd site && npx next start -p 3728
//   node docs/brand/review-728/walk-728.mjs http://localhost:3728 docs/brand/review-728
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3728").replace(/\/$/, "");
const jsonDir = process.argv[3] ?? here;
const WIDTHS = [[1280, 900, false], [390, 844, true]];
const TAB = "/cost-of-power?view=allgrids&mw=1000";
const js = (s) => JSON.stringify(s);
const STEPS = [
  { id: "04-headroom", page: `${TAB}&sort=headroom`, focus: "p[data-allgrids-sort]" },
  { id: "05-headroom-zones", page: `${TAB}&sort=headroom&kind=zone`, focus: "p[data-allgrids-sort]" },
  { id: "05b-headroom-zones-nyiso", page: `${TAB}&sort=headroom&kind=zone&grid=nyiso`, focus: "p[data-allgrids-sort]" },
];
const LOOK = (focus) => `(() => {
  const el = document.querySelector(${js(focus)});
  const text = (e) => (e ? e.textContent.replace(/\\s+/g, " ").trim() : null);
  const tipOf = (b) => { const id = b.getAttribute("aria-describedby"); const t = id ? document.getElementById(id) : null; return t ? text(t) : null; };
  return {
    url: location.pathname + location.search, found: !!el,
    errorText: (document.body.innerText.match(/[^\\n]*(Application error|could not be read)[^\\n]*/) || [""])[0],
    sortLine: text(document.querySelector("p[data-allgrids-sort]")),
    zones: [...document.querySelectorAll("[data-headroom-zone]")].slice(0, 30).map((e) => ({ row: e.closest("[data-allgrids-row]")?.getAttribute("data-allgrids-row"), kind: e.getAttribute("data-headroom-zone"), text: text(e), tip: (() => { const b = e.querySelector("[data-tip-trigger]"); return b ? tipOf(b) : null; })() })),
    nZones: document.querySelectorAll("[data-headroom-zone]").length,
    nKeys: document.querySelectorAll("[data-check^='allgrids|zdemand|']").length,
    scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth, totalH: document.documentElement.scrollHeight,
  };
})()`;
let failed = 0;
for (const [width, height, mobile] of WIDTHS) {
  const res = await withBrowser(async ({ go, evaluate, unlock, send, sleep, errors }) => {
    await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile });
    await unlock(base);
    const out = [];
    for (const s of STEPS) {
      const rec = { step: s.id, width };
      try {
        await go(base + s.page);
        await sleep(2500);
        await evaluate(`(() => { const el = document.querySelector(${js(s.focus)}); if (el) el.scrollIntoView({ block: "start" }); return !!el; })()`);
        await sleep(800);
        Object.assign(rec, await evaluate(LOOK(s.focus)));
        const shot = await send("Page.captureScreenshot", { format: "png" });
        fs.writeFileSync(path.join(here, `${s.id}_${width}.png`), Buffer.from(shot.data, "base64"));
        rec.shot = `${s.id}_${width}.png`;
        console.log(`${rec.found ? "ok  " : "MISS"} ${s.id} ${width}: ${rec.url} (${rec.nZones} zone lines, ${rec.nKeys} keys)`);
      } catch (e) { failed += 1; rec.error = String(e.message ?? e); console.log(`FAIL ${s.id} ${width}: ${rec.error}`); }
      out.push(rec);
    }
    return { steps: out, pageErrors: errors };
  }, { width, height });
  if (!res) { console.log("no browser on this machine"); process.exit(1); }
  fs.writeFileSync(path.join(jsonDir, `walk-${width}.json`), JSON.stringify(res, null, 1));
}
process.exit(failed ? 1 : 0);
