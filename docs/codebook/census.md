# Codebook: census

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 6 public tables (6 series; tiers: 6 source); 6 documented in full.

- [`census_bps_state_annual`](#census_bps_state_annual): One state's (or DC's) count or value of new housing authorized by building permits for one structure type in one year, the Census Bureau's estimates.
- [`census_c30_construction_monthly`](#census_c30_construction_monthly): The value of construction put in place in one month for one owner (private, public, state and local, federal) and type of construction, US.
- [`census_cbp_hosting_annual`](#census_cbp_hosting_annual): One state's establishments, employment or annual payroll in NAICS 518210 (data processing, hosting and related services) in one year, County Business Patterns.
- [`census_county_population`](#census_county_population): One county's population, the 2020 census count or the Census Bureau's estimate of 1 July of one year.
- [`census_metro_population`](#census_metro_population): One metropolitan statistical area's population, whole or its part in one state, at the 2020 estimates base or the estimate of 1 July 2025.
- [`census_qss_utilities_hosting_quarterly`](#census_qss_utilities_hosting_quarterly): One industry's (the utilities, NAICS 22, 2211, 2212, 2213, or data processing and hosting, 518) revenue or expenses figure in one quarter, the Quarterly Services Survey's 2024 benchmark.

### `census_bps_state_annual`

One state's (or DC's) count or value of new housing authorized by building permits for one structure type in one year, the Census Bureau's estimates.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 6732.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z (freq P1Y).
- **Revisions:** A snapshot, replaced whole by each run; vintage is each year's file's Last-Modified time.
- **Source:** census:bps_state_annual U.S. Census Bureau, Building Permits Survey, annual state files (https://www2.census.gov/econ/bps/State/)
- **Method note:** [`docs/methods/census_bps_state_annual.md`](../methods/census_bps_state_annual.md)
- **Cite as:** Census Bureau. Building Permits Survey: annual state files. Via the Energy Research Warehouse (ERW), table `census_bps_state_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: census_bps:<state postal code, lowercase> | none | text | for example census_bps:ak, census_bps:al, census_bps:ar; 51 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 46062625000.0; 4073 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 51 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 6732 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The state as the Bureau names it, not a pricing node | none | text | for example Alabama, Alaska, Arizona; 51 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | census:bps_state_annual | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www2.census.gov/econ/bps/State/st2015a.txt, https://www2.census.gov/econ/bps/State/st2016a.txt, https://www2.census.gov/econ/bps/State/st2017a.txt, https://www2.census.gov/econ/bps/State/st2018a.txt, https://www2.census.gov/econ/bps/State/st2019a.txt, https://www2.census.gov/econ/bps/State/st2020a.txt, https://www2.census.gov/econ/bps/State/st2021a.txt, https://www2.census.gov/econ/bps/State/st2022a.txt, https://www2.census.gov/econ/bps/State/st2023a.txt, https://www2.census.gov/econ/bps/State/st2024a.txt, https://www2.census.gov/econ/bps/State/st2025a.txt | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T23:53:30Z, 2026-10-23T23:54:24Z, 2026-10-23T23:55:39Z, 2026-10-23T23:55:42Z, 2026-10-23T23:55:44Z, 2026-10-23T23:55:46Z, 2026-10-23T23:55:48Z, 2026-10-23T23:55:50Z, 2026-10-23T23:55:52Z, 2026-10-23T23:55:54Z, 2026-10-23T23:55:56Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Last-Modified time of the year's file | none | utc time | 2016-09-30T13:17:03Z, 2017-05-01T12:06:07Z, 2018-05-01T11:26:06Z, 2019-06-20T12:29:57Z, 2020-05-01T15:09:42Z, 2021-05-03T11:37:40Z, 2022-04-27T21:02:59Z, 2024-04-23T19:28:45Z, 2025-05-01T12:10:36Z, 2025-09-18T15:15:30Z, 2026-05-14T13:30:25Z | 0 |
| `x_fips` | The state's FIPS code | none | integer | 1 to 56; 51 distinct | 0 |
| `x_code` | The code the year's file gives the state (areas are matched by it) | none | integer | 1 to 56; 51 distinct | 0 |

Variables (12):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `buildings_1_unit` | One-unit buildings authorized | count | 561 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `buildings_2_units` | Two-unit buildings authorized | count | 561 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `buildings_3_4_units` | Buildings of three or four units authorized | count | 561 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `buildings_5_plus_units` | Buildings of five or more units authorized | count | 561 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `units_1_unit` | Housing units authorized in one-unit buildings | count | 561 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `units_2_units` | Housing units authorized in two-unit buildings | count | 561 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `units_3_4_units` | Housing units authorized in buildings of three or four units | count | 561 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `units_5_plus_units` | Housing units authorized in buildings of five or more units | count | 561 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `value_1_unit` | Value of the one-unit buildings authorized, USD (the Bureau's thousands times 1,000) | USD | 561 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `value_2_units` | Value of the two-unit buildings authorized, USD (the Bureau's thousands times 1,000) | USD | 561 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `value_3_4_units` | Value of the buildings of three or four units authorized, USD (the Bureau's thousands times 1,000) | USD | 561 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `value_5_plus_units` | Value of the buildings of five or more units authorized, USD (the Bureau's thousands times 1,000) | USD | 561 | 2015-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `census_c30_construction_monthly`

The value of construction put in place in one month for one owner (private, public, state and local, federal) and type of construction, US.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 82760.

- **Time:** ts_utc is the month's first day at 00:00:00Z (freq P1M).
- **Revisions:** A snapshot, rewritten whole by each run (the Bureau revises recent months at each release); vintage is the workbook's Last-Modified time, and x_status marks the release's preliminary and revised months.
- **Source:** census:c30_construction_spending U.S. Census Bureau, Construction Spending, monthly time series (privsatime, privtime, pubsatime, pubtime) (https://www.census.gov/construction/c30/historical_data.html)
- **Method note:** [`docs/methods/census_c30_construction_monthly.md`](../methods/census_c30_construction_monthly.md)
- **Cite as:** U.S. Census Bureau. Construction Spending (C30), monthly time series by type. Via the Energy Research Warehouse (ERW), table `census_c30_construction_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: census_c30:<owner>:<type> | none | text | for example census_c30:federal:amusement_and_recreation, census_c30:federal:commercial, census_c30:federal:conservation_and_development; 110 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 1993-01-01T00:00:00Z to 2026-08-01T00:00:00Z; 404 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 1745310000000.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US on every row | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 82760 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The column as the Census Bureau names it (the same as x_column), not a pricing node | none | text | for example Air, Amusement and Recreation, Automotive; 110 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | census:c30_construction_spending | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.census.gov/construction/c30/xlsx/privsatime.xlsx, https://www.census.gov/construction/c30/xlsx/privtime.xlsx, https://www.census.gov/construction/c30/xlsx/pubsatime.xlsx, https://www.census.gov/construction/c30/xlsx/pubtime.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T04:17:06Z, 2026-10-24T04:17:09Z, 2026-10-24T04:17:14Z, 2026-10-24T04:17:38Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-01T14:00:31Z, 2026-10-01T14:01:56Z, 2026-10-01T14:02:13Z, 2026-10-01T15:28:41Z | 0 |
| `x_column` | The Census Bureau's column name of the construction type | none | text | for example Air, Amusement and Recreation, Automotive; 110 distinct | 0 |
| `x_status` | The release's mark: p preliminary, r revised | none | text | p, r | 82100: No mark in the release (the months before the newest three) |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `value_put_in_place` | Value of construction put in place in the month, not seasonally adjusted, USD (millions times 1,000,000) | USD | 41380 | 1993-01-01T00:00:00Z | 2026-08-01T00:00:00Z |
| `value_put_in_place_saar` | Value of construction put in place, seasonally adjusted annual rate, USD (millions times 1,000,000) | USD | 41380 | 1993-01-01T00:00:00Z | 2026-08-01T00:00:00Z |

### `census_cbp_hosting_annual`

One state's establishments, employment or annual payroll in NAICS 518210 (data processing, hosting and related services) in one year, County Business Patterns.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1836.

- **Time:** ts_utc is 1 January of the reference year at 00:00:00Z (freq P1Y).
- **Revisions:** A snapshot, replaced whole by each run; vintage is each year's file's Last-Modified time.
- **Source:** census:cbp_state_518210 U.S. Census Bureau, County Business Patterns, state files (https://www2.census.gov/programs-surveys/cbp/datasets/)
- **Method note:** [`docs/methods/census_cbp_hosting_annual.md`](../methods/census_cbp_hosting_annual.md)
- **Cite as:** Census Bureau. County Business Patterns: state files, NAICS 518210. Via the Energy Research Warehouse (ERW), table `census_cbp_hosting_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: census_cbp_518210:<state postal code, lowercase> | none | text | for example census_cbp_518210:ak, census_cbp_518210:al, census_cbp_518210:ar; 51 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 27301760000.0; 1536 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 51 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1836 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The state's postal code, not a pricing node | none | text | for example AK, AL, AR; 51 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | census:cbp_state_518210 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www2.census.gov/programs-surveys/cbp/datasets/2012/cbp12st.zip, https://www2.census.gov/programs-surveys/cbp/datasets/2013/cbp13st.zip, https://www2.census.gov/programs-surveys/cbp/datasets/2014/cbp14st.zip, https://www2.census.gov/programs-surveys/cbp/datasets/2015/cbp15st.zip, https://www2.census.gov/programs-surveys/cbp/datasets/2016/cbp16st.zip, https://www2.census.gov/programs-surveys/cbp/datasets/2017/cbp17st.zip, https://www2.census.gov/programs-surveys/cbp/datasets/2018/cbp18st.zip, https://www2.census.gov/programs-surveys/cbp/datasets/2019/cbp19st.zip, https://www2.census.gov/programs-surveys/cbp/datasets/2020/cbp20st.zip, https://www2.census.gov/programs-surveys/cbp/datasets/2021/cbp21st.zip, https://www2.census.gov/programs-surveys/cbp/datasets/2022/cbp22st.zip, https://www2.census.gov/programs-surveys/cbp/datasets/2023/cbp23st.zip | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T00:23:53Z, 2026-10-24T00:24:51Z, 2026-10-24T00:24:56Z, 2026-10-24T00:25:00Z, 2026-10-24T00:25:05Z, 2026-10-24T00:25:09Z, 2026-10-24T00:25:14Z, 2026-10-24T00:25:18Z, 2026-10-24T00:25:22Z, 2026-10-24T00:25:26Z, 2026-10-24T00:25:30Z, 2026-10-24T00:25:35Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2017-05-09T20:25:03Z, 2017-05-19T11:34:13Z, 2018-04-19T18:27:42Z, 2018-09-12T13:55:44Z, 2018-09-13T13:14:51Z, 2019-11-26T18:58:28Z, 2020-06-25T11:01:49Z, 2021-04-22T10:53:32Z, 2022-04-28T10:35:51Z, 2023-04-27T11:41:44Z, 2024-06-27T11:29:29Z, 2025-06-26T12:00:29Z | 0 |
| `x_emp_noise` | The Bureau's noise flag for employment: G low, H moderate, J high noise, N not available; D and S mark a figure the Bureau withholds, kept as a zero (the source's name: emp_nf) | none | text | D, G, H, J, S | 0 |
| `x_ap_noise` | The Bureau's noise flag for annual payroll: G low, H moderate, J high noise, N not available; D marks a figure the Bureau withholds, kept as a zero (the source's name: ap_nf) | none | text | D, G, H, J | 0 |
| `x_naics_vintage` | The NAICS edition the connector assigns the year: 2022 from 2022, else 2017 | none | integer | 2017, 2022 | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `annual_payroll` | Annual payroll, USD (the Bureau's thousands times 1,000; noise infused by the Bureau) | USD | 612 | 2012-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `employment` | Employment in the pay period including 12 March (noise infused by the Bureau) | count | 612 | 2012-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `establishments` | Establishments in the industry in the state | count | 612 | 2012-01-01T00:00:00Z | 2023-01-01T00:00:00Z |

### `census_county_population`

One county's population, the 2020 census count or the Census Bureau's estimate of 1 July of one year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 28293.

- **Time:** ts_utc is 2020-04-01 for population_census_2020 (freq empty) and 1 July of each year, 2018 to 2025, for population_estimate (freq P1Y), at 00:00:00Z.
- **Revisions:** Merged by key (entity, variable, ts_utc), a run's rows replacing earlier rows with the same key; vintage is not filled, and x_product names the Bureau's product.
- **Source:** census:popest/intercensal_county_2010_2020 2010-2020 Intercensal County Population Estimates (by age group and sex) (https://www.census.gov/data/datasets/time-series/demo/popest/intercensal-2010-2020-counties.html)
- **Source:** census:popest/co-est2025-alldata County Population Totals, Vintage 2025 (co-est2025-alldata.csv) (https://www.census.gov/data/datasets/time-series/demo/popest/2020s-counties-total.html)
- **Method note:** [`docs/methods/county_population_and_regions.md`](../methods/county_population_and_regions.md)
- **Cite as:** U.S. Census Bureau. 2010-2020 Intercensal County Population Estimates (by age group and sex); County Population Totals, Vintage 2025. Via the Energy Research Warehouse (ERW), table `census_county_population`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: census:county:<five-digit state and county FIPS>; Connecticut's planning regions and former counties each under their own code | none | text | for example census:county:01001, census:county:01003, census:county:01005; 3152 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-01T00:00:00Z, 2019-07-01T00:00:00Z, 2020-04-01T00:00:00Z, 2020-07-01T00:00:00Z, 2021-07-01T00:00:00Z, 2022-07-01T00:00:00Z, 2023-07-01T00:00:00Z, 2024-07-01T00:00:00Z, 2025-07-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 46 to 10098683; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is. Here: Empty on the population_census_2020 rows (a single count, not an interval) | none | text | P1Y | 3143 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 51 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 28293 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The Bureau's county name (CTYNAME), not a pricing node | none | text | for example Abbeville County, Acadia Parish, Accomack County; 1887 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | census:popest/co-est2025-alldata, census:popest/intercensal_county_2010_2020 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | for example https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/intercensal/county/asrh/cc-est2020int-agesex-01.csv, https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/intercensal/county/asrh/cc-est2020int-agesex-02.csv, https://www2.census.gov/programs-surveys/popest/datasets/2010-2020/intercensal/county/asrh/cc-est2020int-agesex-04.csv; 52 distinct | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-18T01:26:49Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 28293 |
| `x_state` | The state's name as the Bureau writes it (the source's name: STNAME) | none | text | for example Alabama, Alaska, Arizona; 51 distinct | 0 |
| `x_product` | The Bureau's file the row came from: intercensal 2010-2020 (2018, 2019 and the 2020 count) or vintage 2025 (2020 to 2025) | none | text | intercensal 2010-2020, vintage 2025 | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `population_census_2020` | The county's 2020 census count of 1 April 2020 (the Modified Age and Race Census file as the intercensal files print it) | count | 3143 | 2020-04-01T00:00:00Z | 2020-04-01T00:00:00Z |
| `population_estimate` | The Census Bureau's estimate of the county's population on 1 July of the year | count | 25150 | 2018-07-01T00:00:00Z | 2025-07-01T00:00:00Z |

### `census_metro_population`

One metropolitan statistical area's population, whole or its part in one state, at the 2020 estimates base or the estimate of 1 July 2025.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1650.

- **Time:** ts_utc is 2020-04-01 for population_base_2020 and 2025-07-01 for population_2025, at 00:00:00Z; freq empty.
- **Revisions:** Merged by key (entity, variable, ts_utc); vintage is the Bureau's vintage, 2025.
- **Source:** census:popest_cbsa U.S. Census Bureau, Population Estimates Program, Metropolitan and Micropolitan Statistical Areas Totals, vintage 2025 (https://www.census.gov/data/tables/time-series/demo/popest/2020s-total-metro-and-micro-statistical-areas.html)
- **Method note:** [`docs/methods/census_metro_population.md`](../methods/census_metro_population.md)
- **Cite as:** U.S. Census Bureau. Population Estimates Program, Metropolitan and Micropolitan Statistical Areas Totals (vintage 2025). Via the Energy Research Warehouse (ERW), table `census_metro_population`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: census:cbsa:<code> for a whole area; census:cbsa:<code>:<state FIPS> for its part in one state | none | text | for example census:cbsa:10180, census:cbsa:10180:48, census:cbsa:10420; 825 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2020-04-01T00:00:00Z, 2025-07-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 4570 to 20112448; 960 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is. Here: Empty on every row (two single dates) | none | empty | no cell holds a value | 1650 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1650 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The Bureau's name for the area, not a pricing node | none | text | for example Abilene, TX, Akron, OH, Albany, GA; 387 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | census:popest_cbsa | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www2.census.gov/programs-surveys/popest/datasets/2020-2025/metro/totals/cbsa-est2025-alldata.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-06T00:36:54Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The Population Estimates vintage, 2025 (a year, not a UTC time) | none | integer | 2025 | 0 |
| `x_state` | The state's FIPS code of a part by state | none | integer | 1 to 56; 51 distinct | 774: Empty on a whole area's rows |
| `x_counties` | How many of the area's counties lie in that state, as the file lists them (summed for the part) | count | integer | 1, 10, 11, 12, 13, 14, 15, 17, 2, 29, 3, 4, 5, 6, 7, 8, 9 | 774: Empty on a whole area's rows |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `population_2025` | The Bureau's population estimate, 1 July 2025 | count | 825 | 2025-07-01T00:00:00Z | 2025-07-01T00:00:00Z |
| `population_base_2020` | The Bureau's estimates base population, 1 April 2020 | count | 825 | 2020-04-01T00:00:00Z | 2020-04-01T00:00:00Z |

### `census_qss_utilities_hosting_quarterly`

One industry's (the utilities, NAICS 22, 2211, 2212, 2213, or data processing and hosting, 518) revenue or expenses figure in one quarter, the Quarterly Services Survey's 2024 benchmark.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 784.

- **Time:** ts_utc is the quarter's first day at 00:00:00Z (freq P3M).
- **Revisions:** A snapshot, replaced whole by each run; vintage is the benchmark file's Last-Modified time.
- **Source:** census:qss_benchmark U.S. Census Bureau, Quarterly Services Survey, Historical Annual Benchmark Dataset (2024) (https://www.census.gov/services/qss/benchmark.html)
- **Method note:** [`docs/methods/census_qss_utilities_hosting_quarterly.md`](../methods/census_qss_utilities_hosting_quarterly.md)
- **Cite as:** U.S. Census Bureau. Quarterly Services Survey, Historical Annual Benchmark Dataset (2024). Via the Energy Research Warehouse (ERW), table `census_qss_utilities_hosting_quarterly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: census_qss:<NAICS code> | none | text | census_qss:22, census_qss:2211, census_qss:2212, census_qss:2213, census_qss:518 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2003-10-01T00:00:00Z to 2024-10-01T00:00:00Z; 85 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 252000000.0 to 205605000000.0; 778 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD | 0 |
| `freq` | How long the interval of the row is | none | text | P3M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 784 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The category as the Census Bureau names it (code and title), not a pricing node | none | text | 2211: Electric Power Generation, Transmission and Distribution, 2212: Natural Gas Distribution, 2213: Water, Sewage and Other Systems, 22: Utilities, 518: Data Processing, Hosting, and Related Services | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | census:qss_benchmark | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www2.census.gov/services/qss/2024/qss-mf-24.csv | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T04:42:06Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2025-05-22T14:15:27Z | 0 |
| `x_cv` | The coefficient of variation QSS gives for the figure | pct | number | 1.6 to 29.8; 120 distinct | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `revenue_from_businesses` | Revenue from businesses, USD (millions times 1,000,000) | USD | 45 | 2003-10-01T00:00:00Z | 2017-07-01T00:00:00Z |
| `revenue_from_governments` | Revenue from governments, USD (millions times 1,000,000) | USD | 60 | 2003-10-01T00:00:00Z | 2021-07-01T00:00:00Z |
| `revenue_from_households` | Revenue from households, USD (millions times 1,000,000) | USD | 29 | 2003-10-01T00:00:00Z | 2022-04-01T00:00:00Z |
| `total_revenue` | Total revenue in the quarter, USD (millions times 1,000,000) | USD | 325 | 2003-10-01T00:00:00Z | 2024-10-01T00:00:00Z |
| `total_revenue_sa` | Total revenue in the quarter, seasonally adjusted, USD (millions times 1,000,000) | USD | 325 | 2003-10-01T00:00:00Z | 2024-10-01T00:00:00Z |

