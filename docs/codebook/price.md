# Codebook: price

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 4 public tables (4 series; tiers: 4 derived); 0 documented in full.

- [`price_board_latest`](#price_board_latest): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261106T003628Z-github (2026-11-06T00:36:28Z); that run's own header of the table follows
- [`price_board_peak_offpeak`](#price_board_peak_offpeak): Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261116T155131Z-github (2026-11-16T15:51:31Z); that run's own header of the table follows
- [`price_board_spreads`](#price_board_spreads): price board, spark spreads, implied heat rates, Henry Hub and Brent minus WTI, daily (derived)
- [`price_years_by_window`](#price_years_by_window): the price years, each economics page's figure under every window of years held (derived, session 357)

### `price_board_latest`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 3250.

- **Source:** erw:price_board ERW derived price board metrics (docs/methods/price_board.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/price_board.md)
- **Method note:** [`docs/methods/price_board.md`](../methods/price_board.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Price board v2 metrics (docs/methods/price_board.md). Via the Energy Research Warehouse (ERW), table `price_board_latest`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | for example caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, caiso:TH_ZP26_GEN-APND; 39 distinct | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2026-09-03T00:00:00Z to 2026-11-07T07:00:00Z; 75 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -65.3902 to 2784.0; 2679 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count, pct | 0 |
| `freq` | How long the interval of the row is | none | text | P1D, PT15M, PT1H | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_dam, caiso_rtm, ercot_dam, ercot_rtm, isone_dam, isone_rtm, miso_dam, miso_rtm, nyiso_dam, nyiso_rtm, spp_dam, spp_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | for example .H.INTERNAL_HUB, .Z.CONNECTICUT, .Z.MAINE; 39 distinct | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:price_board | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/price_board.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-29T10:35:16Z to 2026-11-05T23:44:58Z; 30 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 3250 |

Variables (27):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `da_avg_30d` |  | USD/MWh | 39 | 2026-10-03T00:00:00Z | 2026-11-06T00:00:00Z |
| `da_avg_7d` |  | USD/MWh | 39 | 2026-10-03T00:00:00Z | 2026-11-06T00:00:00Z |
| `da_daily_mean` |  | USD/MWh | 1168 | 2026-09-04T00:00:00Z | 2026-11-06T00:00:00Z |
| `da_day_change` |  | USD/MWh | 39 | 2026-10-03T00:00:00Z | 2026-11-06T00:00:00Z |
| `da_day_change_pct` |  | pct | 39 | 2026-10-03T00:00:00Z | 2026-11-06T00:00:00Z |
| `da_days_30d` |  | count | 39 | 2026-10-03T00:00:00Z | 2026-11-06T00:00:00Z |
| `da_days_7d` |  | count | 39 | 2026-10-03T00:00:00Z | 2026-11-06T00:00:00Z |
| `da_intervals_30d` |  | count | 39 | 2026-10-04T04:00:00Z | 2026-11-07T07:00:00Z |
| `da_latest_day_mean` |  | USD/MWh | 39 | 2026-10-03T00:00:00Z | 2026-11-06T00:00:00Z |
| `da_latest_interval` |  | USD/MWh | 39 | 2026-10-04T04:00:00Z | 2026-11-07T07:00:00Z |
| `da_max_30d` |  | USD/MWh | 39 | 2026-10-03T00:00:00Z | 2026-11-06T00:00:00Z |
| `da_min_30d` |  | USD/MWh | 39 | 2026-10-03T00:00:00Z | 2026-11-06T00:00:00Z |
| `da_minus_rt` |  | USD/MWh | 39 | 2026-10-02T00:00:00Z | 2026-11-04T00:00:00Z |
| `da_previous_day_mean` |  | USD/MWh | 39 | 2026-10-02T00:00:00Z | 2026-11-05T00:00:00Z |
| `rt_avg_30d` |  | USD/MWh | 39 | 2026-10-02T00:00:00Z | 2026-11-04T00:00:00Z |
| `rt_avg_7d` |  | USD/MWh | 39 | 2026-10-02T00:00:00Z | 2026-11-04T00:00:00Z |
| `rt_daily_mean` |  | USD/MWh | 1107 | 2026-09-03T00:00:00Z | 2026-11-04T00:00:00Z |
| `rt_day_change` |  | USD/MWh | 39 | 2026-10-02T00:00:00Z | 2026-11-04T00:00:00Z |
| `rt_day_change_pct` |  | pct | 39 | 2026-10-02T00:00:00Z | 2026-11-04T00:00:00Z |
| `rt_days_30d` |  | count | 39 | 2026-10-02T00:00:00Z | 2026-11-04T00:00:00Z |
| `rt_days_7d` |  | count | 39 | 2026-10-02T00:00:00Z | 2026-11-04T00:00:00Z |
| `rt_intervals_30d` |  | count | 39 | 2026-10-03T04:00:00Z | 2026-11-05T07:45:00Z |
| `rt_latest_day_mean` |  | USD/MWh | 39 | 2026-10-02T00:00:00Z | 2026-11-04T00:00:00Z |
| `rt_latest_interval` |  | USD/MWh | 39 | 2026-10-03T04:00:00Z | 2026-11-05T07:45:00Z |
| `rt_max_30d` |  | USD/MWh | 39 | 2026-10-02T00:00:00Z | 2026-11-04T00:00:00Z |
| `rt_min_30d` |  | USD/MWh | 39 | 2026-10-02T00:00:00Z | 2026-11-04T00:00:00Z |
| `rt_previous_day_mean` |  | USD/MWh | 39 | 2026-10-01T00:00:00Z | 2026-11-03T00:00:00Z |

### `price_board_peak_offpeak`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 5028.

- **Source:** erw:price_board ERW derived price board metrics (docs/methods/price_board.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/price_board.md)
- **Method note:** [`docs/methods/price_board.md`](../methods/price_board.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Price board v2 metrics (docs/methods/price_board.md). Via the Energy Research Warehouse (ERW), table `price_board_peak_offpeak`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:TH_SP15_GEN-APND, ercot:HB_HUBAVG, isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, nyiso:N.Y.C., spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z to 2026-11-16T00:00:00Z; 152 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -74.6751 to 877.6525; 3106 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1D, P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-NY, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_dam, caiso_rtm, ercot_dam, ercot_rtm, isone_dam, isone_rtm, miso_dam, miso_rtm, nyiso_dam, nyiso_rtm, spp_dam, spp_rtm | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | .H.INTERNAL_HUB, HB_HUBAVG, INDIANA.HUB, N.Y.C., SPPNORTH_HUB, TH_SP15_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:price_board | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/price_board.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-29T10:35:16Z to 2026-11-16T14:59:49Z; 36 distinct | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 5028 |

Variables (22):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `da_all_mean` |  | USD/MWh | 502 | 2026-07-02T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_offpeak_intervals` |  | count | 502 | 2026-07-02T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_offpeak_mean` |  | USD/MWh | 502 | 2026-07-02T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_peak_intervals` |  | count | 367 | 2026-07-02T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_peak_mean` |  | USD/MWh | 367 | 2026-07-02T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_peak_minus_offpeak` |  | USD/MWh | 367 | 2026-07-02T00:00:00Z | 2026-11-16T00:00:00Z |
| `da_year_all_mean` |  | USD/MWh | 12 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `da_year_days` |  | count | 12 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `da_year_offpeak_mean` |  | USD/MWh | 12 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `da_year_peak_mean` |  | USD/MWh | 12 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `da_year_peak_minus_offpeak` |  | USD/MWh | 12 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `rt_all_mean` |  | USD/MWh | 445 | 2026-06-30T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_offpeak_intervals` |  | count | 445 | 2026-06-30T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_offpeak_mean` |  | USD/MWh | 445 | 2026-06-30T00:00:00Z | 2026-11-15T00:00:00Z |
| `rt_peak_intervals` |  | count | 322 | 2026-06-30T00:00:00Z | 2026-11-14T00:00:00Z |
| `rt_peak_mean` |  | USD/MWh | 322 | 2026-06-30T00:00:00Z | 2026-11-14T00:00:00Z |
| `rt_peak_minus_offpeak` |  | USD/MWh | 322 | 2026-06-30T00:00:00Z | 2026-11-14T00:00:00Z |
| `rt_year_all_mean` |  | USD/MWh | 12 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `rt_year_days` |  | count | 12 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `rt_year_offpeak_mean` |  | USD/MWh | 12 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `rt_year_peak_mean` |  | USD/MWh | 12 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `rt_year_peak_minus_offpeak` |  | USD/MWh | 12 | 2015-01-01T00:00:00Z | 2026-01-01T00:00:00Z |

### `price_board_spreads`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 2812.

- **Source:** erw:price_board ERW derived price board metrics (docs/methods/price_board.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/price_board.md)
- **Method note:** [`docs/methods/price_board.md`](../methods/price_board.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. Price board v2 metrics (docs/methods/price_board.md). Via the Energy Research Warehouse (ERW), table `price_board_spreads`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:TH_SP15_GEN-APND, eia:henry_hub, ercot:HB_HUBAVG, erw:brent_minus_wti, isone:.H.INTERNAL_HUB, miso:INDIANA.HUB, nyiso:N.Y.C., spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-09-29T00:00:00Z to 2026-11-15T00:00:00Z; 413 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -176.6208 to 654.0325; 2641 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MMBtu/MWh, USD/MMBtu, USD/MWh, USD/bbl | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-AR,US-IL,US-IN,US-IA,US-KY,US-LA,US-MI,US-MN,US-MS,US-MO,US-MT,US-ND,US-SD,US-TX,US-WI, US-CA, US-CT,US-MA,US-ME,US-NH,US-RI,US-VT, US-LA, US-NY, US-TX | 246 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso_dam, ercot_dam, isone_dam, miso_dam, nyiso_dam, spp_dam | 493 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | .H.INTERNAL_HUB, HB_HUBAVG, INDIANA.HUB, N.Y.C., SPPNORTH_HUB, TH_SP15_GEN-APND | 493 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:price_board | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/price_board.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-09-29T10:35:16Z, 2026-11-16T14:59:49Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 2812 |
| `x_gas_date` | not yet written |  | text | for example 2025-09-29T00:00:00Z, 2025-09-30T00:00:00Z, 2025-10-01T00:00:00Z; 470 distinct | 246 |

Variables (5):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `brent_minus_wti` |  | USD/bbl | 246 | 2025-11-17T00:00:00Z | 2026-11-11T00:00:00Z |
| `da_daily_mean` |  | USD/MWh | 773 | 2025-09-29T00:00:00Z | 2026-11-15T00:00:00Z |
| `henry_hub` |  | USD/MMBtu | 247 | 2025-11-17T00:00:00Z | 2026-11-11T00:00:00Z |
| `implied_heat_rate` |  | MMBtu/MWh | 773 | 2025-09-29T00:00:00Z | 2026-11-15T00:00:00Z |
| `spark_spread_7` |  | USD/MWh | 773 | 2025-09-29T00:00:00Z | 2026-11-15T00:00:00Z |

### `price_years_by_window`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 2754.

- **Source:** erw:price_years ERW derived table, the price years (docs/methods/price_years.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/price_years.md)
- **Method note:** [`docs/methods/price_years.md`](../methods/price_years.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The price years, each economics page's figure under every window of years held (warehouse/derived/price_years.py). Via the Energy Research Warehouse (ERW), table `price_years_by_window`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | caiso:TH_NP15_GEN-APND, caiso:TH_SP15_GEN-APND, caiso:TH_ZP26_GEN-APND, ercot:HB_BUSAVG, ercot:HB_HOUSTON, ercot:HB_HUBAVG, ercot:HB_NORTH, ercot:HB_SOUTH, ercot:HB_WEST, ercot:LZ_AEN, ercot:LZ_CPS, ercot:LZ_HOUSTON, ercot:LZ_LCRA, ercot:LZ_NORTH, ercot:LZ_RAYBN, ercot:LZ_SOUTH, ercot:LZ_WEST, spp:SPPNORTH_HUB, spp:SPPSOUTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2015-01-01T00:00:00Z, 2016-01-01T00:00:00Z, 2017-01-01T00:00:00Z, 2018-01-01T00:00:00Z, 2018-07-01T00:00:00Z, 2019-01-01T00:00:00Z, 2020-01-01T00:00:00Z, 2021-01-01T00:00:00Z, 2022-01-01T00:00:00Z, 2023-01-01T00:00:00Z, 2023-07-01T00:00:00Z, 2023-08-01T00:00:00Z, 2024-01-01T00:00:00Z, 2024-09-01T00:00:00Z, 2025-01-01T00:00:00Z, 2025-10-01T00:00:00Z, 2025-11-01T00:00:00Z, 2026-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 6.014534 to 3440.997279; 2718 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MWh, USD/kW-year | 0 |
| `freq` | How long the interval of the row is | none | text | P106M, P10M, P12M, P142M, P25M, P26M, P36M, P39M, P40M, P4M, P5M, P6M, P84M, P94M, P9M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA, US-KS,US-NE,US-NM,US-OK,US-TX, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | text | caiso, ercot, spp | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | HB_BUSAVG, HB_HOUSTON, HB_HUBAVG, HB_NORTH, HB_SOUTH, HB_WEST, LZ_AEN, LZ_CPS, LZ_HOUSTON, LZ_LCRA, LZ_NORTH, LZ_RAYBN, LZ_SOUTH, LZ_WEST, SPPNORTH_HUB, SPPSOUTH_HUB, TH_NP15_GEN-APND, TH_SP15_GEN-APND, TH_ZP26_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:price_years | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/price_years.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-11-14T10:07:37Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 2754 |
| `x_tool` | not yet written |  | text | battery, datacenter, generator | 0 |
| `x_grid` | not yet written |  | text | caiso, ercot, spp | 0 |
| `x_config` | not yet written |  | text | battery, dayahead_2h, dayahead_4h, dayahead_8h, flat_da, flat_rt, foresight_2h, foresight_4h, foresight_8h, hours_da, hours_rt, peaker, share_da, share_rt, shift_da, shift_rt, solar, wind | 0 |
| `x_window` | not yet written |  | text | for example all, all_less_caiso_notices_20230815, all_less_caiso_notices_20230828; 30 distinct | 0 |
| `x_window_kind` | not yet written |  | text | all, all_less, avg_3y, avg_7y, last_12, year | 0 |
| `x_left_out` | not yet written |  | text | caiso_notices_20230815, caiso_notices_20230815+caiso_notices_20230828+caiso_notices_20240703+caiso_notices_20240715+caiso_notices_20240724+caiso_notices_20240805+caiso_notices_20240904+caiso_notices_20250120+caiso_notices_20260909+caiso_notices_20261005, caiso_notices_20230828, caiso_notices_20240703, caiso_notices_20240715, caiso_notices_20240724, caiso_notices_20240805, caiso_notices_20240904, caiso_notices_20250120, caiso_notices_20260909, caiso_notices_20261005, elliott_2022, elliott_2022+ercot_heat_2023+uri_2021, ercot_heat_2023, none, uri_2021, uri_2021+elliott_2022+ercot_heat_2023 | 0 |
| `x_from` | not yet written |  | text | 2015-01, 2016-01, 2017-01, 2018-01, 2018-07, 2019-01, 2020-01, 2021-01, 2022-01, 2023-01, 2023-07, 2023-08, 2024-01, 2024-09, 2025-01, 2025-10, 2025-11, 2026-01 | 0 |
| `x_to` | not yet written |  | text | 2015-12, 2016-12, 2017-12, 2018-12, 2019-12, 2020-12, 2021-12, 2022-12, 2023-12, 2024-12, 2025-12, 2026-09, 2026-10 | 0 |
| `x_months` | not yet written |  | integer | 10, 106, 12, 142, 25, 26, 36, 39, 4, 40, 5, 6, 84, 9, 94 | 0 |
| `x_complete` | not yet written |  | boolean | false, true | 0 |

Variables (470; the first 300 by name):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `battery_dayahead_2h_all` |  | USD/kW-year | 3 | 2018-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `battery_dayahead_2h_all_less_caiso_notices_20230815` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_2h_all_less_caiso_notices_20230828` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_2h_all_less_caiso_notices_20240703` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_2h_all_less_caiso_notices_20240715` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_2h_all_less_caiso_notices_20240724` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_2h_all_less_caiso_notices_20240805` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_2h_all_less_caiso_notices_20240904` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_2h_all_less_caiso_notices_20250120` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_2h_all_less_caiso_notices_20260909` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_2h_all_less_caiso_notices_20261005` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_2h_all_less_elliott_2022` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_dayahead_2h_all_less_ercot_heat_2023` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_dayahead_2h_all_less_events` |  | USD/kW-year | 2 | 2018-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_2h_all_less_uri_2021` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_dayahead_2h_avg_3y` |  | USD/kW-year | 1 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `battery_dayahead_2h_avg_7y` |  | USD/kW-year | 1 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `battery_dayahead_2h_last_12` |  | USD/kW-year | 3 | 2025-10-01T00:00:00Z | 2025-11-01T00:00:00Z |
| `battery_dayahead_2h_year_2018` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_dayahead_2h_year_2019` |  | USD/kW-year | 1 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `battery_dayahead_2h_year_2020` |  | USD/kW-year | 1 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `battery_dayahead_2h_year_2021` |  | USD/kW-year | 1 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `battery_dayahead_2h_year_2022` |  | USD/kW-year | 1 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `battery_dayahead_2h_year_2023` |  | USD/kW-year | 2 | 2023-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_2h_year_2024` |  | USD/kW-year | 3 | 2024-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `battery_dayahead_2h_year_2025` |  | USD/kW-year | 3 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `battery_dayahead_2h_year_2026` |  | USD/kW-year | 3 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `battery_dayahead_4h_all` |  | USD/kW-year | 3 | 2018-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `battery_dayahead_4h_all_less_caiso_notices_20230815` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_4h_all_less_caiso_notices_20230828` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_4h_all_less_caiso_notices_20240703` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_4h_all_less_caiso_notices_20240715` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_4h_all_less_caiso_notices_20240724` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_4h_all_less_caiso_notices_20240805` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_4h_all_less_caiso_notices_20240904` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_4h_all_less_caiso_notices_20250120` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_4h_all_less_caiso_notices_20260909` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_4h_all_less_caiso_notices_20261005` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_4h_all_less_elliott_2022` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_dayahead_4h_all_less_ercot_heat_2023` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_dayahead_4h_all_less_events` |  | USD/kW-year | 2 | 2018-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_4h_all_less_uri_2021` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_dayahead_4h_avg_3y` |  | USD/kW-year | 1 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `battery_dayahead_4h_avg_7y` |  | USD/kW-year | 1 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `battery_dayahead_4h_last_12` |  | USD/kW-year | 3 | 2025-10-01T00:00:00Z | 2025-11-01T00:00:00Z |
| `battery_dayahead_4h_year_2018` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_dayahead_4h_year_2019` |  | USD/kW-year | 1 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `battery_dayahead_4h_year_2020` |  | USD/kW-year | 1 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `battery_dayahead_4h_year_2021` |  | USD/kW-year | 1 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `battery_dayahead_4h_year_2022` |  | USD/kW-year | 1 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `battery_dayahead_4h_year_2023` |  | USD/kW-year | 2 | 2023-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_4h_year_2024` |  | USD/kW-year | 3 | 2024-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `battery_dayahead_4h_year_2025` |  | USD/kW-year | 3 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `battery_dayahead_4h_year_2026` |  | USD/kW-year | 3 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `battery_dayahead_8h_all` |  | USD/kW-year | 3 | 2018-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `battery_dayahead_8h_all_less_caiso_notices_20230815` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_8h_all_less_caiso_notices_20230828` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_8h_all_less_caiso_notices_20240703` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_8h_all_less_caiso_notices_20240715` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_8h_all_less_caiso_notices_20240724` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_8h_all_less_caiso_notices_20240805` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_8h_all_less_caiso_notices_20240904` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_8h_all_less_caiso_notices_20250120` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_8h_all_less_caiso_notices_20260909` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_8h_all_less_caiso_notices_20261005` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_8h_all_less_elliott_2022` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_dayahead_8h_all_less_ercot_heat_2023` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_dayahead_8h_all_less_events` |  | USD/kW-year | 2 | 2018-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_8h_all_less_uri_2021` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_dayahead_8h_avg_3y` |  | USD/kW-year | 1 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `battery_dayahead_8h_avg_7y` |  | USD/kW-year | 1 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `battery_dayahead_8h_last_12` |  | USD/kW-year | 3 | 2025-10-01T00:00:00Z | 2025-11-01T00:00:00Z |
| `battery_dayahead_8h_year_2018` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_dayahead_8h_year_2019` |  | USD/kW-year | 1 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `battery_dayahead_8h_year_2020` |  | USD/kW-year | 1 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `battery_dayahead_8h_year_2021` |  | USD/kW-year | 1 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `battery_dayahead_8h_year_2022` |  | USD/kW-year | 1 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `battery_dayahead_8h_year_2023` |  | USD/kW-year | 2 | 2023-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_dayahead_8h_year_2024` |  | USD/kW-year | 3 | 2024-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `battery_dayahead_8h_year_2025` |  | USD/kW-year | 3 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `battery_dayahead_8h_year_2026` |  | USD/kW-year | 3 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `battery_foresight_2h_all` |  | USD/kW-year | 3 | 2018-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `battery_foresight_2h_all_less_caiso_notices_20230815` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_2h_all_less_caiso_notices_20230828` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_2h_all_less_caiso_notices_20240703` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_2h_all_less_caiso_notices_20240715` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_2h_all_less_caiso_notices_20240724` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_2h_all_less_caiso_notices_20240805` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_2h_all_less_caiso_notices_20240904` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_2h_all_less_caiso_notices_20250120` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_2h_all_less_caiso_notices_20260909` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_2h_all_less_caiso_notices_20261005` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_2h_all_less_elliott_2022` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_foresight_2h_all_less_ercot_heat_2023` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_foresight_2h_all_less_events` |  | USD/kW-year | 2 | 2018-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_2h_all_less_uri_2021` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_foresight_2h_avg_3y` |  | USD/kW-year | 1 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `battery_foresight_2h_avg_7y` |  | USD/kW-year | 1 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `battery_foresight_2h_last_12` |  | USD/kW-year | 3 | 2025-10-01T00:00:00Z | 2025-11-01T00:00:00Z |
| `battery_foresight_2h_year_2018` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_foresight_2h_year_2019` |  | USD/kW-year | 1 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `battery_foresight_2h_year_2020` |  | USD/kW-year | 1 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `battery_foresight_2h_year_2021` |  | USD/kW-year | 1 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `battery_foresight_2h_year_2022` |  | USD/kW-year | 1 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `battery_foresight_2h_year_2023` |  | USD/kW-year | 2 | 2023-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_2h_year_2024` |  | USD/kW-year | 3 | 2024-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `battery_foresight_2h_year_2025` |  | USD/kW-year | 3 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `battery_foresight_2h_year_2026` |  | USD/kW-year | 3 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `battery_foresight_4h_all` |  | USD/kW-year | 3 | 2018-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `battery_foresight_4h_all_less_caiso_notices_20230815` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_4h_all_less_caiso_notices_20230828` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_4h_all_less_caiso_notices_20240703` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_4h_all_less_caiso_notices_20240715` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_4h_all_less_caiso_notices_20240724` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_4h_all_less_caiso_notices_20240805` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_4h_all_less_caiso_notices_20240904` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_4h_all_less_caiso_notices_20250120` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_4h_all_less_caiso_notices_20260909` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_4h_all_less_caiso_notices_20261005` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_4h_all_less_elliott_2022` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_foresight_4h_all_less_ercot_heat_2023` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_foresight_4h_all_less_events` |  | USD/kW-year | 2 | 2018-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_4h_all_less_uri_2021` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_foresight_4h_avg_3y` |  | USD/kW-year | 1 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `battery_foresight_4h_avg_7y` |  | USD/kW-year | 1 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `battery_foresight_4h_last_12` |  | USD/kW-year | 3 | 2025-10-01T00:00:00Z | 2025-11-01T00:00:00Z |
| `battery_foresight_4h_year_2018` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_foresight_4h_year_2019` |  | USD/kW-year | 1 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `battery_foresight_4h_year_2020` |  | USD/kW-year | 1 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `battery_foresight_4h_year_2021` |  | USD/kW-year | 1 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `battery_foresight_4h_year_2022` |  | USD/kW-year | 1 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `battery_foresight_4h_year_2023` |  | USD/kW-year | 2 | 2023-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_4h_year_2024` |  | USD/kW-year | 3 | 2024-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `battery_foresight_4h_year_2025` |  | USD/kW-year | 3 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `battery_foresight_4h_year_2026` |  | USD/kW-year | 3 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `battery_foresight_8h_all` |  | USD/kW-year | 3 | 2018-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `battery_foresight_8h_all_less_caiso_notices_20230815` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_8h_all_less_caiso_notices_20230828` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_8h_all_less_caiso_notices_20240703` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_8h_all_less_caiso_notices_20240715` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_8h_all_less_caiso_notices_20240724` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_8h_all_less_caiso_notices_20240805` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_8h_all_less_caiso_notices_20240904` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_8h_all_less_caiso_notices_20250120` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_8h_all_less_caiso_notices_20260909` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_8h_all_less_caiso_notices_20261005` |  | USD/kW-year | 1 | 2023-08-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_8h_all_less_elliott_2022` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_foresight_8h_all_less_ercot_heat_2023` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_foresight_8h_all_less_events` |  | USD/kW-year | 2 | 2018-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_8h_all_less_uri_2021` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_foresight_8h_avg_3y` |  | USD/kW-year | 1 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `battery_foresight_8h_avg_7y` |  | USD/kW-year | 1 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `battery_foresight_8h_last_12` |  | USD/kW-year | 3 | 2025-10-01T00:00:00Z | 2025-11-01T00:00:00Z |
| `battery_foresight_8h_year_2018` |  | USD/kW-year | 1 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `battery_foresight_8h_year_2019` |  | USD/kW-year | 1 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `battery_foresight_8h_year_2020` |  | USD/kW-year | 1 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `battery_foresight_8h_year_2021` |  | USD/kW-year | 1 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `battery_foresight_8h_year_2022` |  | USD/kW-year | 1 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `battery_foresight_8h_year_2023` |  | USD/kW-year | 2 | 2023-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `battery_foresight_8h_year_2024` |  | USD/kW-year | 3 | 2024-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `battery_foresight_8h_year_2025` |  | USD/kW-year | 3 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `battery_foresight_8h_year_2026` |  | USD/kW-year | 3 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `datacenter_flat_da_all` |  | USD/MWh | 19 | 2015-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_flat_da_all_less_caiso_notices_20230815` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_flat_da_all_less_caiso_notices_20230828` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_flat_da_all_less_caiso_notices_20240703` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_flat_da_all_less_caiso_notices_20240715` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_flat_da_all_less_caiso_notices_20240724` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_flat_da_all_less_caiso_notices_20240805` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_flat_da_all_less_caiso_notices_20240904` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_flat_da_all_less_caiso_notices_20250120` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_flat_da_all_less_caiso_notices_20260909` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_flat_da_all_less_caiso_notices_20261005` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_flat_da_all_less_elliott_2022` |  | USD/MWh | 14 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_flat_da_all_less_ercot_heat_2023` |  | USD/MWh | 14 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_flat_da_all_less_events` |  | USD/MWh | 17 | 2015-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_flat_da_all_less_uri_2021` |  | USD/MWh | 14 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_flat_da_avg_3y` |  | USD/MWh | 15 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `datacenter_flat_da_avg_7y` |  | USD/MWh | 15 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `datacenter_flat_da_last_12` |  | USD/MWh | 19 | 2025-11-01T00:00:00Z | 2025-11-01T00:00:00Z |
| `datacenter_flat_da_year_2015` |  | USD/MWh | 14 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_flat_da_year_2016` |  | USD/MWh | 14 | 2016-01-01T00:00:00Z | 2016-01-01T00:00:00Z |
| `datacenter_flat_da_year_2017` |  | USD/MWh | 14 | 2017-01-01T00:00:00Z | 2017-01-01T00:00:00Z |
| `datacenter_flat_da_year_2018` |  | USD/MWh | 14 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `datacenter_flat_da_year_2019` |  | USD/MWh | 15 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `datacenter_flat_da_year_2020` |  | USD/MWh | 15 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `datacenter_flat_da_year_2021` |  | USD/MWh | 15 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `datacenter_flat_da_year_2022` |  | USD/MWh | 15 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `datacenter_flat_da_year_2023` |  | USD/MWh | 18 | 2023-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_flat_da_year_2024` |  | USD/MWh | 19 | 2024-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_flat_da_year_2025` |  | USD/MWh | 19 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `datacenter_flat_da_year_2026` |  | USD/MWh | 19 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `datacenter_flat_rt_all` |  | USD/MWh | 14 | 2015-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_flat_rt_all_less_caiso_notices_20230815` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_flat_rt_all_less_caiso_notices_20230828` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_flat_rt_all_less_caiso_notices_20240703` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_flat_rt_all_less_caiso_notices_20240715` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_flat_rt_all_less_caiso_notices_20240724` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_flat_rt_all_less_caiso_notices_20240805` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_flat_rt_all_less_caiso_notices_20240904` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_flat_rt_all_less_caiso_notices_20250120` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_flat_rt_all_less_caiso_notices_20260909` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_flat_rt_all_less_caiso_notices_20261005` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_flat_rt_all_less_elliott_2022` |  | USD/MWh | 10 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_flat_rt_all_less_ercot_heat_2023` |  | USD/MWh | 10 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_flat_rt_all_less_events` |  | USD/MWh | 13 | 2015-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_flat_rt_all_less_uri_2021` |  | USD/MWh | 10 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_flat_rt_avg_3y` |  | USD/MWh | 10 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `datacenter_flat_rt_avg_7y` |  | USD/MWh | 10 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `datacenter_flat_rt_last_12` |  | USD/MWh | 14 | 2025-10-01T00:00:00Z | 2025-11-01T00:00:00Z |
| `datacenter_flat_rt_year_2015` |  | USD/MWh | 10 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_flat_rt_year_2016` |  | USD/MWh | 10 | 2016-01-01T00:00:00Z | 2016-01-01T00:00:00Z |
| `datacenter_flat_rt_year_2017` |  | USD/MWh | 10 | 2017-01-01T00:00:00Z | 2017-01-01T00:00:00Z |
| `datacenter_flat_rt_year_2018` |  | USD/MWh | 10 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `datacenter_flat_rt_year_2019` |  | USD/MWh | 10 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `datacenter_flat_rt_year_2020` |  | USD/MWh | 10 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `datacenter_flat_rt_year_2021` |  | USD/MWh | 10 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `datacenter_flat_rt_year_2022` |  | USD/MWh | 10 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `datacenter_flat_rt_year_2023` |  | USD/MWh | 12 | 2023-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_flat_rt_year_2024` |  | USD/MWh | 14 | 2024-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_flat_rt_year_2025` |  | USD/MWh | 14 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `datacenter_flat_rt_year_2026` |  | USD/MWh | 14 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `datacenter_hours_da_all` |  | USD/MWh | 19 | 2015-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_hours_da_all_less_caiso_notices_20230815` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_hours_da_all_less_caiso_notices_20230828` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_hours_da_all_less_caiso_notices_20240703` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_hours_da_all_less_caiso_notices_20240715` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_hours_da_all_less_caiso_notices_20240724` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_hours_da_all_less_caiso_notices_20240805` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_hours_da_all_less_caiso_notices_20240904` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_hours_da_all_less_caiso_notices_20250120` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_hours_da_all_less_caiso_notices_20260909` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_hours_da_all_less_caiso_notices_20261005` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_hours_da_all_less_elliott_2022` |  | USD/MWh | 14 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_hours_da_all_less_ercot_heat_2023` |  | USD/MWh | 14 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_hours_da_all_less_events` |  | USD/MWh | 17 | 2015-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_hours_da_all_less_uri_2021` |  | USD/MWh | 14 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_hours_da_avg_3y` |  | USD/MWh | 15 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `datacenter_hours_da_avg_7y` |  | USD/MWh | 15 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `datacenter_hours_da_last_12` |  | USD/MWh | 19 | 2025-11-01T00:00:00Z | 2025-11-01T00:00:00Z |
| `datacenter_hours_da_year_2015` |  | USD/MWh | 14 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_hours_da_year_2016` |  | USD/MWh | 14 | 2016-01-01T00:00:00Z | 2016-01-01T00:00:00Z |
| `datacenter_hours_da_year_2017` |  | USD/MWh | 14 | 2017-01-01T00:00:00Z | 2017-01-01T00:00:00Z |
| `datacenter_hours_da_year_2018` |  | USD/MWh | 14 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `datacenter_hours_da_year_2019` |  | USD/MWh | 15 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `datacenter_hours_da_year_2020` |  | USD/MWh | 15 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `datacenter_hours_da_year_2021` |  | USD/MWh | 15 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `datacenter_hours_da_year_2022` |  | USD/MWh | 15 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `datacenter_hours_da_year_2023` |  | USD/MWh | 18 | 2023-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_hours_da_year_2024` |  | USD/MWh | 19 | 2024-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_hours_da_year_2025` |  | USD/MWh | 19 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `datacenter_hours_da_year_2026` |  | USD/MWh | 19 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `datacenter_hours_rt_all` |  | USD/MWh | 14 | 2015-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_hours_rt_all_less_caiso_notices_20230815` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_hours_rt_all_less_caiso_notices_20230828` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_hours_rt_all_less_caiso_notices_20240703` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_hours_rt_all_less_caiso_notices_20240715` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_hours_rt_all_less_caiso_notices_20240724` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_hours_rt_all_less_caiso_notices_20240805` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_hours_rt_all_less_caiso_notices_20240904` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_hours_rt_all_less_caiso_notices_20250120` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_hours_rt_all_less_caiso_notices_20260909` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_hours_rt_all_less_caiso_notices_20261005` |  | USD/MWh | 3 | 2023-08-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_hours_rt_all_less_elliott_2022` |  | USD/MWh | 10 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_hours_rt_all_less_ercot_heat_2023` |  | USD/MWh | 10 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_hours_rt_all_less_events` |  | USD/MWh | 13 | 2015-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_hours_rt_all_less_uri_2021` |  | USD/MWh | 10 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_hours_rt_avg_3y` |  | USD/MWh | 10 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `datacenter_hours_rt_avg_7y` |  | USD/MWh | 10 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `datacenter_hours_rt_last_12` |  | USD/MWh | 14 | 2025-10-01T00:00:00Z | 2025-11-01T00:00:00Z |
| `datacenter_hours_rt_year_2015` |  | USD/MWh | 10 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_hours_rt_year_2016` |  | USD/MWh | 10 | 2016-01-01T00:00:00Z | 2016-01-01T00:00:00Z |
| `datacenter_hours_rt_year_2017` |  | USD/MWh | 10 | 2017-01-01T00:00:00Z | 2017-01-01T00:00:00Z |
| `datacenter_hours_rt_year_2018` |  | USD/MWh | 10 | 2018-01-01T00:00:00Z | 2018-01-01T00:00:00Z |
| `datacenter_hours_rt_year_2019` |  | USD/MWh | 10 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `datacenter_hours_rt_year_2020` |  | USD/MWh | 10 | 2020-01-01T00:00:00Z | 2020-01-01T00:00:00Z |
| `datacenter_hours_rt_year_2021` |  | USD/MWh | 10 | 2021-01-01T00:00:00Z | 2021-01-01T00:00:00Z |
| `datacenter_hours_rt_year_2022` |  | USD/MWh | 10 | 2022-01-01T00:00:00Z | 2022-01-01T00:00:00Z |
| `datacenter_hours_rt_year_2023` |  | USD/MWh | 12 | 2023-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_hours_rt_year_2024` |  | USD/MWh | 14 | 2024-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_hours_rt_year_2025` |  | USD/MWh | 14 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `datacenter_hours_rt_year_2026` |  | USD/MWh | 14 | 2026-01-01T00:00:00Z | 2026-01-01T00:00:00Z |
| `datacenter_share_da_all` |  | USD/MWh | 19 | 2015-01-01T00:00:00Z | 2024-09-01T00:00:00Z |
| `datacenter_share_da_all_less_caiso_notices_20230815` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_share_da_all_less_caiso_notices_20230828` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_share_da_all_less_caiso_notices_20240703` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_share_da_all_less_caiso_notices_20240715` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_share_da_all_less_caiso_notices_20240724` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_share_da_all_less_caiso_notices_20240805` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_share_da_all_less_caiso_notices_20240904` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_share_da_all_less_caiso_notices_20250120` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_share_da_all_less_caiso_notices_20260909` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_share_da_all_less_caiso_notices_20261005` |  | USD/MWh | 3 | 2023-07-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_share_da_all_less_elliott_2022` |  | USD/MWh | 14 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_share_da_all_less_ercot_heat_2023` |  | USD/MWh | 14 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_share_da_all_less_events` |  | USD/MWh | 17 | 2015-01-01T00:00:00Z | 2023-08-01T00:00:00Z |
| `datacenter_share_da_all_less_uri_2021` |  | USD/MWh | 14 | 2015-01-01T00:00:00Z | 2015-01-01T00:00:00Z |
| `datacenter_share_da_avg_3y` |  | USD/MWh | 15 | 2023-01-01T00:00:00Z | 2023-01-01T00:00:00Z |
| `datacenter_share_da_avg_7y` |  | USD/MWh | 15 | 2019-01-01T00:00:00Z | 2019-01-01T00:00:00Z |
| `datacenter_share_da_last_12` |  | USD/MWh | 19 | 2025-11-01T00:00:00Z | 2025-11-01T00:00:00Z |

