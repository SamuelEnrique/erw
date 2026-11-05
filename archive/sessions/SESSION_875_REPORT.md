# Session 875 report: coal receipts at power plants, mine to plant

23 October 2026, from 03:37 UTC, on lab-desktop (the data machine), a session of `queue/done/047-night-23-october-data-utilities-plants.md` (one of its two "more sources"). Model spend USD 0.

## Read these first

- **`eia_coal_receipts_annual` is written: 270,547 rows, 2008 to 2025**: each mine's coal delivered to each power plant by supplier, rank, contract type and transport mode, with quantity (short tons), average delivered price (USD/short_ton), heat content (Btu/lb, Decision 52), sulfur and ash (pct); 1,129 mines and 471 plants (route `coal/shipments/receipts`, Form EIA-923). Validated, archived, in coverage (sector coal;power, public), in the release package, both holds.
- **Why this source:** session 870 found the by-mine-by-plant route without a key; the receipts route carries contract type and transport mode, and with them only 104 keys (a mine, plant, supplier, rank, contract and transport mode in one year) are given twice with two values; their 208 records are left out whole (0.4 percent of EIA's 57,066; the header counts the keys). Session 877's note found the count of records. It links the mines of `eia_coal_mine_production_annual` to the plants of `eia860_plants_annual` and `eia923_plant_fuel_annual`.
- **EIA's totals are in it:** rank `TOT` is EIA's sum of the ranks beside it (419.4 million short tons in 2020 = 130.6 bituminous + 241.4 subbituminous + 43.9 lignite + 3.5 waste coal); the header says to leave it out of a sum over ranks.
- **The cross-check:** the TOT receipts' quantity-weighted price against EIA's electric power sector delivered price (`eia_coal_delivered_price_annual`, U.S.): within 1.1 percent every year from 2016 to 2025 (2020: 36.52 against 36.13 USD/short_ton); 2.2 to 13 percent below in 2008 to 2015, when more prices were withheld.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| api.eia.gov | 12 of 20 | the trial's 12 pages, which the write reused (the route's count was taken by session 870) |

## Decisions made without you

- EIA's rank totals kept beside the ranks, as `eia_coal_production_annual` keeps them, named in the header.
- This source taken now, as it was ready; chain 048 need not add it.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_coal_receipts.py`, `tests/test_session875.py` (3 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c047/s875/`, `runs/s875_*`.
