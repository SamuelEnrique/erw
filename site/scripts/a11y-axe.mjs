// Energy Research Warehouse (ERW) site, session 3778 (chain 212): an accessibility read of pages in the internal view,
// with the axe-core engine the site's packages already hold (node_modules/axe-core), in the machine's own headless
// Chrome (scripts/browser.mjs, the internal view opened by its form, the token never in an address). AccessLint's live
// audit cannot carry the internal cookie, and every page is in review, so a visitor's read is the in-review page; this
// reads the page itself. WCAG 2.0, 2.1 and 2.2 A and AA rules only. Not a gate: it prints what it finds.
//
//   node scripts/a11y-axe.mjs <base> <path> [<path> ...]   e.g. http://localhost:3212 "/cost-of-power?view=allgrids"
//   A11Y_WIDTH=390 node scripts/a11y-axe.mjs ...           the same at another window width (default 1280)
//   A11Y_DETAIL=1 node scripts/a11y-axe.mjs ...            also the first 30 elements of each rule, as HTML
//   A11Y_WAIT_MS=4000 node scripts/a11y-axe.mjs ...        wait longer after each load before axe runs (default 2000)
//
// Prints one line per rule broken (its impact, id, the number of elements and the first selector) and a total a page;
// exits 0 when every page was read (whatever it found), 1 when a page could not be read, 2 without a browser.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { withBrowser } from "./browser.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const [base, ...paths] = process.argv.slice(2);
if (!base || !paths.length) {
  console.error("usage: node scripts/a11y-axe.mjs <base> <path> [<path> ...]");
  process.exit(2);
}
const AXE = fs.readFileSync(path.join(here, "..", "node_modules", "axe-core", "axe.min.js"), "utf-8");
const TAGS = ["wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22a", "wcag22aa"];
const width = Number(process.env.A11Y_WIDTH ?? 1280);

// Session 5423: axe runs after the page has hydrated and components/ScrollRegions.tsx has made each scrolling box a
// stop of the keyboard (it marks them 150 ms after it mounts, and again on every change). Run straight after the load,
// axe met the Grid's monthly mix table at 390 px before it was marked and reported scrollable-region-focusable, which
// the same page after a wait does not break. A11Y_WAIT_MS sets the wait (default 2000).
const WAIT = Number(process.env.A11Y_WAIT_MS ?? 2000);

const code = await withBrowser(async ({ go, evaluate, unlock, sleep }) => {
  await unlock(base);
  let failed = 0;
  for (const p of paths) {
    try {
      await go(base + p);
      await sleep(WAIT);
      const review = await evaluate(`document.body.innerText.includes("in review") && document.querySelectorAll("main *").length < 60`);
      if (review) { console.log(`${p}: the in-review page, not the page (the internal view did not open)`); failed += 1; continue; }
      await evaluate(AXE + ";true");
      const r = await evaluate(`axe.run(document, { runOnly: { type: "tag", values: ${JSON.stringify(TAGS)} }, resultTypes: ["violations"] })
        .then((x) => JSON.stringify(x.violations.map((v) => ({ id: v.id, impact: v.impact, help: v.help, n: v.nodes.length, first: (v.nodes[0]?.target ?? []).join(" "), html: v.nodes.slice(0, 30).map((n) => n.html.replace(/\\s+/g, " ").slice(0, 120)) }))))`);
      const v = JSON.parse(r);
      for (const x of v) console.log(`${p} | ${x.impact} | ${x.id} | ${x.n} element(s) | ${x.help} | first: ${x.first}`);
      if (process.env.A11Y_DETAIL === "1") for (const x of v) for (const h of x.html) console.log(`  ${x.id}: ${h}`);
      console.log(`${p}: ${v.length} rule(s) broken, ${v.reduce((s, x) => s + x.n, 0)} element(s), at ${width} px`);
    } catch (e) {
      console.log(`${p}: not read: ${e.message}`);
      failed += 1;
    }
  }
  return failed ? 1 : 0;
}, { width, height: 900 });
if (code === null) { console.log("no browser on this machine: not read"); process.exit(2); }
process.exit(code);
