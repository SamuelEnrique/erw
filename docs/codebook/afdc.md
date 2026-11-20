# Codebook: afdc

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 3 public tables (3 series; tiers: 3 source); 0 documented in full.

- [`afdc_ev_charging_state_annual`](#afdc_ev_charging_state_annual): U.S. Department of Energy, Alternative Fuels Data Center, historical station counts: public and private (non-residential) EV charging stations and ports by state, near the end of December, 2014 to 2025 (session 2155)
- [`afdc_station_counts_annual`](#afdc_station_counts_annual): U.S. Department of Energy, Alternative Fuels Data Center, historical alternative fueling station counts by state and fuel type, near the end of each December, 2007 to 2025 (session 2141)
- [`afdc_vehicle_registrations_annual`](#afdc_vehicle_registrations_annual): U.S. Department of Energy, Alternative Fuels Data Center (AFDC), Vehicle Registration Counts by State: light-duty vehicles registered by state and fuel type, 2016 to 2025 (session 2036)

### `afdc_ev_charging_state_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 3060.

- **Source:** afdc:historical_station_counts U.S. Department of Energy, Alternative Fuels Data Center, Historical Alternative Fueling Station Counts (https://afdc.energy.gov/stations/states)
- **Method note:** [`docs/methods/afdc_ev_charging_state_annual.md`](../methods/afdc_ev_charging_state_annual.md)
- **Cite as:** U.S. Department of Energy (DOE). Historical Alternative Fueling Station Counts (EV charging stations and ports by state). Via the Energy Research Warehouse (ERW), table `afdc_ev_charging_state_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example afdc_ev:ak, afdc_ev:al, afdc_ev:ar; 51 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.0 to 74599.0; 1341 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US-AK, US-AL, US-AR; 51 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 3060 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Alabama, Alaska, Arizona; 51 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | afdc:historical_station_counts | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://afdc.energy.gov/files/docs/historical-station-counts.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T00:01:46Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-06-23T22:12:10Z | 0 |
| `x_counted_at` | not yet written |  | text | near the end of December 2014, near the end of December 2015, near the end of December 2016, near the end of December 2017, near the end of December 2018, near the end of December 2019, near the end of December 2020, near the end of December 2021, near the end of December 2022, near the end of December 2023, near the end of December 2024, near the end of December 2025 | 0 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `ev_dcfast_ports` |  | count | 612 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_level1_ports` |  | count | 612 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_level2_ports` |  | count | 612 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_ports` |  | count | 612 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_stations` |  | count | 612 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `afdc_station_counts_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 13520.

- **Source:** doe:afdc_station_counts DOE, Alternative Fuels Data Center, Historical Station Counts,  (linked from (https://afdc.energy.gov/stations/states)
- **Method note:** [`docs/methods/afdc_station_counts_annual.md`](../methods/afdc_station_counts_annual.md)
- **Cite as:** U.S. Department of Energy (DOE). Alternative Fuels Data Center: Historical Alternative Fueling Station Counts. Via the Energy Research Warehouse (ERW), table `afdc_station_counts_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example afdc_st:AK, afdc_st:AL, afdc_st:AR; 52 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2007-01-01T00:00:00Z, 2008-01-01T00:00:00Z, 2009-01-01T00:00:00Z, 2010-01-01T00:00:00Z, 2011-01-01T00:00:00Z, 2012-01-01T00:00:00Z, 2013-01-01T00:00:00Z, 2014-01-01T00:00:00Z, 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 0 to 284265; 1845 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 13520 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | Biodiesel, CNG, E85, Electric, Electric: DC Fast, Electric: Level 1, Electric: Level 2, Electric: charging outlets, Electric: stations, Hydrogen, Hydrogen: non-retail, Hydrogen: retail, Hydrogen: total, LNG, Propane, Propane: primary, Propane: secondary, Propane: total, Renewable Diesel, Total, Totald | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | doe:afdc_station_counts | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://afdc.energy.gov/files/docs/historical-station-counts.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-24T00:06:25Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-06-23T22:12:10Z | 0 |
| `x_layout` | not yet written |  | text | 2007_2013, 2014_on | 0 |

Variables (17):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `ev_locations` |  | count | 832 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_ports` |  | count | 780 | 2011-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_ports_dc_fast` |  | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_ports_level1` |  | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `ev_ports_level2` |  | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_biodiesel` |  | count | 988 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_cng` |  | count | 988 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_e85` |  | count | 988 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_hydrogen` |  | count | 988 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_hydrogen_non_retail` |  | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_hydrogen_retail` |  | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_lng` |  | count | 988 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_propane` |  | count | 988 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_propane_primary` |  | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_propane_secondary` |  | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_renewable_diesel` |  | count | 624 | 2014-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `stations_total` |  | count | 988 | 2007-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `afdc_vehicle_registrations_annual`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 6240.

- **Source:** doe:afdc_vehicle_registrations U.S. Department of Energy, Alternative Fuels Data Center, Vehicle Registration Counts by State (https://afdc.energy.gov/vehicle-registration)
- **Method note:** [`docs/methods/afdc_vehicle_registrations_annual.md`](../methods/afdc_vehicle_registrations_annual.md)
- **Cite as:** U.S. Department of Energy (DOE). Alternative Fuels Data Center (AFDC): Vehicle Registration Counts by State. Via the Energy Research Warehouse (ERW), table `afdc_vehicle_registrations_annual`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example afdc_reg:AK, afdc_reg:AL, afdc_reg:AR; 52 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | integer | 0 to 243320500; 2266 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | for example US, US-AK, US-AL; 52 distinct | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 6240 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | Biodiesel, Compressed Natural Gas (CNG), Diesel, Electric (EV), Ethanol/Flex (E85), Gasoline, Hybrid Electric (HEV), Hydrogen, Methanol, Plug-In Hybrid Electric (PHEV), Propane, Unknown Fuel | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | doe:afdc_vehicle_registrations | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://afdc.energy.gov/vehicle-registration?year=2016, https://afdc.energy.gov/vehicle-registration?year=2017, https://afdc.energy.gov/vehicle-registration?year=2018, https://afdc.energy.gov/vehicle-registration?year=2019, https://afdc.energy.gov/vehicle-registration?year=2020, https://afdc.energy.gov/vehicle-registration?year=2021, https://afdc.energy.gov/vehicle-registration?year=2022, https://afdc.energy.gov/vehicle-registration?year=2023, https://afdc.energy.gov/vehicle-registration?year=2024, https://afdc.energy.gov/vehicle-registration?year=2025 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T19:49:21Z, 2026-10-23T19:49:23Z, 2026-10-23T19:49:24Z, 2026-10-23T19:49:25Z, 2026-10-23T19:49:27Z, 2026-10-23T19:49:28Z, 2026-10-23T19:49:29Z, 2026-10-23T19:49:30Z, 2026-10-23T19:49:32Z, 2026-10-23T19:49:33Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 6240 |

Variables (12):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `registrations_biodiesel` |  | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_cng` |  | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_diesel` |  | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_e85` |  | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_ev` |  | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_gasoline` |  | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_hev` |  | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_hydrogen` |  | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_methanol` |  | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_phev` |  | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_propane` |  | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `registrations_unknown_fuel` |  | count | 520 | 2016-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

