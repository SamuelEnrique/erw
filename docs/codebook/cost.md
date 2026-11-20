# Codebook: cost

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 3 public tables (3 series; tiers: 3 derived); 3 documented in full.

- [`cost_of_power_carbon`](#cost_of_power_carbon): One ISO hub's load-weighted real-time price, or its balancing authority's carbon intensity, over one local month.
- [`cost_of_power_hourly_profile`](#cost_of_power_hourly_profile): One ISO hub's average real-time price at one local hour of the day in one local month, or the number of hours averaged.
- [`cost_of_power_monthly`](#cost_of_power_monthly): One ISO hub's value of one cost-of-power measure (load-weighted or simple mean price, shape premium, hours) for one market over one local month.

### `cost_of_power_carbon`

One ISO hub's load-weighted real-time price, or its balancing authority's carbon intensity, over one local month.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 1393.

- **Time:** ts_utc is the first day of the ISO's local month at 00:00:00Z (freq P1M): ERCOT and SPP America/Chicago, CAISO America/Los_Angeles, NYISO and ISO-NE America/New_York, MISO EST.
- **Revisions:** Rebuilt by each run of the builder; months the rolling input tables no longer reach are carried over from the previous file (header). vintage is not filled.
- **Source:** erw:cost_of_power ERW derived table, cost-of-power method (docs/methods/cost_of_power.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/cost_of_power.md)
- **Method note:** [`docs/methods/cost_of_power.md`](../methods/cost_of_power.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Cost of power, market-based: load-weighted wholesale prices, hour-of-day profiles and carbon (docs/methods/cost_of_power.md). Via the Energy Research Warehouse (ERW), table `cost_of_power_carbon`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: <iso>:<hub or zone> (the price board's main hubs, with CAISO NP15 and ERCOT's LZ_HOUSTON and LZ_NORTH) | none | text | caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, ercot:HB_HUBAVG, ercot:LZ_HOUSTON, ercot:LZ_NORTH, isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, nyiso:N.Y.C., spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-01T00:00:00Z to 2026-11-01T00:00:00Z; 101 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 6.0625 to 1789.4565; 943 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, kgCO2/MWh | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: <iso>_rtm: every figure is over the real-time hours | none | text | caiso_rtm, ercot_rtm, isone_rtm, miso_rtm, nyiso_rtm, spp_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | .H.INTERNAL_HUB, HB_HUBAVG, INDIANA.HUB, LZ_HOUSTON, LZ_NORTH, N.Y.C., SPPNORTH_HUB, TH_NP15_GEN-APND, TH_SP15_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:cost_of_power | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/cost_of_power.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:56:14Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1393 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48) | none | text | ciso, erco, isne, miso, nyis, swpp | 0 |

Variables (3):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `intensity_demand` | kg of CO2 per MWh of demand: EIA's CO2 emissions consumed times 1000 over demand, over the month's real-time hours | kgCO2/MWh | 421 | 2018-07-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `intensity_generation` | kg of CO2 per MWh generated: EIA's CO2 emissions generated times 1000 over net generation, over the month's real-time hours | kgCO2/MWh | 480 | 2018-07-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_load_weighted` | Real-time price weighted by the balancing authority's demand: the sum of each hour's price times demand over the sum of demand | USD/MWh | 492 | 2018-07-01T00:00:00Z | 2026-11-01T00:00:00Z |

### `cost_of_power_hourly_profile`

One ISO hub's average real-time price at one local hour of the day in one local month, or the number of hours averaged.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 5808.

- **Time:** ts_utc is the first day of the ISO's local month at 00:00:00Z (freq P1M); the last 12 local months each hub holds with demand.
- **Revisions:** Rebuilt by each run of the builder; months the rolling input tables no longer reach are carried over from the previous file (header). vintage is not filled.
- **Source:** erw:cost_of_power ERW derived table, cost-of-power method (docs/methods/cost_of_power.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/cost_of_power.md)
- **Method note:** [`docs/methods/cost_of_power.md`](../methods/cost_of_power.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Cost of power, market-based: load-weighted wholesale prices, hour-of-day profiles and carbon (docs/methods/cost_of_power.md). Via the Energy Research Warehouse (ERW), table `cost_of_power_hourly_profile`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: <iso>:<hub or zone> (the price board's main hubs, with CAISO NP15 and ERCOT's LZ_HOUSTON and LZ_NORTH) | none | text | caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, ercot:HB_HUBAVG, ercot:LZ_HOUSTON, ercot:LZ_NORTH, isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, nyiso:N.Y.C., spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-10-01T00:00:00Z, 2025-11-01T00:00:00Z, 2025-12-01T00:00:00Z, 2026-01-01T00:00:00Z, 2026-02-01T00:00:00Z, 2026-03-01T00:00:00Z, 2026-04-01T00:00:00Z, 2026-05-01T00:00:00Z, 2026-06-01T00:00:00Z, 2026-07-01T00:00:00Z, 2026-08-01T00:00:00Z, 2026-09-01T00:00:00Z, 2026-10-01T00:00:00Z, 2026-11-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -12.0239 to 494.775; 2914 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: <iso>_rtm: every figure is of the real-time price | none | text | caiso_rtm, ercot_rtm, isone_rtm, miso_rtm, nyiso_rtm, spp_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | .H.INTERNAL_HUB, HB_HUBAVG, INDIANA.HUB, LZ_HOUSTON, LZ_NORTH, N.Y.C., SPPNORTH_HUB, TH_NP15_GEN-APND, TH_SP15_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:cost_of_power | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/cost_of_power.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T12:23:36Z, 2026-10-04T02:26:12Z, 2026-11-19T17:56:14Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 5808 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48) | none | text | ciso, erco, isne, miso, nyis, swpp | 0 |

Variables (48):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `rt_days_h00` | The hours averaged in rt_mean_h00 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h01` | The hours averaged in rt_mean_h01 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h02` | The hours averaged in rt_mean_h02 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h03` | The hours averaged in rt_mean_h03 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h04` | The hours averaged in rt_mean_h04 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h05` | The hours averaged in rt_mean_h05 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h06` | The hours averaged in rt_mean_h06 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h07` | The hours averaged in rt_mean_h07 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h08` | The hours averaged in rt_mean_h08 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h09` | The hours averaged in rt_mean_h09 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h10` | The hours averaged in rt_mean_h10 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h11` | The hours averaged in rt_mean_h11 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h12` | The hours averaged in rt_mean_h12 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h13` | The hours averaged in rt_mean_h13 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h14` | The hours averaged in rt_mean_h14 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h15` | The hours averaged in rt_mean_h15 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h16` | The hours averaged in rt_mean_h16 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h17` | The hours averaged in rt_mean_h17 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h18` | The hours averaged in rt_mean_h18 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h19` | The hours averaged in rt_mean_h19 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h20` | The hours averaged in rt_mean_h20 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h21` | The hours averaged in rt_mean_h21 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h22` | The hours averaged in rt_mean_h22 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_days_h23` | The hours averaged in rt_mean_h23 (one a day) | count | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h00` | Average real-time price of the month's complete price hours starting at local hour 00 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h01` | Average real-time price of the month's complete price hours starting at local hour 01 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h02` | Average real-time price of the month's complete price hours starting at local hour 02 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h03` | Average real-time price of the month's complete price hours starting at local hour 03 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h04` | Average real-time price of the month's complete price hours starting at local hour 04 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h05` | Average real-time price of the month's complete price hours starting at local hour 05 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h06` | Average real-time price of the month's complete price hours starting at local hour 06 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h07` | Average real-time price of the month's complete price hours starting at local hour 07 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h08` | Average real-time price of the month's complete price hours starting at local hour 08 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h09` | Average real-time price of the month's complete price hours starting at local hour 09 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h10` | Average real-time price of the month's complete price hours starting at local hour 10 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h11` | Average real-time price of the month's complete price hours starting at local hour 11 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h12` | Average real-time price of the month's complete price hours starting at local hour 12 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h13` | Average real-time price of the month's complete price hours starting at local hour 13 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h14` | Average real-time price of the month's complete price hours starting at local hour 14 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h15` | Average real-time price of the month's complete price hours starting at local hour 15 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h16` | Average real-time price of the month's complete price hours starting at local hour 16 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h17` | Average real-time price of the month's complete price hours starting at local hour 17 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h18` | Average real-time price of the month's complete price hours starting at local hour 18 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h19` | Average real-time price of the month's complete price hours starting at local hour 19 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h20` | Average real-time price of the month's complete price hours starting at local hour 20 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h21` | Average real-time price of the month's complete price hours starting at local hour 21 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h22` | Average real-time price of the month's complete price hours starting at local hour 22 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_mean_h23` | Average real-time price of the month's complete price hours starting at local hour 23 | USD/MWh | 121 | 2025-10-01T00:00:00Z | 2026-11-01T00:00:00Z |

### `cost_of_power_monthly`

One ISO hub's value of one cost-of-power measure (load-weighted or simple mean price, shape premium, hours) for one market over one local month.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 4428.

- **Time:** ts_utc is the first day of the ISO's local month at 00:00:00Z (freq P1M): ERCOT and SPP America/Chicago, CAISO America/Los_Angeles, NYISO and ISO-NE America/New_York, MISO EST.
- **Revisions:** Rebuilt by each run of the builder; months the rolling input tables no longer reach are carried over from the previous file (header). vintage is not filled.
- **Source:** erw:cost_of_power ERW derived table, cost-of-power method (docs/methods/cost_of_power.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/cost_of_power.md)
- **Method note:** [`docs/methods/cost_of_power.md`](../methods/cost_of_power.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Cost of power, market-based: load-weighted wholesale prices, hour-of-day profiles and carbon (docs/methods/cost_of_power.md). Via the Energy Research Warehouse (ERW), table `cost_of_power_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: <iso>:<hub or zone> (the price board's main hubs, with CAISO NP15 and ERCOT's LZ_HOUSTON and LZ_NORTH) | none | text | caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, ercot:HB_HUBAVG, ercot:LZ_HOUSTON, ercot:LZ_NORTH, isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, nyiso:N.Y.C., spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-07-01T00:00:00Z to 2026-11-01T00:00:00Z; 101 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -0.9461 to 1789.4565; 2963 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: <iso>_dam on day-ahead rows, <iso>_rtm on real-time rows; empty on the hours_in_month rows, which belong to neither | none | text | caiso_dam, caiso_rtm, ercot_dam, ercot_rtm, isone_dam, isone_rtm, miso_dam, miso_rtm, nyiso_dam, nyiso_rtm, spp_dam, spp_rtm | 492 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | .H.INTERNAL_HUB, HB_HUBAVG, INDIANA.HUB, LZ_HOUSTON, LZ_NORTH, N.Y.C., SPPNORTH_HUB, TH_NP15_GEN-APND, TH_SP15_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:cost_of_power | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/cost_of_power.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-19T17:56:14Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 4428 |
| `ba` | The balancing authority (the grid operator of an area) in EIA's code, lowercase (ciso, erco, us48) | none | text | ciso, erco, isne, miso, nyis, swpp | 0 |

Variables (9):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `da_hours` | Day-ahead hours counted in the month | count | 492 | 2018-07-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `da_load_weighted` | Day-ahead price weighted by the balancing authority's demand: the sum of each hour's price times demand over the sum of demand | USD/MWh | 492 | 2018-07-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `da_shape_premium` | Day-ahead load-weighted price less the simple mean (each rounded to 4 decimals first) | USD/MWh | 492 | 2018-07-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `da_simple_mean` | The simple mean of the same day-ahead hours | USD/MWh | 492 | 2018-07-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `hours_in_month` | The hours of the local month (a month is complete when rt_hours equals it) | count | 492 | 2018-07-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_hours` | Real-time hours counted in the month | count | 492 | 2018-07-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_load_weighted` | Real-time price weighted by the balancing authority's demand: the sum of each hour's price times demand over the sum of demand | USD/MWh | 492 | 2018-07-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_shape_premium` | Real-time load-weighted price less the simple mean (each rounded to 4 decimals first) | USD/MWh | 492 | 2018-07-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `rt_simple_mean` | The simple mean of the same real-time hours | USD/MWh | 492 | 2018-07-01T00:00:00Z | 2026-11-01T00:00:00Z |

