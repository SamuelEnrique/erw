// Energy Research Warehouse (ERW), session 585: a shot of the battery page's source line (the foot drawn by
// components/tool/ToolPage.tsx SourceLine), at 1280 and at 390, before and after the session's fix, and its text.
//
//   node docs/brand/review-585/foot-585.mjs http://localhost:3585 <before|after>
//
// The internal view is opened by unlock(base) from site/scripts/browser.mjs (the token posted by the form, never printed).
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3585").replace(/\/$/, "");
const tag = process.argv[3] ?? "before";
const PAGES = [["battery-ercot", "/cost-of-power/battery"], ["battery-caiso", "/cost-of-power/battery?grid=caiso&dur=4&strat=dayahead&mw=100"]];
const texts = {};
for (const [width, height, mobile] of [[1280, 900, false], [390, 844, true]]) {
  const ok = await withBrowser(async ({ go, evaluate, unlock, send, sleep }) => {
    await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile });
    await unlock(base);
    for (const [name, p] of PAGES) {
      await go(base + p);
      await sleep(3000);
      const t = await evaluate(`(() => { const ps = [...document.querySelectorAll("main p")].filter((e) => e.textContent.trim().startsWith("Source: ERW tables")); const e = ps[ps.length - 1]; if (!e) return null; e.scrollIntoView({ block: "center" }); return e.textContent.replace(/\\s+/g, " ").trim(); })()`);
      await sleep(800);
      texts[`${name}_${width}`] = t;
      const shot = await send("Page.captureScreenshot", { format: "png" });
      fs.writeFileSync(path.join(here, `foot-${name}_${tag}_${width}.png`), Buffer.from(shot.data, "base64"));
      console.log(`${name} ${width} ${tag}: ${t ? t.slice(0, 160) : "NO SOURCE LINE"}`);
    }
    return 0;
  }, { width, height });
  if (ok === null) { console.log("no browser on this machine"); process.exit(1); }
}
fs.writeFileSync(path.join(here, `foot-${tag}.json`), JSON.stringify(texts, null, 1));
