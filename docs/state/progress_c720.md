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
| 5b. The page seen in a build at 1280 and 390 px, on the fixture (layout only) | in hand: the first build of the session is running | 10401 |
| 5c. On window B's real files: the five cases, every figure beside the files, the keyboard, the back button | waiting: `site/data/predict/` is not on main | |
| Landing requested | after 5b | |
| A tour stop, held | done on the branch: `WAITING_STOPS` in `site/lib/tour.ts` (a new stop is `landed` exactly when its page exists, so a page that lands before its files cannot be held by that flag) | 10401 |

## Part D: energy equities

| Step | State | Session |
|---|---|---|

## Part E

| Step | State | Session |
|---|---|---|

## The standing step (rows of `docs/state/landing_request_portable_w2.md`)

| Row | State | Session |
|---|---|---|
