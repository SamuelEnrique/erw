# Session 354 report: the datacenter's four summer peaks, a node's band and capacity charges

20 October 2026, from about 13:58 UTC, unattended, on samueloldlaptop (the code machine), the fourth session of the chain of 20 October, night (`queue/done/010-night-20-october-code.md`). Branch `wip/354-datacenter` in the worktree `erw-296`, from session 353's branch (352 and 353 land first); lands on main as `task/354-datacenter`. Model spend USD 0; no warehouse data written; nothing pulled.

## Read these first

On `/cost-of-power`. **Every default figure is what it was** (check-values 1,377 of 1,377 on the economics pages; `check-datacenter-scenarios` 119 of 119 and `check-datacenter-face` 23 of 23).

- **ERCOT's four summer peaks**, read from the data machine's `ercot_4cp_intervals` (seven summers: 2018 to 2025 without 2021; **summer 2026 is not held**, for the data machine). Each interval is mapped to its hour of the grid's standard-time year and the flexible way's own weight read there (the rule's hours; for a flat load, the hours-off run beside it). Under the scenarios a paragraph says what share of its four-peak demand the flexible way avoided in the newest summer held and what that is worth at the Commission's newest approved postage stamp rate (2025, USD 68.547301 per kW a year); a fold lists every summer's four intervals with ERCOT's load in each (a key each) and the load on or off. "Four summer peaks" in the box (`cp=1`, default off) takes the saving off the flexible way's cost at this site in scenario A and B. At `LZ_NORTH`, off in the 100 dearest hours by the rule, the load was on in all four intervals of 2025: nothing saved. Off in 10 percent of hours it avoided three or four of four in 2018, 2019, 2020, 2022 and 2023.
- **A node's band**, ERCOT, under the cost table: the twelve months' mean of the 10th percentile, median and 90th percentile of every resource node's day-ahead basis to the hub average (`node_basis_summary`): USD -7.97, 0.31 and 7.39 per MWh, each month in a fold with its keys. A load settles at its load zone; the band is what a site behind a generator's meter would see. Added to no figure.
- **Capacity charges**, a row of the cost table: ERCOT's words (an energy-only market whose four peaks set the transmission charge); elsewhere "no public figure" with the reason. `iso_all_capacity_prices` (ISO-NE, NYISO) is an internal table, not in the live set; CAISO's resource adequacy is bilateral and SPP has no capacity market.
- `scripts/check-values.mjs` reads `series|ercot_4cp_intervals|...` as whole MW, as it reads other MW figures.
- Method note `datacenter_pays_algorithm.md`, a subsection "Session 354" under "Checks"; pack `datacenter.md` items 4, 5 and 6 of section 6 and question 5.

## What to review

In the internal view, after the landing:

1. https://erw-flame.vercel.app/cost-of-power?run=share&pct=10 : "ERCOT's four summer peaks" under the scenarios, and its fold.
2. The same with `&cp=1`: the flexible way's cost in scenario A and B.
3. https://erw-flame.vercel.app/cost-of-power : the band under the cost table, and the row "Capacity charges"; then `?grid=caiso`.
4. `docs/brand/review-354/`.

## Checks

| Check | Exit | Result |
|---|---|---|
| `tests.test_session354` and every test that reads a file this session changed (18 modules, 303 tests) | 1, then 0 | one pin (194: the hours-off run beside a flat load is kept whole for its weights): updated |
| The tests reading the two notes (162) and `check-values.mjs` (29 modules, 379) | 1, then 0 | the new section belongs under "Checks" with the anchor kept above "Cross-checks" (190, 196): moved |
| `tsc --noEmit`; `eslint` on the two files | 0 | |
| `finish_build.sh 354` (`39cfa73e`): build | 0 | no statement timeout |
| `check-values` on `/cost-of-power` | 1, then 0 | 28 of the 4CP loads written whole against check-values' two decimals; the rule for whole MW now names the table; rerun on the same build: **1,377 of 1,377** |
| `check-routes` | 0 | every page |
| `check-datacenter-scenarios`, `check-datacenter-face` | 0 | 119 of 119; 23 of 23 |
| `check-datacenter` | 1 | **22 failures, the same 22 on production** (run at 14:15 UTC): a check of session 138 no longer matched by the page. Not this session's |
| `check-table-downloads` | 1 | asked of a page with no downloads line: a mistake of the call |
| Impeccable `detect --json` | 0 | no finding |
| The probe at 390 (the default, and `?run=hours&cp=1`) | 0 | 390 within 390 |
| Shots, 1280 and 390 | 0 | `docs/brand/review-354/` |

## Landing

Below, once it is done: no landing from 14:00 to 16:15 UTC.

## Decisions made without you

- **The rate is the Commission's newest approved postage stamp rate**, the wholesale charge every page already shows, not a utility's retail factor (Oncor's and AEP's are per kW a month and stand in the delivery table); 2026's rate is filed, not approved, and not used.
- **The newest summer held sets the saving**, against the flexible way's hours in that summer (the twelve months shown hold no summer the table has yet).
- **The saving is not counted by default**: it is shown with its parts, and the box counts it.
- **Capacity outside ERCOT: words, not numbers.** The one table that holds auction results is internal.

## For Samuel's ruling

- Nothing that changes a number at the default.
- For the data machine: summer 2026's four intervals (and 2021's) for `ercot_4cp_intervals`; NYISO's ICAP spot rows in a public table of their own, if the page should show them.

## Files

- `site/app/cost-of-power/model.ts`, `page.tsx`; `site/scripts/check-values.mjs` (the whole-MW rule).
- `docs/methods/datacenter_pays_algorithm.md`, `docs/reviews/packs/datacenter.md`.
- `tests/test_session354.py` (new); `tests/test_session194.py` (pin).
- `docs/brand/review-354/` (shots).
