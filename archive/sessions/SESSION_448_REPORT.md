# Session 448 report: the economics pages against Lazard and the ATB

21 October 2026, about 07:16 to 07:40 UTC, unattended, on portable-laptop (the code role), in the main checkout on `wip/441-450-third`. The chain of 21 October, night, third machine (`queue/done/017-night-21-october-third.md`, session 448). Model spend USD 0; no warehouse data written; no `site/` change, so no build. Requests: 9 of the ceiling of 10, to Lazard and to NLR (formerly NREL) only.

## Read these first

- **The review is `docs/reviews/cross-checks-external.md`**: 34 comparisons of the battery, generator and datacenter pages with Lazard's *Levelized Cost of Energy+* (June 2025) and NLR's Annual Technology Baseline 2025. 8 of them are rows already in the Method notes, read again against the sources (they hold). The other **26 are new rows** (battery 10, generator 13, datacenter 3), written in the five columns `site/scripts/check-cross-checks.mjs` reads, ready to append to the notes. The same rows, with where each ERW figure lives, are in `docs/reviews/cross-checks-external.json`.
- **The datacenter page's cost of capital, 9.6 percent, labelled "a generator's WACC, Lazard"**, is a pre-tax weighting (0.6 x 8 + 0.4 x 12). The figure Lazard itself calls the WACC of that structure is 7.7 percent, after tax (page 9 note; page 12).
- **The battery's sourced sensitivity says the investment tax credit has "none published as a range"** (`site/lib/battery/finance.ts:548`). Lazard's page 43, the source of every other storage default, prints 30 to 40 percent.
- **No assumption default on the three pages carries a check-values key**: each is a constant in `site/lib/`. The rows name the file and line instead; the energy figures name their `ms|` keys.
- **Requests: 9 of 10**, all answered 200: Lazard's robots file, terms of use and the report (one copy, kept in `runs/`, not in git); the ATB's robots file, NLR's disclaimer, and the ATB's pages for utility-scale PV, land-based wind, fossil technologies, and financial cases. Every one is in the review's "The requests" and in `runs/chain_oct21_third/s448/requests.csv`. Neither publisher's terms forbid automated reading. Lazard's allow "a single copy ... for your own use" and forbid reproducing content for commercial use, so figures are quoted with their page and nothing is copied. NLR's grant use and copying with the notice and a credit.

## What to review

- The review: `https://github.com/SamuelEnrique/erw/blob/wip/441-450-third/docs/reviews/cross-checks-external.md`, its "What to look at first" (five items) and "Rows for the code machine to land".
- The rows file: `docs/reviews/cross-checks-external.json`.
- The test: `tests/test_session448.py`.

## Checks

Every gate redirected to a file under `runs/chain_oct21_third/s448/`, never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `tests.test_session448` | 0 | 7 tests OK. No em or en dash. The requests numbered 1 to 9, within 10, all to Lazard's or NLR's hosts, each publisher's robots file and terms read before its documents. Every row has a source link to Lazard, NLR or OpenEI with a page or row reference, a date read, and a place in the code. The rows are in the five columns of `check-cross-checks.mjs`: no empty cell, a link in every source, a reason over 30 characters, no stray pipe. The review's tables and the JSON hold the same rows. The pages' counts today (15, 21, 6) match their `data-checked-against` |
| The same test against a copy with an em dash, a request to another host and a changed line | 1 | 3 failures, as it should |
| The whole suite | not run | the parent runs it once for the chain; this session changed only new files under `docs/reviews/` and `tests/` |
| Build, snapshot, browser checks | none | no `site/` change |

## Decisions made without you

1. **Two of NLR's sources were not requested again.** The battery's ATB figures came from `site/data/sourced_ranges.json` (the ATB workbook, read by session 306 with sheet, row and column), and the NLR terms are record #65 of `docs/licenses.md`, read again here as request 5. The ATB battery page itself was not requested.
2. **Rows already in the notes were not rewritten.** Where the notes compare a figure already, the review says "already" and reads it again. New rows cover only what is missing: Lazard's page numbers for the generator's defaults, the 2- and 8-hour battery, capacity factors, cost of capital, coverage, credits, cycles, and the datacenter's rate and term.
3. **Lazard's page 9 (subsidized LCOE) and the dollar bars of page 30 (regional LCOE with firming) were not used.** The PDF's text gives two values a bar in an order that cannot be matched with certainty. The unambiguous tables of page 30 (capacity factors, ELCC, Net CONE) were used.
4. **The ATB's combustion turbine was not compared.** Its figures are in the page's interactive chart, not its text. The tenth request was kept rather than spent on the workbook, which is the data machine's source (`nlr:atb-2025-v1`).
5. **Capacity factors were computed as MWh per MW over 8,760 hours (8,784 in 2024)**, from figures the Method notes already state (2,580, 3,028, 2,075, 3,125 and 2,105 MWh per MW). No table was read again for them.
6. **Where the cause of a gap was not tested, the reason says so** (the fleets' capacity factors against Lazard's regional plants), rather than guessing at one.
7. **The rows file is JSON beside the review, not a change under `site/`**: `check-cross-checks.mjs` reads the notes as the site renders them, so landing means appending to the three notes and raising each page's `data-checked-against` (battery 15 to 25, generator 21 to 34, datacenter 6 to 9).

## For Samuel's ruling

- **The datacenter page's default cost of capital**: keep 9.6 percent with a label that says "pre-tax" (the weighting of Lazard's structure), or take Lazard's own after-tax WACC of 7.7 percent. Either moves the label; the second moves every figure the rate discounts.
- **The battery sensitivity's tax credit words**: replace "none published as a range" with Lazard's 30 to 40 percent (page 43) as the sourced range, or keep the credit out of the sourced mode with words that are true. The default of no credit is not in question.
- **The 8-hour battery's dollar year**: keep the cost report's 2024 dollars, or take the workbook's 2023-dollar Moderate case that the warehouse holds (USD 2,137.36 per kW, fixed O&M USD 85.49).
- **The generator's peaker capacity factor** (24.0 percent in ERCOT in 2024 under the page's rule, against Lazard's 10 to 15): leave the rule as it is, now with this row beside it, or add a start cost or minimum run.

## To finish

- The code machine appends the 26 rows to `docs/methods/battery_earns_algorithm.md`, `generator_earns_algorithm.md` and `datacenter_pays_algorithm.md` (under each "Cross-checks" table). It raises `data-checked-against` and the source line's words at `site/app/cost-of-power/battery/page.tsx:302` (15 to 25), `site/app/cost-of-power/seller/page.tsx:382` (21 to 34) and `site/app/cost-of-power/page.tsx:358` (6 to 9). Then it runs `node scripts/check-cross-checks.mjs` on the build and the tests that pin those counts. D1 and B14 wait for the rulings above before their words land.
- Land `docs/reviews/cross-checks-external.md`, `.json` and `tests/test_session448.py` with the branch (docs and a test only).

## Files

- `docs/reviews/cross-checks-external.md` (new).
- `docs/reviews/cross-checks-external.json` (new).
- `tests/test_session448.py` (new).
- This report.
- Not in git: `runs/chain_oct21_third/s448/requests.csv` (the request log), `raw/` (the copy of Lazard's report, the pages read, their text), `test.out`, `test_negative.out`.
