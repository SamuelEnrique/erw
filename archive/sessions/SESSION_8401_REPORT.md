# Session 8401 report: the six screenshot faults read against their branches (chain 503, part A, step 4)

19 November 2026, samueloldlaptop (code role), unattended. Model spend USD 0. Nothing landed: the six branches are ruling alternatives, not for landing. No default changed, no hold lifted, `site/lib/release.ts` untouched. Nothing was seen in a browser (this machine cannot build the site), so each fixed row goes back to `wanted`.

## The six rows of `docs/state/browser_reads_wanted.md`

| Row | Branch | What it was | Result |
|---:|---|---|---|
| 341 | `wip/alt-impact-26` | the branch's code: at 390 px the A and B table ran to 409 px | fixed at `e313c0d4f`, pushed; under 640 px the table's figures wrap; `tests/test_alt_impact_26.py` failed before, 6 of 6 after; `wanted` |
| 362 | `wip/alt-prices-3` | the branch's code: the A less B table stood in no scrolling frame (504 px) | fixed at `e0d5fc2ac`, pushed; `site/scripts/test-prices-read.mjs` 27 of 29 before, 29 of 29 after; `wanted` |
| 366 | `wip/alt-supply-2` | the branch's code: the same (490 px) | fixed at `9b4d3f1c8`, pushed; `site/scripts/test-alt-supply-ab-frame.mjs` 3 of 5 before, 5 of 5 after; `wanted` |
| 363 | `wip/alt-storage-1` | the branch's code, not the data: the new column was summed from the panel's 45-day read, in which no calendar month is whole | fixed at `3858e0432`, pushed; the column has its own read; `site/scripts/test-alt-storage-month.mjs` 4 of 17 before, 17 of 17 after; `wanted` |
| 357 | `wip/alt-prices-2` | a data fault: the live `hub_price_comparison` holds no real-time row for the Southwest Power Pool's North hub for October 2026 (the builder needs 95 percent of the month's hours) | branch unchanged (`859d18fde`); request row 321 for the data machine; stays `fault` |
| 345 | `wip/alt-events-2` | neither: the hold of 21 October as it stands (the table `event_window_daily` is held, so PJM's figures read "license needed") | nothing changed (`3dc90d84a`); no hold lifted; stays `fault` until the owner rules on alternative 1 |

## What else was written

- The six State cells of `docs/state/browser_reads_wanted.md`, each with the earlier words kept after "Earlier:".
- Rows 321 and 322 of `docs/state/data_requests_done_line.md`: the Southwest Power Pool's real-time hours of October 2026 (row 357), and three missing days of `storage_daily_cycle` (no row for the Southwest Power Pool on 14 and 15 October, none for California on 1 November), found beside row 363.
- One line in each tool's `docs/reviews/ruling-alternatives-<tool>-2026-11-17.md` (impact, prices twice, supply, storage, events).

## What to review

- Nothing on production: these are branches of choices that wait for a ruling. Each fixed row says in its State cell what a reader with a browser should now see on a build of the branch at 390 px.

## Tests not run, and failures that were there before

- No full suite and no build; `tsc` on the storage page and its library alone (exit 0).
- Failing without these changes, each run on the branch as it came: `tests/test_session7203_allgrids_read.py` (row 10 of the All grids read), `tests/test_session179.py` (the steps file against this machine's table), the first check of `site/scripts/test-supply-read.mjs` on `wip/alt-supply-2`, and `tests/test_session148.py` `TheNodeTests` on `wip/alt-storage-1`.
- On `wip/alt-storage-1` the page now makes five reads, so session 148's pin of four reads counts five there (main: four).

## Needs the key

- Nothing.

## Decisions made without you

- Row 341: the figures wrap under 640 px; the three columns on a phone stay, as the row asks.
- Row 366: the frame takes the box's colour, so no white band stands inside the box. Not seen: a reader with a browser should look at it.
- Row 363: a read of its own for the column, from the first day of the month two before, so no standing figure can move.
- The live set was read with the public key, read only, for public grids only; no figure of a held grid is in any committed file.
- Six worktrees are left in place on this machine, clean and at their remotes (`C:\Users\lossa\Documents\erw-c503-*`).

## For Samuel's ruling

- **`wip/alt-events-1` has its own fault, described and not fixed:** it refuses the reads of the three held grids, and the event study makes all six reads in one attempt, so its whole section reads "license needed". The fix decides what a refused read draws under a hold, which is his to rule with entry 71 of the ranked list. Default taken: left as it is.
