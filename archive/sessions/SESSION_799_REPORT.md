# Session 799 report: the replication, extended

22 October 2026, from 23:23 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-799` on `wip/799-allgrids` (cut from `wip/798-allgrids`). Chain `queue/done/065-late-22-october-code-allgrids-5.md`, session 799. Model spend USD 0. No warehouse data written; no request to a publisher. The reads: the live set with the anon key, the warehouse's CSVs, a local build of `wip/796-allgrids`.

## Read these first

- **794's figures are computed a second time** from `node_basis_daily`'s daily rows (`--tables`), for two nodes as A and B (`a=ercot:7RNCHSLR_ALL&b=ercot:A4_DGR1_RN`, added to the replication's pages):
  - each month's mean daily basis (`nodemonth`, 26 figures);
  - B less A for the basis spread (`nodediff`).
- **Against the build: 123 figures computed, 111 beside the page, 0 differ.**
- **Not replicated**:
  - 795's groups, which are words on the page, not figures; their exactness is held by test 795, which compares the groups' monthly figures and days;
  - 793's download, the page's own figures in a file;
  - B less A for the swing, which is the difference of two swings already replicated (746).

## What to review

1. `runs/chain_062/repl799.out` on this machine.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| the replication against the build, `--tables` | 0 | 123 / 111 / 0 differ |

## The landing

Sessions 794 to 799 landed in one push (`task/794-799-allgrids`, commit `6beea9d4`), merged into main at 23:57 UTC (`96a865c3`, run 39874035357).

- **The gate** (`land_check.py` on `6beea9d4`):
  - freeze 0; main in the commit; no `task/` branch in flight;
  - suite 5,966 tests OK (304 skipped); npm ci 0; build 0;
  - check-values 8,045 of 8,046 values equal; it failed only on the ten held floors and the 21 October Digest's revised WTI (production the same).
- **The steps after check-values**, on a build of the same commit: check-routes 0 (226 pages, 0 failed), check-cross-checks 0 (92 of 92), check-csp 0 (97 pages, 0 violations).
- **Before the push**: freeze status 0; the push conditional on the ancestry check.
- **Snapshots**: `s799-before` at 23:46 UTC; Vercel's deployment of `96a865c3` completed at 23:59; `s799-after` at 00:00 on 23 October. `compare s799-before s799-after`: **0 differences** on 25 pages, expected (every page is in review).
- The merged `wip/` and `task/` branches of 794 to 799 were deleted on GitHub, and their worktrees removed (976 found none left).

## Decisions made without you

1. **Two nodes the replication already reads**, so the months come from the same rows as their spread and swing.

## For Samuel's ruling

- Nothing new.

## Files

- Changed: `warehouse/replication/siting.py` (the months and the spread's difference; one page).
- New: this report.
