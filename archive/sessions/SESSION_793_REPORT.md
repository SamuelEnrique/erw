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

Sessions 788 to 793 landed in one push (`task/788-793-allgrids`, commit `640cc577`), merged into main at 23:14 UTC (`f7e4763f`, run 39868971700).

- **The gate** (on `640cc577`): freeze 0; main in the commit; no `task/` branch in flight; suite 5,962 tests OK (304 skipped); npm ci 0; build 0; check-values 7,990 of 7,991 values equal. The ten held floors failed, and the 21 October Digest's revised WTI (production the same).
- **The steps after check-values**, on a build of the same commit (lock `s793b`, built on `db_probe`'s 0): check-routes 0 (226 pages, 0 failed), check-cross-checks 0 (92 of 92), check-csp 0 (97 pages, 0 violations).
- **Before the push**: freeze status 0; no other `task/` branch but `task/198-battery-data`; the push conditional on the ancestry check (0).
- **Snapshots**: `s793-before` at 23:00 UTC; the push at 23:01:00. Vercel's status on `f7e4763f`: "Deployment has completed" (23:15:51). `compare s793-before s793-after`: **0 differences** on 25 pages, expected (every page is in review).
- The merged `wip/793-allgrids` and `wip/787-records` were deleted on GitHub; the worktrees of 787r and 788 to 793 removed.

## Decisions made without you

1. **The figures in full**, as the page's data holds them, not rounded to the page's two decimals: the file is for reuse.
2. **The utility's kind as its own column**, so a delivery revenue is never read as a bundled price.

## For Samuel's ruling

- Nothing new.

## Files

- New: `site/app/cost-of-power/AllGridsDownload.tsx`, `tests/test_session793.py`, `docs/brand/review-793/`, this report.
- Changed: `site/lib/siting.ts` (`columnWords`), `site/app/cost-of-power/AllGridsView.tsx` (the button).
