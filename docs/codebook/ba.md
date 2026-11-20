# Codebook: ba

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 3 public tables (1 entities, 2 series; tiers: 3 derived); 3 documented in full.

- [`ba_boundaries`](#ba_boundaries): One balancing authority area of the United States (and its Canadian neighbours) as a polygon of HIFLD's Control Areas layer, keyed to its EIA-930 code.
- [`ba_supply_monthly`](#ba_supply_monthly): One balancing authority's (or one of its ties to a neighbour's) value of one supply measure for one month, from 2019.
- [`ba_trade_partners`](#ba_trade_partners): One balancing authority's exchange with one trading partner in one Eastern year, or the authority's share of demand met by net imports in that year.

### `ba_boundaries`

One balancing authority area of the United States (and its Canadian neighbours) as a polygon of HIFLD's Control Areas layer, keyed to its EIA-930 code.

Shape: entities. Keys: `entity_id`. License: public; tier: derived. Rows read on 2026-11-20: 71.

- **Time:** No time column. vintage is HIFLD's SOURCEDATE of the polygon (a date); the table is a snapshot as read on its retrieved_at.
- **Revisions:** One row a polygon, rewritten whole by each run; vintage holds HIFLD's source date, so a redrawn polygon replaces the old.
- **Source:** hifld:control_areas Homeland Infrastructure Foundation-Level Data (HIFLD), Control Areas (ORNL, LANL, INL, NGA HSIP), as served by Penn State's PASDA:  in batches (sha256 7baf60e617f9d3364c9e49dea9f3bc8a1d4dc32c6bc0cf206cac1613145ec57d, saved at warehouse/raw/hifld_control_areas/20261119T103755Z/control_areas.geojson); EIA-861 Balancing_Authority files (warehouse/raw/eia861); EIA-930 reference tables (warehouse/raw/eia930_reference/20261116T152148Z/EIA930_Reference_Tables.xlsx) (https://mapservices.pasda.psu.edu/server/rest/services/pasda/HIFLD_FEMA/MapServer/26/query)
- **Method note:** [`docs/methods/ba_boundaries.md`](../methods/ba_boundaries.md)
- **Cite as:** Homeland Infrastructure Foundation-Level Data (HIFLD), served by Penn State PASDA. Control Areas (balancing authority areas), HIFLD open data layer, PASDA map service HIFLD_FEMA layer 26. Via the Energy Research Warehouse (ERW), table `ba_boundaries`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity_id` | The identifier of the thing, as namespace:native_id. Here: eia930:<code>, or hifld:control_area:<HIFLD ID> where EIA-861 pairs the ID with no EIA-930 code (4 polygons) | none | text | for example eia930:AEC, eia930:AECI, eia930:AVA; 71 distinct | 0 |
| `entity_type` | What kind of thing the row is (plant, generator, project, datacenter, utility, company and the others the standard lists) | none | text | balancing_authority | 0 |
| `name` | The thing's name, as the publisher writes it | none | text | for example ALCOA POWER GENERATING, INC. - YADKIN DIVISION, ARIZONA PUBLIC SERVICE COMPANY, ARLINGTON VALLEY, LLC - AVBA; 71 distinct | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX). Here: The ISO 3166-2 code of the authority's address state (HIFLD's STATE), not its whole area | none | text | for example CA-NB, US-AK, US-AL; 29 distinct | 0 |
| `lat` | Latitude, in decimal degrees (WGS84). Here: The polygon's centroid | degree | number | 21.4547 to 60.30734; 71 distinct | 0 |
| `lon` | Longitude, in decimal degrees (WGS84). Here: The polygon's centroid | degree | number | -157.96851 to -68.34041; 71 distinct | 0 |
| `capacity_mw` | Nameplate capacity, in megawatts, as the publisher states it | MW | empty | no cell holds a value | 71 |
| `status` | The thing's state in the ERW's own words (operating, planned, under_construction, retired, withdrawn, active, completed, suspended). Here: Not filled: no cell holds a value | none | empty | no cell holds a value | 71 |
| `status_date` | The date the status took effect, or was reported where the effective date is unknown | none | empty | no cell holds a value | 71 |
| `operator` | The operator or owner, as the publisher writes it | none | empty | no cell holds a value | 71 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | hifld:control_areas | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://mapservices.pasda.psu.edu/server/rest/services/pasda/HIFLD_FEMA/MapServer/26 | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T10:37:55Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC. Here: HIFLD's SOURCEDATE, a date (YYYY-MM-DD) | none | date | 2018-10-12, 2019-06-20, 2021-06-21 | 0 |
| `x_hifld_id` | HIFLD's ID of the control area, which is EIA's entity identifier of the authority (the source's name: ID) | none | integer | 1 to 59504; 71 distinct | 0 |
| `x_eia930_code` | The authority's EIA-930 code, paired with HIFLD's ID through EIA-861's Balancing_Authority files (the source's name: BA Code (EIA-930 reference tables)) | none | text | for example AEC, AECI, AVA; 70 distinct | 1: No EIA-930 code pairs with the ID (nothing is matched by name) |
| `x_eia930_name` | The authority's name in EIA-930's reference tables (the source's name: BA Name) | none | text | for example Alcoa Power Generating, Inc. - Yadkin Division, Arizona Public Service Company, Arlington Valley, LLC; 67 distinct | 4: No EIA-930 code pairs with the ID |
| `x_region` | EIA-930's region of the authority (CAL, TEX, MIDW and the others) (the source's name: Region/Country Code) | none | text | CAL, CAN, CAR, CENT, FLA, MIDA, MIDW, NE, NW, NY, SE, SW, TEN, TEX | 4: No EIA-930 code pairs with the ID |
| `x_area_km2` | The polygon's area on a sphere of radius 6,371.0088 km, before simplification | km2 | number | 8.0 to 1677182.9; 71 distinct | 0 |
| `x_parts` | The number of parts of the polygon | count | integer | 1 to 1326; 37 distinct | 0 |
| `x_vertices` | The number of vertices of the polygon as HIFLD serves it | count | integer | 4 to 305771; 71 distinct | 0 |
| `x_source_date` | HIFLD's source date of the polygon (the source's name: SOURCEDATE) | none | date | 2018-10-12, 2019-06-20, 2021-06-21 | 0 |
| `x_val_date` | HIFLD's validation date of the polygon (the source's name: VAL_DATE) | none | date | 2019-05-01, 2020-05-15, 2022-06-03 | 0 |
| `x_year` | The year of HIFLD's load figures (the source's name: YEAR) | none | integer | 2017, 2018, 2020 | 5: HIFLD's YEAR is not a year |
| `x_peak_load_mw` | The authority's peak load as HIFLD prints it (the source's name: PEAK_LOAD) | MW | number | 0.0 to 144530.0; 58 distinct | 6: HIFLD printed -999 or nothing |
| `x_total_cap_mw` | The authority's total capacity as HIFLD prints it (the source's name: TOTAL_CAP) | MW | number | 0.0 to 163030.0; 59 distinct | 7: HIFLD printed -999 or nothing |
| `x_raw_sha256` | The SHA-256 of the raw GeoJSON file the row was read from | none | text | 7baf60e617f9d3364c9e49dea9f3bc8a1d4dc32c6bc0cf206cac1613145ec57d | 0 |

### `ba_supply_monthly`

One balancing authority's (or one of its ties to a neighbour's) value of one supply measure for one month, from 2019.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 158503.

- **Time:** ts_utc is the first day of the month at 00:00:00Z; a month's days are EIA's Eastern days.
- **Revisions:** Rewritten whole by each run of the builder (run by hand); vintage is not filled.
- **Source:** erw:ba_supply ERW derived table, who supplies a grid (docs/methods/grid_network.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_network.md)
- **Method note:** [`docs/methods/ba_supply_monthly.md`](../methods/ba_supply_monthly.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Who supplies a grid: net imports by neighbour and month (docs/methods/grid_network.md). Via the Energy Research Warehouse (ERW), table `ba_supply_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:<BA> for a balancing authority's rows, eia930:<BA>-<NEIGHBOUR> for a tie's rows | none | text | for example eia930:AEC, eia930:AEC-MISO, eia930:AEC-SOCO; 473 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2019-01-01T00:00:00Z to 2026-09-01T00:00:00Z; 93 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -10805407.0 to 4165722983.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | empty | no cell holds a value | 158503 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 158503 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 158503 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:ba_supply | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/grid_network.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T23:03:48Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 158503 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48). Here: The balancing authority whose supply the row measures | none | text | for example aec, aeci, ava; 83 distinct | 0 |
| `x_to_ba` | The neighbour on the other side of the tie, EIA-930 code in lowercase | none | text | for example aec, aeci, aeso; 93 distinct | 63502: Empty on a balancing authority's own rows (not a tie) |

Variables (21):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `balance_all_days_mwh` | Demand less net generation over every day both are held | MWh | 651 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `balance_days` | The days demand and net generation are both held | count | 651 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `days_held` | Days counted: every regular neighbour reported and no pair-day was screened out | count | 7455 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `days_in_month` | The days of the month | count | 7455 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `days_left_out` | Days not counted (a neighbour missing or a pair-day screened out, or nothing reported) | count | 7455 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `demand_all_days_mwh` | Demand over every day it is held | MWh | 651 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `demand_mwh` | Demand over the share days | MWh | 648 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `neighbor_report_days` | The days the neighbour reported the tie | count | 29544 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `neighbor_report_mwh` | The same tie's flow by the neighbour's own report | MWh | 29544 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `net_import_balance_mwh` | Net imports as demand less net generation, over the share days (the seven ISOs only) | MWh | 648 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `net_import_balance_share_pct` | net_import_balance_mwh as a percent of demand over the share days | pct | 648 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `net_import_mwh` | Net imports over the tie in the month: positive when the neighbour supplied the authority (EIA's sign flipped) | MWh | 31620 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `net_import_pairs_mwh` | Net imports as the sum of the authority's reported ties (the headline measure) | MWh | 7067 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `net_import_pairs_share_pct` | net_import_pairs_mwh as a percent of demand over the share days | pct | 648 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `net_import_share_pct` | The tie's net imports as a percent of the authority's demand over the share days | pct | 4293 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `net_import_total_interchange_mwh` | Net imports as EIA's total interchange of the authority, sign turned | MWh | 6602 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `net_import_total_interchange_share_pct` | net_import_total_interchange_mwh as a percent of demand over the share days | pct | 608 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `share_days` | Held days whose demand is held: the days every share is taken over | count | 648 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `thin_month` | 1 when fewer than two thirds of the month's days are held, else 0 | count | 7455 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `total_interchange_all_days_mwh` | EIA's total interchange, sign turned, over every day it covers | MWh | 7106 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |
| `total_interchange_days` | The days EIA's total interchange covers | count | 7106 | 2019-01-01T00:00:00Z | 2026-09-01T00:00:00Z |

### `ba_trade_partners`

One balancing authority's exchange with one trading partner in one Eastern year, or the authority's share of demand met by net imports in that year.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 5987.

- **Time:** ts_utc is the first day of the Eastern year at 00:00:00Z.
- **Revisions:** Rewritten whole by each run of the builder; no vintage column.
- **Source:** erw:interchange_pairs ERW derived table (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/interchange_pairs.md)
- **Method note:** [`docs/methods/interchange_pairs.md`](../methods/interchange_pairs.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Who trades with whom: interchange by pair of balancing authorities and of regions, partners, events (docs/methods/interchange_pairs.md). Via the Energy Research Warehouse (ERW), table `ba_trade_partners`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:<BA>-<partner> for a partner row, from the authority's side; eia930:<BA> for the share of demand | none | text | for example eia930:AEC, eia930:AEC-MISO, eia930:AEC-SOCO; 406 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-01-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2024-01-01T00:00:00Z, 2025-01-01T00:00:00Z, 2026-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -427197192.0 to 445474028.0; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:interchange_pairs | 0 |
| `x_ba` | The balancing authority whose report the row is read from, EIA-930 code | none | text | for example AEC, AECI, AVA; 70 distinct | 0 |
| `x_partner` | The trading partner, EIA-930 code | none | text | for example AEC, AECI, AESO; 78 distinct | 487: Empty on the authority's share-of-demand rows |
| `x_rank_gross` | The partner's rank among the authority's partners in the year by gross exchange (1 the largest) | rank | integer | 1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 2, 3, 4, 5, 6, 7, 8, 9 | 487: Empty on the share-of-demand rows |
| `x_rank_net` | The partner's rank among the authority's partners in the year by net exchange, by size whichever direction (1 the largest) | rank | integer | 1, 10, 11, 12, 13, 14, 15, 16, 17, 18, 2, 3, 4, 5, 6, 7, 8, 9 | 487: Empty on the share-of-demand rows |
| `x_hours` | The hours the authority reported in the year | hour count | integer | 24 to 8784; 231 distinct | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `exchange_gross_mwh` | The sum of the absolute hourly flows with the partner, by the authority's own report | MWh | 2750 | 2018-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `net_import_mwh` | The same flows signed: positive when the authority received power | MWh | 2750 | 2018-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `net_import_share_of_demand_pct` | Total interchange with the sign turned, over demand in the hours both are held, percent (below zero a net exporter) | pct | 487 | 2018-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

