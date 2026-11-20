# Codebook: carbon

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 3 public tables (3 series; tiers: 3 derived); 3 documented in full.

- [`carbon_intensity_daily`](#carbon_intensity_daily): One balancing authority's carbon intensity of generation or of demand over one complete UTC day.
- [`carbon_intensity_hourly`](#carbon_intensity_hourly): One balancing authority's carbon intensity of generation or of demand in one hour.
- [`carbon_intensity_monthly`](#carbon_intensity_monthly): One balancing authority's value of one carbon intensity measure over one UTC month.

### `carbon_intensity_daily`

One balancing authority's carbon intensity of generation or of demand over one complete UTC day.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 47325.

- **Time:** ts_utc is the UTC day at 00:00:00Z (freq P1D); complete UTC days only.
- **Revisions:** Rewritten whole by each run of the builder; vintage is not filled.
- **Source:** erw:carbon_intensity ERW derived table, emissions method (docs/methods/emissions.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/emissions.md)
- **Method note:** [`docs/methods/emissions.md`](../methods/emissions.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. California's carbon intensity of generation from the join of 16 December 2025 (docs/methods/eia930_caiso_break.md); Carbon intensity per balancing authority (docs/methods/emissions.md). Via the Energy Research Warehouse (ERW), table `carbon_intensity_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:<BA>, the seven ISO balancing authorities and US48 | none | text | eia930:CISO, eia930:ERCO, eia930:ISNE, eia930:MISO, eia930:NYIS, eia930:PJM, eia930:SWPP, eia930:US48 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-02T00:00:00Z to 2026-11-12T00:00:00Z; 3056 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.1355 to 10001.5932; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kgCO2/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-DE,US-DC,US-IL,US-IN,US-KY,US-MD,US-MI,US-NJ,US-NC,US-OH,US-PA,US-TN,US-VA,US-WV, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 47325 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 47325 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:carbon_intensity, erw:carbon_intensity_caiso | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/eia930_caiso_break.md, https://github.com/SamuelEnrique/erw/blob/main/docs/methods/emissions.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-17T04:13:59Z, 2026-11-17T04:43:53Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 47325 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48) | none | text | ciso, erco, isne, miso, nyis, pjm, swpp, us48 | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `intensity_demand` | kg of CO2 per MWh of demand: EIA's CO2 emissions consumed (generated plus imported less exported) over EIA's demand, the day's CO2 over the day's MWh | kgCO2/MWh | 23668 | 2018-07-02T00:00:00Z | 2026-11-12T00:00:00Z |
| `intensity_generation` | kg of CO2 per MWh generated: EIA's CO2 emissions generated over EIA's net generation, the day's CO2 over the day's MWh (California from 2025-12-16T08:00Z over CAISO's own net generation) | kgCO2/MWh | 23657 | 2018-07-02T00:00:00Z | 2026-11-12T00:00:00Z |

### `carbon_intensity_hourly`

One balancing authority's carbon intensity of generation or of demand in one hour.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 1136248.

- **Time:** ts_utc is the hour's start, UTC (freq PT1H).
- **Revisions:** Rewritten whole by each run of the builder; vintage is not filled.
- **Source:** erw:carbon_intensity ERW derived table, emissions method (docs/methods/emissions.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/emissions.md)
- **Method note:** [`docs/methods/emissions.md`](../methods/emissions.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. California's carbon intensity of generation from the join of 16 December 2025 (docs/methods/eia930_caiso_break.md); Carbon intensity per balancing authority (docs/methods/emissions.md). Via the Energy Research Warehouse (ERW), table `carbon_intensity_hourly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:<BA>, the seven ISO balancing authorities and US48 | none | text | eia930:CISO, eia930:ERCO, eia930:ISNE, eia930:MISO, eia930:NYIS, eia930:PJM, eia930:SWPP, eia930:US48 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-02T00:00:00Z to 2026-11-12T23:00:00Z; more than 5000 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -22.096 to 137776.3078; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | kgCO2/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-DE,US-DC,US-IL,US-IN,US-KY,US-MD,US-MI,US-NJ,US-NC,US-OH,US-PA,US-TN,US-VA,US-WV, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 1136248 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 1136248 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:carbon_intensity, erw:carbon_intensity_caiso | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/eia930_caiso_break.md, https://github.com/SamuelEnrique/erw/blob/main/docs/methods/emissions.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-17T04:13:59Z, 2026-11-17T04:43:53Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1136248 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48) | none | text | ciso, erco, isne, miso, nyis, pjm, swpp, us48 | 0 |

Variables (2):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `intensity_demand` | kg of CO2 per MWh of demand: EIA's CO2 emissions consumed (generated plus imported less exported) over EIA's demand | kgCO2/MWh | 568211 | 2018-07-02T00:00:00Z | 2026-11-12T23:00:00Z |
| `intensity_generation` | kg of CO2 per MWh generated: EIA's CO2 emissions generated over EIA's net generation (California from 2025-12-16T08:00Z over CAISO's own net generation) | kgCO2/MWh | 568037 | 2018-07-02T00:00:00Z | 2026-11-12T23:00:00Z |

### `carbon_intensity_monthly`

One balancing authority's value of one carbon intensity measure over one UTC month.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 4380.

- **Time:** ts_utc is the first day of the UTC month at 00:00:00Z (freq P1M).
- **Revisions:** Rewritten whole by each run of the builder; vintage is not filled.
- **Source:** erw:carbon_intensity ERW derived table, emissions method (docs/methods/emissions.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/emissions.md)
- **Method note:** [`docs/methods/emissions.md`](../methods/emissions.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. California's carbon intensity of generation from the join of 16 December 2025 (docs/methods/eia930_caiso_break.md); Carbon intensity per balancing authority (docs/methods/emissions.md). Via the Energy Research Warehouse (ERW), table `carbon_intensity_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: eia930:<BA>, the seven ISO balancing authorities and US48 | none | text | eia930:CISO, eia930:ERCO, eia930:ISNE, eia930:MISO, eia930:NYIS, eia930:PJM, eia930:SWPP, eia930:US48 | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-01T00:00:00Z to 2026-11-01T00:00:00Z; 101 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 4.4718 to 744.0; 1530 distinct | 0 |
| `unit` | The unit of the row's value | none | text | count, kgCO2/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US, US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-DE,US-DC,US-IL,US-IN,US-KY,US-MD,US-MI,US-NJ,US-NC,US-OH,US-PA,US-TN,US-VA,US-WV, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 4380 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 4380 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:carbon_intensity, erw:carbon_intensity_caiso | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/eia930_caiso_break.md, https://github.com/SamuelEnrique/erw/blob/main/docs/methods/emissions.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-17T04:13:59Z, 2026-11-17T04:43:53Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 4380 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48) | none | text | ciso, erco, isne, miso, nyis, pjm, swpp, us48 | 0 |

Variables (6):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `intensity_demand` | kg of CO2 per MWh of demand over a UTC month whose every day is complete: the month's CO2 consumed over its demand | kgCO2/MWh | 644 | 2018-08-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `intensity_demand_hours_held` | Hours of the month with intensity_demand written (of 24 times its days, UTC) | count | 803 | 2018-07-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `intensity_demand_over_held_hours` | The month's CO2 consumed over its demand in the hours held, written where at least 90 percent of the month's hours are held | kgCO2/MWh | 755 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `intensity_generation` | kg of CO2 per MWh generated over a UTC month whose every day is complete: the month's CO2 generated over its net generation | kgCO2/MWh | 641 | 2018-08-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `intensity_generation_hours_held` | Hours of the month with intensity_generation written (of 24 times its days, UTC) | count | 792 | 2018-07-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `intensity_generation_over_held_hours` | The month's CO2 generated over its net generation in the hours held, written where at least 90 percent of the month's hours are held | kgCO2/MWh | 745 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |

