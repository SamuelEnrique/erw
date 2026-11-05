# Session 981 report: the other minerals of energy (the USGS's Mineral Commodity Summaries, the saved file)

23 October 2026, from 13:53 UTC, on lab-desktop (the data machine), a session of `queue/done/055-afternoon-23-october-data-outlook-hybrids-loans-dams.md`. Model spend USD 0. Pulls: none (the 2026 data release session 954 saved).

## Read these first

- **In place of the Federal Reserve's G.17** (held, `frb_utility_output_monthly`, session 889), as chain 054's session 964 rewrote this session: **ten more chapters added to `usgs_mcs_critical_minerals`:** aluminum, gallium, germanium, indium, manganese, the platinum-group metals, the heavy rare earths, silicon, tellurium and vanadium. The table now holds 1,600 rows, 653 series, for 16 chapters (from 692 rows for 6); written again, validated, archived (908 new rows), coverage refreshed.
- **New units and statistics, each mapped with a test:** kilograms written as `t` over 1,000; dollars per troy ounce as `USD/kg` (a troy ounce is 31.1034768 g exactly); capacity, shipment and supply as variables.
- **A unit corrected by the detail:** manganese's price is "dollars per metric ton unit" in USGS's own detail (a metric ton unit is 10 kg of content), though its unit column says "dollars per metric ton"; it is written per metric ton of manganese content, times 100 (2025: 450 USD/t), and a metric ton unit price with any other unit stops the run.
- **Four figures USGS prints in two sections with the same value** (the U.S. platinum and palladium mine production of 2024 and 2025, in the salient statistics and the world table) are kept once; a repeat with two values would stop the run.
- **The cross-checks:** aluminum's U.S. market spot price runs 15 to 23 percent above the World Bank's LME price through 2024 (the U.S. Midwest premium) and 51 percent in 2025; a different price, not compared further. The six chapters of session 954 are unchanged in their rows.

## Decisions made without you

- **The same table, not a new one:** one source, one file, one shape; no page reads it.
- **Session 954's test adjusted** to count one production row a chapter (`len(U.CHAPTERS) + 3`), since the chapters are now sixteen.

## Errors

- **The finish step reported the table already in the release package,** which it is (its rows were added in session 954); the release and license checks pass.

## For Samuel's ruling

- None new.

## Files

- New: `tests/test_session981.py` (3 tests), this report.
- Changed: `warehouse/connectors/usgs_mcs.py`, `tests/test_session954.py`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`.
- On the data machine only: `runs/c055/s981*`, `runs/s981*`.
