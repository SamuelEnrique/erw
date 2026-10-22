# Session 793 report: the hub table's download

22 October 2026, from 22:31 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-793` on `wip/793-allgrids` (cut from `wip/792-allgrids`). Chain `queue/done/065-late-22-october-code-allgrids-5.md`, session 793. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **"Download these N rows (CSV)" above the hub table**, as 724 gave the node list. It holds the rows shown, with the sort and filters as set, in the page's own figures, and is made in the browser, so there is no new route.
  - **The header**: the tab and its address, the load, the tables, the method.
  - **The columns**: one per column of the table, plus `utility_kind` (bundled, delivery only, energy only, 726's words).
- **Words where the page draws words, never a number** (`lib/siting.ts`, `columnWords`, each cell function's own words):
  - PJM's energy and capacity read "license needed";
  - CAISO's transmission and all-in read "not held";
  - ERCOT's capacity reads "no capacity market", where the page shows those words and the all-in counts zero.
- **Tried in a browser**: the button pressed, the file saved and read (48 rows sorted by all-in; PJM and CAISO by the utility sort).
- **No figure moved**: check-values 2,908 of 2,908; the existing tab 0 differences.

## What to review

1. After the landing, `https://erw-flame.vercel.app/cost-of-power?view=allgrids&mw=1000&sort=allin&dir=asc` (internal view): press "Download these 48 rows (CSV)" and open the file.
2. Shots: `docs/brand/review-793/`.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session793`, `716`, `774` | 0 | OK |
| `db_probe.py` (the build only on its 0) | 0 | |
| `npm ci`, `npm run build` twice (lock `s793`, beat) | 0 | |
| `runs/chain_062/dl793.mjs`, the button pressed in a browser | 0 | the file saved: 48 rows; 3 for PJM and CAISO |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power` | 0 | 2,908 of 2,908 |
| `check-existing-tab.mjs` | 0 | every figure the same |

## The landing

Sessions 788 to 793 land together from this branch (below, once done).

## Decisions made without you

1. **The figures in full**, as the page's data holds them, not rounded to the page's two decimals: the file is for reuse.
2. **The utility's kind as its own column**, so a delivery revenue is never read as a bundled price.

## For Samuel's ruling

- Nothing new.

## Files

- New: `site/app/cost-of-power/AllGridsDownload.tsx`, `tests/test_session793.py`, `docs/brand/review-793/`, this report.
- Changed: `site/lib/siting.ts` (`columnWords`), `site/app/cost-of-power/AllGridsView.tsx` (the button).
