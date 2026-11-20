# Sessions 7801 to 7803 report: chain 401 parts C and D

Energy Research Warehouse (ERW). Chain 401 of 17 November 2026, lab-desktop, data machine. Model spend USD 0: no script called a model. Session numbers 7801 to 7803 checked free on origin/main and every branch (7900 on is the old laptop's chain 402).

## Part C: the warehouse from seven grids to all thirteen regions

### Tables 1 to 3, EIA-930 (session 7801), on `wip/c401-eia930`

- `eia930_region_hourly` 3,064,131 rows (the 13 regions), `eia930_ba_demand_hourly` 7,829,972 and `eia930_ba_supply_hourly` 9,137,257 (every balancing authority), `eia930_region_pair_hourly` 1,820,134 (region pairs, derived), `eia930_ba_interchange_hourly_2018` to `_2026` 21,780,045 rows together (each side's report its own row). Hourly from 2018-07-01 to 2026-11-16/18, from the 34 six-month files (`warehouse/connectors/eia930_region_hourly.py`, `eia930_ba_interchange_hourly.py`), each passing the validator, archived (13 tables, 43,631,539 rows), internal tier: held out of the live catalogue and of release v1, not on Redivis.
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

### Table 8 (session 7803), on `wip/c401-county`

- `iso_hub_prices_history_2018` 219,720 rows: SPP's North Hub (SPPNORTH_HUB), 43,944 day-ahead hours and 175,776 real-time quarter hours (15-minute means of the 5-minute prices), 1 July 2018 to 5 July 2023, no day missing, from SPP's own daily files by `hub_history.py`'s backfill (`warehouse/connectors/hub_history_2018.py` writes the table from it). Method: `docs/methods/hub_prices_history_2018.md`.

### The landing of tables 4 to 8

- One gate for the fourteen tables (`wip/c401-county`). The first gate run failed test 2718 (`eia_county_region`'s coverage row was built with main's validator, which does not know the `county` entity type), the second I stopped myself after test 3298 failed in my own run (`package/llms.txt` written before the license record); both fixed on the branch (coverage rebuilt with the branch's validator copied into main, `build_llms.py` after `licenses.py write`). The third gate (8df90d20d) passed every step but its worktree cleanup.
- Main had moved by then (NOVEC's tariff commit changed `llms.txt` and coverage): I merged origin/main into the branch, rebuilt `llms.txt`, ran the registration tests (159 pass) and pushed that merge (f6606fd89) to `task/c401-county` without a fourth local gate; GitHub's own run passed and merged it as 3c5c99e9f. Snapshots `c401-county-before` and `-after`: 0 differences.
- Archived: tables 4 to 7 (13 tables, 16,623,190 rows) and table 8 (219,720 rows). Held out of release v1 and the live catalogue (`STORAGE_HELD`, `catalogue_hold`), not on Redivis; the license record holds 684 tables with no problems.
- Test `tests/test_session7802_county_region.py` (5 tests): the county-name rule and the station rule.

## Part D: the filed large-load tariffs

- The count: 80 groups, 6 grid operators, 74 utility groups (11 of them generation and transmission cooperatives); 19 groups had a registry file, 55 none. Every one of the 55 now has a line in `docs/state/progress_c401.md`.
- **Read whole and written (public): 5 utilities, 23 rows.** PPL Electric, Rate Schedule LP-6 (4 rows); Northern Virginia Electric Cooperative, Schedule HV-2 (4 rows; a scan, read as page images, the charges again at 300 dpi); Rappahannock Electric Cooperative, Schedule LP-3, its largest transmission-level schedule since it files none for 100 MW (5 rows); Grant County PUD, Rate Schedules 15 and 94 (4 rows); Santee Cooper, Schedule L-25-LL (6 rows). The table went from 60 to 83 rows, 37 schedules, 20 utilities, 16 schedules held; `site/data/siting/tariffs.json` rebuilt after each (the other siting files restored).
- **Read whole and held:** El Paso Electric, Schedule No. 33A (its terms and the PUCT's ask permission).
- **Held by the host's terms, schedule not read** (personal or non-commercial use only, or written permission): Southern California Edison, CMS Energy, AES, Omaha Public Power District, TXNM (PNM), Nebraska Public Power District, Idaho Power, SMUD, Austin Energy, MidAmerican, NorthWestern and Black Hills (Bright Horizon Energy's terms), Eversource, Florida Power & Light, Basin Electric, Great River Energy, Associated Electric, Oglethorpe.
- **Not read: robots or terms refuse automated or AI readers:** Tucson Electric Power (terms), Wisconsin PSC (robots name ClaudeBot), NiSource (terms), CPS Energy, OGE Energy and Western Farmers (robots name Claude), Puget Sound Energy and Tri-State (terms forbid bots and AI), the Kentucky PSC for Big Rivers and East Kentucky (robots refuse Python readers).
- **Behind a bot check (an access control, not gone around):** Duquesne Light, Alliant Energy, Cleco, Tennessee Valley Authority. **No answer:** JEA (twice).
- **Pending, so no row:** DTE (U-22061), Tampa Electric (LLCS-1), Otter Tail (North Dakota PU-26-215, read from the PSC's docket), Minnesota Power (docket 26-126, agenda of 24 November).
- **No standing schedule:** FirstEnergy, Exelon (ComEd's change is to deposits and security), Hoosier Energy (a policy), AES Indiana and NIPSCO (special contracts), Idaho Power (special contracts over 20 MW), Avista (large data center applications paused, special contracts), Wabash Valley, ODEC, BPA, LCRA (wholesale).
- **Open:** WEC (the Commission refuses Claude; its own site not read), SDG&E, PSEG, Colorado Springs Utilities, LADWP (no terms found or a script-rendered terms page), Avista's Schedule 25.

## Decisions made without you

- **Five EIA-930 tables (and nine yearly interchange tables) where the chain named three.** One table of every balancing authority and region hourly since July 2018 is about 20 million rows and 5 GB; this machine's validator read the 1.2 GB table at 3.2 GB of memory, so a 5 GB table cannot pass. The balancing authority tables are split by measurement, as `eia930_all_demand`, `_generation` and `_interchange` are (decision 28 holds); the interchange table, one variable, is one table a UTC year, as `eia930_subba_demand_hourly_<year>` (session 612). Rows carry the file's short tag (`x_file`) and the header every file's URL and dates, not the URL on each of twenty million rows.
- **The region rows are sums of the balancing authorities** (the six-month files hold no region rows), written only when every balancing authority of the region has the hour.
- **The primary balancing authority of a shared county:** the one whose serving utilities have the most retail customers in the state (bundled and delivery customers of EIA-861); the other rule that was open, the most utilities in the county, is kept in `x_ba_by_count`.
- **Table 8:** CAISO's own archive (OASIS) keeps about 39 months, so it holds nothing before July 2023 (the reason `iso_hub_prices_history` starts on 6 July 2023); only SPP is pulled.
- **Table 6 as new tables, not `noaa_isd_hourly` widened.** `noaa_isd_hourly` is read by three pages (`/events/caiso-heat-2022` and two Decisions components), and the chain changes no production figure; the 216 stations' hours are about 15.7 million rows, past what this machine's validator reads in one table. So the stations are `noaa_region_stations` and their hours `noaa_region_station_hourly_<year>`; stations `noaa_grid_weather.py` already saved were read from its raw files, not asked again.
- **A station counts only when its LCD lines up with its ISD-Lite** (an offset agreeing in 80 percent of July 2025); otherwise the next nearest is taken. Without it nine regions lost every hour from August 2025, since a region's hour needs every one of its stations.
- **The large-load rows of a held host were not read.** Where a utility's own terms allow personal or non-commercial use only, or ask written permission, its rows would be held (`license: internal`) and add nothing public; I recorded the terms and moved on to the hosts that allow reuse, rather than reading every held schedule.
- **Grant PUD's figures are Schedule 15's.** A new large load is served only under Schedule 94, which sets its energy price (the greater of Mid-C or Schedule 15's top block, plus 5%) and keeps the demand charges of the underlying schedule: for a load of 10 MW or more that is Schedule 15, so its basic and demand charges are recorded and no energy charge.
- **NOVEC's 45 MW** is the smaller of its two thresholds (65 MW, or 45 MW at 34.5 kV or more from dedicated facilities at a 230 kV point); both are in the row's printed words.

## For Samuel's ruling

- **Table 8, publishers not pulled:** NYISO and ISO-NE (license needed under the hold of 21 October), MISO (paused since 4 October), PJM (the chain), CAISO (its archive holds nothing so old). Default: not pulled.
- **The thirteen EIA-930 tables in release v1:** held out as the other late tables are (and about 3.6 GB against a Redivis account whose free 10 GB is noted as full). Default: held.
- **PPL's book stands public without the Commission's copy**, as PG&E's does (the question of session 2921). Default: public. The same holds for NOVEC, Rappahannock, Grant PUD and Santee Cooper, each read from its own site; the last two set their own rates (a public utility district and a state agency), and the Virginia SCC was not asked since it is paused.
- **The fourteen tables of part C, tables 4 to 8, in release v1:** held out like the thirteen EIA-930 tables. Default: held.
- **Two finished games posted to `game_plays`** by part B's browser before I added the check header (about 23:49 and 23:55 UTC on 17 November), unmarked. Default: left as they are; delete them if they should not count.
- **Row 367's card** disagrees with its own line in the ruling-alternatives file (session 7800's report says how). Default: the row stays `seen` with both figures.

## Pushes and snapshots

- Every push that changed `site/data/siting/tariffs.json` (NOVEC 96a65b0, Rappahannock 9818867, Grant PUD 0845af8, Santee Cooper 173786d) and the landing (3c5c99e9f) had a before and after snapshot: 0 differences each (every page is in review). The progress and report pushes in between deployed without their own pair; the pairs on either side of them show 0 differences.
