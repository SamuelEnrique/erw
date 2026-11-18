# Sessions 7801 to 7803 report: chain 401 parts C and D (in progress)

Energy Research Warehouse (ERW). Chain 401 of 17 November 2026, lab-desktop, data machine. Model spend USD 0: no script called a model. Session numbers 7801 to 7803 checked free on origin/main and every branch (7900 on is the old laptop's chain 402).

## Part C: the warehouse from seven grids to all thirteen regions

### Tables 1 to 3, EIA-930 (session 7801), on `wip/c401-eia930`

- `eia930_region_hourly` 3,064,131 rows (the 13 regions), `eia930_ba_demand_hourly` 7,829,972 and `eia930_ba_supply_hourly` 9,137,257 (every balancing authority), `eia930_region_pair_hourly` 1,820,134 (region pairs, derived), `eia930_ba_interchange_hourly_2018` to `_2026` 21,980,045 rows together (each side's report its own row). Hourly from 2018-07-01 to 2026-11-16/18, from the 34 six-month files (`warehouse/connectors/eia930_region_hourly.py`, `eia930_ba_interchange_hourly.py`), each passing the validator, archived (13 tables, 43,631,539 rows), internal tier: held out of the live catalogue and of release v1, not on Redivis.
- The hour convention checked against EIA's API: ERCOT's and CAISO's demand equal `eia930_all_demand` to 0.01 MW at the same hour (about 1,410 MW either side).
- Test `tests/test_session7801_eia930_regions.py` on real rows of 1 July 2025: CAL's five balancing authorities sum to the table's 42,684 MW; FLA's and SE's six reports give -413 and -424 (gap 11).
- Method: `docs/methods/eia930_region_hourly.md`.

### Tables 4 and 5 (session 7802), on `wip/c401-county`

- `census_county_population` 28,293 rows, 3,152 counties: the 2020 census count (the intercensal files' YEAR 12) and the estimates of 1 July 2018 and 2019 (intercensal) and 2020 to 2025 (vintage 2025), from www2.census.gov.
- `eia_county_region` 3,117 counties of the lower 48: 1,027 shared, 24 with no balancing authority (Connecticut's nine planning regions among them), one territory name unmatched (Virginia's Bedford City, folded into Bedford County in 2013). `county` joins the entity types (Decision 79).
- Method: `docs/methods/county_population_and_regions.md`.

### Tables 6 and 7 (session 7803), on `wip/c401-county`

- `noaa_region_stations` (271 counties: each region's most populous counties to 80 percent of its population, at most 25), 216 stations, each the nearest to the county's 2020 center of population that holds 95 percent of each year's hours in ISD-Lite and whose LCD lines up with it; `noaa_region_station_hourly_2018` to `_2026` (one table a UTC year); `region_weather_hourly` 879,553 region-hours.
- Each station's local standard time offset was read from the data (the offset under which LCD and ISD-Lite agree over July 2025): 103 stations at -5 hours, 73 at -6, 14 at -7, 26 at -8; the agreement is at least 0.99 at 215 of the 216 and 0.977 at the last. The farthest station is 79.1 km from its county's center. A first build kept nine stations whose LCD lined up under no offset; their regions then had no hours from August 2025 (825,005 region-hours). The rule now passes such a station over for the next nearest: 879,553, every region holding 80 to 99 percent of its hours (the Carolinas 80, the Southwest 99).
- Method: `docs/methods/region_weather.md`.

### Table 8 (session 7803): SPP pulling (hub_history.py's backfill, 1 July 2018 to 5 July 2023)

## Part D: the filed large-load tariffs

- The count: 80 groups, 6 grid operators, 74 utility groups (11 of them generation and transmission cooperatives); 19 groups had a registry file, 55 none.
- El Paso Electric: Schedule No. 33A read whole; held internal (the company's terms and the PUCT's ask permission).
- PPL: Rate Schedule LP-6 read whole; public, 4 rows; the table 64 rows.

## Decisions made without you

- **Five EIA-930 tables (and nine yearly interchange tables) where the chain named three.** One table of every balancing authority and region hourly since July 2018 is about 20 million rows and 5 GB; this machine's validator read the 1.2 GB table at 3.2 GB of memory, so a 5 GB table cannot pass. The balancing authority tables are split by measurement, as `eia930_all_demand`, `_generation` and `_interchange` are (decision 28 holds); the interchange table, one variable, is one table a UTC year, as `eia930_subba_demand_hourly_<year>` (session 612). Rows carry the file's short tag (`x_file`) and the header every file's URL and dates, not the URL on each of twenty million rows.
- **The region rows are sums of the balancing authorities** (the six-month files hold no region rows), written only when every balancing authority of the region has the hour.
- **The primary balancing authority of a shared county:** the one whose serving utilities have the most retail customers in the state (bundled and delivery customers of EIA-861); the other rule that was open, the most utilities in the county, is kept in `x_ba_by_count`.
- **Table 8:** CAISO's own archive (OASIS) keeps about 39 months, so it holds nothing before July 2023 (the reason `iso_hub_prices_history` starts on 6 July 2023); only SPP is pulled.

## For Samuel's ruling

- **Table 8, publishers not pulled:** NYISO and ISO-NE (license needed under the hold of 21 October), MISO (paused since 4 October), PJM (the chain), CAISO (its archive holds nothing so old). Default: not pulled.
- **The thirteen EIA-930 tables in release v1:** held out as the other late tables are (and about 3.6 GB against a Redivis account whose free 10 GB is noted as full). Default: held.
- **PPL's book stands public without the Commission's copy**, as PG&E's does (the question of session 2921). Default: public.
