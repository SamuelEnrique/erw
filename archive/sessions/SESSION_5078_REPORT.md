# Session 5078 report: chain 243, a second read of the five's variants; battery row 11 fixed

Energy Research Warehouse (ERW). Chain 243, portable laptop window P1, 13 November 2026, about 20:15 to 20:24 UTC (corrected by session 5079: this line said 20:20 to 20:35). Opus 5.5. Model spend USD 0. Branch `wip/5072-read` (the fix made on `wip/5072-fixes` and moved onto it).

- **Read** on production in the internal view at 1280 and 390 (1.4 GB free before): ERCOT's 2-hour battery on the day-ahead schedule, CAISO's 8-hour on the day-ahead schedule, ERCOT's wind on the generator page, the datacenter page's all-grids view, CAISO's grid page, and the finding card `batteries_lunch_grids`. Every page at both widths: no sideways scroll, no exception, no broken word.
- **Battery row 11, new and fixed:** CAISO's 8-hour day-ahead summary read "... and covered its debt -0.14 times.": USD 85.65 per kW earned against a fixed O&M of 92 leaves nothing for the debt. A coverage below zero now reads "did not earn its fixed O&M, so nothing was left for its debt (coverage -0.14 times)." in both forms of the sentence (`site/app/cost-of-power/battery/Scenarios.tsx`); the keyed figure is kept, so check-values reads it as before; at every default the sentence is unchanged (coverage 2.63 at ERCOT's). `check-battery-scenarios.mjs` asserts the old words only for a positive coverage at ERCOT's defaults, and `check-battery-production.mjs` only the sentence's opening: both still hold.
- **Not faults:** "Real-time,load-weighted" in the all-grids view's text is an SVG legend label wrapped on two lines (the code reads "Real-time, load-weighted"); the all-grids table's month, 2026-09, is the newest complete for every ISO, as it says. CAISO's 8-hour price years default (86.41 beside 85.65) is row 10's cause.
- **Tests:** `tests/test_session5078.py` (new, 4 tests: both sentence forms, the order after "no debt", the case's arithmetic, the faults row); the 21 test files that read `Scenarios.tsx` or the sentence: 324 tests, OK, 5 skipped. The page not built here (memory); the landing's build and check-values are its proof on a build.

## Decisions made without you

- The words for a negative coverage. Default, as written: "did not earn its fixed O&M, so nothing was left for its debt (coverage -0.14 times)."

## For Samuel's ruling

- Nothing new beyond the words above.
