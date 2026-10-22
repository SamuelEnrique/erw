// Energy Research Warehouse (ERW), session 729 (chain 062): the tracker (/datacenters) and the tab's address a tracked
// facility's link opens, on a build of wip/729-allgrids in the internal view at 1280 and 390 px. The facilities table
// is held whole, so the tracker shows no row and no link; the shots record that, and the link's address as it draws.
//
//   cd site && npx next start -p 3729
//   node docs/brand/review-729/walk-729.mjs http://localhost:3729 docs/brand/review-729
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3729").replace(/\/$/, "");
const jsonDir = process.argv[3] ?? here;
const WIDTHS = [[1280, 900, false], [390, 844, true]];
const js = (s) => JSON.stringify(s);
const STEPS = [
  { id: "10-tracker", page: "/datacenters", focus: "h1" },
  { id: "link-address", page: "/cost-of-power?view=allgrids&mw=1400&a=ercot%3ALZ_NORTH", focus: "[data-allgrids-headline]" },
];
const LOOK = (focus) => `(() => {
  const el = document.querySelector(${js(focus)});
  const text = (e) => (e ? e.textContent.replace(/\\s+/g, " ").trim() : null);
  return {
    url: location.pathname + location.search, found: !!el,
    errorText: (document.body.innerText.match(/[^\\n]*(Application error|could not be read)[^\\n]*/) || [""])[0].slice(0, 200),
    links: document.querySelectorAll("[data-facility-siting]").length,
    ways: [...document.querySelectorAll("[data-facility-siting]")].map((e) => e.getAttribute("data-facility-siting")),
    held: /license needed/.test(document.body.innerText),
    headline: text(document.querySelector("[data-allgrids-headline]")),
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
        await evaluate(`(() => { const f = ${js(s.focus)}; const el = document.querySelector(f); if (el) { if (f === "h1") window.scrollTo(0, 0); else el.scrollIntoView({ block: "start" }); } return !!el; })()`);
        await sleep(800);
        Object.assign(rec, await evaluate(LOOK(s.focus)));
        const shot = await send("Page.captureScreenshot", { format: "png" });
        fs.writeFileSync(path.join(here, `${s.id}_${width}.png`), Buffer.from(shot.data, "base64"));
        rec.shot = `${s.id}_${width}.png`;
        console.log(`${rec.found ? "ok  " : "MISS"} ${s.id} ${width}: ${rec.url} (${rec.links} links, held ${rec.held})`);
      } catch (e) { failed += 1; rec.error = String(e.message ?? e); console.log(`FAIL ${s.id} ${width}: ${rec.error}`); }
      out.push(rec);
    }
    return { steps: out, pageErrors: errors };
  }, { width, height });
  if (!res) { console.log("no browser on this machine"); process.exit(1); }
  fs.writeFileSync(path.join(jsonDir, `walk-${width}.json`), JSON.stringify(res, null, 1));
}
process.exit(failed ? 1 : 0);
