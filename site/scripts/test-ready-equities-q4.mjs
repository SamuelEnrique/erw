// Energy Research Warehouse (ERW) site, session 11408 (chain 770, part C): the ready branch "a fourth quarter worked out
// as the year less its nine months" (lib/equities.ts fourthQuarters), on a fixture, and counted on the real series files.
//   node --import ./scripts/events-page-register.mjs scripts/test-ready-equities-q4.mjs [series dir]
// Prints one line of counts as JSON last; exits 1 on a failed check.
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SITE = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const E = await import("../lib/equities.ts");
let bad = 0;
const check = (ok, words) => { if (!ok) { bad++; console.log(`FAIL ${words}`); } else console.log(`ok   ${words}`); };

const M = 1_000_000;
const cols = ["period_start", "period_end", "months", "fy", "fp", "form", "filed", "revenue", "net_income", "capex", "debt", "shares_outstanding", "accession", "url"];
const rows = [
  ["2026-01-01", "2026-03-31", 3, 2026, "Q1", "10-Q", "2026-05-05", 800 * M, 140 * M, 310 * M, 7800 * M, 77.6 * M, "a", null],
  ["2025-01-01", "2025-12-31", 12, 2025, "FY", "10-K", "2026-02-26", 3200 * M, 490 * M, 1400 * M, 8700 * M, 77.5 * M, "b", null],
  ["2025-01-01", "2025-09-30", 9, 2025, "Q3", "10-Q", "2025-11-07", 2350 * M, 360 * M, 1000 * M, 7600 * M, 77.4 * M, "c", null],
  ["2025-07-01", "2025-09-30", 3, 2025, "Q3", "10-Q", "2025-11-07", 820 * M, 130 * M, null, 7600 * M, 77.4 * M, "c", null],
  // a year whose fourth quarter was filed on its own: nothing is worked out
  ["2024-10-01", "2024-12-31", 3, 2024, "Q4", "10-K", "2025-02-20", 900 * M, 100 * M, null, 7000 * M, 77 * M, "d", null],
  ["2024-01-01", "2024-12-31", 12, 2024, "FY", "10-K", "2025-02-20", 3100 * M, 400 * M, 1300 * M, 7000 * M, 77 * M, "d", null],
  ["2024-01-01", "2024-09-30", 9, 2024, "Q3", "10-Q", "2024-11-07", 2200 * M, 300 * M, 950 * M, 6900 * M, 76.9 * M, "e", null],
  // a year with no nine months filed: no point
  ["2023-01-01", "2023-12-31", 12, 2023, "FY", "10-K", "2024-02-20", 3000 * M, 380 * M, 1200 * M, 6800 * M, 76.5 * M, "f", null],
];
const fsx = E.filingsOf({ quarterly_columns: cols, quarterly: rows });
const q4 = E.fourthQuarters(fsx, "revenue");
check(q4.length === 1 && q4[0].f.period_end === "2025-12-31" && q4[0].v === 850 * M && q4[0].nine.period_end === "2025-09-30",
  "2025: the year's 3,200 less the nine months' 2,350 is a fourth quarter of 850, from its two filings");
check(E.fourthQuarters(fsx, "capex").map((p) => p.v / M).join(" ") === "350 400", "capital spending: 1,300 less 950 and 1,400 less 1,000 (no quarter of it is filed in either year)");
check(E.fourthQuarters(fsx, "debt").length === 0 && E.fourthQuarters(fsx, "shares_outstanding").length === 0, "debt and shares are at a period's end: never worked out");
check(E.figureLine(fsx, "revenue", "3").map((p) => p.f.period_end).join(" ") === "2024-12-31 2025-09-30 2026-03-31", "the filed line is unchanged");

// the real files: how many companies and quarters gain a point, revenue by 3 months
const dir = process.argv[2] ?? path.join(SITE, "data", "equities", "series");
let files = 0, companies = 0, filed = 0, worked = 0, withQ4Before = 0, withQ4After = 0;
for (const name of fs.readdirSync(dir).filter((n) => n.endsWith(".json"))) {
  const s = JSON.parse(fs.readFileSync(path.join(dir, name), "utf8"));
  if (s.kind !== "company") continue;
  files++;
  const f = E.filingsOf(s);
  if (!f.length) continue;
  const line = E.figureLine(f, "revenue", "3"), w = E.fourthQuarters(f, "revenue");
  const ends = new Set(E.figureLine(f, "revenue", "12").map((p) => p.f.period_end));
  const isQ4 = (p) => ends.has(p.f.period_end);
  if (line.length) companies++;
  filed += line.length; worked += w.length;
  if (line.some(isQ4)) withQ4Before++;
  if (line.some(isQ4) || w.length) withQ4After++;
}
console.log(JSON.stringify({ files, companies_with_quarters: companies, quarters_filed: filed, fourth_quarters_worked: worked, companies_with_a_fourth_quarter_before: withQ4Before, after: withQ4After }));
process.exitCode = bad ? 1 : 0;
