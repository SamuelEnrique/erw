// Energy Research Warehouse (ERW), session 541: the two pages whose words session 541 changed, in the internal view
// (every page is in review), at 1280 and at 390 px wide, before and after. For each page and width: a shot of the window
// with the changed line in its middle (<name>_<width>_<stage>.png, this folder), the changed line's own text, and every
// checked figure the page carries (data-check, data-raw, the text shown) into <run-dir>/measure-<width>-<stage>.json, so
// that the after run can be compared with the before run figure for figure.
//
//   cd site && npx next start -p 3541
//   node docs/brand/review-541/shots-541.mjs http://localhost:3541 <stage: before|after> <run-dir>
//
// The internal view is opened by unlock(base) from site/scripts/browser.mjs: the token is posted by the form, never in
// an address, and never printed. Exit 1 when a page or its line could not be read.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "../../../site/scripts/browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const base = (process.argv[2] ?? "http://localhost:3541").replace(/\/$/, "");
const stage = process.argv[3] ?? "before";
const runDir = process.argv[4] ?? here;
fs.mkdirSync(runDir, { recursive: true });
const WIDTHS = [[1280, 900, false], [390, 844, true]];
// name, address, the selector of the changed line (the first match is put in the middle of the window)
const PAGES = [
  ["research-library", "/research", "[data-finding-cards]"],
  ["research-archive", "/research", "[data-archive-weekly]"],
  ["cost-of-power-load", "/cost-of-power", "[data-load-reset]"],
];
// what each page says in the lines session 541 is about, read the same way before and after
const LINES = `(() => {
  const t = (e) => e ? e.textContent.replace(/\\s+/g, " ").trim() : null;
  const reset = [...document.querySelectorAll("form a[href]")].find((a) => /^Reset/.test(t(a)));
  return {
    findingCards: t(document.querySelector("[data-finding-cards]")),
    archiveDaily: t(document.querySelector("p[data-archive-daily]")),
    archiveWeekly: t(document.querySelector("p[data-archive-weekly]")),
    loadReset: t(reset),
    methodLinks: [...document.querySelectorAll("a[href]")].filter((a) => t(a) === "Method note").map((a) => a.getAttribute("href")),
  };
})()`;
const CHECKS = `[...document.querySelectorAll("[data-check]")].map((e) => [e.getAttribute("data-check"), e.getAttribute("data-raw"), e.textContent.replace(/\\s+/g, " ").trim()])`;

let failed = 0;
for (const [width, height, mobile] of WIDTHS) {
  const res = await withBrowser(async ({ go, evaluate, wait, unlock, send, sleep, errors }) => {
    await send("Emulation.setDeviceMetricsOverride", { width, height, deviceScaleFactor: 1, mobile });
    await unlock(base);
    const out = [];
    for (const [name, page, sel] of PAGES) {
      const rec = { name, page, width };
      try {
        await go(base + page);
        await wait("document.readyState === 'complete'", 60000, page);
        await sleep(3500);   // the charts draw after hydration
        rec.inReview = await evaluate(`!!document.querySelector("[data-in-review]")`);
        rec.unreadable = await evaluate(`(document.body.innerText.match(/[^\\n]*could not be read[^\\n]*/g) || []).slice(0, 5)`);
        rec.lines = await evaluate(LINES);
        rec.checks = await evaluate(CHECKS);
        // the before build has no data-load-reset: the Reset link of the load form stands in for it
        const found = await evaluate(`(() => { let e = document.querySelector(${JSON.stringify(sel)});
          if (!e && ${JSON.stringify(sel)} === "[data-load-reset]") e = [...document.querySelectorAll("form a[href]")].find((a) => /^Reset/.test(a.textContent.trim()));
          if (!e) return false; e.scrollIntoView({ block: "center" }); return true; })()`);
        if (!found) throw new Error(`no ${sel} on ${page}`);
        await sleep(500);
        const shot = await send("Page.captureScreenshot", { format: "png" });
        fs.writeFileSync(path.join(here, `${name}_${width}_${stage}.png`), Buffer.from(shot.data, "base64"));
        console.log(`ok   ${name} ${width}: ${rec.checks.length} checked figures${rec.unreadable.length ? ", UNREADABLE: " + rec.unreadable[0] : ""}${rec.inReview ? ", IN REVIEW (not unlocked)" : ""}; ${JSON.stringify(rec.lines)}`);
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
