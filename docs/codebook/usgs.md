# Codebook: usgs

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 3 public tables (1 events, 2 series; tiers: 3 source); 0 documented in full.

- [`usgs_comcat_earthquakes_south_central`](#usgs_comcat_earthquakes_south_central): USGS ComCat earthquakes of magnitude 2.5 and above, 2010-01-01 to 2026-10-23 (not included), in the bounding box of Oklahoma, Kansas, Texas and New Mexico (session 2120)
- [`usgs_mcs_critical_minerals`](#usgs_mcs_critical_minerals): U.S. Geological Survey, Mineral Commodity Summaries 2026: the minerals of the energy transition (lithium, cobalt, nickel, graphite, copper, the rare earths, aluminum, gallium, germanium, indium, manganese, the platinum-group metals, silicon, tellurium, vanadium), U.S. salient statistics, import sources and world mine production and reserves by country (session 954)
- [`usgs_streamflow_daily`](#usgs_streamflow_daily): U.S. Geological Survey, NWIS daily values, the daily mean discharge at 8 gauges below large hydropower plants, 2015-01-01 to 2026-10-22 (session 2113)

### `usgs_comcat_earthquakes_south_central`

What a row is: not yet written.

Shape: events. Keys: `event_id`. License: public; tier: source. Rows read on 2026-11-20: 16000.

- **Source:** usgs:comcat U.S. Geological Survey (USGS) Earthquake Hazards Program, ANSS Comprehensive Earthquake Catalog (ComCat), FDSN event web service (https://earthquake.usgs.gov/fdsnws/event/1/)
- **Method note:** [`docs/methods/usgs_comcat_earthquakes_south_central.md`](../methods/usgs_comcat_earthquakes_south_central.md)
- **Cite as:** U.S. Geological Survey (USGS), Earthquake Hazards Program. ANSS Comprehensive Earthquake Catalog (ComCat), FDSN event web service. Via the Energy Research Warehouse (ERW), table `usgs_comcat_earthquakes_south_central`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `event_id` | The identifier of the event, as namespace:native_id or a stable hash the connector documents | none | text | for example usgs_comcat:ismpkansas70019608, usgs_comcat:ismpkansas70019833, usgs_comcat:ismpkansas70020388; more than 5000 distinct | 0 |
| `event_date` | The date the event happened or was announced (each table's file says which) | none | utc time | 2010-01-01T18:45:51Z to 2026-10-22T05:48:51Z; more than 5000 distinct | 0 |
| `event_type` | What kind of event the row is (ppa, interconnection_request, filing, announcement, acquisition, financing and others) | none | text | earthquake | 0 |
| `parties` | The parties to the event, as the publisher names them, separated by semicolons | none | empty | no cell holds a value | 16000 |
| `entity_ids` | The entity_id values of the things involved, separated by semicolons | none | empty | no cell holds a value | 16000 |
| `mw` | The capacity involved, in megawatts | MW | empty | no cell holds a value | 16000 |
| `price` | The price, in the row's currency per MWh unless the table's file says otherwise | the row's currency per MWh, unless the table's file says otherwise | empty | no cell holds a value | 16000 |
| `currency` | The currency of the price, as an ISO 4217 code (USD) | none | empty | no cell holds a value | 16000 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended) | none | text | automatic, reviewed | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | usgs:comcat | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://earthquake.usgs.gov/fdsnws/event/1/query?format=csv&eventtype=earthquake&orderby=time-asc&starttime=2010-01-01&endtime=2026-10-23&minmagnitude=2.5&minlatitude=25.8&maxlatitude=40.0&minlongitude=-109.06&maxlongitude=-93.5 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T22:27:51Z | 0 |
| `x_time_utc` | not yet written |  | text | for example 2010-01-01T18:45:51.600Z, 2010-01-11T05:16:00.070Z, 2010-01-14T10:05:34.150Z; more than 5000 distinct | 0 |
| `x_latitude` | not yet written |  | number | 25.8001 to 39.9889; more than 5000 distinct | 0 |
| `x_longitude` | not yet written |  | number | -109.0587 to -93.5339; more than 5000 distinct | 0 |
| `x_depth_km` | not yet written |  | number | -1.25 to 56.21; more than 5000 distinct | 0 |
| `x_magnitude` | not yet written |  | number | 2.5 to 5.8; 153 distinct | 0 |
| `x_magnitude_type` | not yet written |  | text | mb, mb_lg, mblg, md, ml, ml(texnet), mlg, mlv, mw, mwc, mwr, mww | 0 |
| `x_place` | not yet written |  | text | for example 0 km E of Azle, Texas, 0 km E of Choctaw, Oklahoma, 0 km E of Coyle, Oklahoma; more than 5000 distinct | 0 |
| `x_place_state` | not yet written |  | text | Arizona, Arkansas, Colorado, Kansas, Louisiana, Mexico, Missouri, Nebraska, New Mexico, Oklahoma, Texas, Utah | 5 |
| `x_net` | not yet written |  | text | ismpkansas, nm, ok, tx, us, uu | 0 |
| `x_location_source` | not yet written |  | text | ceri, ismp, ismpkansas, nm, ok, spec, tul, tx, unm, us, us_tul, uu | 0 |
| `x_magnitude_source` | not yet written |  | text | gcmt, ismp, ismpkansas, nc, nm, ok, slm, tul, tx, unm, us, us_tul, us_unm, uu | 0 |
| `x_stations` | not yet written |  | integer | 4 to 474; 115 distinct | 10278 |
| `x_gap_degrees` | not yet written |  | number | 13.0 to 315.7684326; 716 distinct | 626 |
| `x_horizontal_error_km` | not yet written |  | number | 0.0 to 11.6; 4053 distinct | 2629 |
| `x_depth_error_km` | not yet written |  | number | 0.0 to 31.61; 4291 distinct | 714 |
| `x_magnitude_error` | not yet written |  | number | 0.0 to 1.0; 259 distinct | 8456 |
| `x_updated_utc` | not yet written |  | text | for example 2013-09-25T17:45:52.000Z, 2013-10-12T21:32:31.000Z, 2013-10-12T21:32:32.000Z; more than 5000 distinct | 0 |

### `usgs_mcs_critical_minerals`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 1600.

- **Source:** usgs:mcs_2026_data U.S. Geological Survey, 2026, Mineral Commodity Summaries 2026 Data Release, Commodity Salient U.S. and World Statistics; Mineral commodity summaries 2026 (https://www.sciencebase.gov/catalog/item/69837e43b66b01367d7ec7c7)
- **Method note:** [`docs/methods/usgs_mcs_critical_minerals.md`](../methods/usgs_mcs_critical_minerals.md)
- **Cite as:** U.S. Geological Survey (USGS). Mineral Commodity Summaries 2026 Data Release, Commodity Salient U.S. and World Statistics. Via the Energy Research Warehouse (ERW), table `usgs_mcs_critical_minerals`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example usgs_mcs:aluminum:australia:smelter_production, usgs_mcs:aluminum:australia:yearend_capacity, usgs_mcs:aluminum:bahrain:all; 653 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.001 to 1700000000.0; 967 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/kg, USD/lb, USD/t, count, pct, t | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y, P4Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 663 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1600 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example Aluminum, Australia: Smelter production, Aluminum, Australia: Yearend capacity, Aluminum, Bahrain: All; 653 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | usgs:mcs_2026_data | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://www.sciencebase.gov/catalog/file/get/69837e43b66b01367d7ec7c7?f=__disk__d3%2Fac%2F84%2Fd3ac8466552946c5e8caa2c2c6338d9e1aff655d | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T12:33:41Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-10-23T12:33:39Z | 0 |
| `x_chapter` | not yet written |  | text | ALUMINUM, COBALT, COPPER, GALLIUM, GERMANIUM, GRAPHITE (NATURAL), INDIUM, LITHIUM, MANGANESE, NICKEL, PLATINUM-GROUP METALS, RARE EARTHS, RARE EARTHS (Heavy), SILICON, TELLURIUM, VANADIUM | 0 |
| `x_section` | not yet written |  | text | Import Sources, Salient Statistics: United States, World Low-Purity Production and Production Capacity, World Mine Production (manganese content) and Reserves, World Mine Production and Reserves, World Mine and Refinery Production and Reserves, World Production, World Refinery Production and Capacity, World Smelter Production and Capacity | 0 |
| `x_commodity` | not yet written |  | text | for example Aluminum, Cerium, Cobalt; 35 distinct | 0 |
| `x_country` | not yet written |  | text | for example Argentina, Australia, Austria; 64 distinct | 0 |
| `x_statistic` | not yet written |  | text | Capacity, Consumption, Employment, Export, Import, Import sources 2021-2024, Net import reliance, Price, Production, Reserves, Shipment, Stock, Supply | 0 |
| `x_detail` | not yet written |  | text | for example All, Combined total, Consumption (includes secondary): Apparent; 226 distinct | 0 |
| `x_usgs_unit` | not yet written |  | text | cents per pound, dollars per kilogram, dollars per metric ton, dollars per pound, dollars per troy ounce, kilograms, metric tons, number, percent, thousand metric tons | 0 |
| `x_notes` | not yet written |  | text | for example Alumina and aluminum production workers (North American Industry Classification System: 3313). Source: U.S. Department of Labor, Bureau of Labor Statistics., Average European price for minimum 99.999% purity. Source: Argus Media group, Argus Non-Ferrous Markets., Chinese annual average V2O5 prices (98% V2O5 content). Source Argus Media, Argus Non-Ferrous Markets.; 151 distinct | 471 |
| `x_critical_2025` | not yet written |  | text | No, Yes | 0 |

Variables (13):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capacity` |  | t | 50 | 2024-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `consumption` |  | t | 106 | 2021-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `employment` |  | count | 25 | 2021-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `export` |  | t | 165 | 2021-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `import` |  | t | 196 | 2021-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `import_share` |  | pct | 146 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `net_import_reliance` |  | pct | 62 | 2021-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `price` |  | USD/kg; USD/lb; USD/t | 216 | 2021-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `production` |  | t | 465 | 2021-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `reserves` |  | t | 98 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `shipment` |  | t | 3 | 2021-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `stock` |  | t | 63 | 2021-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `supply` |  | t | 5 | 2021-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `usgs_streamflow_daily`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 33421.

- **Source:** usgs:nwis_daily_values U.S. Geological Survey, National Water Information System, daily values service (https://waterservices.usgs.gov/nwis/dv/)
- **Method note:** [`docs/methods/usgs_streamflow_daily.md`](../methods/usgs_streamflow_daily.md)
- **Cite as:** U.S. Geological Survey (USGS). National Water Information System, daily values (discharge, daily mean). Via the Energy Research Warehouse (ERW), table `usgs_streamflow_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | usgs_gauge:06342500, usgs_gauge:09380000, usgs_gauge:09421500, usgs_gauge:11370500, usgs_gauge:11407000, usgs_gauge:12436500, usgs_gauge:13290450, usgs_gauge:14105700 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-10-22T00:00:00Z; 4313 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 505.0 to 513000.0; 2545 distinct | 0 |
| `unit` | The unit of the row's value | none | text | ft3/s | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AZ, US-CA, US-ND, US-OR, US-WA | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 33421 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | COLORADO RIVER AT LEES FERRY, AZ, COLORADO RV BLW HOOVER DAM, AZ-NV, COLUMBIA RIVER AT GRAND COULEE, WA, COLUMBIA RIVER AT THE DALLES, OR, FEATHER R A OROVILLE CA, MISSOURI RIVER AT BISMARCK, ND, SACRAMENTO R A KESWICK CA, SNAKE RIVER AT HELLS CANYON DAM ID-OR STATE LINE | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | usgs:nwis_daily_values | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=06342500&parameterCd=00060&statCd=00003&startDT=2015-01-01, https://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=09380000&parameterCd=00060&statCd=00003&startDT=2015-01-01, https://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=09421500&parameterCd=00060&statCd=00003&startDT=2015-01-01, https://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=11370500&parameterCd=00060&statCd=00003&startDT=2015-01-01, https://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=11407000&parameterCd=00060&statCd=00003&startDT=2015-01-01, https://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=12436500&parameterCd=00060&statCd=00003&startDT=2015-01-01, https://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=13290450&parameterCd=00060&statCd=00003&startDT=2015-01-01, https://waterservices.usgs.gov/nwis/dv/?format=rdb&sites=14105700&parameterCd=00060&statCd=00003&startDT=2015-01-01 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-23T22:37:20Z, 2026-10-23T22:38:16Z, 2026-10-23T22:38:18Z, 2026-10-23T22:38:20Z, 2026-10-23T22:38:23Z, 2026-10-23T22:38:25Z, 2026-10-23T22:38:27Z, 2026-10-23T22:38:29Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 33421 |
| `x_site` | not yet written |  | integer | 06342500, 09380000, 09421500, 11370500, 11407000, 12436500, 13290450, 14105700 | 0 |
| `x_plant` | not yet written |  | text | Garrison, Glen Canyon, Grand Coulee, Hells Canyon, Hoover, Oroville, Shasta, The Dalles | 0 |
| `x_qual` | not yet written |  | text | A, A:R, A:e, P, P:e | 0 |

Variables (1):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `discharge` |  | ft3/s | 33421 | 2015-01-01T00:00:00Z | 2026-10-22T00:00:00Z |

