# Codebook: battery

Drawn from `warehouse/metadata/variables/` by `warehouse/codebook/build_docs.py`; never written by hand. The column names many tables share (`ts_utc`, `value`, `entity` and the others) are defined once in [`_shared.yaml`](../../warehouse/metadata/variables/_shared.yaml) and in the [index](README.md).

**What the family holds.** 4 public tables (4 series; tiers: 3 derived, 1 source); 3 documented in full.

- [`battery_sourced_ranges`](#battery_sourced_ranges): published low and high cases of the battery's assumptions, one row per source, case and assumption (session 306)
- [`battery_stack_monthly`](#battery_stack_monthly): One modelled battery's value of one revenue or day-count measure for one hub, strategy, duration (2, 4 or 8 hours) and local month, per MW of rated power (ERCOT and CAISO).
- [`battery_stack_review_monthly`](#battery_stack_review_monthly): One modelled battery's value of one revenue or day-count measure for one hub, strategy, duration (2, 4 or 8 hours) and local month, per MW of rated power, on the grids in review (NYISO, SPP).
- [`battery_stack_stress_daily`](#battery_stack_stress_daily): One modelled battery's revenue by stream on one local day inside a stress event's window, for one hub, strategy and duration, per MW of rated power.

### `battery_sourced_ranges`

What a row is: not yet written.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: source. Rows read on 2026-11-20: 90.

- **Source:** nlr:atb-2025-v1 National Laboratory of the Rockies (NLR), 2025 Electricity Annual Technology Baseline (ATB), workbook 2025_v1_Workbook_08-27-2026.xlsx, sheet Utility-Scale Battery - R&D (battery costs from Cole, Ramasamy and Olmez Turan, Cost Projections for Utility-Scale Battery Storage: 2025 Update, NREL/TP-6A40-93281) (https://data.openei.org/files/8759/2025_v1_Workbook_08-27-2026.xlsx)
- **Method note:** [`docs/methods/battery_sourced_ranges.md`](../methods/battery_sourced_ranges.md)
- **Cite as:** National Laboratory of the Rockies (NLR, formerly NREL). 2025 Electricity Annual Technology Baseline (ATB), workbook 2025_v1_Workbook_08-27-2026.xlsx. Via the Energy Research Warehouse (ERW), table `battery_sourced_ranges`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station) | none | text | nlr_atb_2025:utility_battery:advanced, nlr_atb_2025:utility_battery:conservative, nlr_atb_2025:utility_battery:moderate, nlr_atb_2025:utility_battery_10h:advanced, nlr_atb_2025:utility_battery_10h:conservative, nlr_atb_2025:utility_battery_10h:moderate, nlr_atb_2025:utility_battery_2h:advanced, nlr_atb_2025:utility_battery_2h:conservative, nlr_atb_2025:utility_battery_2h:moderate, nlr_atb_2025:utility_battery_4h:advanced, nlr_atb_2025:utility_battery_4h:conservative, nlr_atb_2025:utility_battery_4h:moderate, nlr_atb_2025:utility_battery_6h:advanced, nlr_atb_2025:utility_battery_6h:conservative, nlr_atb_2025:utility_battery_6h:moderate, nlr_atb_2025:utility_battery_8h:advanced, nlr_atb_2025:utility_battery_8h:conservative, nlr_atb_2025:utility_battery_8h:moderate | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2025-01-01T00:00:00Z | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | 0.065 to 2891.047166; 56 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/kW, USD/kW-year, USD/kWh, ratio, year | 0 |
| `freq` | How long the interval of the row is | none | text | P1Y | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm) | none | empty | no cell holds a value | 90 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | empty | no cell holds a value | 90 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | nlr:atb-2025-v1 | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://data.openei.org/files/8759/2025_v1_Workbook_08-27-2026.xlsx | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-19T06:12:19Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | utc time | 2026-08-27T00:00:00Z | 0 |
| `x_case` | not yet written |  | text | high, low, mid | 0 |
| `x_published_case` | not yet written |  | text | Advanced, Conservative, Moderate | 0 |
| `x_duration_h` | not yet written |  | integer | 10, 2, 4, 6, 8 | 15 |
| `x_document` | not yet written |  | text | National Laboratory of the Rockies (NLR), 2025 Electricity Annual Technology Baseline (ATB), workbook 2025_v1_Workbook_08-27-2026.xlsx, sheet Utility-Scale Battery - R&D (battery costs from Cole, Ramasamy and Olmez Turan, Cost Projections for Utility-Scale Battery Storage: 2025 Update, NREL/TP-6A40-93281) | 0 |
| `x_page` | not yet written |  | text | for example sheet Utility-Scale Battery - R&D, row 104, column 2025, sheet Utility-Scale Battery - R&D, row 105, column 2025, sheet Utility-Scale Battery - R&D, row 106, column 2025; 88 distinct | 0 |
| `x_dollar_year` | not yet written |  | integer | 2023 | 24 |

Variables (10):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `capex` |  | USD/kW | 15 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `energy_capital_cost` |  | USD/kWh | 3 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `fixed_om` |  | USD/kW-year | 15 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `grid_connection_cost` |  | USD/kW | 15 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `interest_rate_nominal` |  | ratio | 3 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `overnight_capital_cost` |  | USD/kW | 15 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `power_capital_cost` |  | USD/kW | 3 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `return_on_equity_nominal` |  | ratio | 3 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `round_trip_efficiency` |  | ratio | 15 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |
| `technical_life` |  | year | 3 | 2025-01-01T00:00:00Z | 2025-01-01T00:00:00Z |

### `battery_stack_monthly`

One modelled battery's value of one revenue or day-count measure for one hub, strategy, duration (2, 4 or 8 hours) and local month, per MW of rated power (ERCOT and CAISO).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 11634.

- **Time:** ts_utc is the first day of the market's local month at 00:00:00Z (freq P1M).
- **Revisions:** Rebuilt by each run of the builder, except that a (hub, strategy, duration, month) whose earlier file rested on more days keeps its earlier rows, and months the run's inputs no longer reach are carried; vintage is not filled.
- **Source:** erw:battery_stack ERW derived table, the battery revenue stack (docs/methods/battery_stack.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/battery_stack.md)
- **Method note:** [`docs/methods/battery_stack.md`](../methods/battery_stack.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The battery revenue stack: energy and ancillary services co-optimized, per MW (docs/methods/battery_stack.md). Via the Energy Research Warehouse (ERW), table `battery_stack_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: <market>:<hub> (ercot:HB_HUBAVG, caiso:TH_SP15_GEN-APND) | none | text | caiso:TH_SP15_GEN-APND, ercot:HB_HUBAVG | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2018-01-01T00:00:00Z to 2026-11-01T00:00:00Z; 107 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -44237.9335 to 3152926.5657; more than 5000 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh/MW, USD/MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: The grid (ercot, caiso), the partition column | none | text | caiso, ercot | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | HB_HUBAVG, TH_SP15_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:battery_stack | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/battery_stack.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T21:00:50Z, 2026-10-03T14:48:07Z, 2026-10-03T17:09:57Z, 2026-10-06T14:47:01Z, 2026-10-12T15:03:07Z, 2026-10-13T15:03:39Z, 2026-10-14T12:07:36Z, 2026-10-19T16:26:22Z, 2026-10-20T01:04:16Z, 2026-10-22T15:05:29Z, 2026-10-23T15:04:47Z, 2026-10-24T15:12:22Z, 2026-10-25T14:55:44Z, 2026-10-27T14:58:35Z, 2026-10-29T14:54:33Z, 2026-10-30T15:05:44Z, 2026-11-12T22:14:35Z, 2026-11-13T15:16:06Z, 2026-11-14T10:03:46Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 11634 |
| `x_strategy` | The strategy: foresight (perfect foresight, the upper bound) or dayahead (the day-ahead schedule, no real-time trading) | none | text | dayahead, foresight | 0 |
| `x_duration_hours` | The battery's duration: hours of discharge at full power (2, 4 or 8) | hour | integer | 2, 4, 8 | 0 |
| `x_metric` | The measure, the part of the variable after <strategy>_<N>h_ | none | text | days_held, days_in_month, days_left_out, days_left_out_ancillary, days_left_out_energy, discharged_mwh_per_mw, revenue_ancillary_usd_per_mw, revenue_ecrs_usd_per_mw, revenue_energy_usd_per_mw, revenue_nonspin_usd_per_mw, revenue_nspin_usd_per_mw, revenue_regdn_usd_per_mw, revenue_regup_usd_per_mw, revenue_rrs_usd_per_mw, revenue_spin_usd_per_mw, revenue_total_usd_per_mw | 0 |

Variables (96):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dayahead_2h_days_held` | 2-hour battery, day-ahead schedule: days solved (every hour of every price held) | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_2h_days_in_month` | 2-hour battery, day-ahead schedule: days in the month | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_2h_days_left_out` | 2-hour battery, day-ahead schedule: days left out (a price hour not held) | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_2h_days_left_out_ancillary` | 2-hour battery, day-ahead schedule: days left out for an ancillary price not held | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_2h_days_left_out_energy` | 2-hour battery, day-ahead schedule: days left out for an energy price not held | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_2h_discharged_mwh_per_mw` | 2-hour battery, day-ahead schedule: energy delivered to the grid, MWh per MW | MWh/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_2h_revenue_ancillary_usd_per_mw` | 2-hour battery, day-ahead schedule: ancillary services revenue (the products summed) over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_2h_revenue_ecrs_usd_per_mw` | 2-hour battery, day-ahead schedule: revenue from ERCOT Contingency Reserve Service over the held days, USD per MW | USD/MW | 41 | 2023-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_revenue_energy_usd_per_mw` | 2-hour battery, day-ahead schedule: energy revenue over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_2h_revenue_nonspin_usd_per_mw` | 2-hour battery, day-ahead schedule: revenue from CAISO Non-Spinning Reserve over the held days, USD per MW | USD/MW | 40 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_2h_revenue_nspin_usd_per_mw` | 2-hour battery, day-ahead schedule: revenue from ERCOT Non-Spin reserve over the held days, USD per MW | USD/MW | 106 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_revenue_regdn_usd_per_mw` | 2-hour battery, day-ahead schedule: revenue from Regulation Down over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_2h_revenue_regup_usd_per_mw` | 2-hour battery, day-ahead schedule: revenue from Regulation Up over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_2h_revenue_rrs_usd_per_mw` | 2-hour battery, day-ahead schedule: revenue from ERCOT Responsive Reserve over the held days, USD per MW | USD/MW | 106 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_revenue_spin_usd_per_mw` | 2-hour battery, day-ahead schedule: revenue from CAISO Spinning Reserve over the held days, USD per MW | USD/MW | 40 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_2h_revenue_total_usd_per_mw` | 2-hour battery, day-ahead schedule: total revenue, energy plus ancillary, over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_4h_days_held` | 4-hour battery, day-ahead schedule: days solved (every hour of every price held) | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_4h_days_in_month` | 4-hour battery, day-ahead schedule: days in the month | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_4h_days_left_out` | 4-hour battery, day-ahead schedule: days left out (a price hour not held) | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_4h_days_left_out_ancillary` | 4-hour battery, day-ahead schedule: days left out for an ancillary price not held | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_4h_days_left_out_energy` | 4-hour battery, day-ahead schedule: days left out for an energy price not held | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_4h_discharged_mwh_per_mw` | 4-hour battery, day-ahead schedule: energy delivered to the grid, MWh per MW | MWh/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_4h_revenue_ancillary_usd_per_mw` | 4-hour battery, day-ahead schedule: ancillary services revenue (the products summed) over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_4h_revenue_ecrs_usd_per_mw` | 4-hour battery, day-ahead schedule: revenue from ERCOT Contingency Reserve Service over the held days, USD per MW | USD/MW | 41 | 2023-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_revenue_energy_usd_per_mw` | 4-hour battery, day-ahead schedule: energy revenue over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_4h_revenue_nonspin_usd_per_mw` | 4-hour battery, day-ahead schedule: revenue from CAISO Non-Spinning Reserve over the held days, USD per MW | USD/MW | 40 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_4h_revenue_nspin_usd_per_mw` | 4-hour battery, day-ahead schedule: revenue from ERCOT Non-Spin reserve over the held days, USD per MW | USD/MW | 106 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_revenue_regdn_usd_per_mw` | 4-hour battery, day-ahead schedule: revenue from Regulation Down over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_4h_revenue_regup_usd_per_mw` | 4-hour battery, day-ahead schedule: revenue from Regulation Up over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_4h_revenue_rrs_usd_per_mw` | 4-hour battery, day-ahead schedule: revenue from ERCOT Responsive Reserve over the held days, USD per MW | USD/MW | 106 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_revenue_spin_usd_per_mw` | 4-hour battery, day-ahead schedule: revenue from CAISO Spinning Reserve over the held days, USD per MW | USD/MW | 40 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_4h_revenue_total_usd_per_mw` | 4-hour battery, day-ahead schedule: total revenue, energy plus ancillary, over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_8h_days_held` | 8-hour battery, day-ahead schedule: days solved (every hour of every price held) | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_8h_days_in_month` | 8-hour battery, day-ahead schedule: days in the month | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_8h_days_left_out` | 8-hour battery, day-ahead schedule: days left out (a price hour not held) | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_8h_days_left_out_ancillary` | 8-hour battery, day-ahead schedule: days left out for an ancillary price not held | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_8h_days_left_out_energy` | 8-hour battery, day-ahead schedule: days left out for an energy price not held | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_8h_discharged_mwh_per_mw` | 8-hour battery, day-ahead schedule: energy delivered to the grid, MWh per MW | MWh/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_8h_revenue_ancillary_usd_per_mw` | 8-hour battery, day-ahead schedule: ancillary services revenue (the products summed) over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_8h_revenue_ecrs_usd_per_mw` | 8-hour battery, day-ahead schedule: revenue from ERCOT Contingency Reserve Service over the held days, USD per MW | USD/MW | 41 | 2023-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_revenue_energy_usd_per_mw` | 8-hour battery, day-ahead schedule: energy revenue over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_8h_revenue_nonspin_usd_per_mw` | 8-hour battery, day-ahead schedule: revenue from CAISO Non-Spinning Reserve over the held days, USD per MW | USD/MW | 40 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_8h_revenue_nspin_usd_per_mw` | 8-hour battery, day-ahead schedule: revenue from ERCOT Non-Spin reserve over the held days, USD per MW | USD/MW | 106 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_revenue_regdn_usd_per_mw` | 8-hour battery, day-ahead schedule: revenue from Regulation Down over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_8h_revenue_regup_usd_per_mw` | 8-hour battery, day-ahead schedule: revenue from Regulation Up over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_8h_revenue_rrs_usd_per_mw` | 8-hour battery, day-ahead schedule: revenue from ERCOT Responsive Reserve over the held days, USD per MW | USD/MW | 106 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_revenue_spin_usd_per_mw` | 8-hour battery, day-ahead schedule: revenue from CAISO Spinning Reserve over the held days, USD per MW | USD/MW | 40 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `dayahead_8h_revenue_total_usd_per_mw` | 8-hour battery, day-ahead schedule: total revenue, energy plus ancillary, over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_2h_days_held` | 2-hour battery, perfect foresight: days solved (every hour of every price held) | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_2h_days_in_month` | 2-hour battery, perfect foresight: days in the month | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_2h_days_left_out` | 2-hour battery, perfect foresight: days left out (a price hour not held) | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_2h_days_left_out_ancillary` | 2-hour battery, perfect foresight: days left out for an ancillary price not held | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_2h_days_left_out_energy` | 2-hour battery, perfect foresight: days left out for an energy price not held | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_2h_discharged_mwh_per_mw` | 2-hour battery, perfect foresight: energy delivered to the grid, MWh per MW | MWh/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_2h_revenue_ancillary_usd_per_mw` | 2-hour battery, perfect foresight: ancillary services revenue (the products summed) over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_2h_revenue_ecrs_usd_per_mw` | 2-hour battery, perfect foresight: revenue from ERCOT Contingency Reserve Service over the held days, USD per MW | USD/MW | 41 | 2023-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_revenue_energy_usd_per_mw` | 2-hour battery, perfect foresight: energy revenue over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_2h_revenue_nonspin_usd_per_mw` | 2-hour battery, perfect foresight: revenue from CAISO Non-Spinning Reserve over the held days, USD per MW | USD/MW | 40 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_2h_revenue_nspin_usd_per_mw` | 2-hour battery, perfect foresight: revenue from ERCOT Non-Spin reserve over the held days, USD per MW | USD/MW | 106 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_revenue_regdn_usd_per_mw` | 2-hour battery, perfect foresight: revenue from Regulation Down over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_2h_revenue_regup_usd_per_mw` | 2-hour battery, perfect foresight: revenue from Regulation Up over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_2h_revenue_rrs_usd_per_mw` | 2-hour battery, perfect foresight: revenue from ERCOT Responsive Reserve over the held days, USD per MW | USD/MW | 106 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_revenue_spin_usd_per_mw` | 2-hour battery, perfect foresight: revenue from CAISO Spinning Reserve over the held days, USD per MW | USD/MW | 40 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_2h_revenue_total_usd_per_mw` | 2-hour battery, perfect foresight: total revenue, energy plus ancillary, over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_4h_days_held` | 4-hour battery, perfect foresight: days solved (every hour of every price held) | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_4h_days_in_month` | 4-hour battery, perfect foresight: days in the month | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_4h_days_left_out` | 4-hour battery, perfect foresight: days left out (a price hour not held) | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_4h_days_left_out_ancillary` | 4-hour battery, perfect foresight: days left out for an ancillary price not held | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_4h_days_left_out_energy` | 4-hour battery, perfect foresight: days left out for an energy price not held | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_4h_discharged_mwh_per_mw` | 4-hour battery, perfect foresight: energy delivered to the grid, MWh per MW | MWh/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_4h_revenue_ancillary_usd_per_mw` | 4-hour battery, perfect foresight: ancillary services revenue (the products summed) over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_4h_revenue_ecrs_usd_per_mw` | 4-hour battery, perfect foresight: revenue from ERCOT Contingency Reserve Service over the held days, USD per MW | USD/MW | 41 | 2023-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_revenue_energy_usd_per_mw` | 4-hour battery, perfect foresight: energy revenue over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_4h_revenue_nonspin_usd_per_mw` | 4-hour battery, perfect foresight: revenue from CAISO Non-Spinning Reserve over the held days, USD per MW | USD/MW | 40 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_4h_revenue_nspin_usd_per_mw` | 4-hour battery, perfect foresight: revenue from ERCOT Non-Spin reserve over the held days, USD per MW | USD/MW | 106 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_revenue_regdn_usd_per_mw` | 4-hour battery, perfect foresight: revenue from Regulation Down over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_4h_revenue_regup_usd_per_mw` | 4-hour battery, perfect foresight: revenue from Regulation Up over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_4h_revenue_rrs_usd_per_mw` | 4-hour battery, perfect foresight: revenue from ERCOT Responsive Reserve over the held days, USD per MW | USD/MW | 106 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_revenue_spin_usd_per_mw` | 4-hour battery, perfect foresight: revenue from CAISO Spinning Reserve over the held days, USD per MW | USD/MW | 40 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_4h_revenue_total_usd_per_mw` | 4-hour battery, perfect foresight: total revenue, energy plus ancillary, over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_8h_days_held` | 8-hour battery, perfect foresight: days solved (every hour of every price held) | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_8h_days_in_month` | 8-hour battery, perfect foresight: days in the month | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_8h_days_left_out` | 8-hour battery, perfect foresight: days left out (a price hour not held) | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_8h_days_left_out_ancillary` | 8-hour battery, perfect foresight: days left out for an ancillary price not held | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_8h_days_left_out_energy` | 8-hour battery, perfect foresight: days left out for an energy price not held | count | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_8h_discharged_mwh_per_mw` | 8-hour battery, perfect foresight: energy delivered to the grid, MWh per MW | MWh/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_8h_revenue_ancillary_usd_per_mw` | 8-hour battery, perfect foresight: ancillary services revenue (the products summed) over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_8h_revenue_ecrs_usd_per_mw` | 8-hour battery, perfect foresight: revenue from ERCOT Contingency Reserve Service over the held days, USD per MW | USD/MW | 41 | 2023-06-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_revenue_energy_usd_per_mw` | 8-hour battery, perfect foresight: energy revenue over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_8h_revenue_nonspin_usd_per_mw` | 8-hour battery, perfect foresight: revenue from CAISO Non-Spinning Reserve over the held days, USD per MW | USD/MW | 40 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_8h_revenue_nspin_usd_per_mw` | 8-hour battery, perfect foresight: revenue from ERCOT Non-Spin reserve over the held days, USD per MW | USD/MW | 106 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_revenue_regdn_usd_per_mw` | 8-hour battery, perfect foresight: revenue from Regulation Down over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_8h_revenue_regup_usd_per_mw` | 8-hour battery, perfect foresight: revenue from Regulation Up over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_8h_revenue_rrs_usd_per_mw` | 8-hour battery, perfect foresight: revenue from ERCOT Responsive Reserve over the held days, USD per MW | USD/MW | 106 | 2018-01-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_revenue_spin_usd_per_mw` | 8-hour battery, perfect foresight: revenue from CAISO Spinning Reserve over the held days, USD per MW | USD/MW | 40 | 2023-08-01T00:00:00Z | 2026-11-01T00:00:00Z |
| `foresight_8h_revenue_total_usd_per_mw` | 8-hour battery, perfect foresight: total revenue, energy plus ancillary, over the held days, USD per MW | USD/MW | 146 | 2018-01-01T00:00:00Z | 2026-11-01T00:00:00Z |

### `battery_stack_review_monthly`

One modelled battery's value of one revenue or day-count measure for one hub, strategy, duration (2, 4 or 8 hours) and local month, per MW of rated power, on the grids in review (NYISO, SPP).

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 3744.

- **Time:** ts_utc is the first day of the market's local month at 00:00:00Z (freq P1M).
- **Revisions:** Rebuilt by each run of the builder, except that a (hub, strategy, duration, month) whose earlier file rested on more days keeps its earlier rows; vintage is not filled.
- **Source:** erw:battery_stack ERW derived table, the battery revenue stack (docs/methods/battery_stack.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/battery_stack.md)
- **Method note:** [`docs/methods/battery_stack.md`](../methods/battery_stack.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The battery revenue stack: energy and ancillary services co-optimized, per MW (docs/methods/battery_stack.md). Via the Energy Research Warehouse (ERW), table `battery_stack_review_monthly`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: <market>:<hub> (nyiso:N.Y.C., spp:SPPNORTH_HUB) | none | text | nyiso:N.Y.C., spp:SPPNORTH_HUB | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2024-09-01T00:00:00Z to 2026-10-01T00:00:00Z; 26 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -394.9 to 54122.3643; 1872 distinct | 0 |
| `unit` | The unit of the row's value | none | text | MWh/MW, USD/MW, count | 0 |
| `freq` | How long the interval of the row is | none | text | P1M | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-AR,US-IA,US-KS,US-LA,US-MN,US-MO,US-MT,US-NE,US-NM,US-ND,US-OK,US-SD,US-TX,US-WY, US-NY | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: The grid (nyiso, spp), the partition column | none | text | nyiso, spp | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | N.Y.C., SPPNORTH_HUB | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:battery_stack | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/battery_stack.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-04T04:30:49Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 3744 |
| `x_strategy` | The strategy: foresight (perfect foresight, the upper bound) or dayahead (the day-ahead schedule, no real-time trading) | none | text | dayahead, foresight | 0 |
| `x_duration_hours` | The battery's duration: hours of discharge at full power (2, 4 or 8) | hour | integer | 2, 4, 8 | 0 |
| `x_metric` | The measure, the part of the variable after <strategy>_<N>h_ | none | text | days_held, days_in_month, days_left_out, days_left_out_ancillary, days_left_out_energy, discharged_mwh_per_mw, revenue_ancillary_usd_per_mw, revenue_energy_usd_per_mw, revenue_reg_usd_per_mw, revenue_regdn_usd_per_mw, revenue_regup_usd_per_mw, revenue_spin_usd_per_mw, revenue_supp_usd_per_mw, revenue_total_usd_per_mw | 0 |

Variables (84):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dayahead_2h_days_held` | 2-hour battery, day-ahead schedule: days solved (every hour of every price held) | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_days_in_month` | 2-hour battery, day-ahead schedule: days in the month | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_days_left_out` | 2-hour battery, day-ahead schedule: days left out (a price hour not held) | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_days_left_out_ancillary` | 2-hour battery, day-ahead schedule: days left out for an ancillary price not held | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_days_left_out_energy` | 2-hour battery, day-ahead schedule: days left out for an energy price not held | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_discharged_mwh_per_mw` | 2-hour battery, day-ahead schedule: energy delivered to the grid, MWh per MW | MWh/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_revenue_ancillary_usd_per_mw` | 2-hour battery, day-ahead schedule: ancillary services revenue (the products summed) over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_revenue_energy_usd_per_mw` | 2-hour battery, day-ahead schedule: energy revenue over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_revenue_reg_usd_per_mw` | 2-hour battery, day-ahead schedule: revenue from NYISO Regulation Capacity (up and down) over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_revenue_regdn_usd_per_mw` | 2-hour battery, day-ahead schedule: revenue from Regulation Down over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_revenue_regup_usd_per_mw` | 2-hour battery, day-ahead schedule: revenue from Regulation Up over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_revenue_spin_usd_per_mw` | 2-hour battery, day-ahead schedule: revenue from Spinning Reserve (NYISO 10-Minute Spinning Reserve, SPP Spinning Reserve) over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_revenue_supp_usd_per_mw` | 2-hour battery, day-ahead schedule: revenue from SPP Supplemental Reserve over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_2h_revenue_total_usd_per_mw` | 2-hour battery, day-ahead schedule: total revenue, energy plus ancillary, over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_days_held` | 4-hour battery, day-ahead schedule: days solved (every hour of every price held) | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_days_in_month` | 4-hour battery, day-ahead schedule: days in the month | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_days_left_out` | 4-hour battery, day-ahead schedule: days left out (a price hour not held) | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_days_left_out_ancillary` | 4-hour battery, day-ahead schedule: days left out for an ancillary price not held | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_days_left_out_energy` | 4-hour battery, day-ahead schedule: days left out for an energy price not held | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_discharged_mwh_per_mw` | 4-hour battery, day-ahead schedule: energy delivered to the grid, MWh per MW | MWh/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_revenue_ancillary_usd_per_mw` | 4-hour battery, day-ahead schedule: ancillary services revenue (the products summed) over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_revenue_energy_usd_per_mw` | 4-hour battery, day-ahead schedule: energy revenue over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_revenue_reg_usd_per_mw` | 4-hour battery, day-ahead schedule: revenue from NYISO Regulation Capacity (up and down) over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_revenue_regdn_usd_per_mw` | 4-hour battery, day-ahead schedule: revenue from Regulation Down over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_revenue_regup_usd_per_mw` | 4-hour battery, day-ahead schedule: revenue from Regulation Up over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_revenue_spin_usd_per_mw` | 4-hour battery, day-ahead schedule: revenue from Spinning Reserve (NYISO 10-Minute Spinning Reserve, SPP Spinning Reserve) over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_revenue_supp_usd_per_mw` | 4-hour battery, day-ahead schedule: revenue from SPP Supplemental Reserve over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_4h_revenue_total_usd_per_mw` | 4-hour battery, day-ahead schedule: total revenue, energy plus ancillary, over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_days_held` | 8-hour battery, day-ahead schedule: days solved (every hour of every price held) | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_days_in_month` | 8-hour battery, day-ahead schedule: days in the month | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_days_left_out` | 8-hour battery, day-ahead schedule: days left out (a price hour not held) | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_days_left_out_ancillary` | 8-hour battery, day-ahead schedule: days left out for an ancillary price not held | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_days_left_out_energy` | 8-hour battery, day-ahead schedule: days left out for an energy price not held | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_discharged_mwh_per_mw` | 8-hour battery, day-ahead schedule: energy delivered to the grid, MWh per MW | MWh/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_revenue_ancillary_usd_per_mw` | 8-hour battery, day-ahead schedule: ancillary services revenue (the products summed) over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_revenue_energy_usd_per_mw` | 8-hour battery, day-ahead schedule: energy revenue over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_revenue_reg_usd_per_mw` | 8-hour battery, day-ahead schedule: revenue from NYISO Regulation Capacity (up and down) over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_revenue_regdn_usd_per_mw` | 8-hour battery, day-ahead schedule: revenue from Regulation Down over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_revenue_regup_usd_per_mw` | 8-hour battery, day-ahead schedule: revenue from Regulation Up over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_revenue_spin_usd_per_mw` | 8-hour battery, day-ahead schedule: revenue from Spinning Reserve (NYISO 10-Minute Spinning Reserve, SPP Spinning Reserve) over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_revenue_supp_usd_per_mw` | 8-hour battery, day-ahead schedule: revenue from SPP Supplemental Reserve over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `dayahead_8h_revenue_total_usd_per_mw` | 8-hour battery, day-ahead schedule: total revenue, energy plus ancillary, over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_days_held` | 2-hour battery, perfect foresight: days solved (every hour of every price held) | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_days_in_month` | 2-hour battery, perfect foresight: days in the month | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_days_left_out` | 2-hour battery, perfect foresight: days left out (a price hour not held) | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_days_left_out_ancillary` | 2-hour battery, perfect foresight: days left out for an ancillary price not held | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_days_left_out_energy` | 2-hour battery, perfect foresight: days left out for an energy price not held | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_discharged_mwh_per_mw` | 2-hour battery, perfect foresight: energy delivered to the grid, MWh per MW | MWh/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_revenue_ancillary_usd_per_mw` | 2-hour battery, perfect foresight: ancillary services revenue (the products summed) over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_revenue_energy_usd_per_mw` | 2-hour battery, perfect foresight: energy revenue over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_revenue_reg_usd_per_mw` | 2-hour battery, perfect foresight: revenue from NYISO Regulation Capacity (up and down) over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_revenue_regdn_usd_per_mw` | 2-hour battery, perfect foresight: revenue from Regulation Down over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_revenue_regup_usd_per_mw` | 2-hour battery, perfect foresight: revenue from Regulation Up over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_revenue_spin_usd_per_mw` | 2-hour battery, perfect foresight: revenue from Spinning Reserve (NYISO 10-Minute Spinning Reserve, SPP Spinning Reserve) over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_revenue_supp_usd_per_mw` | 2-hour battery, perfect foresight: revenue from SPP Supplemental Reserve over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_2h_revenue_total_usd_per_mw` | 2-hour battery, perfect foresight: total revenue, energy plus ancillary, over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_days_held` | 4-hour battery, perfect foresight: days solved (every hour of every price held) | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_days_in_month` | 4-hour battery, perfect foresight: days in the month | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_days_left_out` | 4-hour battery, perfect foresight: days left out (a price hour not held) | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_days_left_out_ancillary` | 4-hour battery, perfect foresight: days left out for an ancillary price not held | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_days_left_out_energy` | 4-hour battery, perfect foresight: days left out for an energy price not held | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_discharged_mwh_per_mw` | 4-hour battery, perfect foresight: energy delivered to the grid, MWh per MW | MWh/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_revenue_ancillary_usd_per_mw` | 4-hour battery, perfect foresight: ancillary services revenue (the products summed) over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_revenue_energy_usd_per_mw` | 4-hour battery, perfect foresight: energy revenue over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_revenue_reg_usd_per_mw` | 4-hour battery, perfect foresight: revenue from NYISO Regulation Capacity (up and down) over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_revenue_regdn_usd_per_mw` | 4-hour battery, perfect foresight: revenue from Regulation Down over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_revenue_regup_usd_per_mw` | 4-hour battery, perfect foresight: revenue from Regulation Up over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_revenue_spin_usd_per_mw` | 4-hour battery, perfect foresight: revenue from Spinning Reserve (NYISO 10-Minute Spinning Reserve, SPP Spinning Reserve) over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_revenue_supp_usd_per_mw` | 4-hour battery, perfect foresight: revenue from SPP Supplemental Reserve over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_4h_revenue_total_usd_per_mw` | 4-hour battery, perfect foresight: total revenue, energy plus ancillary, over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_days_held` | 8-hour battery, perfect foresight: days solved (every hour of every price held) | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_days_in_month` | 8-hour battery, perfect foresight: days in the month | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_days_left_out` | 8-hour battery, perfect foresight: days left out (a price hour not held) | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_days_left_out_ancillary` | 8-hour battery, perfect foresight: days left out for an ancillary price not held | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_days_left_out_energy` | 8-hour battery, perfect foresight: days left out for an energy price not held | count | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_discharged_mwh_per_mw` | 8-hour battery, perfect foresight: energy delivered to the grid, MWh per MW | MWh/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_revenue_ancillary_usd_per_mw` | 8-hour battery, perfect foresight: ancillary services revenue (the products summed) over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_revenue_energy_usd_per_mw` | 8-hour battery, perfect foresight: energy revenue over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_revenue_reg_usd_per_mw` | 8-hour battery, perfect foresight: revenue from NYISO Regulation Capacity (up and down) over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_revenue_regdn_usd_per_mw` | 8-hour battery, perfect foresight: revenue from Regulation Down over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_revenue_regup_usd_per_mw` | 8-hour battery, perfect foresight: revenue from Regulation Up over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_revenue_spin_usd_per_mw` | 8-hour battery, perfect foresight: revenue from Spinning Reserve (NYISO 10-Minute Spinning Reserve, SPP Spinning Reserve) over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_revenue_supp_usd_per_mw` | 8-hour battery, perfect foresight: revenue from SPP Supplemental Reserve over the held days, USD per MW | USD/MW | 26 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |
| `foresight_8h_revenue_total_usd_per_mw` | 8-hour battery, perfect foresight: total revenue, energy plus ancillary, over the held days, USD per MW | USD/MW | 52 | 2024-09-01T00:00:00Z | 2026-10-01T00:00:00Z |

### `battery_stack_stress_daily`

One modelled battery's revenue by stream on one local day inside a stress event's window, for one hub, strategy and duration, per MW of rated power.

Shape: series. Keys: `entity`, `variable`, `ts_utc`. License: public; tier: derived. Rows read on 2026-11-20: 1890.

- **Time:** ts_utc is the market's local day at 00:00:00Z (freq P1D).
- **Revisions:** Rebuilt by each run of the builder, except that a (hub, strategy, duration, day) held in the earlier file and not reached by the run's inputs keeps its earlier rows; vintage is not filled.
- **Source:** erw:battery_stack ERW derived table, the battery revenue stack (docs/methods/battery_stack.md) (https://github.com/SamuelEnrique/erw/blob/main/docs/methods/battery_stack.md)
- **Method note:** [`docs/methods/battery_stack.md`](../methods/battery_stack.md)
- **Cite as:** Energy Research Warehouse (ERW), derived. The battery revenue stack: energy and ancillary services co-optimized, per MW (docs/methods/battery_stack.md). Via the Energy Research Warehouse (ERW), table `battery_stack_stress_daily`.

| Column | Label | Unit | Type | Values | Empty cells |
|---|---|---|---|---|---|
| `entity` | The thing observed (a price node, a balancing authority, a plant, a country, a station). Here: <market>:<hub> (ercot:HB_HUBAVG, caiso:TH_SP15_GEN-APND) | none | text | caiso:TH_SP15_GEN-APND, ercot:HB_HUBAVG | 0 |
| `variable` | What was measured (a price, a load, a count), in snake_case | none | text | see the variables below | 0 |
| `ts_utc` | The time of the observation, in UTC | none | utc time | 2021-02-07T00:00:00Z to 2026-10-08T00:00:00Z; 99 distinct | 0 |
| `value` | The number observed, in the row's unit | the row's unit column | number | -10466.5448 to 685719.0643; 1668 distinct | 0 |
| `unit` | The unit of the row's value | none | text | USD/MW | 0 |
| `freq` | How long the interval of the row is | none | text | P1D | 0 |
| `geo` | Where the thing is, as an ISO 3166-2 code (US-TX) | none | text | US-CA, US-TX | 0 |
| `market` | The market the value belongs to, lowercase (ercot_dam, ercot_rtm). Here: The grid (ercot, caiso), the partition column | none | text | caiso, ercot | 0 |
| `node` | The pricing node, hub or zone, written exactly as the publisher writes it (HB_NORTH) | none | text | HB_HUBAVG, TH_SP15_GEN-APND | 0 |
| `source` | The publisher and its report or product, as organization:report_id (ercot:NP4-190-CD) | none | text | erw:battery_stack | 0 |
| `source_url` | The address of the exact document the row was read from | none | text | https://github.com/SamuelEnrique/erw/blob/main/docs/methods/battery_stack.md | 0 |
| `retrieved_at` | When the ERW fetched the document, in UTC | none | utc time | 2026-10-02T21:00:50Z, 2026-10-13T07:20:11Z, 2026-10-13T08:10:28Z, 2026-10-14T12:07:36Z | 0 |
| `vintage` | When the publisher published the document the value came from, in UTC | none | empty | no cell holds a value | 1890 |
| `x_strategy` | The strategy: foresight (perfect foresight, the upper bound) or dayahead (the day-ahead schedule, no real-time trading) | none | text | dayahead, foresight | 0 |
| `x_duration_hours` | The battery's duration: hours of discharge at full power (2, 4 or 8) | hour | integer | 2, 4, 8 | 0 |
| `x_metric` | The measure, the part of the variable after <strategy>_<N>h_ | none | text | revenue_ancillary_usd_per_mw, revenue_energy_usd_per_mw, revenue_total_usd_per_mw | 0 |
| `event` | The stress event whose window holds the day: uri_2021 (Winter Storm Uri), elliott_2022 (Winter Storm Elliott), ercot_heat_2023 (the summer 2023 heat), or caiso_notices_<first day> (a run of CAISO's own system-wide notices) | none | text | caiso_notices_20230815, caiso_notices_20230828, caiso_notices_20240703, caiso_notices_20240715, caiso_notices_20240724, caiso_notices_20240805, caiso_notices_20240904, caiso_notices_20250120, caiso_notices_20260909, caiso_notices_20261005, elliott_2022, ercot_heat_2023, uri_2021 | 0 |

Variables (18):

| Variable | Label | Unit | Rows | First | Last |
|---|---|---|---|---|---|
| `dayahead_2h_revenue_ancillary_usd_per_mw` | 2-hour battery, day-ahead schedule: ancillary services revenue (the products summed), USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `dayahead_2h_revenue_energy_usd_per_mw` | 2-hour battery, day-ahead schedule: energy revenue, USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `dayahead_2h_revenue_total_usd_per_mw` | 2-hour battery, day-ahead schedule: total revenue, energy plus ancillary,, USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `dayahead_4h_revenue_ancillary_usd_per_mw` | 4-hour battery, day-ahead schedule: ancillary services revenue (the products summed), USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `dayahead_4h_revenue_energy_usd_per_mw` | 4-hour battery, day-ahead schedule: energy revenue, USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `dayahead_4h_revenue_total_usd_per_mw` | 4-hour battery, day-ahead schedule: total revenue, energy plus ancillary,, USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `dayahead_8h_revenue_ancillary_usd_per_mw` | 8-hour battery, day-ahead schedule: ancillary services revenue (the products summed), USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `dayahead_8h_revenue_energy_usd_per_mw` | 8-hour battery, day-ahead schedule: energy revenue, USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `dayahead_8h_revenue_total_usd_per_mw` | 8-hour battery, day-ahead schedule: total revenue, energy plus ancillary,, USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `foresight_2h_revenue_ancillary_usd_per_mw` | 2-hour battery, perfect foresight: ancillary services revenue (the products summed), USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `foresight_2h_revenue_energy_usd_per_mw` | 2-hour battery, perfect foresight: energy revenue, USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `foresight_2h_revenue_total_usd_per_mw` | 2-hour battery, perfect foresight: total revenue, energy plus ancillary,, USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `foresight_4h_revenue_ancillary_usd_per_mw` | 4-hour battery, perfect foresight: ancillary services revenue (the products summed), USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `foresight_4h_revenue_energy_usd_per_mw` | 4-hour battery, perfect foresight: energy revenue, USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `foresight_4h_revenue_total_usd_per_mw` | 4-hour battery, perfect foresight: total revenue, energy plus ancillary,, USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `foresight_8h_revenue_ancillary_usd_per_mw` | 8-hour battery, perfect foresight: ancillary services revenue (the products summed), USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `foresight_8h_revenue_energy_usd_per_mw` | 8-hour battery, perfect foresight: energy revenue, USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |
| `foresight_8h_revenue_total_usd_per_mw` | 8-hour battery, perfect foresight: total revenue, energy plus ancillary,, USD per MW | USD/MW | 105 | 2021-02-07T00:00:00Z | 2026-10-08T00:00:00Z |

