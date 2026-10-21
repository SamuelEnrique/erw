# Session 538 report: the Grid's and Research's cross-checks read by the check

21 October 2026, from about 20:00 UTC, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-538` on `wip/538-s` (from `origin/main` at `2ecba09d`). Chain 024 (`queue/done/024-night-21-october-code.md`), session 538. Model spend USD 0; no pull from any publisher; no warehouse data written; no page changed.

## Read these first

- **`site/scripts/check-cross-checks.mjs` now reads the two sections session 381 wrote**: "Cross-checks" of the Grid tool's note (`docs/methods/grid_network.md`, 11 rows) and of Research's (`docs/methods/automated_analysis_findings.md`, 4 rows), as it reads the three decision pages' notes: the section at its anchor, the five columns, as many rows as the note's markdown holds and never fewer than 381 wrote, no empty cell, a reason longer than 30 characters, every source a link, "the same", or an ERW Method note that opens. The three decision pages' checks are unchanged.
- **Six of the fifteen rows name a figure by its key, and each is traced** (rule 8 of the script's head):
  - Research, ERCOT's 2025 median (25.68) and 99.9th percentile (311.80): the card `batteries_lunch_grids`'s JSON (`numbers.ercot_median_last`, `ercot_p999_last`, `ercot_last_full_year`), the thesis's table in the note the row cites (`ercot_peak_premium`, "Thesis reproduction (HB_HUBAVG)", 2025), the gap; on a built site, the card page's callout `finding|batteries_lunch_grids|callout|0|after|ercot` equals the row's percentile over its median (12.1x).
  - Research, the queue's withdrawn share (75.2 percent of 3,509 GW): the card `queue_divorce`'s `withdrawn_pct` and `requested_gw`, the thesis's "75 percent of 3,501 GW" as Finding 3 quotes it, both gaps (+0.2 points, +8 GW); on a built site the callout `finding|queue_divorce|callout|0|before|-` ("75% of 3,509 GW").
  - Research, the CDC's rates (6.1 and 2.4): the card's `cdc_marriage_rate`, `cdc_divorce_rate`, and the reason's 39.3 percent and 1.9 times (`cdc_ratio_pct`, `queue_over_cdc`), the CDC's words as the note quotes them; on a built site the callouts `finding|queue_divorce|callout|2|before|-` ("2.4 / 6.1") and `...|2|after|-` ("39%").
  - Grid, net imports by ties in the hour 2026-10-12 03:00 UTC (two rows, seven grids): the Network view's replication file (`/grid/erw_2026_grid_replication.csv`, session 266): its hour, each grid's ties summed (our figure), EIA-930's demand less net generation (the published figure), and the gap, all 21 equal. On a built site the file is read from the site.
- **Nine Grid rows name no figure a check can read** (the 2025 EIA-923 totals, the 360-hour and 888-hour means, the lag of 13 October, the tie of 15 February 2021): the script prints each as a `note` line. They are historical comparisons; no page draws them by a key.
- **`--files`** runs checks 5 to 8 from the repository's files with no browser and no server (`--root` points it at a copy); a machine with no browser now runs the files instead of passing with only a note.

## What to review

- The script: `https://github.com/SamuelEnrique/erw/blob/wip/538-s/site/scripts/check-cross-checks.mjs`
- The test: `tests/test_session538.py` (14 tests, seven planted faults).
- The two sections it reads, in the internal view: `/data/methods/grid_network#cross-checks`, `/data/methods/automated_analysis_findings#cross-checks`; the card pages it reads: `/research/card/batteries_lunch_grids`, `/research/card/queue_divorce`.

## Checks

Every gate redirected to a file under `C:/Users/lossa/Documents/erw/runs/chain_024/s538/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 538"` | 0 | on duty |
| `node scripts/check-cross-checks.mjs --files` (first run) | 1 | 7 of 55: the script read "930" of "EIA-930's demand ..." as a figure; fixed (the figures after the cell's colon) |
| `node scripts/check-cross-checks.mjs --files` | 0 | all 55 passed |
| `tests.test_session538` | 0 | 14 tests OK |
| `tests.test_session448`, `196`, `381` (the tests that read the script or the two notes) | 0 | 24 tests OK |
| `duty.py beat`, `db_probe.py` before the build | 0, 0 | the database open (0.53 s) |
| `npm ci` in the worktree's `site/` (under `runs/build.lock`, taken at 20:18 UTC after session 541 let it go) | 0 | |
| `npm run build` | 0 | no statement timeout in the log |
| `node scripts/check-cross-checks.mjs http://localhost:3538` (the internal view, the built site) | 0 | all 77 passed: the three decision pages as before (17, 34 and 8 published figures), the two notes' sections, and the four card callouts by their check keys (12.1x; 75% of 3,509 GW; 2.4 / 6.1; 39%) |
| The server on 3538 stopped, the mutex let go | | right after the check |
| The whole suite (`ERW_LOCK_EXEMPT=1 ... unittest discover -s tests`) | 1 | 5,252 tests, 268 skipped, 2 failures, neither this session's (below) |

The two failures of the whole suite, neither reading the file this session changed:

- `test_session156.TheNodeTests.test_the_sessions_own_tests_pass_with_no_request_and_no_switch_set`: known on this machine tonight (the orchestrator's list). Last line: `AssertionError: 1 != 0 : ok 1 the ten tables of the live set are in the panel's scope, ...`.
- `test_session153.TheNodeTests.test_the_sessions_own_tests_pass_with_no_request`: the ask panel's node tests, check 13: `p07: last_twelve_months.premium_usd_per_mwh 14.69 !== 14.66` (a replayed question's twelve months against the tables on this machine: a test that watches the day or the local table, session 534's subject). Last line: `AssertionError: 1 != 0 : ... each value the table's own row`.

## Decisions made without you

- **Extended the script rather than a sibling**: the two notes are checked by the same rules and the same run as the three decision pages, so one command proves all five; the three pages' code is unchanged, and `test_session448`'s two pinned strings stay.
- **A source by an ERW Method note passes**: three Research rows give as their source the owner's thesis, held in `docs/methods/ercot_peak_premium.md` and in Finding 3 of the note itself, which has no public address. The check accepts a source that names a Method note that opens on the site, prints each such row as a `note` line, and then reads the published figure in that note (the thesis's table, Finding 3's words), so the row is checked where it says it was read. No note's words were changed to add a link.
- **The Grid's rows by the replication file**: the page draws the newest hour, not 12 October's, so no figure of `/grid` carries the row's key today; the Network view's replication file for that hour (`/grid/erw_2026_grid_replication.csv`, served by the build) is the page's published record of it, and the check reads it from the built site.
- **A callout held for a license is named, not failed**: none was held tonight (ERCOT's and the queue card's figures are not held).
- **With no browser on a machine, the files are checked** instead of a pass with only a note.

## For Samuel's ruling

- Research's three thesis rows have no publisher's link because the thesis has no public address: keep the source as the Method note that holds it (as the check now accepts), or give the thesis an address the rows can link.
- Session 381's item stands: a "Checked against" line on `/grid` (11 published figures) and `/research` (4), which this session did not add.

## Files

- `site/scripts/check-cross-checks.mjs` (extended)
- `tests/test_session538.py` (new)
- `archive/sessions/SESSION_538_REPORT.md` (this report)
