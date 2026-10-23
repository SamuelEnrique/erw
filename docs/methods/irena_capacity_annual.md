# Installed electricity capacity by country and technology, a year (IRENA's IRENASTAT)

Energy Research Warehouse (ERW), method note written in session 2094 (chain 068) for a table first written on 23 October 2026 (session 2085).

Tables: `irena_capacity_annual`

## Publisher and address

International Renewable Energy Agency (IRENA), IRENASTAT, the table "Electricity statistics by Country/area, Technology, Data Type, Grid connection and Year" (its 2026 H2 file), served by IRENASTAT's PxWeb service at `https://pxweb.irena.org/api/v1/en/IRENASTAT/Power%20Capacity%20and%20Generation/Country_ELECSTAT_2026_H2_PX.px` (`TABLE_URL`). The same address serves the table's metadata by GET and answers a JSON query by POST. The connector reads the metadata, then sends one query (`query`): every country and area, every technology, the data type "Electrical Installed Capacity (MW)", the grid connection "All", and the years asked (2015 to 2025 by default, `YEARS`, `--years`). The answer names its source as "IRENA (2026), Renewable Energy Statistics 2026, International Renewable Energy Agency (IRENA), Abu Dhabi." Source id `irena:irenastat_elecstat`. Connector: `warehouse/connectors/irena_capacity.py` (session 2085).

`www.irena.org` answered the ERW's reader with HTTP 403, an Azure WAF challenge, and is not asked; the connector asks only `pxweb.irena.org`.

## Vintage and revision

The file on the data machine was written by run `20261023T210948Z` (23 October 2026), offline, from the metadata and answer that session 2085's trial saved in `warehouse/raw/irena_capacity/capacity_query_2015_2025.json`. `retrieved_at` is 2026-10-23T21:07:46Z on all 20,662 rows, the time of the trial's query. IRENASTAT's folder listing, read by session 2085, gives the table's update as 2026-09-28T17:56:28; the answer's own `updated` field reads 9999-12-31T23:59:59Z, and `vintage` is empty on every row.

Each run builds the table whole and replaces the file (`ip.write_snapshot`). A run that is not offline asks for the metadata fresh and sends the query again, so IRENA's revisions of the years asked are taken. The address names the 2026 H2 file: a later issue under another name is not read until `TABLE_URL` is changed. No age check is made.

Because the metadata and the answer share one address, the raw store cannot tell them apart by address; `post` saves both, with the query, in one file under `warehouse/raw/irena_capacity/`, and an offline run reads both from it (`load_saved`).

## Shape and variables

Series, 20,662 rows: 224 countries and areas, 23 technologies, 1,962 series (a country and a technology), 2015 to 2025. Every country and area has at least one row in every year; rows a year run from 1,795 (2015) to 1,924 (2025).

- `entity` `irena:<code>`, IRENA's country code, three capital letters (ISO 3166 alpha-3 as IRENA writes it, with `XKX` for Kosovo); `node` the name as IRENA writes it, often shortened ("Amer Samoa", "United Arab Em", "USA").
- `variable` `capacity_<technology>`, IRENA's name in lower case with underscores; `x_technology_code` IRENA's code.
- `unit` MW on every row; `ts_utc` the year's first day, for the capacity at the year's end; `freq` P1Y; `geo` empty (IRENA's codes are alpha-3, the standard's geo is alpha-2); `market` and `vintage` empty.
- 90 rows are 0, as IRENA gives them; no value is negative.

| Code | Variable | Rows |
|---|---|---|
| 0 | `capacity_total_non_renewable` (IRENA's total) | 2,463 |
| 1 | `capacity_total_renewable` (IRENA's total) | 2,440 |
| 2 | `capacity_oil` | 1,893 |
| 3 | `capacity_renewable_hydropower` | 1,785 |
| 4 | `capacity_solar_photovoltaic` | 2,385 |
| 5 | `capacity_onshore_wind_energy` | 1,656 |
| 6 | `capacity_natural_gas` | 898 |
| 7 | `capacity_coal` | 609 |
| 8 | `capacity_renewable_waste` | 518 |
| 9 | `capacity_solar_thermal_energy` | 205 |
| 10 | `capacity_solid_biofuels` | 1,271 |
| 11 | `capacity_other_fossil_fuels` | 710 |
| 12 | `capacity_gas_biofuels` | 1,153 |
| 13 | `capacity_mechanical_storage_pumped_hydro` | 413 |
| 14 | `capacity_nuclear_energy` | 353 |
| 15 | `capacity_geothermal_energy` | 325 |
| 16 | `capacity_mixed_hydropower` | 226 |
| 17 | `capacity_marine_energy` | 178 |
| 18 | `capacity_other_non_renewable_energy` | 480 |
| 19 | `capacity_non_renewable_waste` | 251 |
| 20 | `capacity_liquid_biofuels` | 244 |
| 21 | `capacity_offshore_wind_energy` | 195 |
| 25 | `capacity_pure_hydropower` | 11 (Kosovo only) |

The metadata lists 26 technologies; codes 22 (Oil shale-sands), 23 (Peat and peat products) and 24 (Non-renewable energy) have no value in 2015 to 2025, so no row. The two totals are IRENA's own, not sums the ERW makes: a sum over the technologies must leave them out.

## Reading the source

- The metadata's variables must be the five of `VARS` (Country/area, Technology, Data Type, Grid connection, Year), in that order, or the run stops; so must the answer's first five columns (`parse`).
- Metadata with no capacity data type, no grid connection "All", or not every year asked stops the run (`query`).
- A country or technology code in the answer that is not in the metadata stops the run.
- A cell that is empty, "..", "-" or "." has no row and is counted: 43,402 cells here, all "..", as the header says (20,662 plus 43,402 is the 64,064 cells asked: 224 countries and areas, 26 technologies, 11 years). Any other value that is not a number stops the run. Nothing is filled.
- An answer with no value, or a country, technology and year given twice, stops the run.
- The metadata is asked through `ip.fetch_raw` (up to 4 tries, a pause of 1 second, timeout 60 seconds); the query is one POST with no retry, timeout 180 seconds (`post`); any answer but HTTP 200 is a failure.
- Ceiling: two requests a run, the metadata and the query. No row ceiling is set in the code.
- Any failure is recorded as a failure, and no file is written.
- The connector does not call `iso_prices.paused()`; IRENA is not in `warehouse/metadata/paused_sources.csv`.

## License

Held internal, with no verdict. `sources.csv` has `internal` for `irena:irenastat_elecstat`; the header: "License: not settled (IRENA's terms of use are on www.irena.org, which answered the ERW's reader with a challenge)." `license_verdicts.csv` has no row for IRENA, and `docs/licenses.md` lists the table as not settled. IRENA's terms of use live on `www.irena.org`, which refused the reader, so they have not been read.

Robots and pages, in `license_reads.csv` (session 2085): the robots read of `www.irena.org` disallows `/DocumentDownloads/` and two other paths; the read of the Renewable Capacity Statistics 2026 page answered HTTP 403, a challenge, and the host was not asked again; the robots read of `pxweb.irena.org` found no robots file (HTTP 404).

## Cross-checks (session 2094)

- The counts above were computed from the rows, read past the header lines; they equal the header's (20,662 rows, 224 countries, 23 technologies). No (entity, variable, ts_utc) appears twice.
- IRENA's totals against its parts, every country and year that has the total: `capacity_total_non_renewable` equals coal, natural gas, oil, nuclear, other fossil fuels, other non-renewable energy, non-renewable waste and pumped hydro within 0.01 MW on all 2,463 rows. `capacity_total_renewable` equals renewable hydropower, mixed and pure hydropower, solar photovoltaic and thermal, onshore and offshore wind, the solid, liquid and gas biofuels, renewable waste, geothermal and marine within 0.5 MW on all 2,440 rows; without mixed and pure hydropower, 237 rows differ. So IRENA counts pumped hydro in its non-renewable total and mixed hydropower in its renewable total.
- Session 2085 compared IRENA's `irena:USA` with `eia_state_capacity_annual` (EIA's net summer capacity, all sectors, summed over the 50 states and DC) in 2018, 2021, 2023 and 2024. Recomputed here for every year from 2015 to 2024: nuclear the same to the MW (98,391.2 MW in 2024; the one difference is 0.2 MW in 2016); wind (onshore and offshore) 1.000 to 1.001 of EIA's; natural gas 1.000 to 1.006; coal 1.006 to 1.012; hydropower (renewable and mixed) 1.047 to 1.054, against EIA's conventional hydroelectric. Solar (photovoltaic and thermal) is 1.43 to 1.72 of EIA's, highest in 2015 and lowest in 2024: IRENA's photovoltaic includes the small-scale systems EIA's state table does not hold. Session 2085's narrower ranges came from its four years.

## What it does not hold

- Electricity generation, which the same IRENASTAT table holds under its other data type; and the on-grid and off-grid splits.
- The years before 2015, which the table offers from 2000.
- IRENA's regional totals (its Region table) and the world's: a sum over the countries is the reader's.
- Geo codes: the entity carries IRENA's alpha-3 code and `geo` is empty.
- United States capacity by state: that is `eia_state_capacity_annual`.
