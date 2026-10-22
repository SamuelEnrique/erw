# Session 589 report: chain 034's sessions merged and landed, the note, the queue

22 October 2026, from about 23:46 UTC on 21 October, unattended, on samueloldlaptop (the code machine), the last session of `queue/done/034-night-22-october-code.md` (sessions 577 to 589, written by session 506). Model spend USD 0. No warehouse data written.

## Read these first

LANDING_READ_FIRST

- **Sessions 577 to 588 ran as agents**, one worktree each (`C:\Users\lossa\Documents\erw-5NN`), at most four at a time, the heavy steps through `scripts/buildlock.py`. Each pushed its `wip/NNN-s` branch and wrote its report; none landed. This session merged them onto `wip/589-land` with main, in the order they finished, and also `wip/506-combined` (session 506's records of chain 023).
- **The landing ran through session 579's `scripts/land_check.py`**, its first real run. The first run stopped on `task/198-battery-data` (last commit 11 October, never merged), which the script took for a branch in flight; this session made a branch quiet for 48 hours "left over, not judged", with two tests, and ran it again.

## How the chain ran

| Session | Branch, last commit | Merged | Its checks (its report has each) |
|---|---|---|---|
| 577 | `wip/577-s`, `1515627b` | clean | 575 tests of the brief, Roundup, email and chart template OK |
| 578 | `wip/578-s`, `d4bca7e2` | clean | the suite as GitHub runs it, its one error Node's libuv exit on Windows |
| 579 | `wip/579-s`, `d7361723` | clean | 25 tests, then 27 with this session's two |
| 580 | `wip/580-s`, `1e165167` | clean; its test's pin of the count line moved to main's form (session 562's resolution) | build 0, check-routes 0 (226 pages) |
| 581 | `wip/581-s`, `9d882a61` | clean | two builds, check-links 85 problems then 0; check-values 2,857 equal |
| 582 | `wip/582-s`, `c14daaf7` | clean | five replications against the pages |
| 583 | `wip/583-s`, `abe419e9` | clean | three builds; AccessLint 271 findings then 30; check-values 2,578 equal |
| 584 | `wip/584-s`, `10025b80` | clean | three builds; check-390 43 pages then 5; check-values 6,446 of 6,457 (11 newer latest prices) |
| 585 | `wip/585-s`, `34bb27b2` | clean | two builds; the walk 32 of 32; check-values 748 of 748 |
| 586 | `wip/586-s`, `a6800a86` | clean | `npm audit --omit=dev` 0 |
| 587 | `wip/587-s`, `8fbca167` | clean | build 0, check-routes 0; 14 rows equal to the CSV |
| 588 | `wip/588-s`, `edda5f79` | clean | two builds; check-findings-grids 173 of 173 |

The build lock was held for long stretches by single sessions (583 for 73 minutes while it mended its scanner), so 588 and 584 waited; a message asked 583 to release between heavy steps.

## The landing

`scripts/land_check.py --ref wip/589-land --lock-as s589` at `be0a73d7` (all twelve sessions, `wip/506-combined` and main merged), 03:40 to 03:58 UTC; its record is `runs/land_check/be0a73d7d1a5fee09117ad06610769e3f286bc69.txt` in the worktree (not in git):

| Step | Exit | Result |
|---|---|---|
| freeze | 0 | no freeze |
| main merged | 0 | origin/main in the commit |
| task/ branches | 0 | `task/617-623-sources` (the data machine's) in flight and merging cleanly; `task/198-battery-data` left over (10 days) |
| db_probe | 0 | |
| build lock | 0 | held by s589 |
| the suite in a clean worktree | 0 | 5,762 tests in 466 s, 302 skipped, OK |
| npm ci, build | 0, 0 | 89 s |
| check-values, all pages | 1 | 6,456 of 6,456 values equal; 11 floors: session 408's ten held ones and `/digest` (0 against 9) |

`/digest`'s floor is the day's: before the 14:00 UTC run there is no Digest for 22 October, and production fails the same floor (`CHECK_VALUES_PAGES=/digest` against production at 04:05 UTC: 70 of 70 equal, the same floor). So the run is a pass by the chain's rule with that one named. The gate stops at check-values' exit 1 and did not reach check-routes, check-cross-checks or check-csp; those ran by hand on a fresh build of the branch's head (`runs/s589_rest.sh`):

REST_TABLE

## Decisions made without you

1. **The branches were cut from `wip/506-combined`**, which held chain 023 before portable-laptop's session 563 landed it at 00:12 UTC; later ones merged main.
2. **Agents, three or four at a time**, with one brief (`runs/chain_034/BRIEF.md`, not in git) and the heavy steps on the build lock.
3. **584 cut from `wip/589-land`** so its shared-component fixes sit on 583's.
4. **`land_check.py` amended at its first real run**: a `task/` branch quiet for 48 hours is left over (named on the step's line), not in flight.
5. **Test 580's pin** follows main's form of the count line.
6. **The ten held floors** of session 408 pass; `/digest`'s floor before the day's Digest (14:00 UTC) is the day's, not a fault.

## For Samuel's ruling

- `task/198-battery-data` (session 198, 11 October, never merged): delete it, or land it.
- The rest are the sessions' own, one a line in each report, gathered in `docs/state/review_2026-10-23_code.md`.

## To finish

TO_FINISH_589
