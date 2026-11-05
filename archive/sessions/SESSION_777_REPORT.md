# Session 777 report: the node list's payload

22 October 2026, from 20:45 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-777` on `wip/777-allgrids` (cut from `wip/776-allgrids`). Chain `queue/done/064-night-22-october-code-allgrids-4.md`, session 777. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **Where the node list's bytes went**: the 873 rows handed to the browser were 201 KB of JSON.
  - About 70 KB of that was each field's name repeated on every row.
  - 17 KB was an id that is the node's name after "ercot:".
- **What changed, with no word or figure moved**: the rows go to the browser **column by column** (`lib/siting.ts`, `nodeColumns`), and the browser puts them back together (`nodeRowsOf`, the id rebuilt from the name). A test checks that the rows come back equal, field by field, under the flexible profile (`tests/test_session777.py`).
- **The node list's page: 340,129 to 226,143 bytes** (a third less); the server's payload in it 258 KB to 144 KB.
- **No figure moved**: check-values 2,908 of 2,908; the existing tab 0 differences.

## What to review

1. After the landing, `https://erw-flame.vercel.app/cost-of-power?view=allgrids&rows=nodes` (internal view): the same list, sorts, filters and download.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session777`, `724`, `746`, `772`, `716` | 0 | OK |
| `db_probe.py` (the build only on its 0) | 0 | |
| `npm ci`, `npm run build` (lock `s777`, beat) | 0 | |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power` | 0 | 2,908 of 2,908 |
| `check-existing-tab.mjs` | 0 | every figure the same |
| `weigh.mjs`, the node list | 0 | 226,143 bytes (was 340,129) |

## The landing

Sessions 766 to 777 landed in one push (`task/766-777-allgrids`, commit `59ce3050`), merged into main at 21:29 UTC (`587d192e`, run 39855479271). The landing the chain file put at 771 was moved here, so 778 to 780 walk a production that holds 772 to 777.

- **The gate** (on `59ce3050`): freeze 0; main in the commit; no `task/` branch in flight; suite 5,960 tests OK (304 skipped); npm ci 0; build 0; check-values 7,990 of 7,991 values equal. The ten held floors failed, and the 21 October Digest's revised WTI (production the same).
- **The steps after check-values**, on a build of the same commit (lock `s777b`, built on `db_probe`'s 0): check-routes 0 (226 pages, 0 failed), check-cross-checks 0 (92 of 92), check-csp 0 (97 pages, 0 violations).
- **Before the push**: freeze status 0; no other `task/` branch but `task/198-battery-data`; the push conditional on the ancestry check (0).
- **Snapshots**: `s777-before` at 21:13 UTC; the push at 21:13:26. Vercel's status on `587d192e`: "Deployment has completed" (21:30:21). Production showed 773's card at 21:30:43. `compare s777-before s777-after`: **0 differences** on 25 pages, expected (every page is in review).
- The merged `wip/777-allgrids` and `wip/765-records` were deleted on GitHub; the worktrees of 765r and 766 to 777 removed.

## Decisions made without you

1. **No figure rounded**: the full figures stay (check-values compares them to the recomputed ones); only the shape of the hand-over changed.

## For Samuel's ruling

- Nothing new.

## Files

- Changed: `site/lib/siting.ts` (`NodeColumns`, `nodeColumns`, `nodeRowsOf`), `site/app/cost-of-power/AllGridsNodes.tsx`, `site/app/cost-of-power/AllGridsView.tsx`.
- New: `tests/test_session777.py`, `docs/brand/review-777/`, this report.
