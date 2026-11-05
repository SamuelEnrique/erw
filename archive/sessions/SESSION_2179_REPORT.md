# Session 2179 report: Canada's oil and gas supply (Statistics Canada)

24 October 2026, from 01:35 UTC, on lab-desktop (the data machine), a session of `queue/done/097-day-1-november-data-canada-offshore-inspections-supply.md`. Model spend USD 0. Pulls: www150.statcan.gc.ca, 5 requests of 15, at least 2.5 seconds apart (its robots file asks 2):
- its robots file, in a call of its own;
- the full-table zips of 25-10-0063-01 and 25-10-0055-01;
- 25-10-0055-01's page, which names its replacement;
- the replacement's zip, 25-10-0086-01.

The trial and the write ran offline from the saved zips. Also Supabase, for the locks and the archive.

## Read these first

- **One series table, `statcan_oil_gas_supply_monthly`:** 56,007 monthly figures in 463 series, by province and for Canada, from two tables:
  - crude oil and equivalent from table 25-10-0063-01 (January 2016 to July 2026);
  - natural gas from table 25-10-0086-01 (January 2016 to August 2026).

  The table covers production, imports, refinery inputs, exports (to the U.S. by pipeline and other modes), inventories, and gas deliveries to residential, commercial and industrial consumers with their customer counts. Volumes are in cubic metres. The gas table gives thousand cubic metres; they are written times 1,000.
- **Decision 70, `m3`,** joins the unit vocabulary in `docs/datastandard.md` and the validator (agreed with chain 098's agent, whose Decisions are 71 `ft` and 72 `acre-ft`).
- **The gas table the chain file names, 25-10-0055-01, is inactive.** StatCan archived it; it ends in December 2025, and its page says it is "Replaced by" 25-10-0086-01, so the table takes 25-10-0086-01. Where both give a figure for Canada, they agree:
  - 676 of 732 figures are within 1 percent;
  - the median difference is 0;
  - total imports differ most, by a median of 0.85 percent.
- **The crude table gives every figure in cubic metres and in barrels.** The cubic metres are kept. Each of the 25,533 barrel figures is checked against them in the connector and agrees to rounding at 6.2898 barrels a cubic metre; one that did not would stop the run.
- **Withheld and not taken, counted in the header:**
  - figures StatCan marks `x` (suppressed for confidentiality: 5,265 crude, 384 gas) or `..` (not available: 539 crude, 23,158 gas);
  - the gas table's 43,264 figures in gigajoules, since the standard has no unit for them;
  - its 10,752 in Canadian dollars, since a currency other than USD is a standing question.
- **Names repeated in the crude table:** its inventory items (fields and plants, transporters, refineries) appear under both opening and closing inventory with the same names. Each figure is keyed by StatCan's member ids, and such an item's variable carries its parent's name (`closing_inventory_refineries`). `x_parent` names the item each figure is part of. Canada and the Atlantic provinces are marked `x_area_total`.
- **The cross-check** (`runs/c097/s2179/cross.py`):
  - **Crude:** Canada's exports to the U.S. are 95 to 98 percent of EIA's imports from Canada (`eia_crude_imports_detail_monthly`, every grade, U.S. destination) in each year 2016 to 2025. For example, 1,459 against 1,487 million barrels in 2024. The ratio rose from 0.95 (2016 to 2018) to 0.98 (2022 on).
  - **Gas:** exports to the U.S. are 98 to 101 percent of EIA's pipeline imports from Canada (`eia_gas_trade_country_monthly`, N9102CN2) from 2016 to 2025. 2026 differs (1.13) because StatCan's months run past EIA's.
- **Registered:**
  - the sector rule (`oil;gas`);
  - both holds;
  - the release package's rows (1 table, 65 variables);
  - the license tables (licenses check: 0 problems; release check: 0 differences).

  No row is given twice. Statistics Canada's verdict (its Open Licence) goes in session 2181's round, as for session 2176's table. The test is `tests/test_session2179.py` (4 tests).

## Errors

- **The metadata patch did not apply to the branch,** because session 2178's rows sat beside the new ones. Both sides only added rows, and `runs/union_resolve.py` joined them; each new row appears once.
- **The first test run failed on the test's own fixture,** which wrote an item name with a comma unquoted. The fixture now writes through the csv module.

## Decisions made without you

- **25-10-0086-01 taken in place of 25-10-0055-01,** as StatCan's page directs. The old table is inactive and is not taken.
- **Cubic metres kept and barrels checked,** not both kept, so one quantity is never in the table twice.
- **Gigajoules not taken** rather than adding a second new unit; a later session can add `GJ` if the heat content is wanted.
- **The gas table's customer counts kept** as `count`, with `_customers` after the item's name.

## For Samuel's ruling

- None new. The gas table's Canadian dollars wait on the standing currency question.

## Files

- New: `warehouse/connectors/statcan_oil_gas.py`, `tests/test_session2179.py`, this report.
- Changed: `docs/datastandard.md` (Decision 70), `warehouse/validate/erw_validate.py`, `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c097/s2179/`.
