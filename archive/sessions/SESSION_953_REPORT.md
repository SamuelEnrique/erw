# Session 953 report: the primary energy overview (EIA's Monthly Energy Review, Tables 1.1 to 1.3)

23 October 2026, from 12:25 UTC, on lab-desktop (the data machine), a session of `queue/done/054-day-23-october-data-federal-royalties-wind-costs-minerals.md`. Model spend USD 0. Pulls: 14 requests of 15 (api.eia.gov's robots file, asked in a call of its own: the host has none and answers "API key missing"; the `total-energy` route's list of series ids; four pages for each of three runs, two trials and the write).

## Read these first

- **One table written, validated, archived, in coverage (sectors power, gas, oil, coal, public), in the release package, both holds:** `eia_primary_energy_monthly`, 15,156 rows, 24 series, January 1973 to June 2026, in TBtu: U.S. primary energy production (total, fossil fuels, coal, dry gas, crude oil, NGPL, renewables, biomass), imports, exports, net imports, stock change and other, and consumption (total, fossil fuels, coal, natural gas, petroleum, renewables, biomass), with nuclear, hydro, geothermal, solar and wind, which EIA gives as one "Consumption/Production" series in both tables. No ERW table held them: `eia_sector_energy_consumption_monthly` holds Tables 2.3 and 2.4.
- **A new table of `eia_series.py`,** so the daily run takes it from tomorrow (about four API requests a day).
- **The cross-checks against SEDS (`eia_seds_state_energy`, U.S. totals, years with twelve months):** total consumption, coal, nuclear and renewables within 0.5 percent in 35 of 35 years (2024: 94,582 and 94,543 TBtu); natural gas within 1.1 percent in every year. Petroleum differs by up to 5 percent (2024: 35,590 and 37,535): MER's series excludes biofuels, SEDS's includes them. **The overview's identity:** production plus net imports plus stock change and other equals consumption within 0.01 TBtu in all 53 full years.

## Decisions made without you

- **EIA's "Not Available"** (solar's 132 months and wind's 120 before EIA counts them) **omitted, as "none" is:** the connector's check now names both marks.
- **One report text for the source row `eia:total-energy`,** which the two MER tables share: a run of either wrote its own report over the other's. Both now name Tables 1.1 to 1.3 and 2.3 and 2.4; `eia_sector_energy_consumption_monthly`'s header line takes the new text at its next daily run (its rows do not change).
- **The variable from each series id** (`variable_of`), since one table holds production, trade and consumption.

## For Samuel's ruling

- None new.

## Files

- New: `tests/test_session953.py` (4 tests), this report.
- Changed: `warehouse/connectors/eia_series.py`, `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c054/s953/`, `runs/license_reads/s953/`, `runs/s953*`.
