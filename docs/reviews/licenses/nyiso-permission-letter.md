# Draft: permission to republish NYISO's public market data in a research warehouse

Written by session 378 (20 October 2026), brought up to date by chain 229, session 4104 (13 November 2026), for Samuel to send himself, from his own address. Nothing here was sent. Fill what stands in brackets first.

Why it is needed: NYISO's legal notice, read again on 13 November 2026 (read 1670 of `warehouse/metadata/license_reads.csv`, https://www.nyiso.com/legal-notice; the sentence of read 5 is still on the page, word for word), says: "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site, including any confidential or proprietary information or intellectual property of any kind or nature, and the NYISO hereby expressly reserves such rights and property in its entirety." By the owner's ruling of 12 October 2026 the tables below show "license needed" in place of NYISO's numbers until a permission is recorded in `warehouse/metadata/license_status.csv`.

Who to write to: NYISO, 10 Krey Boulevard, Rensselaer, NY 12144; main switchboard 518.356.6000 (its contact page, read 1703, 13 November 2026). The only email address the page prints is media_relations@nyiso.com, for media inquiries; no legal or market data contact is named. [Ask the switchboard for the legal department's address, or write to the address above.]

---

**To:** NYISO, 10 Krey Boulevard, Rensselaer, NY 12144; main switchboard 518.356.6000

**Subject:** Permission to republish NYISO's public market data in an open research data warehouse

Hello,

I am Samuel [surname], [role] at Stanford University. I run the Energy Research Warehouse (ERW), an open, citable research warehouse of the US energy system at Stanford: prices, flows, projects and policy, each number traced to its source report. Its tables are versioned and citable as a dataset on Redivis, and its code and documentation are public at github.com/SamuelEnrique/erw. A public site shows figures derived from the tables (averages, spreads, comparisons between grids); it is in review and not yet open to visitors. The ERW sells nothing.

What we hold from NYISO, all from NYISO's public pages and reports (31 tables; the fields of each are listed in the appendix below):

- `nyiso_dam_zone_prices`, `nyiso_rtm_zone_prices`, `nyiso_dam_cleared_energy`, `nyiso_as_prices`, `nyiso_zone_load_hourly`, `nyiso_interconnection_queue`, `nyiso_load_queue`, `iso_hub_prices_history`, `iso_zone_prices_history`, `iso_rt_top_intervals`, `iso_trader_daily`, `hub_price_comparison`, `price_board_latest`, `price_board_peak_offpeak`, `price_board_spreads`, `scarcity_hours_by_grid`, `grid_stress_days`, `event_window_daily`, `event_study_estimates`, `merchant_revenue_monthly`, `battery_stack_review_monthly`, `clean_energy_hourly`, `clean_energy_summary`, `cost_of_power_carbon`, `cost_of_power_hourly_profile`, `cost_of_power_monthly`, `datacenter_queue_positions`, `datacenter_facilities`, `ai_power_regions`, `iso_queue_statistics`, `iso_all_capacity_prices`.
- NYISO's market notices, as links and titles with the ERW's own fields, in `news_index`.

What I am asking for:

- Permission to read NYISO's public reports by script, at the rate and times NYISO sets.
- Permission to publish the values in the tables listed below, as NYISO states them, and figures computed from them, in tables, charts and downloads, with NYISO named as the source.
- The same for the ERW's citable dataset on Redivis, version by version.
- [Only if the ERW may sell anything one day: the same in a paid product. Strike this line otherwise.]

What we offer:

- NYISO named as the source beside every figure, in the words you prefer, with a link to NYISO's own report.
- No resale or redistribution of NYISO's raw files as such: we publish the values in our tables and what we compute from them.
- Any request rate, time of day or file route you set; a bulk file or a key if you prefer.
- A line in our records for your answer, so that every table shows the permission it rests on.

If a license or a fee applies, I would be glad to know its terms.

Thank you,
Samuel [surname]
[email address]

---

## Appendix: the exact tables and fields

Read on 13 November 2026 from each table's file on the data machine (its header's title, its columns, and for a series table the variables and units in NYISO's rows, found by the entity, grid or market column). A table whose rows name no grid holds a figure computed across grids.

### `nyiso_dam_zone_prices`

- Energy Research Warehouse (ERW): NYISO day-ahead market LBMPs, 11 load zones
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- NYISO's rows: 19,283; variables: `lmp_dam` (USD/MWh)

### `nyiso_rtm_zone_prices`

- Energy Research Warehouse (ERW): NYISO real-time (RTD) LBMPs, 11 load zones, 15-minute means of 5-minute prices
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- NYISO's rows: 73,964; variables: `lmp_rtm_15m_mean` (USD/MWh)

### `nyiso_dam_cleared_energy`

- Energy Research Warehouse (ERW): NYISO, load scheduled in the day-ahead market by hour, system-wide (P-30, Day-Ahead Market Daily Energy Report, Total Load Scheduled) (session 136)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- NYISO's rows: 10,080; variables: `dam_cleared_energy` (MW)

### `nyiso_as_prices`

- Energy Research Warehouse (ERW): NYISO day-ahead ancillary service prices, hourly, by reserve region
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- NYISO's rows: 293,376; variables: `as_price_dam_nsync10` (USD/MW-hour); `as_price_dam_op30` (USD/MW-hour); `as_price_dam_reg` (USD/MW-hour); `as_price_dam_spin10` (USD/MW-hour)

### `nyiso_zone_load_hourly`

- Energy Research Warehouse (ERW): NYISO, hourly load by zone, the integrated real-time actual load of its eleven load zones (P-58C, palIntegrated) (session 138)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- NYISO's rows: 753,291; variables: `load` (MW)

### `nyiso_interconnection_queue`

- Energy Research Warehouse (ERW): NYISO interconnection queue
- Columns: entity_id, entity_type, name, geo, lat, lon, capacity_mw, status, status_date, operator, source, source_url, retrieved_at, vintage, queue_id, county, state, poi, zone, transmission_owner, fuel_technology, iso_status, queue_date, proposed_in_service_date, actual_in_service_date, withdrawn_date

### `nyiso_load_queue`

- Energy Research Warehouse (ERW): NYISO load interconnection requests
- Columns: entity_id, entity_type, name, geo, lat, lon, capacity_mw, status, status_date, operator, source, source_url, retrieved_at, vintage, workbook_last_modified, sheet, sheet_row, queue_id, county, state, poi, zone, zone_entity, transmission_owner, affected_transmission_owner, end_use, end_use_words, record_type, type_fuel, iso_status, iso_status_words, sis_bundle, availability_of_studies, queue_date_printed, queue_date, last_updated_printed, last_updated_date, ia_tender_printed, ia_tender_date, fs_completion_printed, fs_completion_date, proposed_initial_backfeed_printed, proposed_initial_backfeed_date, proposed_initial_backfeed_month

### `iso_hub_prices_history`

- Energy Research Warehouse (ERW): main-hub day-ahead and real-time prices, history from 2023-07-06 (session 49 from 2025-09-01; session 64 the year before, from 2024-09-01): CAISO SP15 and NP15, MISO Indiana Hub, NYISO N.Y.C., ISO-NE .H.INTERNAL_HUB, SPP SPPNORTH_HUB
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- NYISO's rows: 92,285; variables: `lmp_dam` (USD/MWh); `lmp_rtm_15m_mean` (USD/MWh)

### `iso_zone_prices_history`

- Energy Research Warehouse (ERW): zone and hub prices, history from 2019 (session 140): NYISO's eleven load zones, CAISO ZP26 (TH_ZP26_GEN-APND) and SPP South (SPPSOUTH_HUB), day-ahead and real-time. ISO-NE's eight load zones are in isone_zone_prices_history: the same columns, internal (ISO-NE's noti
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- NYISO's rows: 1,493,734; variables: `lmp_dam` (USD/MWh); `lmp_rtm` (USD/MWh)

### `iso_rt_top_intervals`

- Energy Research Warehouse (ERW): the 10 highest real-time intervals of each ISO's latest 7 complete local days, all hubs (derived; platform tool 24)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- NYISO's rows: 10; variables: `rt_price_top10_week` (USD/MWh)

### `iso_trader_daily`

- Energy Research Warehouse (ERW): the trader view, daily metrics per hub, every ISO (derived; platform tool 24)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- NYISO's rows: 6,534; variables: `da_mean_usd` (USD/MWh); `da_offpeak_mean_usd` (USD/MWh); `da_onpeak_mean_usd` (USD/MWh); `da_rt_spread_max_usd` (USD/MWh); `da_rt_spread_mean_usd` (USD/MWh); `da_volatility_30d_usd` (USD/MWh); `hours_rt_over_da_50` (count); `implied_heat_rate` (MMBtu/MWh); `rt_mean_usd` (USD/MWh)

### `hub_price_comparison`

- Energy Research Warehouse (ERW): where power is cheap, every public hub and zone price held, compared over twelve months and over the last whole month (session 96)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- NYISO's rows: 168; variables: `dam_above_200_hours_share_pct` (pct); `dam_avg_price` (USD/MWh); `dam_day_spread_top4_bottom4` (USD/MWh); `dam_hours_held` (count); `dam_hours_in_window` (count); `dam_negative_hours_share_pct` (pct); `grid_carbon_days_held` (count); `grid_carbon_intensity` (kgCO2/MWh); `rtm_above_200_hours_share_pct` (pct); `rtm_avg_price` (USD/MWh); `rtm_day_spread_top4_bottom4` (USD/MWh); `rtm_hours_held` (count); `rtm_hours_in_window` (count); `rtm_negative_hours_share_pct` (pct)

### `price_board_latest`

- Energy Research Warehouse (ERW): price board, latest day per hub and zone, day-ahead and real-time (derived)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- NYISO's rows: 924; variables: `da_avg_30d` (USD/MWh); `da_avg_7d` (USD/MWh); `da_daily_mean` (USD/MWh); `da_day_change` (USD/MWh); `da_day_change_pct` (pct); `da_days_30d` (count); `da_days_7d` (count); `da_intervals_30d` (count); `da_latest_day_mean` (USD/MWh); `da_latest_interval` (USD/MWh); `da_max_30d` (USD/MWh); `da_min_30d` (USD/MWh); `da_minus_rt` (USD/MWh); `da_previous_day_mean` (USD/MWh); `rt_avg_30d` (USD/MWh); `rt_avg_7d` (USD/MWh); `rt_daily_mean` (USD/MWh); `rt_day_change` (USD/MWh); `rt_day_change_pct` (pct); `rt_days_30d` (count); `rt_days_7d` (count); `rt_intervals_30d` (count); `rt_latest_day_mean` (USD/MWh); `rt_latest_interval` (USD/MWh); `rt_max_30d` (USD/MWh); `rt_min_30d` (USD/MWh); `rt_previous_day_mean` (USD/MWh)

### `price_board_peak_offpeak`

- Energy Research Warehouse (ERW): price board, peak and off-peak means per ISO main hub (derived)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- NYISO's rows: 732; variables: `da_all_mean` (USD/MWh); `da_offpeak_intervals` (count); `da_offpeak_mean` (USD/MWh); `da_peak_intervals` (count); `da_peak_mean` (USD/MWh); `da_peak_minus_offpeak` (USD/MWh); `rt_all_mean` (USD/MWh); `rt_offpeak_intervals` (count); `rt_offpeak_mean` (USD/MWh); `rt_peak_intervals` (count); `rt_peak_mean` (USD/MWh); `rt_peak_minus_offpeak` (USD/MWh)

### `price_board_spreads`

- Energy Research Warehouse (ERW): price board, spark spreads, implied heat rates, Henry Hub and Brent minus WTI, daily (derived)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_gas_date
- NYISO's rows: 219; variables: `da_daily_mean` (USD/MWh); `implied_heat_rate` (MMBtu/MWh); `spark_spread_7` (USD/MWh)

### `scarcity_hours_by_grid`

- Energy Research Warehouse (ERW): each grid's own scarcity signal beside the USD 1,000 price count, hour by hour (derived, session 254)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_detail
- NYISO's rows: none found by entity or grid column (the grid enters through a derived figure)

### `grid_stress_days`

- Energy Research Warehouse (ERW): stress days of the grids by one rule (session 306); docs/methods/stress_days.md; the rule docs/methods/battery_stress_days.md
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_reason, x_event, x_trailing_p98, x_trailing_days, x_notices
- NYISO's rows: 10; variables: `stress_day` (USD/MWh)

### `event_window_daily`

- Energy Research Warehouse (ERW): event windows, daily figures around an event and the same calendar days of earlier years (Historical Event Analyzer v0, derived, session 36B)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba, event
- NYISO's rows: 162; variables: `da_max` (USD/MWh); `da_mean` (USD/MWh); `rt_max` (USD/MWh); `rt_mean` (USD/MWh)

### `event_study_estimates`

- Energy Research Warehouse (ERW): event studies, the estimated effect of each event on each grid's daily demand served and ERCOT's daily hub price (derived, research, session 47)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba, event, x_std_error, x_ci_low, x_ci_high, x_n, x_spec, x_term
- NYISO's rows: 13; variables: `rt_mean_counterfactual_mean` (USD/MWh); `rt_mean_effect_day` (USD/MWh); `rt_mean_effect_pooled` (USD/MWh)

### `merchant_revenue_monthly`

- Energy Research Warehouse (ERW): merchant revenue per MW at each ISO's main hub, by asset type and month (derived, session 51, the seller's side of the cost of power)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba
- NYISO's rows: 780; variables: `battery_2h_capture_price` (USD/MWh); `battery_2h_capture_rate` (pct); `battery_2h_energy_per_mw` (MWh/MW); `battery_2h_flat_price` (USD/MWh); `battery_2h_hours` (count); `battery_2h_revenue_per_mw` (USD/MW); `battery_2h_sales_per_mw` (USD/MW); `battery_4h_capture_price` (USD/MWh); `battery_4h_capture_rate` (pct); `battery_4h_energy_per_mw` (MWh/MW); `battery_4h_flat_price` (USD/MWh); `battery_4h_hours` (count); `battery_4h_revenue_per_mw` (USD/MW); `battery_4h_sales_per_mw` (USD/MW); `flat_price` (USD/MWh); `hours_in_month` (count); `peaker_capture_price` (USD/MWh); `peaker_capture_rate` (pct); `peaker_energy_per_mw` (MWh/MW); `peaker_flat_price` (USD/MWh); `peaker_hours` (count); `peaker_revenue_per_mw` (USD/MW); `peaker_sales_per_mw` (USD/MW); `wind_capture_price` (USD/MWh); `wind_capture_rate` (pct); `wind_energy_per_mw` (MWh/MW); `wind_flat_price` (USD/MWh); `wind_hours` (count); `wind_revenue_per_mw` (USD/MW); `wind_sales_per_mw` (USD/MW)

### `battery_stack_review_monthly`

- Energy Research Warehouse (ERW): the battery revenue stack on the grids in review (NYISO, SPP), energy and ancillary services co-optimized, per MW, by market, hub, duration (2, 4, 8 hours), strategy and local month (derived, session 86)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_strategy, x_duration_hours, x_metric
- NYISO's rows: 1,716; variables: `dayahead_2h_days_held` (count); `dayahead_2h_days_in_month` (count); `dayahead_2h_days_left_out` (count); `dayahead_2h_days_left_out_ancillary` (count); `dayahead_2h_days_left_out_energy` (count); `dayahead_2h_discharged_mwh_per_mw` (MWh/MW); `dayahead_2h_revenue_ancillary_usd_per_mw` (USD/MW); `dayahead_2h_revenue_energy_usd_per_mw` (USD/MW); `dayahead_2h_revenue_reg_usd_per_mw` (USD/MW); `dayahead_2h_revenue_spin_usd_per_mw` (USD/MW); `dayahead_2h_revenue_total_usd_per_mw` (USD/MW); `dayahead_4h_days_held` (count); `dayahead_4h_days_in_month` (count); `dayahead_4h_days_left_out` (count); `dayahead_4h_days_left_out_ancillary` (count); `dayahead_4h_days_left_out_energy` (count); `dayahead_4h_discharged_mwh_per_mw` (MWh/MW); `dayahead_4h_revenue_ancillary_usd_per_mw` (USD/MW); `dayahead_4h_revenue_energy_usd_per_mw` (USD/MW); `dayahead_4h_revenue_reg_usd_per_mw` (USD/MW); `dayahead_4h_revenue_spin_usd_per_mw` (USD/MW); `dayahead_4h_revenue_total_usd_per_mw` (USD/MW); `dayahead_8h_days_held` (count); `dayahead_8h_days_in_month` (count); `dayahead_8h_days_left_out` (count); `dayahead_8h_days_left_out_ancillary` (count); `dayahead_8h_days_left_out_energy` (count); `dayahead_8h_discharged_mwh_per_mw` (MWh/MW); `dayahead_8h_revenue_ancillary_usd_per_mw` (USD/MW); `dayahead_8h_revenue_energy_usd_per_mw` (USD/MW); `dayahead_8h_revenue_reg_usd_per_mw` (USD/MW); `dayahead_8h_revenue_spin_usd_per_mw` (USD/MW); `dayahead_8h_revenue_total_usd_per_mw` (USD/MW); `foresight_2h_days_held` (count); `foresight_2h_days_in_month` (count); `foresight_2h_days_left_out` (count); `foresight_2h_days_left_out_ancillary` (count); `foresight_2h_days_left_out_energy` (count); `foresight_2h_discharged_mwh_per_mw` (MWh/MW); `foresight_2h_revenue_ancillary_usd_per_mw` (USD/MW); `foresight_2h_revenue_energy_usd_per_mw` (USD/MW); `foresight_2h_revenue_reg_usd_per_mw` (USD/MW); `foresight_2h_revenue_spin_usd_per_mw` (USD/MW); `foresight_2h_revenue_total_usd_per_mw` (USD/MW); `foresight_4h_days_held` (count); `foresight_4h_days_in_month` (count); `foresight_4h_days_left_out` (count); `foresight_4h_days_left_out_ancillary` (count); `foresight_4h_days_left_out_energy` (count); `foresight_4h_discharged_mwh_per_mw` (MWh/MW); `foresight_4h_revenue_ancillary_usd_per_mw` (USD/MW); `foresight_4h_revenue_energy_usd_per_mw` (USD/MW); `foresight_4h_revenue_reg_usd_per_mw` (USD/MW); `foresight_4h_revenue_spin_usd_per_mw` (USD/MW); `foresight_4h_revenue_total_usd_per_mw` (USD/MW); `foresight_8h_days_held` (count); `foresight_8h_days_in_month` (count); `foresight_8h_days_left_out` (count); `foresight_8h_days_left_out_ancillary` (count); `foresight_8h_days_left_out_energy` (count); `foresight_8h_discharged_mwh_per_mw` (MWh/MW); `foresight_8h_revenue_ancillary_usd_per_mw` (USD/MW); `foresight_8h_revenue_energy_usd_per_mw` (USD/MW); `foresight_8h_revenue_reg_usd_per_mw` (USD/MW); `foresight_8h_revenue_spin_usd_per_mw` (USD/MW); `foresight_8h_revenue_total_usd_per_mw` (USD/MW)

### `clean_energy_hourly`

- Energy Research Warehouse (ERW): the carbon-free share of each grid's generation by hour, the seven ISO grids (derived, session 122)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_carbon_free_mwh, x_generation_mwh, x_side
- NYISO's rows: none found by entity or grid column (the grid enters through a derived figure)

### `clean_energy_summary`

- Energy Research Warehouse (ERW): how clean each grid's generation is by month and year, what an annual clean purchase covers hour by hour, and what moving load into the cleanest hours changes (derived, session 122)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- NYISO's rows: none found by entity or grid column (the grid enters through a derived figure)

### `cost_of_power_carbon`

- Energy Research Warehouse (ERW): load-weighted real-time price and carbon intensity per ISO and month (cost-of-power model v0, derived, session 37)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba
- NYISO's rows: 69; variables: `intensity_demand` (kgCO2/MWh); `intensity_generation` (kgCO2/MWh); `rt_load_weighted` (USD/MWh)

### `cost_of_power_hourly_profile`

- Energy Research Warehouse (ERW): average real-time price by local hour of day and month, per ISO main hub (cost-of-power model v0, derived, session 37)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba
- NYISO's rows: 624; variables: `rt_days_h00` (count); `rt_days_h01` (count); `rt_days_h02` (count); `rt_days_h03` (count); `rt_days_h04` (count); `rt_days_h05` (count); `rt_days_h06` (count); `rt_days_h07` (count); `rt_days_h08` (count); `rt_days_h09` (count); `rt_days_h10` (count); `rt_days_h11` (count); `rt_days_h12` (count); `rt_days_h13` (count); `rt_days_h14` (count); `rt_days_h15` (count); `rt_days_h16` (count); `rt_days_h17` (count); `rt_days_h18` (count); `rt_days_h19` (count); `rt_days_h20` (count); `rt_days_h21` (count); `rt_days_h22` (count); `rt_days_h23` (count); `rt_mean_h00` (USD/MWh); `rt_mean_h01` (USD/MWh); `rt_mean_h02` (USD/MWh); `rt_mean_h03` (USD/MWh); `rt_mean_h04` (USD/MWh); `rt_mean_h05` (USD/MWh); `rt_mean_h06` (USD/MWh); `rt_mean_h07` (USD/MWh); `rt_mean_h08` (USD/MWh); `rt_mean_h09` (USD/MWh); `rt_mean_h10` (USD/MWh); `rt_mean_h11` (USD/MWh); `rt_mean_h12` (USD/MWh); `rt_mean_h13` (USD/MWh); `rt_mean_h14` (USD/MWh); `rt_mean_h15` (USD/MWh); `rt_mean_h16` (USD/MWh); `rt_mean_h17` (USD/MWh); `rt_mean_h18` (USD/MWh); `rt_mean_h19` (USD/MWh); `rt_mean_h20` (USD/MWh); `rt_mean_h21` (USD/MWh); `rt_mean_h22` (USD/MWh); `rt_mean_h23` (USD/MWh)

### `cost_of_power_monthly`

- Energy Research Warehouse (ERW): cost of power per ISO main hub and month, load-weighted and simple averages of the real-time and day-ahead price (cost-of-power model v0, derived, session 37)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba
- NYISO's rows: 234; variables: `da_hours` (count); `da_load_weighted` (USD/MWh); `da_shape_premium` (USD/MWh); `da_simple_mean` (USD/MWh); `hours_in_month` (count); `rt_hours` (count); `rt_load_weighted` (USD/MWh); `rt_shape_premium` (USD/MWh); `rt_simple_mean` (USD/MWh)

### `datacenter_queue_positions`

- Energy Research Warehouse (ERW): ISO queue positions that name a datacenter or a large load (session 22)
- Columns: entity_id, entity_type, name, geo, lat, lon, capacity_mw, status, status_date, operator, source, source_url, retrieved_at, vintage, queue_id, county, state, poi, zone, transmission_owner, fuel_technology, iso_status, queue_date, proposed_in_service_date, actual_in_service_date, withdrawn_date, matched

### `datacenter_facilities`

- Energy Research Warehouse (ERW): Datacenter facilities from the news, the operators and the ISO queues (the datacenter power tracker, platform tool 4; session 22)
- Columns: entity_id, entity_type, name, geo, lat, lon, capacity_mw, status, status_date, operator, source, source_url, retrieved_at, vintage, kind, kinds, site_type, developer, state, county, city, country, mw, mw_span, mw_from, queue_mw, project_status, phase, planned_year, power_source, utility, confidence, first_story_at, geo_precision, geo_note, n_members, member_ids, source_urls, grid, grid_basis, mw_basis, power_kind, energized_year, utility_eia861, utility_eia861_number, utilities_in_county

### `ai_power_regions`

- Energy Research Warehouse (ERW): where the next gigawatts for AI can come from, one row of measures per ISO region (derived, session 62)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_window, x_note
- NYISO's rows: none found by entity or grid column (the grid enters through a derived figure)

### `iso_queue_statistics`

- Energy Research Warehouse (ERW): interconnection queue statistics by ISO and entry year (derived, session 348)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_iso, x_entry_year, x_rule, x_input_run
- NYISO's rows: 352; variables: `mw_entered` (MW); `mw_operating` (MW); `mw_waiting` (MW); `mw_withdrawn` (MW); `positions_entered` (count); `positions_operating` (count); `positions_status_not_stated` (count); `positions_waiting` (count); `positions_withdrawn` (count); `wait_positions` (count); `wait_years_mean` (year); `wait_years_median` (year); `withdrawal_rate` (ratio)

### `iso_all_capacity_prices`

- Energy Research Warehouse (ERW): capacity prices, PJM Base Residual Auction, NYISO ICAP spot auction, ISO-NE Forward Capacity Auction, MISO Planning Resource Auction
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_auction, x_period_end, x_note, x_license
- NYISO's rows: 424; variables: `capacity_price` (USD/kW-month)

---

## The first draft (session 378), kept as it was

# Draft: permission to republish NYISO's public market data in a research warehouse

Written by session 378 (20 October 2026) for Samuel to send himself, from his own address. Nothing here was sent. Fill what stands in brackets first.

Why it is needed: NYISO's legal notice (read 5 of `warehouse/metadata/license_reads.csv`, https://www.nyiso.com/legal-notice, 12 October 2026; a copy saved on 7 October under `warehouse/raw/nyiso_load_queue/`) says: "Access to this Web site does not confer any license or ownership interest in either the form or content of the Web site, including any confidential or proprietary information or intellectual property of any kind or nature, and the NYISO hereby expressly reserves such rights and property in its entirety." By the ruling of 12 October 2026 (session 207) the tables below show "license needed" in place of NYISO's numbers from 21 October until a permission is recorded in `warehouse/metadata/license_status.csv`. The page names no contact: the address below is to be found.

---

**To:** [NYISO's legal or market data contact: the page names none]

**Subject:** Permission to republish NYISO's public market data in a research data warehouse

Hello,

I am Samuel [surname], [role and affiliation]. I run the Energy Research Warehouse (ERW), an open, noncommercial record of the US energy system: prices, flows, projects and policy, each number traced to its source. The code and the documentation are public at github.com/SamuelEnrique/erw.

What we hold of yours, all from NYISO's public pages and reports:

- NYISO's own tables: day-ahead and real-time zonal prices (`nyiso_dam_zone_prices`, `nyiso_rtm_zone_prices`), day-ahead cleared energy (`nyiso_dam_cleared_energy`), ancillary service prices (`nyiso_as_prices`), hourly zone load (`nyiso_zone_load_hourly`), the interconnection queue (`nyiso_interconnection_queue`) and the large-load queue (`nyiso_load_queue`).
- NYISO's rows in tables that compare grids: `iso_hub_prices_history`, `iso_zone_prices_history`, `iso_rt_top_intervals`, `iso_trader_daily`, `hub_price_comparison`, `price_board_latest`, `price_board_peak_offpeak`, `price_board_spreads`, `scarcity_hours_by_grid`, `grid_stress_days`, `event_window_daily`, `event_study_estimates`, `merchant_revenue_monthly`, `battery_stack_review_monthly`, `clean_energy_hourly`, `clean_energy_summary`, `cost_of_power_carbon`, `cost_of_power_hourly_profile`, `cost_of_power_monthly`, `datacenter_queue_positions`, `datacenter_facilities`, `ai_power_regions`.
- NYISO's market notices as news items (`news_index`).

What I am asking for:

- Read those public reports by script, at the rate and times NYISO sets.
- Publish the values as NYISO states them, and figures computed from them (averages, spreads, comparisons with other grids), in tables, charts and downloads, with NYISO named as the source and a link to the report.
- The same for a citable archive of those tables (the ERW's dataset on Redivis), version by version.
- [Only if the ERW may sell anything: the same in a paid product. Strike this line otherwise.]

What we offer:

- Attribution to NYISO beside every figure, in the words you prefer.
- A link to NYISO's own report for every series.
- No resale of NYISO's raw files. We publish what we compute from them.
- Any request rate, time of day or file route you set; a bulk file or an API key if you prefer.

If a license or a fee applies, I would be glad to know its terms.

Thank you,
Samuel [surname]
[email address]
