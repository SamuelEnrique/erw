# Progress of chain 720 (the portable laptop's first window: the ERW forecast page and the energy equities pages)

Energy Research Warehouse (ERW). The chain's file: `queue/done/720-night-26-november-portable-forecast-equities-pages.md`. One line a step, a view or a row, with its state and session. States: `done` with the commit, `waiting` with what for, `ruling` with the default taken, `needs the key` with the cost, `not built` with the free memory read.

## The start

| Step | State | Session |
|---|---|---|
| Stray work in the folder pushed as `wip/c720-stray-2026-11-26` (one screenshot, `bd74e2d02`); main put at origin/main | done | 10400 |
| Precheck; fetch; main at origin/main; free memory 681 MB of 15,974 MB | done | 10400 |
| The chain's file taken (`07b7be27d`) | done | 10400 |
| The resume file `queue/next/721-resume-chain-720.md` (`634b4f87a`) | done | 10400 |
| This file | done | 10400 |

## Part A: rows 44 to 51 of `docs/state/landing_request_portable.md`

All eight were checked against main first, as the chain asks. Each head is an ancestor of origin/main: the desktop's second window (session 9203) merged the ten fix branches of chain 620 as `wip/w2-c620-fixes`, built that stack and saw each fix in the build, and chain 601's desk landed it at `0fc82399d` (task/c601-desk10, 21 November 2026 00:10 UTC; row 4 of `docs/state/landing_request_window2.md`). Each fix's own test passes on main's tree today (the ten test files, 56 passed, `runs/c720/rows_tests_on_main.out`). No build was made for part A: nothing was left to see. The rows' State cells in `docs/state/landing_request_portable.md` now say landed. Rows 52 and 53 stood in the same state for the same cause and are marked with them.

| Row | Branch | State | Session |
|---|---|---|---|
| 44 | `wip/9601-back-button-lists` | done: already landed at `0fc82399d`, marked so | 10400 |
| 45 | `wip/9601-findings-phone` | done: already landed at `0fc82399d`, marked so | 10400 |
| 46 | `wip/9601-resource-set-legend` | done: already landed at `0fc82399d`, marked so | 10400 |
| 47 | `wip/9601-authority-facts-words` | done: already landed at `0fc82399d`, marked so | 10400 |
| 48 | `wip/9601-tour-headings` | done: already landed at `0fc82399d`, marked so | 10400 |
| 49 | `wip/9601-policy-held-page` | done: already landed at `0fc82399d`, marked so | 10400 |
| 50 | `wip/9601-price-map-window` | done: already landed at `0fc82399d`, marked so | 10400 |
| 51 | `wip/9601-line-ends-unnamed` | done: already landed at `0fc82399d`, marked so | 10400 |
| 52, 53 | `wip/9601-method-pages-phone`, `wip/9602-faults-page-phone` | done: the same landing, marked so (not in the chain's list; the same fact) | 10400 |

## Part B: the ground for both pages

| Step | State | Session |
|---|---|---|
| `docs/reviews/pages-ground-2026-11-26.md`: what both pages reuse (the frame, the chart with a band, the place picker, A and B, the board's rows and held rows, the workbench's pure parts, the downloads), what they do not, what the contracts leave open, and five cases a page | done | 10400 |

## Part C: the ERW forecast, `/forecast`

Branch `wip/c720-forecast`, cut from origin/main. The contract `docs/state/page_files_predict.md` was on main at the start. The real files (`site/data/predict/`) are on no branch yet (read at about 11:35 UTC on 26 November): the page is built and tested against the contract's example files and a fixture of the contract's shape, and reads the real files with no change of code when they land.

| Step | State | Session |
|---|---|---|
| 1. Tomorrow: the ERW forecast by hour with its band, the operator's forecast beside it, three figures, the hours as a table; a tab for price; a held price a blank with "license needed" | done on the branch (`site/app/forecast/view.tsx`, `site/lib/predict.ts`) | 10401 |
| 2. How it has done: any past day beside what happened with the day's errors; the last 30 days and the backtest; the score by month, by hour of day, the other cuts; every place at once, in the index's order | done on the branch | 10401 |
| 3. Two places side by side; the hour made and the method on the place's hover; "ERW forecast" on every chart | done on the branch | 10401 |
| 4. Downloads: `/forecast/rows` and `/forecast/scores`, each with a Python and a Stata reader; every figure with its key into its file and its source on hover | done on the branch | 10401 |
| 5a. Tests that pin what a reader sees: `site/scripts/test-forecast.mjs` (105 checks: no files, the contract's examples, a fixture) and `tests/test_session10401_forecast.py` (10 passed); the 90 test files that name a changed module: 1,202 passed, 2 failed (test 8430, which fails on main on this laptop; test 8902's flag rule, mended: the tour stop waits in a list of its own); lint clean | done | 10401 |
| 5b. The page seen in a build at 1280 and 390 px | done: three builds (exit 0, 70 to 118 s, 2.6 to 3.7 GB free before each). With no files (as main is): the title and one blank; a visitor gets the in-review page. With the server pointed at the test's fixture (layout only, made-up values, this machine only): one place, two places, demand and price, no sideways scroll at 390 px, the chart under a mouse and a finger, the keyboard from top to bottom (46 stops, each with a ring), the back button after two choices, the six downloads. What the look changed: two places' scores became columns of one table (they were two cramped tables), the band is named in the chart's legend (its name stood on the line's), the metric follows the series, the choices stay in view | 10401 |
| 5c. On window B's real files: the five cases, every figure beside the files, the keyboard, the back button | done before their landing, on a copy of the files from `origin/wip/c730-predict-v2` (33 files, built 11:49 UTC): `site/scripts/check-forecast-files.mjs` draws 120 pages (29 places, both series, both metrics, four pairs) and sets 60,474 figures beside the files, 0 differing, and 134 figures of a day's error computed again, 0 differing; the five cases taken start to finish in a build at 1280 px, two places side by side at 1280 and 390 px, the keyboard (67 stops, each with a ring) and the back button. What the real files changed in the page is in session 10401's report. To do once more on production after the files land | 10401 |
| Landing requested | done: row 54 of `docs/state/landing_request_portable.md`; the head moved to `dc8f59d7f` at 12:50 UTC | 10401 |
| A tour stop, held | done on the branch: `WAITING_STOPS` in `site/lib/tour.ts` (a new stop is `landed` exactly when its page exists, so a page that lands before its files cannot be held by that flag) | 10401 |

## Part D: energy equities

Branch `wip/c720-equities`, stacked on `wip/c720-forecast` (it shares the download readers). The contract `docs/state/page_files_equities.md` and its six example files (every value null) were on main at the start; no real file is on main or on any branch yet (read 12:15 UTC).

| Step | State | Session |
|---|---|---|
| 1. The group on `/board`: the contract's rows turned into the board's own rows, after the board's own groups (`withEquities`, `site/lib/equities.ts`); its table has the latest value, its date, the five moves and the trend; a held row is the board's own blank with its hover; a row opens its series on `/equities`. With the example files the group is one blank row | done on the branch | 10402 |
| 2. `/equities`: a segment, an index or a company as a line over any window with an energy price laid over on its own axis; a segment's two weightings named plainly; a company's filed figures (the newest period side by side, every period behind a fold, each period a link to its filing); two side by side; every company in one table that filters and sorts; segments and indices | done on the branch | 10402 |
| 3a. Downloads (`/equities/rows`, `/equities/filed`, `/equities/list`, each with Python and Stata readers) and tests: `site/scripts/test-equities.mjs` 93 of 93, `tests/test_session10402_equities.py` 10 passed; the 111 test files that name the board, the tour, the routes or the config: 5 older tests of the board's source failed at first (each pins a line of the board's code) and pass now with those lines kept as they were; test 8430 fails as on main | done | 10402 |
| 3b. The build at 1280 and 390 px | done: five builds (exit 0). As main stands: the board's own 25 groups as they were and the new one last with one blank row; `/equities` its title and one blank. With the test's fixture (made-up values, this machine only): the group's rows, filter, held row and the way to `/equities` by a click and by the keyboard; `/equities` with a segment, two companies and an oil price, an index and a monthly price, the table filtered and sorted; no sideways scroll at 390 px; 49 stops of the keyboard; the back button; nine downloads | 10402 |
| 3c. On window A's real files, every figure beside the files | done before their landing, on a copy of the files from `origin/wip/c701-desk-1` (built 12:14 UTC). **They hold no company, index or segment line yet** (SEC EDGAR refuses the ERW's contact string; no price source a license allows): 15 segments, 30 board rows not held, 12 energy prices of which 8 shown. The page was reworked for that state (it said "not built yet", which was wrong): each part says why it is held, and a new section draws the energy prices. `site/scripts/check-equities-files.mjs`: 25 pages, 1,092 figures, 0 differing. Seen in a build with those files at 1280 and 390 px. The five cases of an equity reader cannot be taken until a company's series exists | 10402 |
| Data request 574 (what the built files carry beyond the contract's text: `rule_why`, the list's `held`, a `paused` status, a quarterly step) | requested of window A | 10402 |
| Data requests 571 and 572 (the list's last close, moves and market value; the board rows' other cells) | requested of window A, `docs/state/data_requests_done_line.md` | 10401 |
| Data request 573 (the board's older row named "Energy equities", which will stand beside the new group) | requested of window A | 10402 |
| Landing requested | done: row 55 of `docs/state/landing_request_portable.md`; the head moved to `011838634` at 13:08 UTC (it holds row 54's head `dc8f59d7f`) | 10402 |
| A tour stop, held | done on the branch (`WAITING_STOPS`) | 10402 |

## Part E

| Step | State | Session |
|---|---|---|
| The phone's width: each new view at 390 px by a finger | done once for both pages on a build (the forecast on window B's real files, the equities pages on the test's fixture): the chart, the folds, the tabs, the sort heads, a company's name and the filter's box answer a finger; no sideways scroll. Gaps found and mended: the price tables 889 to 1,794 px wide (a long reason printed in every cell); the fold of the hours and the small links of the equities tables under 24 px. Left: the shared charts' Chart and Table switch, 22 px (a line for Samuel's ruling). To take once more through the five cases on production after the landings | 10401, 10402 |
| Parts C and D seen on production after each landing of new files | waiting: rows 54 and 55 are requested, not landed (read 12:57 UTC) | |
| One problem set a page, held out of the dated edition | waiting: a problem set reads its figures from page files on main (`site/lib/problemsets/common.ts` throws on a figure that is not there), and neither page's real files are on main | |
| `docs/reviews/browser-read-2026-11-26.md`: rows that name this window's pages | read at 12:25 UTC: none yet (the review's part C waits for the landings) | 10402 |

## The standing step (rows of `docs/state/landing_request_portable_w2.md`)

| Row | State | Session |
|---|---|---|
| 1, `wip/c750-grid-reliability` (`038ecbfcd`) | done: seen in a build at 390 and 1280 px (390 of 390 px; the table scrolls in its frame), marked requested | 10401 |
| 2, the two commits of `wip/w2-c620-fixes` not on main (`923d4cb4f`) | done: seen in a build (the trend names its fuel, figures unchanged; the COVID page 390 of 390 px with every table shown), marked requested | 10401 |
| 4, `wip/c750-grid-last-week` (`aad80aaba`) | done: seen in a build at 1280 and 390 px on four grids' pages ("Same day last week" holds a figure in each of the day's 24 rows), marked requested | 10402 |
| 3, `wip/c750-conditions` (`569d15885`) | done: seen in a build at 1280 and 390 px (44 notices under a heading that counts 44; 79 rows at 390 px with the page 390 px wide; each operator's line says its clock once), marked requested | 10402 |
