# Session 1055 report: the conformance file, a second version

23 October 2026, about 07:56 UTC, on samueloldlaptop, unattended, on `wip/1042-allgrids`. Chain `queue/done/072-day-23-october-code-allgrids-packages-2.md`, session 1055. Model spend USD 0. Requests: 53 to the live set (ceiling 60), the anon key only.

- **Only call 7 left the live set's window before 1 December** (`eia930_all_demand` on 18 October; 35 days, about 22 November). It now fetches `carbon_intensity_hourly` (ERCOT's `intensity_demand`, the same 24 hours), which the live set keeps 430 days. The next calls to leave are the daily intensity of 1 to 7 October (100 days, about 9 January 2027) and call 7 itself (about 22 December 2027). Every other call and expected answer is as version 1's.
- **A fault found and fixed**: `make.py` wrote the file without its `errors` block (session 1013's sentences, which test 1013 and the runners read). It now carries the block over from the file as it stands. The first remake lost it and was made again, hence two makes of 25 requests.
- **No call added for chain 049's tables**: they are on the live set's hold list, with no live window.
- The Python runner passed call 7 (`run_python.py --only 7`, 3 requests); `write_runners.py` wrote `run_stata.do` and `run_r.R` again for the owner.
- `docs/methods/packages.md`: "Version 2 of the file".

## Checks

| Check | Exit | Result |
|---|---|---|
| `make.py` (twice) | 0 | 20 calls; 25 requests each |
| `run_python.py --only 7` | 0 | ok 07 |
| `write_runners.py` | 0 | |
| tests 1006, 1013 | 0 | |

## The landing

Landed with sessions 1043 to 1061 in one push: `wip/1042-allgrids` gated by `scripts/land_check.py` at `a8a91dde` (freeze, main merged, task branches, the clean-copy suite 6,224 tests OK, npm ci, the build: pass; check-values: 12 failures, all the chain's known three: the ten license-held floors, `/digest` before the day's issue, and the 21 October Digest's revised WTI; every All grids value matched). As the rules say, the same commit was built locally on its own and checked by hand: check-routes 0 (225 pages in review, 0 failed), check-cross-checks 0 (92 passed), check-csp 0 (97 pages, 0 violations). Main then gained one queue file only (data chain 052's), merged without a third gate (`3306941d`). Snapshot `c072a-before` as its own command at 08:58 UTC; pushed to `task/1042-1061-allgrids` after the ancestry check; merged by run 39928557187 as `cbf8662e`; production served the node list's county filter (`data-node-county`) at 09:18 UTC (9 minutes of probing); `c072a-after` and `compare`: **0 differences** on the 25 pages (every page is in review: a visitor sees the in-review page), expected.

## Decisions made without you

1. **Call 7 on the hourly intensity** rather than dropping it: the same hours, a table the live set keeps 430 days.
2. **The full runner was not re-run** (the ceiling): only call 7 changed.

## For Samuel's ruling

- None new.
