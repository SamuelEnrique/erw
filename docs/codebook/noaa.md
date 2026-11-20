# Codebook: noaa

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 21 public tables (2 events, 19 series; tiers: 1 derived, 20 source); 21 documented in full.

- [`noaa_climdiv_state_monthly`](#noaa_climdiv_state_monthly): The statewide (or contiguous U.S.) average temperature or precipitation of one month, from NOAA NCEI's nClimDiv, with NCEI's 1901-2000 mean of that calendar month.
- [`noaa_cpc_degree_days_daily`](#noaa_cpc_degree_days_daily): The population-weighted heating or cooling degree days of one day for one of the 48 contiguous states, one census division or the contiguous U.S., as NOAA's Climate Prediction Center computes them.
- [`noaa_cpc_oni_monthly`](#noaa_cpc_oni_monthly): The Oceanic Nino Index (ONI) of one three-month season, or the season's mean Nino 3.4 sea surface temperature, from NOAA's Climate Prediction Center.
- [`noaa_grid_weather_daily`](#noaa_grid_weather_daily): One grid's weighted daily temperature, dew point, heating or cooling degree days, from five NOAA airport stations a grid weighted by their metropolitan populations, 2019 to now.
- [`noaa_grid_weather_hourly`](#noaa_grid_weather_hourly): One grid's weighted temperature, dew point, heating degrees or cooling degrees for one hour, from five NOAA airport stations a grid weighted by their metropolitan populations, 2019 to now.
- [`noaa_grid_weather_stations`](#noaa_grid_weather_stations): One of the 35 NOAA airport stations behind the grids' weighted weather (five a grid), with one figure about it (its weight, its metropolitan population, or its hours measured, interpolated and missing) over the span counted.
- [`noaa_isd_hourly`](#noaa_isd_hourly): One temperature or dew point observation at one airport station from NOAA's Integrated Surface Database, for the event windows of event_window_daily and their baseline days and for the California alert seasons.
- [`noaa_ncei_billion_disasters`](#noaa_ncei_billion_disasters): One U.S. weather or climate disaster of 1980 to 2024 whose cost reached a billion dollars, from NOAA NCEI's Billion-Dollar Weather and Climate Disasters (the product retired in 2025).
- [`noaa_ncei_storm_events`](#noaa_ncei_storm_events): One storm event of a type that takes power lines down or strains the grid (wind, winter, tropical, tornado, wildfire, heat, cold, lightning, storm surge) in one county or forecast zone, from NOAA NCEI's Storm Events Database, 2015 to 2026.
- [`noaa_region_station_hourly_2018`](#noaa_region_station_hourly_2018): The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2018 (from July).
- [`noaa_region_station_hourly_2019`](#noaa_region_station_hourly_2019): The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2019.
- [`noaa_region_station_hourly_2020`](#noaa_region_station_hourly_2020): The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2020.
- [`noaa_region_station_hourly_2021`](#noaa_region_station_hourly_2021): The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2021.
- [`noaa_region_station_hourly_2022`](#noaa_region_station_hourly_2022): The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2022.
- [`noaa_region_station_hourly_2023`](#noaa_region_station_hourly_2023): The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2023.
- [`noaa_region_station_hourly_2024`](#noaa_region_station_hourly_2024): The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2024.
- [`noaa_region_station_hourly_2025`](#noaa_region_station_hourly_2025): The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2025.
- [`noaa_region_station_hourly_2026`](#noaa_region_station_hourly_2026): The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2026.
- [`noaa_region_stations`](#noaa_region_stations): One county chosen for one EIA region's weather, with its weight in the region and the NOAA station that stands for it.
- [`noaa_station_weather_hourly`](#noaa_station_weather_hourly): The temperature or dew point measured at one of the 35 NOAA airport stations behind the grids' weighted weather, for one hour, 2019 to now.
- [`noaa_uscrn_solar_monthly`](#noaa_uscrn_solar_monthly): The month's average daily total global solar radiation at one of eight U.S. Climate Reference Network (USCRN) stations near CAISO's and ERCOT's solar fleets.

### `noaa_climdiv_state_monthly`

The statewide (or contiguous U.S.) average temperature or precipitation of one month, from NOAA NCEI's nClimDiv, with NCEI's 1901-2000 mean of that calendar month.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 31458.

- **Time:** ts_utc is the month's first day at 00:00:00Z.
- **Revisions:** Merged by (entity, variable, ts_utc); a later run replaces a month NCEI restates and keeps the months it no longer reads. vintage is the processing date of NCEI's files.
- **Source:** noaa:climdiv NOAA National Centers for Environmental Information, nClimDiv (Vose et al. 2014), statewide files (https://www.ncei.noaa.gov/pub/data/cirs/climdiv/)
- **Method note:** [`docs/methods/noaa_climdiv_state_monthly.md`](../methods/noaa_climdiv_state_monthly.md)
- **Cite as:** NOAA National Centers for Environmental Information (NCEI). nClimDiv statewide monthly temperature and precipitation, with the 1901-2000 means. Via the Energy Research Warehouse (ERW), table `noaa_climdiv_state_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: noaa_climdiv:<NCEI state code>: 001 Alabama to 048 Wyoming, 110 the contiguous U.S. | none | text | for example noaa_climdiv:001, noaa_climdiv:002, noaa_climdiv:003; 49 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2000-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 321 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -2.7 to 89.2; 2036 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF, in | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AL, US-AR; 49 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 31458 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The state's name (or the contiguous U.S.), not a pricing node | none | text | for example Alabama, Arizona, Arkansas; 49 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | noaa:climdiv | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ncei.noaa.gov/pub/data/cirs/climdiv/climdiv-pcpnst-v1.0.0-20261006, https://www.ncei.noaa.gov/pub/data/cirs/climdiv/climdiv-tmpcst-v1.0.0-20261006 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:51:26Z, 2026-10-23T18:51:28Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The date NCEI processed the four files read, at 00:00:00Z (from the files' names) | none | utc time | 2026-10-06T00:00:00Z | 0 |
| `x_mean_1901_2000` | NCEI's own 1901 to 2000 mean of the state, element and calendar month, from the normals file's period 0031 (not computed here) | the row's unit (degF or in) | number | 0.18 to 82.3; 743 distinct | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `precip` | The month's statewide precipitation, inches, as NCEI publishes it | in | 15729 | 2000-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `temp_avg` | The month's statewide average temperature, degrees F, as NCEI publishes it | degF | 15729 | 2000-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `noaa_cpc_degree_days_daily`

The population-weighted heating or cooling degree days of one day for one of the 48 contiguous states, one census division or the contiguous U.S., as NOAA's Climate Prediction Center computes them.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 118900.

- **Time:** ts_utc is the day CPC labels, at 00:00:00Z.
- **Revisions:** Merged by (entity, variable, ts_utc); the current year's files grow each day and are fetched again on each run, earlier years' are kept. vintage is the Last-Modified of the file the row came from.
- **Source:** noaa:cpc_degree_days NOAA Climate Prediction Center, Degree Days Statistics (https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/)
- **Method note:** [`docs/methods/noaa_cpc_degree_days_daily.md`](../methods/noaa_cpc_degree_days_daily.md)
- **Cite as:** NOAA National Weather Service, Climate Prediction Center. Degree Days Statistics: population-weighted daily heating and cooling degree days. Via the Energy Research Warehouse (ERW), table `noaa_cpc_degree_days_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: cpc_dd:<state> (the 48 contiguous states), cpc_dd:division_<n> (a census division as CPC numbers it, 1 to 9) or cpc_dd:conus | none | text | for example cpc_dd:AL, cpc_dd:AR, cpc_dd:AZ; 58 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-01-01T00:00:00Z to 2026-10-21T00:00:00Z; 1025 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 84.0; 84 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF-day | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, US for the contiguous U.S., empty for a census division | none | text | for example US, US-AL, US-AR; 49 distinct | 18450 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 118900 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The region as CPC's file writes it (a state code, a division number), not a pricing node | none | text | for example 1, 2, 3; 58 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | noaa:cpc_degree_days | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/2024/Population.Cooling.txt, https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/2024/Population.Heating.txt, https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/2024/StatesCONUS.Cooling.txt, https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/2024/StatesCONUS.Heating.txt, https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/2025/Population.Cooling.txt, https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/2025/Population.Heating.txt, https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/2025/StatesCONUS.Cooling.txt, https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/2025/StatesCONUS.Heating.txt, https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/2026/Population.Cooling.txt, https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/2026/Population.Heating.txt, https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/2026/StatesCONUS.Cooling.txt, https://ftp.cpc.ncep.noaa.gov/htdocs/degree_days/weighted/daily_data/2026/StatesCONUS.Heating.txt | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T15:21:37Z, 2026-10-23T15:21:39Z, 2026-10-23T15:21:40Z, 2026-10-23T15:21:53Z, 2026-10-23T15:21:54Z, 2026-10-23T15:21:56Z, 2026-10-23T15:21:57Z, 2026-10-23T15:21:58Z, 2026-10-23T15:22:00Z, 2026-10-23T15:22:01Z, 2026-10-23T15:22:02Z, 2026-10-23T15:22:04Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Last-Modified of CPC's yearly file the row came from | none | utc time | 2025-01-02T08:12:21Z, 2025-01-02T08:12:22Z, 2026-01-02T08:09:54Z, 2026-10-23T08:07:00Z | 0 |
| `x_regions` | CPC's set of regions the row comes from: StatesCONUS (the states) or Population (the census divisions and the contiguous U.S.) | none | text | Population, StatesCONUS | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `cdd` | Cooling degree days of the day at a base of 65 F, weighted by population as CPC computes them, degF-day | degF-day | 59450 | 2024-01-01T00:00:00Z | 2026-10-21T00:00:00Z |
| `hdd` | Heating degree days of the day at a base of 65 F, weighted by population as CPC computes them, degF-day | degF-day | 59450 | 2024-01-01T00:00:00Z | 2026-10-21T00:00:00Z |

### `noaa_cpc_oni_monthly`

The Oceanic Nino Index (ONI) of one three-month season, or the season's mean Nino 3.4 sea surface temperature, from NOAA's Climate Prediction Center.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1840.

- **Time:** ts_utc is the first day of the three-month season's middle month at 00:00:00Z (DJF is January, NDJ December; CPC's YR is the middle month's year).
- **Revisions:** A snapshot written whole by each run, which asks for CPC's file fresh, so CPC's revisions of recent seasons are taken. vintage is the file's Last-Modified.
- **Source:** noaa:cpc_oni NOAA Climate Prediction Center, Cold and Warm Episodes by Season (ONI) (https://www.cpc.ncep.noaa.gov/products/analysis_monitoring/ensostuff/ONI_v5.php)
- **Method note:** [`docs/methods/noaa_cpc_oni_monthly.md`](../methods/noaa_cpc_oni_monthly.md)
- **Cite as:** NOAA National Weather Service, Climate Prediction Center. Oceanic Nino Index (ONI): Cold and Warm Episodes by Season. Via the Energy Research Warehouse (ERW), table `noaa_cpc_oni_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: cpc:oni_nino34 in every row | none | text | cpc:oni_nino34 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1950-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 920 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -2.04 to 29.15; 647 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degC | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | empty | no cell holds a value | 1840 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1840 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: Nino 3.4 in every row: the ocean region of the index, not a pricing node | none | text | Nino 3.4 | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | noaa:cpc_oni | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.cpc.ncep.noaa.gov/data/indices/oni.ascii.txt | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T21:29:32Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Last-Modified of CPC's file oni.ascii.txt | none | utc time | 2026-10-03T18:32:01Z | 0 |
| `x_season` | CPC's three letters of the three-month season (DJF, JFM, ... NDJ) (the source's name: SEAS) | none | text | AMJ, ASO, DJF, FMA, JAS, JFM, JJA, MAM, MJJ, NDJ, OND, SON | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `nino34_sst` | CPC's TOTAL: the three-month running mean of the Nino 3.4 sea surface temperature, degC | degC | 920 | 1950-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `oni_anomaly` | The Oceanic Nino Index: CPC's ANOM, the anomaly of the three-month running mean of the Nino 3.4 sea surface temperature, degC | degC | 920 | 1950-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `noaa_grid_weather_daily`

One grid's weighted daily temperature, dew point, heating or cooling degree days, from five NOAA airport stations a grid weighted by their metropolitan populations, 2019 to now.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 119494.

- **Time:** ts_utc is the grid's local day at 00:00:00Z (America/Chicago for ERCOT, MISO and SPP, America/Los_Angeles for CAISO, America/New_York for NYISO, ISO-NE and PJM). A day is written only when every one of its hours is held.
- **Revisions:** Each run deletes the table and writes it whole from the saved files, so a day is recomputed every run; with --refresh the later answer's hours replace the held ones. vintage is not filled.
- **Source:** noaa:isd_lite NOAA National Centers for Environmental Information, Integrated Surface Database, ISD-Lite (https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database)
- **Source:** noaa:lcd_v2 NOAA National Centers for Environmental Information, Local Climatological Data version 2 (https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data)
- **Method note:** [`docs/methods/noaa_grid_weather_daily.md`](../methods/noaa_grid_weather_daily.md)
- **Cite as:** NOAA National Centers for Environmental Information. ISD-Lite (Integrated Surface Database, hourly); Local Climatological Data v2. Via the Energy Research Warehouse (ERW), table `noaa_grid_weather_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: iso:<grid> | none | text | iso:caiso, iso:ercot, iso:isone, iso:miso, iso:nyiso, iso:pjm, iso:spp | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-11-06T00:00:00Z; 2858 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -20.996 to 106.348; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF, degF-day | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: The states the grid serves, comma-separated | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-DE,US-DC,US-IL,US-IN,US-KY,US-MD,US-MI,US-NJ,US-NC,US-OH,US-PA,US-TN,US-VA,US-WV, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 119494 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The grid's name (CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP), not a pricing node | none | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | noaa:isd_lite, noaa:lcd_v2 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2019/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2020/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2021/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2022/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2023/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2024/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2025/, https://www.ncei.noaa.gov/access/services/data/v1?dataset=local-climatological-data-v2 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T18:05:35Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 119494 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48). Here: The grid's EIA-930 code (ciso, erco, isne, miso, nyis, pjm, swpp), to join eia930 tables | none | text | ciso, erco, isne, miso, nyis, pjm, swpp | 0 |
| `x_hours` | The hours of the grid's local day: 24, or 23 and 25 on the clock-change days | count | integer | 23, 24, 25 | 0 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `cooling_degree_days` | The sum of the day's hourly cooling degrees (base 65 F) over 24, degF-day | degF-day | 19918 | 2019-01-01T00:00:00Z | 2026-11-06T00:00:00Z |
| `dew_point_f` | The mean of the day's weighted hourly dew points, degrees F | degF | 19904 | 2019-01-01T00:00:00Z | 2026-11-06T00:00:00Z |
| `heating_degree_days` | The sum of the day's hourly heating degrees (base 65 F) over 24, degF-day | degF-day | 19918 | 2019-01-01T00:00:00Z | 2026-11-06T00:00:00Z |
| `temperature_f` | The mean of the day's weighted hourly temperatures, degrees F | degF | 19918 | 2019-01-01T00:00:00Z | 2026-11-06T00:00:00Z |
| `temperature_max_f` | The day's highest weighted hourly temperature, degrees F | degF | 19918 | 2019-01-01T00:00:00Z | 2026-11-06T00:00:00Z |
| `temperature_min_f` | The day's lowest weighted hourly temperature, degrees F | degF | 19918 | 2019-01-01T00:00:00Z | 2026-11-06T00:00:00Z |

### `noaa_grid_weather_hourly`

One grid's weighted temperature, dew point, heating degrees or cooling degrees for one hour, from five NOAA airport stations a grid weighted by their metropolitan populations, 2019 to now.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1921373.

- **Time:** ts_utc is the hour in UTC; the reading is the one taken in the ten minutes up to it (Local Climatological Data's local standard times moved to UTC). freq PT1H.
- **Revisions:** Each run deletes the table and writes it whole; with --refresh the later answer's hours replace the held ones from its first hour on. vintage is not filled.
- **Source:** noaa:isd_lite NOAA National Centers for Environmental Information, Integrated Surface Database, ISD-Lite (https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database)
- **Source:** noaa:lcd_v2 NOAA National Centers for Environmental Information, Local Climatological Data version 2 (https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data)
- **Method note:** [`docs/methods/noaa_grid_weather_hourly.md`](../methods/noaa_grid_weather_hourly.md)
- **Cite as:** NOAA National Centers for Environmental Information. ISD-Lite (Integrated Surface Database, hourly); Local Climatological Data v2. Via the Energy Research Warehouse (ERW), table `noaa_grid_weather_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: iso:<grid> | none | text | iso:caiso, iso:ercot, iso:isone, iso:miso, iso:nyiso, iso:pjm, iso:spp | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-11-07T14:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -29.38 to 106.35; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: The states of the grid, comma-separated | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-DE,US-DC,US-IL,US-IN,US-KY,US-MD,US-MI,US-NJ,US-NC,US-OH,US-PA,US-TN,US-VA,US-WV, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1921373 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The grid's name (CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP), not a pricing node | none | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | noaa:isd_lite, noaa:lcd_v2 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2019/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2020/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2021/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2022/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2023/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2024/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2025/, https://www.ncei.noaa.gov/access/services/data/v1?dataset=local-climatological-data-v2 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T18:05:35Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 1921373 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48). Here: The grid's EIA-930 code, to join eia930 tables | none | text | ciso, erco, isne, miso, nyis, pjm, swpp | 0 |
| `x_interpolated` | How many of the five stations' temperatures in the hour are interpolated (across at most 3 hours) | count | integer | 0, 1, 2, 3, 4, 5 | 0 |

Variables (4):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `cooling_degrees_f` | The weighted mean over the stations of max(T - 65, 0), degrees F | degF | 480361 | 2019-01-01T00:00:00Z | 2026-11-07T14:00:00Z |
| `dew_point_f` | The weighted mean of the stations' dew points, degrees F | degF | 480290 | 2019-01-01T00:00:00Z | 2026-11-07T14:00:00Z |
| `heating_degrees_f` | The weighted mean over the stations of max(65 - T, 0), degrees F | degF | 480361 | 2019-01-01T00:00:00Z | 2026-11-07T14:00:00Z |
| `temperature_f` | The weighted mean of the stations' temperatures, degrees F (NOAA's tenths of a degree C times 9/5 plus 32) | degF | 480361 | 2019-01-01T00:00:00Z | 2026-11-07T14:00:00Z |

### `noaa_grid_weather_stations`

One of the 35 NOAA airport stations behind the grids' weighted weather (five a grid), with one figure about it (its weight, its metropolitan population, or its hours measured, interpolated and missing) over the span counted.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 245.

- **Time:** ts_utc is 2019-01-01T00:00:00Z, the start of the span counted; the span runs x_hours hours to x_through. freq is blank.
- **Revisions:** Each run deletes the table and writes it whole, recounting over the whole span and taking the weights again from census_metro_population. vintage is not filled.
- **Source:** noaa:isd_lite NOAA National Centers for Environmental Information, Integrated Surface Database, ISD-Lite (https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database)
- **Source:** noaa:lcd_v2 NOAA National Centers for Environmental Information, Local Climatological Data version 2 (https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data)
- **Method note:** [`docs/methods/noaa_grid_weather_stations.md`](../methods/noaa_grid_weather_stations.md)
- **Cite as:** NOAA National Centers for Environmental Information. ISD-Lite (Integrated Surface Database, hourly). Via the Energy Research Warehouse (ERW), table `noaa_grid_weather_stations`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: noaa:<GHCN identifier> (USW000 and the WBAN) | none | text | for example noaa:USW00003102, noaa:USW00003927, noaa:USW00003928; 35 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.039034 to 13204693.0; 155 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, ratio | 0 |
| `freq` | How long the interval of the row is. Here: Not filled: the counts run over the span from ts_utc to x_through | none | empty | no cell holds a value | 245 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> of the station | none | text | US-CA, US-CT, US-IL, US-IN, US-KS, US-MA, US-MD, US-MI, US-MN, US-MO, US-NE, US-NY, US-OK, US-PA, US-RI, US-TX, US-VA, US-WI | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 245 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The grid the station stands for, not a pricing node | none | text | CAISO, ERCOT, ISO-NE, MISO, NYISO, PJM, SPP | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | noaa:isd_lite | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/ | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T18:05:35Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 245 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48). Here: The grid's EIA-930 code | none | text | ciso, erco, isne, miso, nyis, pjm, swpp | 0 |
| `x_airport` | The station's airport code (DFW, LAX and the others) | none | text | for example ALB, AUS, BDL; 35 distinct | 0 |
| `x_station` | NOAA's station identifier, USAF-WBAN | none | text | for example 722430-12960, 722506-12959, 722530-12921; 35 distinct | 0 |
| `x_name` | The station's name as NOAA gives it (isd-history.csv) | none | text | for example ALBANY INTERNATIONAL AIRPORT, AUSTIN-BERGSTROM INTL AIRPORT, BALTIMORE-WASHINGTON INTL AIRPORT; 35 distinct | 0 |
| `x_lat` | The station's latitude as NOAA gives it (isd-history.csv) | degree | number | 26.179 to 44.885; 35 distinct | 0 |
| `x_lon` | The station's longitude as NOAA gives it (isd-history.csv) | degree | number | -122.366 to -71.01; 35 distinct | 0 |
| `x_metro` | The metropolitan area the station stands for | none | text | for example Albany-Schenectady-Troy, Austin-Round Rock-Georgetown, Baltimore-Columbia-Towson; 35 distinct | 0 |
| `x_hours` | The hours of the span the counts run over | hour | integer | 68823 | 0 |
| `x_through` | The last hour of the span, UTC: the last hour every station reaches | none | utc time | 2026-11-07T14:00:00Z | 0 |
| `x_cbsa` | The Census Bureau's code of the metropolitan area, with a state after a colon where only a part is counted | none | text | for example 10580, 12420, 12580; 35 distinct | 0 |

Variables (7):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dew_point_hours_missing` | Hours of the span with no dew point, count | count | 35 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `hours_interpolated` | Hours of the span with a temperature interpolated across at most 3 hours, count | count | 35 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `hours_measured` | Hours of the span with a measured temperature, count | count | 35 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `hours_missing` | Hours of the span with no temperature, count | count | 35 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `longest_gap_hours` | The longest run of missing hours, count | count | 35 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `population_base_2020` | The Census Bureau's estimates base of 1 April 2020 for the station's metropolitan area (x_cbsa), count | count | 35 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `weight` | The station's share of its grid: its metropolitan population over the sum of its grid's five (ratio) | ratio | 35 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |

### `noaa_isd_hourly`

One temperature or dew point observation at one airport station from NOAA's Integrated Surface Database, for the event windows of event_window_daily and their baseline days and for the California alert seasons.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 412435.

- **Time:** ts_utc is the observation's time in UTC (irregular times; freq left blank).
- **Revisions:** Merged by key across runs (entity, variable, ts_utc), a later run's rows replacing the held ones; restored from the Redivis draft by scripts/sync.py. vintage is not filled.
- **Source:** noaa:isd_global_hourly NOAA NCEI Integrated Surface Database (global-hourly) (https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database)
- **Method note:** [`docs/methods/noaa_isd_hourly.md`](../methods/noaa_isd_hourly.md)
- **Cite as:** NOAA National Centers for Environmental Information (NCEI). Integrated Surface Database (global-hourly). Via the Energy Research Warehouse (ERW), table `noaa_isd_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: noaa:<airport code> | none | text | noaa:BOS, noaa:DFW, noaa:FAT, noaa:IAH, noaa:JFK, noaa:LAX, noaa:MSP, noaa:OKC, noaa:ORD, noaa:PHL, noaa:SAC | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-03-04T05:51:00Z to 2025-08-27T06:53:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -20.02 to 114.08; 201 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF | 0 |
| `freq` | How long the interval of the row is. Here: Not filled: observation times are irregular | none | empty | no cell holds a value | 412435 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 412435 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 412435 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: ISD's report type (FM-15 the routine hourly report, FM-12 synoptic, FM-16 special, SY-MT); where two reports share an instant, FM-15 is kept | none | text | FM-12, FM-15, FM-16, SY-MT | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | noaa:isd_global_hourly | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www.ncei.noaa.gov/access/services/data/v1?dataset=global-hourly&stations=72243012960&startDate=2019-02-07T06%3A00%3A00&endDate=2019-02-25T05%3A59%3A59&dataTypes=TMP%2CDEW&format=csv&includeStationName=true, https://www.ncei.noaa.gov/access/services/data/v1?dataset=global-hourly&stations=72243012960&startDate=2020-02-07T06%3A00%3A00&endDate=2020-02-25T05%3A59%3A59&dataTypes=TMP%2CDEW&format=csv&includeStationName=true, https://www.ncei.noaa.gov/access/services/data/v1?dataset=global-hourly&stations=72243012960&startDate=2020-12-21T06%3A00%3A00&endDate=2021-01-01T05%3A59%3A59&dataTypes=TMP%2CDEW&format=csv&includeStationName=true; 78 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-01T03:55:28Z, 2026-10-02T04:48:18Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 412435 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48). Here: The grid the station stands for | none | text | ciso, erco, isne, miso, nyis, pjm, swpp | 0 |
| `x_station_id` | NCEI's station identifier | none | integer | 72243012960, 72259003927, 72295023174, 72353013967, 72389093193, 72408013739, 72483023232, 72509014739, 72530094846, 72658014922, 74486094789 | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dew_point_f` | The observed dew point, degrees F (ISD's tenths of a degree C times 9/5 plus 32, to 2 decimals) | degF | 206155 | 2018-03-04T05:51:00Z | 2025-08-27T06:53:00Z |
| `temperature_f` | The observed temperature, degrees F (ISD's tenths of a degree C times 9/5 plus 32, to 2 decimals); missing and quality codes 2, 3, 6, 7 not written | degF | 206280 | 2018-03-04T05:51:00Z | 2025-08-27T06:53:00Z |

### `noaa_ncei_billion_disasters`

One U.S. weather or climate disaster of 1980 to 2024 whose cost reached a billion dollars, from NOAA NCEI's Billion-Dollar Weather and Climate Disasters (the product retired in 2025).

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 403.

- **Time:** event_date is the disaster's begin date; x_end_date its end.
- **Revisions:** A snapshot written whole each run; the file is reused from the raw files once saved, as the retired record no longer changes. No vintage column.
- **Source:** noaa:billion_dollar_disasters NOAA National Centers for Environmental Information (NCEI) U.S. Billion-Dollar Weather and Climate Disasters (2025), https://www.ncei.noaa.gov/access/billions/, DOI: 10.25921/stkw-7w73 (https://www.ncei.noaa.gov/access/billions/)
- **Method note:** [`docs/methods/noaa_ncei_billion_disasters.md`](../methods/noaa_ncei_billion_disasters.md)
- **Cite as:** NOAA National Centers for Environmental Information (NCEI). U.S. Billion-Dollar Weather and Climate Disasters, events 1980 to 2024 (retired 2025). Via the Energy Research Warehouse (ERW), table `noaa_ncei_billion_disasters`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: noaa_billion:<begin date>:<12 hex of the SHA-1 of the name>, the ERW's own (NCEI gives none) | none | text | for example noaa_billion:1980-04-10:c84bdae69481, noaa_billion:1980-06-01:976696562e71, noaa_billion:1980-08-07:16808a4cc470; 403 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which). Here: The disaster's begin date | none | date | 1980-04-10 to 2024-10-09; 400 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: NCEI's disaster type in snake case: severe_storm, tropical_cyclone, flooding, drought, winter_storm, wildfire, freeze | none | text | drought, flooding, freeze, severe_storm, tropical_cyclone, wildfire, winter_storm | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: Empty in every row | none | empty | no cell holds a value | 403 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons. Here: Empty in every row | none | empty | no cell holds a value | 403 |
| `mw` | The capacity involved, in megawatts. Here: Empty in every row | MW | empty | no cell holds a value | 403 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise. Here: Empty in every row | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 403 |
| `currency` | The currency of the price, as an ISO 4217 code (USD). Here: Empty in every row | none | empty | no cell holds a value | 403 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 403 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | noaa:billion_dollar_disasters | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ncei.noaa.gov/access/billions/events-US-1980-2024.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T20:19:06Z | 0 |
| `x_name` | NCEI's name of the disaster (the source's name: Name) | none | text | for example Arizona Flooding (October 1983), Arizona Severe Weather (October 2010), Arkansas River Flooding (June 2019); 400 distinct | 0 |
| `x_disaster` | NCEI's disaster type in its own words (Severe Storm, Tropical Cyclone, Flooding, Drought, Winter Storm, Wildfire, Freeze) (the source's name: Disaster) | none | text | Drought, Flooding, Freeze, Severe Storm, Tropical Cyclone, Wildfire, Winter Storm | 0 |
| `x_end_date` | The disaster's end date (the source's name: End Date) | none | date | 1980-04-17 to 2024-12-31; 395 distinct | 0 |
| `x_cost_cpi_adjusted_usd` | NCEI's cost of the disaster adjusted by the consumer price index, its millions written as dollars (the source's name: CPI-Adjusted Cost) | USD | integer | 1063800000 to 201297500000; 399 distinct | 0 |
| `x_cost_unadjusted_usd` | NCEI's cost of the disaster not adjusted for inflation, its millions written as dollars (the source's name: Unadjusted Cost) | USD | integer | 400000000 to 125029500000; 388 distinct | 0 |
| `x_deaths` | The deaths NCEI counts for the disaster, as published (the source's name: Deaths) | count | integer | 0 to 2981; 92 distinct | 0 |

### `noaa_ncei_storm_events`

One storm event of a type that takes power lines down or strains the grid (wind, winter, tropical, tornado, wildfire, heat, cold, lightning, storm surge) in one county or forecast zone, from NOAA NCEI's Storm Events Database, 2015 to 2026.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 411139.

- **Time:** event_date is the event's begin time in UTC (NCEI's local time less the offset its CZ_TIMEZONE names); x_begin_local and x_end_local keep NCEI's local times.
- **Revisions:** A snapshot written whole by each run, so an event NCEI drops leaves it; a revised yearly file has a new name and is fetched. No vintage column; x_file_created is the file's creation date.
- **Source:** noaa:storm_events NOAA National Centers for Environmental Information, Storm Events Database (the National Weather Service's Storm Data) (https://www.ncei.noaa.gov/stormevents/)
- **Method note:** [`docs/methods/noaa_ncei_storm_events.md`](../methods/noaa_ncei_storm_events.md)
- **Cite as:** National Oceanic and Atmospheric Administration (NOAA), National Centers for Environmental Information (NCEI). Storm Events Database, bulk details files. Via the Energy Research Warehouse (ERW), table `noaa_ncei_storm_events`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents. Here: noaa_storm:<EVENT_ID>, NCEI's own identifier | none | text | for example noaa_storm:1000000, noaa_storm:1000001, noaa_storm:1000003; more than 5000 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which). Here: The event's begin time in UTC, YYYY-MM-DDTHH:MM:SSZ | none | utc time | 2015-01-01T06:00:00Z to 2026-07-01T05:49:00Z; more than 5000 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others). Here: NCEI's EVENT_TYPE in snake case (thunderstorm_wind, high_wind, winter_storm, tornado and others) | none | text | blizzard, cold_wind_chill, excessive_heat, extreme_cold_wind_chill, heat, heavy_snow, high_wind, hurricane, hurricane_typhoon, ice_storm, lightning, storm_surge_tide, strong_wind, thunderstorm_wind, tornado, tropical_depression, tropical_storm, wildfire, winter_storm | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons. Here: Empty in every row | none | empty | no cell holds a value | 411139 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons. Here: Empty in every row | none | empty | no cell holds a value | 411139 |
| `mw` | The capacity involved, in megawatts. Here: Empty in every row | MW | empty | no cell holds a value | 411139 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise. Here: Empty in every row | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 411139 |
| `currency` | The currency of the price, as an ISO 4217 code (USD). Here: Empty in every row | none | empty | no cell holds a value | 411139 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 411139 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | noaa:storm_events | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2015_c20260323.csv.gz, https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2016_c20260323.csv.gz, https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2017_c20260519.csv.gz, https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2018_c20260323.csv.gz, https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2019_c20260323.csv.gz, https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2020_c20260323.csv.gz, https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2021_c20260323.csv.gz, https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2022_c20260625.csv.gz, https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2023_c20260323.csv.gz, https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2024_c20260728.csv.gz, https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2025_c20260819.csv.gz, https://www.ncei.noaa.gov/pub/data/swdi/stormevents/csvfiles/StormEvents_details-ftp_v1.0_d2026_c20260918.csv.gz | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T18:27:36Z, 2026-10-23T18:27:39Z, 2026-10-23T18:27:42Z, 2026-10-23T18:27:56Z, 2026-10-23T18:28:00Z, 2026-10-23T18:28:04Z, 2026-10-23T18:28:08Z, 2026-10-23T18:28:12Z, 2026-10-23T18:28:17Z, 2026-10-23T18:28:21Z, 2026-10-23T18:28:26Z, 2026-10-23T18:28:30Z | 0 |
| `x_noaa_event_type` | NCEI's event type in its own words (Thunderstorm Wind, High Wind, Winter Storm, Tornado and others) (the source's name: EVENT_TYPE) | none | text | Blizzard, Cold/Wind Chill, Excessive Heat, Extreme Cold/Wind Chill, Heat, Heavy Snow, High Wind, Hurricane, Hurricane (Typhoon), Ice Storm, Lightning, Storm Surge/Tide, Strong Wind, Thunderstorm Wind, Tornado, Tropical Depression, Tropical Storm, Wildfire, Winter Storm | 0 |
| `x_geo` | The state's ISO 3166-2 code (US-TX), from NCEI's state code (96 to 99 its codes for the territories); the events shape has no geo column of its own (the source's name: STATE_FIPS) | none | text | for example US-AK, US-AL, US-AR; 55 distinct | 0 |
| `x_begin_local` | The event's begin time in NCEI's local time (the zone x_timezone names) (the source's name: BEGIN_YEARMONTH, BEGIN_DAY, BEGIN_TIME) | none | text | for example 2015-01-01T00:00:00, 2015-01-01T00:15:00, 2015-01-01T00:30:00; more than 5000 distinct | 0 |
| `x_end_local` | The event's end time in NCEI's local time (the source's name: END_YEARMONTH, END_DAY, END_TIME) | none | text | for example 2015-01-01T02:00:00, 2015-01-01T03:00:00, 2015-01-01T06:00:00; more than 5000 distinct | 0 |
| `x_end_utc` | The event's end time in UTC (x_end_local less the zone's offset) | none | utc time | 2015-01-01T09:00:00Z to 2026-07-01T07:59:00Z; more than 5000 distinct | 0 |
| `x_damage_property_usd` | Property damage, NCEI's K, M and B figures read as dollars (K alone is 0) (the source's name: DAMAGE_PROPERTY) | USD | integer | 0 to 17000000000; 912 distinct | 89007: NCEI's cell is empty |
| `x_damage_crops_usd` | Crop damage, NCEI's K, M and B figures read as dollars (the source's name: DAMAGE_CROPS) | USD | integer | 0 to 500000000; 209 distinct | 92372: NCEI's cell is empty |
| `x_episode_id` | NCEI's identifier of the episode (the storm system) the event belongs to (the source's name: EPISODE_ID) | none | integer | 91225 to 216449; more than 5000 distinct | 0 |
| `x_state` | The state's name as NCEI writes it (the source's name: STATE) | none | text | for example ALABAMA, ALASKA, AMERICAN SAMOA; 55 distinct | 0 |
| `x_state_fips` | NCEI's state code: the state's FIPS code, or 96 to 99 for the territories (the source's name: STATE_FIPS) | none | integer | 1 to 99; 55 distinct | 0 |
| `x_cz_type` | Whether the event is placed by county (C) or by forecast zone (Z), as published (the source's name: CZ_TYPE) | none | text | 5, C, Z | 0 |
| `x_cz_fips` | NCEI's number of the county or forecast zone within the state (the source's name: CZ_FIPS) | none | integer | 1 to 852; 629 distinct | 0 |
| `x_cz_name` | The name of the county or forecast zone (the source's name: CZ_NAME) | none | text | for example ABBEVILLE, ABSAROKA / BEARTOOTH MOUNTAINS, ABSAROKA MOUNTAINS; 3967 distinct | 0 |
| `x_wfo` | The National Weather Service forecast office that reported the event, its code (the source's name: WFO) | none | text | for example ABQ, ABR, AFC; 123 distinct | 0 |
| `x_timezone` | NCEI's time zone of the local times, with its own hours from UTC (EST-5, CST-6, PDT-7, GST10 and others) (the source's name: CZ_TIMEZONE) | none | text | AKST-9, AST-4, CDT-5, CST-6, EDT-4, EST-5, GST10, HST-10, MST-7, PDT-7, PST-8, SST-11 | 0 |
| `x_injuries_direct` | Injuries directly caused by the event, as NCEI publishes them (the source's name: INJURIES_DIRECT) | count | integer | 0 to 806; 76 distinct | 0 |
| `x_injuries_indirect` | Injuries indirectly caused by the event, as NCEI publishes them (the source's name: INJURIES_INDIRECT) | count | integer | 0 to 500; 34 distinct | 0 |
| `x_deaths_direct` | Deaths directly caused by the event, as NCEI publishes them (the source's name: DEATHS_DIRECT) | count | integer | 0 to 102; 32 distinct | 0 |
| `x_deaths_indirect` | Deaths indirectly caused by the event, as NCEI publishes them (the source's name: DEATHS_INDIRECT) | count | integer | 0, 1, 10, 11, 12, 13, 15, 18, 2, 20, 21, 25, 26, 29, 3, 4, 5, 56, 6, 7, 8, 9 | 0 |
| `x_magnitude` | The event's magnitude as NCEI publishes it (knots for wind) (the source's name: MAGNITUDE) | knots for wind | number | 1.0 to 173.0; 129 distinct | 148335: NCEI gives no magnitude (types without one) |
| `x_magnitude_type` | NCEI's code of the kind of magnitude, as published (EG, ES, MG, MS) (the source's name: MAGNITUDE_TYPE) | none | text | EG, ES, MG, MS | 148335: NCEI gives no magnitude |
| `x_tor_f_scale` | The tornado's rating on the Enhanced Fujita scale (EF0 to EF5, EFU), as published (the source's name: TOR_F_SCALE) | none | text | EF0, EF1, EF2, EF3, EF4, EF5, EFU | 393660: Not a tornado |
| `x_tor_length_mi` | The length of the tornado's path (the source's name: TOR_LENGTH) | miles | number | 0.01 to 49.96; 1719 distinct | 393660: Not a tornado |
| `x_tor_width_yd` | The width of the tornado's path (the source's name: TOR_WIDTH) | yards | number | 1.0 to 3960.0; 354 distinct | 393660: Not a tornado |
| `x_begin_lat` | The latitude of the event's begin point (the source's name: BEGIN_LAT) | degree | number | -14.3449 to 66.65; more than 5000 distinct | 183631: NCEI gives no begin point |
| `x_begin_lon` | The longitude of the event's begin point (the source's name: BEGIN_LON) | degree | number | -170.8744 to 171.3065; more than 5000 distinct | 183631: NCEI gives no begin point |
| `x_end_lat` | The latitude of the event's end point (the source's name: END_LAT) | degree | number | -14.4375 to 66.6546; more than 5000 distinct | 183631: NCEI gives no end point |
| `x_end_lon` | The longitude of the event's end point (the source's name: END_LON) | degree | number | -170.8284 to 171.0623; more than 5000 distinct | 183631: NCEI gives no end point |
| `x_data_source` | NCEI's data source code, as published (CSV in every row) (the source's name: DATA_SOURCE) | none | text | CSV | 0 |
| `x_file_created` | The creation date of NCEI's yearly file the row came from (its c<YYYYMMDD>) | none | date | 2026-03-23, 2026-05-19, 2026-06-25, 2026-07-28, 2026-08-19, 2026-09-18 | 0 |

Waiting for a second look: x_magnitude_type: NCEI's codes EG, ES, MG and MS are kept as published and not spelled out in the repository's documents.; x_cz_type: two rows hold 5, as published; NCEI's meaning of it is not documented.; x_data_source: CSV in every row; NCEI's meaning of the code is not documented..

### `noaa_region_station_hourly_2018`

The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2018 (from July).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 950944.

- **Time:** ts_utc is the hour in UTC; the reading is ISD-Lite's for the hour (from ten minutes before the hour up to it, the closest to it).
- **Revisions:** A snapshot written whole by each run of the connector (one table a UTC year); not in the daily run. No vintage column.
- **Source:** noaa:isd_lite ISD-Lite (Integrated Surface Database, hourly) (https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database)
- **Source:** noaa:lcd_v2 Local Climatological Data v2 (NCEI Access Data Service) (https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data)
- **Method note:** [`docs/methods/region_weather.md`](../methods/region_weather.md)
- **Cite as:** NOAA National Centers for Environmental Information. ISD-Lite (Integrated Surface Database, hourly). Via the Energy Research Warehouse (ERW), table `noaa_region_station_hourly_2018`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: noaa:<USAF-WBAN>, the station (the node of noaa_region_stations) | none | text | for example noaa:720306-53879, noaa:720307-63804, noaa:720308-04992; 216 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-01T00:00:00Z to 2018-12-31T23:00:00Z; 4416 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -0.94 to 116.96; 1005 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD). Here: noaa:isd_lite in every row | none | text | noaa:isd_lite | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `temperature_f` | The station's temperature in the hour, degrees F; runs of at most three missing hours between two measured hours are interpolated on a straight line | degF | 950944 | 2018-07-01T00:00:00Z | 2018-12-31T23:00:00Z |

### `noaa_region_station_hourly_2019`

The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2019.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1886738.

- **Time:** ts_utc is the hour in UTC; the reading is ISD-Lite's for the hour (from ten minutes before the hour up to it, the closest to it).
- **Revisions:** A snapshot written whole by each run of the connector (one table a UTC year); not in the daily run. No vintage column.
- **Source:** noaa:isd_lite ISD-Lite (Integrated Surface Database, hourly) (https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database)
- **Source:** noaa:lcd_v2 Local Climatological Data v2 (NCEI Access Data Service) (https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data)
- **Method note:** [`docs/methods/region_weather.md`](../methods/region_weather.md)
- **Cite as:** NOAA National Centers for Environmental Information. ISD-Lite (Integrated Surface Database, hourly). Via the Energy Research Warehouse (ERW), table `noaa_region_station_hourly_2019`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: noaa:<USAF-WBAN>, the station (the node of noaa_region_stations) | none | text | for example noaa:720306-53879, noaa:720307-63804, noaa:720308-04992; 216 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2019-12-31T23:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -29.02 to 114.98; 1447 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD). Here: noaa:isd_lite in every row | none | text | noaa:isd_lite | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `temperature_f` | The station's temperature in the hour, degrees F; runs of at most three missing hours between two measured hours are interpolated on a straight line | degF | 1886738 | 2019-01-01T00:00:00Z | 2019-12-31T23:00:00Z |

### `noaa_region_station_hourly_2020`

The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2020.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1893320.

- **Time:** ts_utc is the hour in UTC; the reading is ISD-Lite's for the hour (from ten minutes before the hour up to it, the closest to it).
- **Revisions:** A snapshot written whole by each run of the connector (one table a UTC year); not in the daily run. No vintage column.
- **Source:** noaa:isd_lite ISD-Lite (Integrated Surface Database, hourly) (https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database)
- **Source:** noaa:lcd_v2 Local Climatological Data v2 (NCEI Access Data Service) (https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data)
- **Method note:** [`docs/methods/region_weather.md`](../methods/region_weather.md)
- **Cite as:** NOAA National Centers for Environmental Information. ISD-Lite (Integrated Surface Database, hourly). Via the Energy Research Warehouse (ERW), table `noaa_region_station_hourly_2020`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: noaa:<USAF-WBAN>, the station (the node of noaa_region_stations) | none | text | for example noaa:720306-53879, noaa:720307-63804, noaa:720308-04992; 216 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-01-01T00:00:00Z to 2020-12-31T23:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -13.0 to 116.96; 1213 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD). Here: noaa:isd_lite in every row | none | text | noaa:isd_lite | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `temperature_f` | The station's temperature in the hour, degrees F; runs of at most three missing hours between two measured hours are interpolated on a straight line | degF | 1893320 | 2020-01-01T00:00:00Z | 2020-12-31T23:00:00Z |

### `noaa_region_station_hourly_2021`

The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2021.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1887351.

- **Time:** ts_utc is the hour in UTC; the reading is ISD-Lite's for the hour (from ten minutes before the hour up to it, the closest to it).
- **Revisions:** A snapshot written whole by each run of the connector (one table a UTC year); not in the daily run. No vintage column.
- **Source:** noaa:isd_lite ISD-Lite (Integrated Surface Database, hourly) (https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database)
- **Source:** noaa:lcd_v2 Local Climatological Data v2 (NCEI Access Data Service) (https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data)
- **Method note:** [`docs/methods/region_weather.md`](../methods/region_weather.md)
- **Cite as:** NOAA National Centers for Environmental Information. ISD-Lite (Integrated Surface Database, hourly). Via the Energy Research Warehouse (ERW), table `noaa_region_station_hourly_2021`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: noaa:<USAF-WBAN>, the station (the node of noaa_region_stations) | none | text | for example noaa:720306-53879, noaa:720307-63804, noaa:720308-04992; 216 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2021-01-01T00:00:00Z to 2021-12-31T23:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -29.02 to 116.96; 1291 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD). Here: noaa:isd_lite in every row | none | text | noaa:isd_lite | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `temperature_f` | The station's temperature in the hour, degrees F; runs of at most three missing hours between two measured hours are interpolated on a straight line | degF | 1887351 | 2021-01-01T00:00:00Z | 2021-12-31T23:00:00Z |

### `noaa_region_station_hourly_2022`

The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2022.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1887706.

- **Time:** ts_utc is the hour in UTC; the reading is ISD-Lite's for the hour (from ten minutes before the hour up to it, the closest to it).
- **Revisions:** A snapshot written whole by each run of the connector (one table a UTC year); not in the daily run. No vintage column.
- **Source:** noaa:isd_lite ISD-Lite (Integrated Surface Database, hourly) (https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database)
- **Source:** noaa:lcd_v2 Local Climatological Data v2 (NCEI Access Data Service) (https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data)
- **Method note:** [`docs/methods/region_weather.md`](../methods/region_weather.md)
- **Cite as:** NOAA National Centers for Environmental Information. ISD-Lite (Integrated Surface Database, hourly). Via the Energy Research Warehouse (ERW), table `noaa_region_station_hourly_2022`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: noaa:<USAF-WBAN>, the station (the node of noaa_region_stations) | none | text | for example noaa:720306-53879, noaa:720307-63804, noaa:720308-04992; 216 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2022-01-01T00:00:00Z to 2022-12-31T23:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -38.02 to 114.98; 1318 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD). Here: noaa:isd_lite in every row | none | text | noaa:isd_lite | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `temperature_f` | The station's temperature in the hour, degrees F; runs of at most three missing hours between two measured hours are interpolated on a straight line | degF | 1887706 | 2022-01-01T00:00:00Z | 2022-12-31T23:00:00Z |

### `noaa_region_station_hourly_2023`

The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2023.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1888010.

- **Time:** ts_utc is the hour in UTC; the reading is ISD-Lite's for the hour (from ten minutes before the hour up to it, the closest to it).
- **Revisions:** A snapshot written whole by each run of the connector (one table a UTC year); not in the daily run. No vintage column.
- **Source:** noaa:isd_lite ISD-Lite (Integrated Surface Database, hourly) (https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database)
- **Source:** noaa:lcd_v2 Local Climatological Data v2 (NCEI Access Data Service) (https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data)
- **Method note:** [`docs/methods/region_weather.md`](../methods/region_weather.md)
- **Cite as:** NOAA National Centers for Environmental Information. ISD-Lite (Integrated Surface Database, hourly). Via the Energy Research Warehouse (ERW), table `noaa_region_station_hourly_2023`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: noaa:<USAF-WBAN>, the station (the node of noaa_region_stations) | none | text | for example noaa:720306-53879, noaa:720307-63804, noaa:720308-04992; 216 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2023-01-01T00:00:00Z to 2023-12-31T23:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -14.98 to 118.94; 1331 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD). Here: noaa:isd_lite in every row | none | text | noaa:isd_lite | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `temperature_f` | The station's temperature in the hour, degrees F; runs of at most three missing hours between two measured hours are interpolated on a straight line | degF | 1888010 | 2023-01-01T00:00:00Z | 2023-12-31T23:00:00Z |

### `noaa_region_station_hourly_2024`

The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2024.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1887418.

- **Time:** ts_utc is the hour in UTC; the reading is ISD-Lite's for the hour (from ten minutes before the hour up to it, the closest to it).
- **Revisions:** A snapshot written whole by each run of the connector (one table a UTC year); not in the daily run. No vintage column.
- **Source:** noaa:isd_lite ISD-Lite (Integrated Surface Database, hourly) (https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database)
- **Source:** noaa:lcd_v2 Local Climatological Data v2 (NCEI Access Data Service) (https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data)
- **Method note:** [`docs/methods/region_weather.md`](../methods/region_weather.md)
- **Cite as:** NOAA National Centers for Environmental Information. ISD-Lite (Integrated Surface Database, hourly). Via the Energy Research Warehouse (ERW), table `noaa_region_station_hourly_2024`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: noaa:<USAF-WBAN>, the station (the node of noaa_region_stations) | none | text | for example noaa:720306-53879, noaa:720307-63804, noaa:720308-04992; 216 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-01-01T00:00:00Z to 2024-12-31T23:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -77.08 to 118.04; 1480 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD). Here: noaa:isd_lite in every row | none | text | noaa:isd_lite | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `temperature_f` | The station's temperature in the hour, degrees F; runs of at most three missing hours between two measured hours are interpolated on a straight line | degF | 1887418 | 2024-01-01T00:00:00Z | 2024-12-31T23:00:00Z |

### `noaa_region_station_hourly_2025`

The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2025.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1853441.

- **Time:** ts_utc is the hour in UTC; the reading is ISD-Lite's before 2025-08-01 and, from it, the Local Climatological Data v2 report put on ISD-Lite's hour rule (from ten minutes before the hour up to it, the closest to it), its local standard time moved to UTC.
- **Revisions:** A snapshot written whole by each run of the connector (one table a UTC year); not in the daily run. No vintage column.
- **Source:** noaa:isd_lite ISD-Lite (Integrated Surface Database, hourly) (https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database)
- **Source:** noaa:lcd_v2 Local Climatological Data v2 (NCEI Access Data Service) (https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data)
- **Method note:** [`docs/methods/region_weather.md`](../methods/region_weather.md)
- **Cite as:** NOAA National Centers for Environmental Information. ISD-Lite (Integrated Surface Database, hourly); Local Climatological Data v2. Via the Energy Research Warehouse (ERW), table `noaa_region_station_hourly_2025`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: noaa:<USAF-WBAN>, the station (the node of noaa_region_stations) | none | text | for example noaa:720306-53879, noaa:720307-63804, noaa:720308-04992; 216 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-01-01T00:00:00Z to 2025-12-31T23:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -18.94 to 190.4; 1809 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD). Here: noaa:isd_lite for hours before 2025-08-01, noaa:lcd_v2 (Local Climatological Data v2) from it | none | text | noaa:isd_lite, noaa:lcd_v2 | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `temperature_f` | The station's temperature in the hour, degrees F; runs of at most three missing hours between two measured hours are interpolated on a straight line | degF | 1853441 | 2025-01-01T00:00:00Z | 2025-12-31T23:00:00Z |

### `noaa_region_station_hourly_2026`

The temperature at one station chosen for EIA's regions' weather in one UTC hour of 2026.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1577028.

- **Time:** ts_utc is the hour in UTC; the reading is the Local Climatological Data v2 report put on ISD-Lite's hour rule (from ten minutes before the hour up to it, the closest to it), its local standard time moved to UTC.
- **Revisions:** A snapshot written whole by each run of the connector (one table a UTC year); not in the daily run, so the year grows only when the connector is run. No vintage column.
- **Source:** noaa:isd_lite ISD-Lite (Integrated Surface Database, hourly) (https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database)
- **Source:** noaa:lcd_v2 Local Climatological Data v2 (NCEI Access Data Service) (https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data)
- **Method note:** [`docs/methods/region_weather.md`](../methods/region_weather.md)
- **Cite as:** NOAA National Centers for Environmental Information. Local Climatological Data v2. Via the Energy Research Warehouse (ERW), table `noaa_region_station_hourly_2026`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: noaa:<USAF-WBAN>, the station (the node of noaa_region_stations) | none | text | for example noaa:720306-53879, noaa:720307-63804, noaa:720308-04992; 215 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-01-01T00:00:00Z to 2026-11-07T14:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -20.92 to 165.2; 2053 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD). Here: noaa:lcd_v2 (Local Climatological Data v2) in every row | none | text | noaa:lcd_v2 | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `temperature_f` | The station's temperature in the hour, degrees F; runs of at most three missing hours between two measured hours are interpolated on a straight line | degF | 1577028 | 2026-01-01T00:00:00Z | 2026-11-07T14:00:00Z |

### `noaa_region_stations`

One county chosen for one EIA region's weather, with its weight in the region and the NOAA station that stands for it.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 271.

- **Time:** ts_utc is 2025-07-01, the date of the population estimates the weights are built from; freq is not filled.
- **Revisions:** A snapshot written whole by each run of the connector; not in the daily run. vintage is not filled.
- **Source:** erw:noaa_region_stations the ERW's choice of counties and stations (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/region_weather.md)
- **Method note:** [`docs/methods/region_weather.md`](../methods/region_weather.md)
- **Cite as:** Energy Research Warehouse. Counties and stations of EIA's regions. Via the Energy Research Warehouse (ERW), table `noaa_region_stations`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: census:county:<FIPS>, the county, not a station | none | text | for example census:county:01003, census:county:01073, census:county:01077; 271 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-07-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.00954195 to 0.56292315; 271 distinct | 0 |
| `unit` | The unit of the row's value | none | text | ratio | 0 |
| `freq` | How long the interval of the row is. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 271 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 271 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 271 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The county's station as NOAA's USAF-WBAN identifier, not a pricing node | none | text | for example 720306-53879, 720307-63804, 720308-04992; 216 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:noaa_region_stations | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/region_weather.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-18T02:52:15Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 271 |
| `x_region` | The EIA region the county is chosen for (CAL, CAR, CENT, FLA, MIDA, MIDW, NE, NW, NY, SE, SW, TEN), its primary region in eia_county_region | none | text | CAL, CAR, CENT, FLA, MIDA, MIDW, NE, NW, NY, SE, SW, TEN, TEX | 0 |
| `x_county` | The county's name | none | text | for example Ada County, Adams County, Alamance County; 233 distinct | 0 |
| `x_population_2025` | The county's population, the Census Bureau's estimate of 1 July 2025 (census_county_population) | count | integer | 80175 to 9694934; 271 distinct | 0 |
| `x_station_name` | The station's name as NOAA's isd-history.csv gives it | none | text | for example ADAMS FIELD AIRPORT, ALBANY INTERNATIONAL AIRPORT, ALBERT J ELLIS AIRPORT; 215 distinct | 0 |
| `x_km` | The distance from the county's 2020 center of population to the station | km | number | 0.3 to 79.1; 172 distinct | 0 |
| `x_lst_offset` | The station's local standard time offset from UTC in hours (-5 to -8), read from the data: the offset under which ISD-Lite and the Local Climatological Data agree in the most hours of July 2025 | hour | integer | -5, -6, -7, -8 | 0 |
| `x_lcd_agreement_jul2025` | The share of July 2025's hours held by both products in which they agree to a tenth of a degree C under that offset | ratio | number | 0.977, 0.992, 0.993, 0.996, 0.997, 0.999, 1.0 | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `station_weight` | The county's population over the population of its region's chosen counties (ratio); a station chosen by several counties carries their sum | ratio | 271 | 2025-07-01T00:00:00Z | 2025-07-01T00:00:00Z |

### `noaa_station_weather_hourly`

The temperature or dew point measured at one of the 35 NOAA airport stations behind the grids' weighted weather, for one hour, 2019 to now.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 4781257.

- **Time:** ts_utc is the hour in UTC; the reading is the one taken in the ten minutes up to it.
- **Revisions:** Each run deletes the table and writes it whole, cut to the hours from 1 January 2019 to the last hour every station reaches; with --refresh the later answer's hours replace the held ones. vintage is not filled.
- **Source:** noaa:isd_lite NOAA National Centers for Environmental Information, Integrated Surface Database, ISD-Lite (https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database)
- **Source:** noaa:lcd_v2 NOAA National Centers for Environmental Information, Local Climatological Data version 2 (https://www.ncei.noaa.gov/products/land-based-station/local-climatological-data)
- **Method note:** [`docs/methods/noaa_station_weather_hourly.md`](../methods/noaa_station_weather_hourly.md)
- **Cite as:** NOAA National Centers for Environmental Information. ISD-Lite (Integrated Surface Database, hourly); Local Climatological Data v2. Via the Energy Research Warehouse (ERW), table `noaa_station_weather_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: noaa:<GHCN identifier> (USW000 and the WBAN) | none | text | for example noaa:USW00003102, noaa:USW00003927, noaa:USW00003928; 35 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-11-07T14:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -36.94 to 116.96; 387 distinct | 0 |
| `unit` | The unit of the row's value | none | text | degF | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> of the station | none | text | US-CA, US-CT, US-IL, US-IN, US-KS, US-MA, US-MD, US-MI, US-MN, US-MO, US-NE, US-NY, US-OK, US-PA, US-RI, US-TX, US-VA, US-WI | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 4781257 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The station's airport code (DFW, LAX and the others), not a pricing node | none | text | for example ALB, AUS, BDL; 35 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | noaa:isd_lite, noaa:lcd_v2 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2019/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2020/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2021/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2022/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2023/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2024/, https://noaa-isd-pds.s3.amazonaws.com/isd-lite/data/2025/, https://www.ncei.noaa.gov/access/services/data/v1?dataset=local-climatological-data-v2 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-16T18:05:35Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 4781257 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48). Here: The EIA-930 code of the grid the station stands for | none | text | ciso, erco, isne, miso, nyis, pjm, swpp | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dew_point_f` | The measured dew point, degrees F (NOAA's tenths of a degree C times 9/5 plus 32, to two decimals); measured values only | degF | 2390431 | 2019-01-01T00:00:00Z | 2026-11-07T14:00:00Z |
| `temperature_f` | The measured temperature, degrees F (NOAA's tenths of a degree C times 9/5 plus 32, to two decimals); an hour with no measured value has no row, nothing interpolated | degF | 2390826 | 2019-01-01T00:00:00Z | 2026-11-07T14:00:00Z |

### `noaa_uscrn_solar_monthly`

The month's average daily total global solar radiation at one of eight U.S. Climate Reference Network (USCRN) stations near CAISO's and ERCOT's solar fleets.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 2025.

- **Time:** ts_utc is the month's first day at 00:00:00Z; NOAA's months are local standard time.
- **Revisions:** A snapshot written whole by each run. A month NOAA writes -9999.0 has no row. vintage is the station file's Last-Modified.
- **Source:** noaa:uscrn_monthly01 National Oceanic and Atmospheric Administration, National Centers for Environmental Information, U.S. Climate Reference Network, monthly01 product (https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/)
- **Method note:** [`docs/methods/noaa_uscrn_solar_monthly.md`](../methods/noaa_uscrn_solar_monthly.md)
- **Cite as:** NOAA NCEI. U.S. Climate Reference Network (USCRN), monthly01 product: SOLRAD_MONTHLY_AVG. Via the Energy Research Warehouse (ERW), table `noaa_uscrn_solar_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: uscrn:<WBAN number> | none | text | uscrn:03047, uscrn:03072, uscrn:04222, uscrn:12987, uscrn:23907, uscrn:53139, uscrn:53151, uscrn:93243 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2003-04-01T00:00:00Z to 2026-09-01T00:00:00Z; 282 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 3.5 to 30.9; 263 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MJ/m2-day | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> of the station | none | text | US-CA, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 2025 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The station's name (CA Merced 23 WSW and the others), not a pricing node | none | text | CA Fallbrook 5 NE, CA Merced 23 WSW, CA Redding 12 WNW, CA Stovepipe Wells 1 SW, TX Austin 33 NW, TX Bronte 11 NNE, TX Edinburg 17 NNE, TX Monahans 6 ENE | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | noaa:uscrn_monthly01 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/CRNM0102-CA_Fallbrook_5_NE.txt, https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/CRNM0102-CA_Merced_23_WSW.txt, https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/CRNM0102-CA_Redding_12_WNW.txt, https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/CRNM0102-CA_Stovepipe_Wells_1_SW.txt, https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/CRNM0102-TX_Austin_33_NW.txt, https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/CRNM0102-TX_Bronte_11_NNE.txt, https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/CRNM0102-TX_Edinburg_17_NNE.txt, https://www.ncei.noaa.gov/pub/data/uscrn/products/monthly01/CRNM0102-TX_Monahans_6_ENE.txt | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T21:31:00Z, 2026-10-23T21:31:01Z, 2026-10-23T21:31:02Z, 2026-10-23T21:31:03Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Last-Modified of NOAA's station file | none | utc time | 2026-10-02T10:36:54Z, 2026-10-02T10:36:57Z | 0 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48). Here: ciso or erco, the grid the station sits in | none | text | ciso, erco | 0 |
| `x_station` | The station's name as NOAA's file writes it (CA_Merced_23_WSW and the others) | none | text | CA_Fallbrook_5_NE, CA_Merced_23_WSW, CA_Redding_12_WNW, CA_Stovepipe_Wells_1_SW, TX_Austin_33_NW, TX_Bronte_11_NNE, TX_Edinburg_17_NNE, TX_Monahans_6_ENE | 0 |
| `x_lat` | The station's latitude (WGS-84), as NOAA's file gives it | degree | number | 26.5258, 30.6222, 31.6219, 32.0408, 33.4392, 36.6020, 37.2381, 40.6507 | 0 |
| `x_lon` | The station's longitude (WGS-84), as NOAA's file gives it | degree | number | -100.2495, -102.8071, -117.1449, -117.1904, -120.8825, -122.6068, -98.0633, -98.0846 | 0 |
| `x_logger` | The version of the station's datalogger program at the month's end | none | number | 1.001, 1.100, 1.201, 1.301, 1.302, 2.302, 2.402, 2.403, 2.412, 2.413, 2.422, 2.423, 2.622, 2.623 | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `solar_radiation` | The month's average daily total global solar radiation, NOAA's SOLRAD_MONTHLY_AVG, MJ per square meter a day | MJ/m2-day | 2025 | 2003-04-01T00:00:00Z | 2026-09-01T00:00:00Z |

