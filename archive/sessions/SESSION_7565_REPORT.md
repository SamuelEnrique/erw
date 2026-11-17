# Session 7565 report: the Grid tool read as an AI lab's energy lead (samueloldlaptop, 17 November 2026 UTC)

- **Asked:** the last of the six reads: `/grid`. Checked first: no `grid-read` file on any branch; part A's 7 rows read.
- **The read:** `docs/reviews/grid-read-2026-11-16.md`. Five cases (PJM now; PJM beside the other ISOs on carbon; ERCOT now; PJM's ties against the Mix tab's hour; the monthly line since 2018), 7 rows: 2 site fixed, 1 data machine (request 311), 2 rulings, 2 browser (311, 312).
- **How:** `/grid` drawn whole without a build, on the live set's public reads with the anon key alone, by two new scripts (`grid-read-page.mjs`, and `grid-read-register.mjs` with `grid-read-loader.mjs`, a stand-in for `next/dynamic`) and React's streaming renderer for the page's async parts.
- **Found:** PJM's Clean tab said its carbon intensity was not in the warehouse, above a ranking of the same table (a four-day window called an empty table); the Mix tab called the daily table's newest hour EIA's newest, while the Network tab on the same page held demand 28 hours newer; the carbon table is three days behind the demand.
- **Fixed on the page:** both, in words (`site/lib/gridwords.ts`; `components/grid/YourGrid.tsx`, `components/grid/NowView.tsx`). The words live in a lib file because `scripts/page_tables.py` splits a component at each top-level export; a first try that exported them from the components failed `test_session502`, which now passes. Tests: `site/scripts/test-grid-read.mjs` 6 of 6; pytest of the fifteen tests naming the two components, 195 passed, 21 skipped.
- **What to review:** `https://erw-flame.vercel.app/grid?grid=pjm&view=clean` (the block's line); `https://erw-flame.vercel.app/grid?grid=pjm&view=mix` (the lead's tip).
- **Needs the key:** nothing (the Ask panel was not asked).
- **Decisions made without you:** the reads used the anon key alone (the service key was unset for the drawing), as a visitor's page does.
- **For Samuel's ruling:** rows 4 (three hours in one row; default: each at its own hour) and 5 (the Mix tab's daily table; default: kept, named).
