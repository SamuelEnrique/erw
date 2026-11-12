# Session 3779 report: the datacenter and findings refresh made to pass its tests (parked 204, session 3284)

Energy Research Warehouse (ERW). Chain 212, data machine (lab-desktop), 12 November 2026, done inside session 3774's time (13:14 to 13:24 UTC) while the daily run held the data lock; this report written at 13:41. Opus 5.5. Model spend USD 0. Requests: none.

## Read these first

- **Why the refresh was put back:** `runs/data_machine_dm_test_replication.out` (the run of 10 November) names three tests, with five failures:
  - **1491** (the datacenter replication): five page figures recorded by hand on 6 November no longer met the refreshed files (the bill, the twelve months' carbon and tonnes, the window's hours and carbon).
  - **538** (the cross-checks): the Research note's `queue_divorce` row read 3,509 GW; the recomputed card reads 3,591.
  - **720** (the siting cards): `siting_gigawatt` and `siting_flexible` were not rebuilt after the page files.
  - Test 190 passed on 9 and 10 November, so it was left as it is.
- **Each test now follows a refresh,** on `wip/c212-data`:
  - **1491:** `replication/datacenter/figures_of_the_page.py` (new) asks the page's own code for the figures, through `site/scripts/datacenter-page-figures.mjs` (new; `lib/datacenter.ts`, `finance.ts` and `answers.ts` on `site/data/datacenter/` and the public carbon file). It rounds each to the digits the page shows and writes `page_figures.json` and `.csv`.
    - The two years by window are the live set's and are kept as read.
    - The published mirror (`replicate.py`) is still a second code held to these figures, so the test still catches a difference between the two.
    - On today's committed files the page's code gives every recorded figure (0 moved). Only the note's sentence changed, to name the files' build day.
  - **538:** `warehouse/analysis/findings/cross_check_rows.py` (new) writes our figure and the gap of the three card-keyed rows (the ERCOT median, the 99.9th percentile, the queue's withdrawn share), and Finding 3's one sentence that quotes the reproduction, from the cards. The thesis's figures, the sources and the reasons are left as they are.
    - A trial on this machine's recompute: `check-cross-checks --files` failed 1 of 70 before, passed 70 of 70 after, and test 538 passed. The trial's files were put back.
  - **720:** `node site/scripts/siting-card.mjs` now runs after the datacenter files.
  - `warehouse/run_data_machine.sh`: the three steps (`dm_siting_card`, `dm_datacenter_figures`, `dm_cross_check_rows`) run before the replication group. The group's steps and its put-back paths include them, and the commit paths include `replication/datacenter/page_figures.*` and the note.
- **The queue card's move is a correction, not drift.** Session 3009's `read_table` fix (6 November) stopped losing the Queued Up rows that hold a `#` in a field: 22,348 requests of 2000 to 2020, not 21,758. The data machine's first refresh after this lands will write 3,591 GW into the card and the note's row (gap +90 GW to the thesis's 3,501).

## Commits

- `993649f1b`: the page figures' writer and script, the run's two steps, test 3206 moved to the group's new steps.
- `ec9611e91`: the cross-check rows' writer, the run's step, test 3779 (10 tests: the rows' writer on the repository, a moved card, the rounding, the order in the run).
- Tests run: those that read the run script (352, OK); 3779 and 3206 (OK); 1491 and 538 on the trial files in the main checkout (OK).

## Decisions made without you

- **The page's code, not a hand reading, gives the page figures.** A refresh can then never fail 1491 by moving a figure the page itself moved. It still fails when the mirror and the page disagree.
- **Our figure moves, the reason does not.** The queue row's reason ("requests are added and reclassified between editions") is left as written; see 3774's ruling item.
- **No test was skipped or loosened.** 3206 now names the group's new steps, the rule it holds.

## For Samuel's ruling

- None beyond session 3774's (the queue row's reason).
