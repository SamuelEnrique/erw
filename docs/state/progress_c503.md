# Progress of chain 503 (the old laptop, sessions 8400 on, 19 November 2026)

The chain file: `queue/done/503-day-19-november-oldlaptop-rulings-evidence-whole-country-pages.md`. One line an entry group, a page or a view: its state and the session. States: `done` with the commit, `in work`, `waiting` with what for, `ruling` with the default taken, `needs the key` with the cost.

## The ground

- The chain file saved as pasted, committed alone and pushed: done (`a37adf1af`), session 8400.
- The resume file `queue/next/530-resume-chain-503.md`: done (`b447803e2`), session 8400. No other resume file of this machine was in `queue/next/` (510 is the data machine's, 520 the desktop's second window's; both left).
- Precheck passed; no freeze; session numbers 8400 to 8599 free on origin/main and every branch (checked 19 November).

## Part A: the evidence behind the rulings

- A1 and A2, the 88 entries, five groups looked up side by side, each entry's block merged into the ranked list in the list's order as it arrives:
  - taxes (entries 17, 32, 34, 35, 36, 38, 42, 43, 45, 50, 51, 52, 54, 66, 88, 97, 112, 124): done, all 18 in the list (keep 10, switch 6, no basis 2), session 8400
  - storage (6, 12, 13, 16, 18, 25, 46, 47, 67, 78, 83, 99, 106, 107, 109, 127): done, all 16 in the list (keep 2, switch 6, no basis 8), session 8400
  - prices (7, 21, 44, 53, 73, 77, 86, 87, 89, 98, 105, 111, 113, 117, 118, 122): done, all 16 in the list (keep 5, switch 5, no basis 6), session 8400
  - grid (2, 23, 24, 26, 49, 59, 61, 62, 69, 82, 94, 95, 110, 116, 119, 129): done, all 16 in the list (keep 5, switch 5, no basis 6), session 8400
  - trackers (3, 5, 8, 14, 20, 28, 29, 31, 37, 48, 55, 57, 58, 64, 74, 75, 80, 81, 92, 120, 121, 128): done, all 22 in the list (keep 11, switch 6, no basis 5), session 8400
  - All 88 are in the list (`27e616d3a`): keep 33, switch 28, still no basis 27. The whole list: switch 54, keep 48, no basis 27 (before: 26, 15, 88).
  - The wording faults the groups found in the entries themselves (23, 75, 77, 94, 107): done, corrected with a section at the list's foot (`27e616d3a`).
  - The terms of use of every host a page was read from (the rule asks for them as well as the robots file; the taxes group read none): done, session 8403, `docs/reviews/rulings-evidence-hosts-2026-11-19.md`. 42 hosts: one bars automated reading (`www.pge.com`; its one sentence withdrawn from entry 61, whose recommendation did not rest on it), one asks permission beyond fair use (entry 34 stands on the rule read elsewhere), three not readable, fourteen with no terms page. No recommendation moved.
- A3, the 12 figures that do not agree: done (`86e038f0c`), session 8402. Each traced; entries 48, 118, 119 and 127 corrected in their own lines; one request to the data machine (row 320 of `docs/state/data_requests_done_line.md`).
- A4, the six screenshot faults (rows 341, 345, 357, 362, 363, 366): done (`c0668e4e2`), session 8401. Four fixed on their branches with a test, pushed, back to `wanted` (341 `e313c0d4f`, 362 `e0d5fc2ac`, 366 `9b4d3f1c8`, 363 `3858e0432`); 357 is a data fault (request row 321; a second small one, row 322); 345 is the hold as it stands. Report: `archive/sessions/SESSION_8401_REPORT.md`.
- A5, the sheet for one sitting: done (`1bd09b3cb`), `docs/reviews/rulings-one-sitting-2026-11-19.md`, session 8400. Built by `runs/c503/build_sheet.py` from the list; run it again if a recommendation moves (the terms check).
- Reports: `archive/sessions/SESSION_8400_REPORT.md`, `SESSION_8402_REPORT.md`.

## Part B: the events pages for the whole country

- The section "The whole country" on the nine event pages and the line of regions on `/events`: done on `wip/8410-events-regions` (`bbefd6dd0`, pushed), session 8410. Tests: the pin 21 of 21 in both modes, the section 77 of 77. Landing requested: row 51 of `docs/state/landing_request_oldlaptop.md`. Browser reads: rows 377 to 382.
- The view waits for its files: `site/data/regions/events/<event>.json` was not on origin/main on 19 November (checked at the start and at the commit); until then the section reads "not built yet". When a file lands: draw the page with it (`site/scripts/events-pages.mjs`), read the section against the contract, and mend any difference of shape on the branch.

## Part C: `/demand` for the whole country

- `/demand` for the whole country, session 8420: done on `wip/8420-demand-regions` at `fc0d257f5` (pushed; made from `wip/8410-events-regions` and merged with it again, the one conflict in `site/next.config.ts` settled with part B's lines, which hold `/demand`'s). Landing requested, row 52; browser reads wanted, rows 383 to 391; one request to the data machine, row 327 (the contract's section 3). Report: `archive/sessions/SESSION_8420_REPORT.md` on the branch.
  - the view: a fourth view "The whole country" (`/demand?view=country`): any of the thirteen regions or any balancing authority, two side by side: demand by day, year by year, where the growth is, a region's weather view, a region beside its grid with the data machine's own sentence on the difference, a table of every region and authority with the six new regions named. The page's own charts are reused (moved unchanged into `site/components/demand/Growth.tsx`).
  - add, never change: the pin of 50 addresses, 101 of 101; the view's test 93 of 93; pytest 92 passed after the merge (887 over 65 files before it). Two older tests follow the new tab (`tests/test_session152.py`, `tests/test_session239.py`).
  - waiting for the files `site/data/regions/index.json`, `demand/<region>.json`, `demand/ba/<code>.json` (not on origin/main): until then each place reads "not built yet". First step when they land: the view's test on the real files (its last block), then browser rows 385 to 391. If `site/data/demand_growth.json` or `demand_weather.json` is rebuilt before landing, the pin says DATA MOVED: row 52's block gives the two commands to pin again from main.
  - for Samuel's ruling, defaults taken: Tennessee and the Carolinas drawn first; every day held drawn; the tab's name and its place as fourth; New England, New York and the Midwest drawn; generation-only authorities listed.

## Part D: `/supply` for the whole country

- `/supply` for the whole country, session 8430: done on `wip/8430-supply-regions` at `a2fbb2eaa` (pushed; made from `wip/8410-events-regions` and merged with it again after the config line). Landing requested, row 53; browser reads wanted, rows 393 to 400; one request to the data machine, row 323 (keys its builders write that the contract does not list). Report: `archive/sessions/SESSION_8430_REPORT.md` on the branch.
  - the views: net imports by month and by neighbour with each side's report and the gap (a gap of 10 percent or more marked and said in words on hover); who trades with whom by year, pairs of regions, pairs of balancing authorities and each authority's partners; the generation mix by month (the page showed no mix of its own, so each region has a chart of shares and a table of the year); two regions side by side; the six new regions by name.
  - add, never change: the pin of 103 addresses holds, 208 of 208; the section's test 109 of 109; Python 25 passed, 1 skipped after the merge.
  - waiting for the files `site/data/regions/trade/<region>.json`, `trade_matrix.json`, `mix/<region>.json` (not on origin/main): the views read on real files. First step when they land: merge origin/main into the branch, run the two node tests, draw the page with `supply-read-page.mjs` and read it.
  - the line of `site/next.config.ts` that names `data/regions` for `/events`, `/demand` and `/supply` (without it the files are not found on Vercel): done on `wip/8410-events-regions` (`f4ab254fa`), with a test; found by session 8430.
  - for Samuel's ruling, defaults taken: the 10 percent; California and the Carolinas first; the year 2025 first; the share of demand not drawn; New England, New York and the Midwest drawn.

## Part E

- The events pages' new views, session 8440, branch `wip/8440-events-regions-done` (`59a1f2e76`, pushed; made from `wip/8410-events-regions`):
  - the replication `replication/events/replicate_regions.py` with `site/scripts/events-regions-figures.mjs`: done, 203 of 203 on the fixture; on the site as it stands it says no file is there.
  - the reader's five cases written (`docs/reviews/events-regions-read-2026-11-19.md` on the branch); three gaps found before any file.
  - waiting for the files `site/data/regions/events/<event>.json` (not on origin/main): the read of the five cases on the page, the replication's count on real files, the Stata do-file's expected values, the cross-check against published figures. First step when a file lands: merge origin/main into the branch, run the two commands the method note gives, then read the five cases.
- `/supply`'s new views, session 8460, branch `wip/8460-supply-regions-done` (`89b73fcd2`, pushed; it holds `wip/8430-supply-regions` whole):
  - the replication `replication/supply/replicate_regions.py` with `site/scripts/supply-regions-figures.mjs`: done, 33,132 of 33,132 on the fixtures (27 files); on the site as it stands it says no file is there; `--same-flow` is written for the day the matrix and the trade files can be set side by side.
  - the reader's five cases written (`docs/reviews/supply-regions-read-2026-11-19.md` on the branch; the reader: an AI lab's energy lead siting a 300 MW campus); 15 gaps found before any file: five fixed on the branch (hovers only; `site/scripts/test-supply-regions-8460.mjs` 20 of 20, the pin 208 of 208 and the section's 109 of 109 hold), three data requests (rows 324 to 326), three for Samuel's ruling, the rest wait for the files or a browser.
  - the method note completed: nine rules the replication could not take from it are now written there.
  - waiting for the files `site/data/regions/trade/<region>.json`, `trade_matrix.json`, `mix/<region>.json` (not on origin/main): the five cases read on the page, the replication's count on real files with `--same-flow`, the Stata do-file's five headline figures, the cross-check.
  - landing: row 53 names this branch and head. Browser reads wanted: rows 403 to 406.
  - for Samuel's ruling, defaults taken: no sorting of the pairs (EIA's order); "not held yet" stays on the face where nothing is to come, with the reason on hover; "large" is judged before rounding.
- `/demand`'s new view, session 8450: in work, worktree `C:\Users\lossa\Documents\erw-8450`, branch `wip/8450-demand-regions-done` (from `wip/8420-demand-regions`). Brief: `runs/c503/brief_done_line.md`. Hand-back: `runs/c503/8450/handback.md`. Rows kept for it: browser reads 410 to 416, data requests 328 to 330.
- Landing row 51 names `wip/8440-events-regions-done` at `0008617ec` (it holds `wip/8410-events-regions` at `dffb83952` whole).
- The queue step after the events page (a dry run, 19 November): the only file for this machine in `queue/next/` is this chain's own resume file, so no new chain file waits and part E goes on. The resume file is taken by no one until the chain's last session removes it.
