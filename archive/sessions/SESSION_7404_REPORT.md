# Session 7404 report: the deal tracker's replication

Energy Research Warehouse (ERW). Chain 303, portable-laptop, 16 November 2026, about 09:48 to 09:56 UTC. Model spend: USD 0.

## What was done

- **Checked first:** `replication/deals/` was on no branch of origin. `scripts/check_deals.py` (session 2241) recomputes the four charts' figures only; it is kept and not redone.
- **The rows.** Read from the live set with the anon key, as session 1851 read them (`replication/deals/fetch_rows.py`): **590 rows** of `energy_deals` (529 on 11 November), the newest deal of 13 November. Every row now carries a `kind`; 61 rows are of the stricter prompt, 529 are the first prompt's rows with the new fields read in code.
- **The page's own functions on the rows.** `site/scripts/deal-tracker-figures.mjs` runs `lib/dealsview.ts`, `lib/deals2.ts` and `lib/dealsai.ts` on the rows with the register's folded pairs. The month's three cells moved, unchanged, from the page into `lib/dealsview.ts` (`monthBlock`) so Node runs what the page runs. No figure and no word of the page changes.
- **The replication.** `replication/deals/replicate.py`, its own Python from the rules: the table (its rows, the month's cells, what its filters count), the tracker tab (the folded deals, the headline counts, every bracket of the panel, the parties, the months), the comparables and the disclosed prices, the AI-power view with its two lists of ten, the four charts, and `/deals/capital`. **1,123 of 1,124 inside the tolerance; the one difference is named**: the capital view's file says 529 rows (built 6 November) and the table holds 590. `page_figures.json` and `.csv` hold both sides.
- **Tests.** `tests/test_session7404_trackers.py`, 7 pass (made-up deals only; two carry the ids of a pair the register folds, so the fold is tested on both sides). The 20 test files that name a changed deals module: 187 passed, 12 skipped. Type check of `app/deals/` and what it imports: 0 diagnostics.

## A change made and taken back

- The tracker's views read a deal's grid from its state alone; the table's Grid column reads a grid a story names first. One row of 590 differs. This session changed the views to read the named grid, then **took the change back**: it reverses a rule sessions 113 and 466 pinned in their tests and moves the comparables' groups. It is faults row 22, for your ruling, default unchanged.

## For Samuel's ruling

- Row 22 above. Default: the state alone in the three views.

## Decisions made without you

- The figures the pages print without a check key (the tracker's headline counts, the panel's brackets, the filters' counts) are in the replication under names of its own (`tracker|...`, `table|...`).
- Where the tenth and eleventh counterparties by megawatts are equal, the replication takes the names the page chose: the page's order of names is the browser's, not Python's.
- `tests/test_session49.py` reads its pinned line from the library file it moved to.

## Needs the key

- Nothing in this session.

## Commit

- `wip/7400-trackers`: `9e2b61d17`.
