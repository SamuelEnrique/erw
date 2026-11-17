// Energy Research Warehouse (ERW) site, session 7561: the deal tracker read as a fund analyst would read it
// (docs/reviews/deals-read-2026-11-16.md, rows 2 and 4). The opening line from the rows' own dates, and the placing
// form drawn to HTML by its own component with no priced deal, as the live set stood on 17 November 2026 (590 rows,
// the earliest dated 2025-01-05, the newest 2026-11-13, 42 dated before 2025-10-01; no PPA or offtake states a price).
//   cd site && node --import ./scripts/tsx-register.mjs scripts/test-deals-read.mjs
import { createElement as h } from "react";
import { renderToStaticMarkup } from "react-dom/server";

const { coverageWords } = await import("../lib/deals2.ts");
const { PlaceDeal } = await import("../app/deals/comparables/PlaceDeal.tsx");

let failed = 0;
const check = (ok, what) => { console.log(`${ok ? "ok  " : "FAIL"} ${what}`); if (!ok) failed++; };

// the 17 November dates in shape: 42 before 2025-10-01 and 548 on or after, with the two ends as the table has them
const dates = ["2025-01-05T08:00:00+00:00", ...Array(41).fill("2025-03-01T00:00:00+00:00"), ...Array(547).fill("2026-10-01T00:00:00+00:00"), "2026-11-13T12:37:09+00:00"];
const line = coverageWords(dates);
check(!line.includes("since 2025-10-01"), "the opening line no longer says 'since 2025-10-01' (42 rows are dated earlier)");
check(line.includes("from 5 January 2025 to 13 November 2026"), `the span is the rows' own: ${line}`);
check(line.includes("most are dated 1 October 2025 or later"), "it says most rows are from 1 October 2025 on");
check(coverageWords([]) === "Energy deals reported in the news, from the stories the ERW scores, each with its sources.", "no rows: the plain line, no span");
check(!coverageWords(["2026-10-02", "2026-11-13"]).includes("most are"), "no early row: no 'most' clause");

const none = renderToStaticMarkup(h(PlaceDeal, { deals: [], technologies: [], grids: [] }));
check(none.includes('data-place-none="0"') && none.includes("No PPA or offtake held states a price"), "with no priced deal the form says so before any typing");
check(!none.includes("Type a price to place it"), "and does not ask for a price it cannot place");

console.log(failed ? `${failed} failed` : "all passed");
process.exitCode = failed ? 1 : 0;
