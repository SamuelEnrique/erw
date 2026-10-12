// Energy Research Warehouse (ERW) site, session 196: the line "Checked against: ..." of the three decision pages, and
// the section of each Method note it links to.
//
//   npm run build && npm start
//   node scripts/check-cross-checks.mjs [base-url]
//
// In the internal view, for /cost-of-power/battery, /cost-of-power/seller and /cost-of-power:
//   1. the page's source line says "Checked against: N published figures (...)", with a link;
//   2. the link opens the page's step-by-step Method note at its section "Cross-checks";
//   3. that section's table has N rows, each with our figure, the published figure, its source, the gap and the reason,
//      and no cell is empty;
//   4. every source of the table is a link to its publisher, the warehouse's own table, or "the same" as the row above.
// Prints the three lines as read from the pages. Exits 1 if any assertion fails; 0 with a note when the machine has no
// browser.
import { withBrowser } from "./browser.mjs";

const base = (process.argv[2] ?? "http://localhost:3000").replace(/\/$/, "");
let failed = 0, n = 0;
const check = (ok, what, detail = "") => { n += 1; if (!ok) failed += 1; console.log(`${ok ? "ok  " : "FAIL"} ${what}${detail ? `: ${detail}` : ""}`); };
const PAGES = [["/cost-of-power/battery", "battery_earns_algorithm"], ["/cost-of-power/seller", "generator_earns_algorithm"], ["/cost-of-power", "datacenter_pays_algorithm"]];

const code = await withBrowser(async ({ go, evaluate, unlock, sleep }) => {
  await unlock(base);
  for (const [path, note] of PAGES) {
    await go(base + path);
    await sleep(1200);
    const line = await evaluate(`(() => { const e = document.querySelector("[data-checked-against]"); return e ? { n: Number(e.getAttribute("data-checked-against")), text: e.textContent.replace(/\\s+/g, " ").trim(), href: e.querySelector("a")?.getAttribute("href") ?? "" } : null; })()`);
    check(!!line && line.n > 0 && line.text.startsWith(`Checked against: ${line.n} published figures (`), `${path}: the source line says what the page was checked against`, line ? line.text : "no line");
    if (!line) continue;
    console.log(`     ${line.text}`);
    check(line.href === `/data/methods/${note}#cross-checks`, `${path}: the line links to its Method note's section`, line.href);
    await go(base + line.href);
    await sleep(800);
    const sec = await evaluate(`(() => {
      const a = document.getElementById("cross-checks");
      const h = [...document.querySelectorAll("h2")].find((x) => x.textContent.trim() === "Cross-checks");
      let t = h; while (t && t.tagName !== "TABLE") t = t.nextElementSibling;
      const rows = t ? [...t.querySelectorAll("tbody tr")].map((r) => [...r.children].map((c) => ({ text: c.textContent.trim(), link: !!c.querySelector('a[href^="https://"]') }))) : [];
      return { anchor: !!a, head: t ? [...t.querySelectorAll("thead th")].map((c) => c.textContent.trim()) : [], rows, review: !!document.querySelector("[data-in-review]") };
    })()`);
    check(sec.anchor && !sec.review, `${note}: the section "Cross-checks" is on the note, at its anchor`);
    check(JSON.stringify(sec.head) === JSON.stringify(["Our figure", "Published figure", "Source and date", "Gap", "Reason"]) && sec.rows.length === line.n, `${note}: the table has the ${line.n} rows the page counts`, `${sec.rows.length} rows`);
    check(sec.rows.every((r) => r.length === 5 && r.every((c) => c.text.length > 0) && r[4].text.length > 30), `${note}: every row has a gap and a reason`);
    check(sec.rows.every((r) => r[2].link || /ercot_storage_dam_awards_monthly/.test(r[2].text) || r[2].text === "the same"), `${note}: every published figure names where it was read`);
  }
  return failed ? 1 : 0;
});
if (code === null) { console.log("no Chrome or Edge on this machine: not proven here"); process.exit(0); }
console.log(failed ? `\ncheck-cross-checks FAILED: ${failed} of ${n}` : `\ncheck-cross-checks: all ${n} passed`);
process.exit(code);
