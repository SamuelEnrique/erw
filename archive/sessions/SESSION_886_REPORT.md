# Session 886 report: electricity of the U.S., Canada and Mexico (EIA's International Energy Statistics)

23 October 2026, from 04:53 UTC, on lab-desktop (the data machine), a session of `queue/done/048-night-23-october-data-utility-files-products.md`. Model spend USD 0. Pulls: EIA's API v2, 5 requests of 20 (the route's description, two facet lists, one year of Canada's records to read the products and units, then one page for the whole table).

## Read these first

- **One table written, validated, archived, in coverage (sector power, public), in the release package, both holds:** `eia_international_electricity_annual`, 4,131 rows, 51 series, 1980 to 2024, from EIA's route `international`: for the U.S., Canada and Mexico, generation by source (total, nuclear, fossil fuels with coal, gas and oil, renewables with hydro, wind, solar, geothermal, biomass, tide and wave), capacity by source, consumption, imports, exports, net imports and distribution losses. EIA's billion kWh as MWh, its million kW as MW.
- **Generation in 2024:** the U.S. 4,393 TWh, Canada 611 TWh (648 in 2015), Mexico 387 TWh (311 in 2015); capacity 1,284 GW, 162 GW and 100 GW.
- **The cross-checks:**
  - imports less exports equal net imports in 45 of 45 years for each country, and nuclear, fossil fuels and renewables sum to the total within 2 percent in every year;
  - the U.S.'s generation here against `eia_state_generation_monthly`'s states summed with their small-scale solar: 4,092.9 TWh against 4,092.8 in 2015, 4,256.7 against 4,274.2 in 2023, 4,392.6 against 4,408.9 in 2024 (within 0.4 percent; EIA's two products are revised at different times);
  - Canada's exports against the U.S.'s imports, two countries' reports of one flow: 43.6 and 45.1 TWh in 2010, 68.3 and 75.8 in 2015, 49.3 and 38.9 in 2023, 35.6 and 33.3 in 2024. Canada's exports in 2024 were about half of 2015's.
- **Not taken:** EIA's copies of the same energy in quadrillion Btu, terajoules and tonnes of oil equivalent. A value EIA marks has no row; where EIA flags a value that rounds to zero, its flag is kept in `x_data_flag` (313 rows).

## Decisions made without you

- The U.S. included beside its two neighbors, so that the table compares the three on one basis.
- Session 887, the second of the two sessions the file gives this subject, takes Canada's own record of its electricity trade with the U.S. (the Canada Energy Regulator), since this table needed one request.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/eia_international_electricity.py`, `tests/test_session886.py` (4 tests), this report. Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`. On the data machine only: `runs/c048/`, `runs/s886*`.

## Corrected by session 891

The method notes' checks (session 891) found these against the code, the tables and EIA's files:

- `x_data_flag` is set on 315 rows: 313 "rounds to zero", one "SMR estimation" (Canada's fossil fuel capacity, 2024) and one flagged preliminary, EIA spelling it "perliminary" (Mexico's fossil fuel capacity, 2024).
