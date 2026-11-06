# Session 929 report: every country's oil, a month (EIA's International Energy Statistics)

23 October 2026, from 10:08 UTC, on lab-desktop (the data machine), a session of `queue/done/052-day-23-october-data-world-oil-reactors-stocks.md`, the first of its two sessions of a source of its own choosing. Model spend USD 0. Pulls: none (the bulk file session 909 saved).

## Read these first

- **Why this source:** monthly crude production by country (Saudi Arabia's, Russia's, the OPEC members') is the figure the oil market trades on each month, and the ERW held it only for the U.S. EIA's bulk file, already on the machine, holds it for every country from 1973, so it costs no request.
- **One table written, validated, archived, in coverage (sector oil, public), in the release package, both holds:** `eia_world_oil_monthly`, 541,215 rows, 1,555 series, January 1973 to July 2026, 258 areas (216 countries, 5 former, 1 part, 36 regions): each area's monthly production of crude oil, NGPL, other liquids, refinery gain and their totals, refined products' consumption (kbbl/d), and stocks (kbbl). A third table of `eia_intl_bulk.py` (`--table eia_world_oil_monthly`); the two annual tables, run again from the new code, are the same row for row.
- **The cross-checks:**
  - **The months against the annual table** (`eia_world_oil_gas_annual`, crude production): of 5,199 area-years with twelve months, 4,944 average within 1 percent of the annual figure and 5,018 within 3 percent. In 2024: the U.S. 13,267 kbbl/d in both, Saudi Arabia 9,209 in both, Russia 9,893 and 9,892, the world 81,958 in both.
  - **The U.S. against `eia_crude_production_state_monthly`** (field production per day): 296 of 306 months within 1 percent and 305 within 2 percent; June 2026, 13,792 and 13,844.
- **Not taken:** the OECD's and seven importers' monthly gross imports by source country (their series put the importer in the product and the exporter in the area), and the tonne copy of crude production (1994 to 1999).

## Decisions made without you

- **This source over another,** since it adds the most used monthly oil figures at no request and with a check against two ERW tables.
- **The imports by source left out** for a table of their own, if wanted: as series they would need an importer and an exporter in one entity.

## For Samuel's ruling

- None new.

## Errors

- The write's metadata patch met session 927's rows; `runs/union_resolve.py` joined both sides, but `sources.csv` then held two lines for `eia:international_bulk` (one naming the oil and gas table, one this table). Joined by hand into one line naming all three tables, and the license record built again (`licenses.py tables`, `write`, `check`: 0 problems).

## Files

- New: `tests/test_session929.py` (2 tests), this report.
- Changed: `warehouse/connectors/eia_intl_bulk.py` (the third table), `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c052/s929/`, `runs/s929*`.
