# Session 927 report: fuel stocks at power plants (EIA)

23 October 2026, from 10:02 UTC, on lab-desktop (the data machine), a session of `queue/done/052-day-23-october-data-world-oil-reactors-stocks.md`. Model spend USD 0. Pulls: EIA's API v2, 19 requests of 20 (the route's description, its sector and fuel facet lists, one page of 2026 to read the stocks' units, one count, then the connector's 14 pages).

## Read these first

- **No ERW table held them:** `eia_state_generation_monthly` takes the route's generation and `eia_power_plant_fuel_costs` its costs; its `stocks` column was not taken.
- **One table written, validated, archived, in coverage (sectors power, coal and oil, public), in the release package, both holds:** `eia_power_fuel_stocks_monthly`, 48,702 rows, 320 series, January 2008 to July 2026: the end-of-month stocks of coal (excluding waste coal), petroleum liquids and petroleum coke at power plants, by state, census region and the U.S., for the electric power sector and for all sectors. Coal in short tons (EIA's thousand short tons times 1,000), petroleum in kbbl.
- **The national figures:** the electric power sector held 147.0 million short tons of coal in January 2008, 187.2 in January 2016, 92.7 in January 2023 and 108.8 in July 2026; petroleum liquids fell from 44.6 to 19.7 million barrels.
- **The cross-check, states against the U.S. row:** they do not sum to it, and should not be read as if they did. EIA withholds many states' stocks (28 to 47 states have a coal figure in a month for the electric power sector), so the states summed are a median 90 percent of the U.S. row; a record without a figure has no row. The census regions sum to about the U.S. row (median 98 percent), but EIA lists both the Pacific region (PAC) and its two parts (PCC, PCN), so their sum overlaps. The Electric Power Monthly's national stocks are this U.S. row: the same series.
- **From 2008, two sectors, three fuels:** the route counts 165,314 records for four sectors and three fuels from 2001; the two sectors from 2008 (67,687 records) fit the ceiling in 14 pages.

## Decisions made without you

- **Sectors 98 (electric power) and 99 (all sectors), from January 2008,** to fit the ceiling; the utilities' and independent producers' own rows and 2001 to 2007 are one run each more.
- **The U.S. and the census regions kept beside the states,** as EIA gives them, the header saying that a sum takes one level and that withheld states keep the states from adding up.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_power_fuel_stocks.py`, `tests/test_session927.py` (3 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c052/s927/`, `runs/s927*`, `warehouse/raw/eia_power_fuel_stocks/`.
