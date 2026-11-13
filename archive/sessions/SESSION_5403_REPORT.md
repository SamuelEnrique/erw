# Session 5403 report: chain 255, the Grid's five other grids read; Grid row 4 fixed (MISO's hours named "EST")

Energy Research Warehouse (ERW). Chain 255, portable laptop window P1, 13 November 2026, about 20:45 to 20:53 UTC. Opus 5.5. Model spend USD 0. Branch `wip/5072-read` (the fix made on `wip/5072-fixes2` and moved onto it).

- **Read** on production in the internal view at 1280 and 390 (1.4 GB free): the Grid's PJM, MISO, NYISO, ISO-NE and SPP pages. No sideways scroll, no exception, no broken word; the license holds named (12 to 14 a page).
- **Grid row 4, new and fixed:** MISO's page named its hours "6:00 PM GMT-5" (the Mix sentence, the hour cards, the conditions) where every other grid's names its zone. MISO keeps Eastern Standard Time all year, the zone `Etc/GMT+5`, which the browser names "GMT-5". `zoneWords` in `site/lib/gridtool.ts` (pure, as the file asks) names it "EST" in every season and leaves every other zone as the browser names it; `components/grid/NowView.tsx`, `YourGrid.tsx` and `Conditions.tsx` use it. No check key moves (the words are outside the keyed figures).
- **Tests:** `tests/test_session5403.py` (new, 3 tests: the three formatters use it; Node runs it on the browser's own output, November and July, MISO and two other zones; the faults row): OK. The 13 test files that read `gridtool.ts` or the three components: 216 tests, 1 failure, 21 skipped. The failure, `tests/test_session137.py` `test_the_panels_own_tests_pass` (`site/scripts/test-ask-panel.mjs`: "the board's rows for ERCOT ... never another grid's"), fails the same on main (`82e74d3a5`) and on this stack without the change: not this fix's; the Ask panel's script is window P3's.

## Decisions made without you

- "EST" for MISO in summer too: its market keeps Eastern Standard Time all year, and "EDT" would be wrong.

## For window P3

- `tests/test_session137.py` `test_the_panels_own_tests_pass` fails on main at `82e74d3a5` (`site/scripts/test-ask-panel.mjs`, line 45: a board row of another grid among ERCOT's).

## For Samuel's ruling

- Nothing new.
