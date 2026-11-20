# Codebook: afdc

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 3 public tables (3 series; tiers: 3 source); 3 documented in full.

- [`afdc_ev_charging_state_annual`](#afdc_ev_charging_state_annual): One state's count of public and private (non-residential) electric vehicle charging stations or ports, in total or by charging level, near the end of December of one year, 2014 to 2025, from AFDC's historical station counts.
- [`afdc_station_counts_annual`](#afdc_station_counts_annual): One state's (or the United States') count of alternative fueling stations of one fuel, or of EV charging locations or ports, near the end of December of one year, 2007 to 2025, from AFDC's historical station counts.
- [`afdc_vehicle_registrations_annual`](#afdc_vehicle_registrations_annual): One state's (or the United States') count of light-duty vehicles registered of one fuel type in one year, 2016 to 2025, from AFDC's Vehicle Registration Counts by State.

### `afdc_ev_charging_state_annual`

One state's count of public and private (non-residential) electric vehicle charging stations or ports, in total or by charging level, near the end of December of one year, 2014 to 2025, from AFDC's historical station counts.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3060.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z; the count was taken near the end of that year's December; freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot); vintage is the workbook's Last-Modified time.
- **Source:** afdc:historical_station_counts U.S. Department of Energy, Alternative Fuels Data Center, Historical Alternative Fueling Station Counts (https://afdc.energy.gov/stations/states)
- **Method note:** [`docs/methods/afdc_ev_charging_state_annual.md`](../methods/afdc_ev_charging_state_annual.md)
- **Cite as:** U.S. Department of Energy (DOE). Historical Alternative Fueling Station Counts (EV charging stations and ports by state). Via the Energy Research Warehouse (ERW), table `afdc_ev_charging_state_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: afdc_ev:<state postal code, lower case> | none | text | for example afdc_ev:ak, afdc_ev:al, afdc_ev:ar; 51 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 74599.0; 1341 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state> | none | text | for example US-AK, US-AL, US-AR; 51 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 3060 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The state's name, not a pricing node | none | text | for example Alabama, Alaska, Arizona; 51 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | afdc:historical_station_counts | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://afdc.energy.gov/files/docs/historical-station-counts.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T00:01:46Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's Last-Modified time | none | utc time | 2026-06-23T22:12:10Z | 0 |
| `x_counted_at` | AFDC's words for when the count was taken (near the end of December <year>) | none | text | near the end of December 2014, near the end of December 2015, near the end of December 2016, near the end of December 2017, near the end of December 2018, near the end of December 2019, near the end of December 2020, near the end of December 2021, near the end of December 2022, near the end of December 2023, near the end of December 2024, near the end of December 2025 | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `ev_dcfast_ports` | DC fast charging ports, count | count | 612 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_level1_ports` | Level 1 charging ports, count | count | 612 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_level2_ports` | Level 2 charging ports, count | count | 612 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_ports` | EV charging ports in the state, count (from 2021 an outlet is a port; before, a connector) | count | 612 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_stations` | EV charging stations in the state, count | count | 612 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `afdc_station_counts_annual`

One state's (or the United States') count of alternative fueling stations of one fuel, or of EV charging locations or ports, near the end of December of one year, 2007 to 2025, from AFDC's historical station counts.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 13520.

- **Time:** ts_utc is 1 January of the year at 00:00:00Z; the count is as of late December of that year; freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot); vintage is the workbook's Last-Modified time.
- **Source:** doe:afdc_station_counts DOE, Alternative Fuels Data Center, Historical Station Counts, https://afdc.energy.gov/files/docs/historical-station-counts.xlsx (linked from (https://afdc.energy.gov/stations/states)
- **Method note:** [`docs/methods/afdc_station_counts_annual.md`](../methods/afdc_station_counts_annual.md)
- **Cite as:** U.S. Department of Energy (DOE). Alternative Fuels Data Center: Historical Alternative Fueling Station Counts. Via the Energy Research Warehouse (ERW), table `afdc_station_counts_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: afdc_st:<state code>, or afdc_st:US for each sheet's own Total row | none | text | for example afdc_st:AK, afdc_st:AL, afdc_st:AR; 52 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 0 to 284265; 1845 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US on the Total row | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 13520 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The sheet's column as printed (Electric: Level 2), not a pricing node | none | text | Biodiesel, CNG, E85, Electric, Electric: DC Fast, Electric: Level 1, Electric: Level 2, Electric: charging outlets, Electric: stations, Hydrogen, Hydrogen: non-retail, Hydrogen: retail, Hydrogen: total, LNG, Propane, Propane: primary, Propane: secondary, Propane: total, Renewable Diesel, Total, Totald | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | doe:afdc_station_counts | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://afdc.energy.gov/files/docs/historical-station-counts.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T00:06:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: The workbook's Last-Modified time | none | utc time | 2026-06-23T22:12:10Z | 0 |
| `x_layout` | The form of the year's sheet: 2007_2013 (one number a fuel) or 2014_on (levels and designations under Electric, Hydrogen and Propane) | none | text | 2007_2013, 2014_on | 0 |

Variables (17):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `ev_locations` | EV charging locations (unique physical places), count (2007 to 2010, and from 2014) | count | 832 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_ports` | EV charging ports (outlets), count (2011 to 2013, and from 2014) | count | 780 | 2011-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_ports_dc_fast` | DC fast EV charging ports, count (from 2014) | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_ports_level1` | Level 1 EV charging ports, count (from 2014) | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_ports_level2` | Level 2 EV charging ports, count (from 2014) | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_biodiesel` | Biodiesel stations, count | count | 988 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_cng` | Compressed natural gas (CNG) stations, count | count | 988 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_e85` | E85 (ethanol blend) stations, count | count | 988 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_hydrogen` | Hydrogen stations, total, count | count | 988 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_hydrogen_non_retail` | Hydrogen stations under AFDC's non-retail designation, count (from 2014) | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_hydrogen_retail` | Hydrogen stations under AFDC's retail designation, count (from 2014) | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_lng` | Liquefied natural gas (LNG) stations, count | count | 988 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_propane` | Propane stations, total, count | count | 988 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_propane_primary` | Propane stations under AFDC's primary designation, count (from 2014) | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_propane_secondary` | Propane stations under AFDC's secondary designation, count (from 2014) | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_renewable_diesel` | Renewable diesel stations, count (from 2014) | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_total` | All stations as AFDC totals them: a station counted once a fuel, electric by ports, count | count | 988 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

Waiting for a second look: stations_propane_primary, stations_propane_secondary, stations_hydrogen_retail, stations_hydrogen_non_retail: AFDC's designations are named but not defined in the header, method note or connector..

### `afdc_vehicle_registrations_annual`

One state's (or the United States') count of light-duty vehicles registered of one fuel type in one year, 2016 to 2025, from AFDC's Vehicle Registration Counts by State.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 6240.

- **Time:** ts_utc is the year's first day at 00:00:00Z; the count is the vehicles registered through the year's end; freq P1Y.
- **Revisions:** Rewritten whole by each run (a snapshot); vintage is not filled (the pages send no Last-Modified).
- **Source:** doe:afdc_vehicle_registrations U.S. Department of Energy, Alternative Fuels Data Center, Vehicle Registration Counts by State (https://afdc.energy.gov/vehicle-registration)
- **Method note:** [`docs/methods/afdc_vehicle_registrations_annual.md`](../methods/afdc_vehicle_registrations_annual.md)
- **Cite as:** U.S. Department of Energy (DOE). Alternative Fuels Data Center (AFDC): Vehicle Registration Counts by State. Via the Energy Research Warehouse (ERW), table `afdc_vehicle_registrations_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: afdc_reg:<state code>, or afdc_reg:US for the page's own United States row | none | text | for example afdc_reg:AK, afdc_reg:AL, afdc_reg:AR; 52 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 0 to 243320500; 2266 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: US-<state>, or US | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 6240 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH). Here: The page's column name (Electric (EV)), not a pricing node | none | text | Biodiesel, Compressed Natural Gas (CNG), Diesel, Electric (EV), Ethanol/Flex (E85), Gasoline, Hybrid Electric (HEV), Hydrogen, Methanol, Plug-In Hybrid Electric (PHEV), Propane, Unknown Fuel | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | doe:afdc_vehicle_registrations | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://afdc.energy.gov/vehicle-registration?year=2016, https://afdc.energy.gov/vehicle-registration?year=2017, https://afdc.energy.gov/vehicle-registration?year=2018, https://afdc.energy.gov/vehicle-registration?year=2019, https://afdc.energy.gov/vehicle-registration?year=2020, https://afdc.energy.gov/vehicle-registration?year=2021, https://afdc.energy.gov/vehicle-registration?year=2022, https://afdc.energy.gov/vehicle-registration?year=2023, https://afdc.energy.gov/vehicle-registration?year=2024, https://afdc.energy.gov/vehicle-registration?year=2025 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T19:49:21Z, 2026-10-23T19:49:23Z, 2026-10-23T19:49:24Z, 2026-10-23T19:49:25Z, 2026-10-23T19:49:27Z, 2026-10-23T19:49:28Z, 2026-10-23T19:49:29Z, 2026-10-23T19:49:30Z, 2026-10-23T19:49:32Z, 2026-10-23T19:49:33Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: Not filled: the pages send no Last-Modified | none | empty | no cell holds a value | 6240 |

Variables (12):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `registrations_biodiesel` | Biodiesel vehicles registered, count (rounded to the closest 100) | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_cng` | Compressed natural gas (CNG) vehicles registered, count (rounded to the closest 100) | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_diesel` | Diesel vehicles registered, count (rounded to the closest 100) | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_e85` | Ethanol flex-fuel (E85) vehicles registered, count (rounded to the closest 100) | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_ev` | Battery electric (EV) light-duty vehicles registered, count (rounded to the closest 100) | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_gasoline` | Gasoline vehicles registered, count (rounded to the closest 100) | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_hev` | Hybrid electric (HEV) vehicles registered, count (rounded to the closest 100) | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_hydrogen` | Hydrogen vehicles registered, count (rounded to the closest 100) | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_methanol` | Methanol vehicles registered, count (rounded to the closest 100) | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_phev` | Plug-in hybrid electric (PHEV) vehicles registered, count (rounded to the closest 100) | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_propane` | Propane vehicles registered, count (rounded to the closest 100) | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_unknown_fuel` | Vehicles of unknown fuel registered, count (rounded to the closest 100) | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

