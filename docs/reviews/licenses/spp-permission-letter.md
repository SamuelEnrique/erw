# Draft: SPP's written authorization, should the ERW ever be a commercial publication

Written by session 378 (20 October 2026), brought up to date by chain 229, session 4104 (13 November 2026), for Samuel to send himself, from his own address. Nothing here was sent. Fill what stands in brackets first.

Why it is needed: SPP's terms, read again on 13 November 2026 (read 1671, https://www.spp.org/terms-conditions/; the sentence of read 6 is still on the page), allow the ERW as it is today and ask written authorization for any commercial use: "Permission is implicitly granted to copy and distribute (via computer network or printed form) in whole or in part (with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication (printed or otherwise) or when the author(s) or SPP will be quoted in commercial materials, forums or publications. Any commercial use of these materials requires prior, express written authorization from the author(s) or a duly authorized officer of SPP." The letter is needed only if the ERW sells anything.

Who to write to: SPP Communications, communication@spp.org, 201 Worthen Drive, Little Rock, AR 72223-4936, (501) 614-3200 (its terms page names the address for copyright inquiries and prints the email, read 1671, 13 November 2026).

---

**To:** SPP Communications, communication@spp.org, 201 Worthen Drive, Little Rock, AR 72223-4936,

**Subject:** Written authorization for SPP's public market data in an open research data warehouse

Hello,

I am Samuel [surname], [role] at Stanford University. I run the Energy Research Warehouse (ERW), an open, citable research warehouse of the US energy system at Stanford: prices, flows, projects and policy, each number traced to its source report. Its tables are versioned and citable as a dataset on Redivis, and its code and documentation are public at github.com/SamuelEnrique/erw. A public site shows figures derived from the tables (averages, spreads, comparisons between grids); it is in review and not yet open to visitors. The ERW sells nothing.

What we hold from SPP, all from SPP's public pages and reports (33 tables; the fields of each are listed in the appendix below):

- `spp_as_prices`, `spp_as_quantities`, `spp_curtailment_daily`, `spp_dam_cleared_energy`, `spp_interconnection_queue`, `energy_projects`, `iso_curtailment_monthly`, `iso_queue_snapshot_summary`, `price_years_by_window`, `battery_stack_review_monthly`, `iso_hub_prices_history`, `iso_zone_prices_history`, `iso_trader_daily`, `hub_price_comparison`, `price_board_latest`, `price_board_peak_offpeak`, `price_board_spreads`, `scarcity_hours_by_grid`, `grid_stress_days`, `event_window_daily`, `event_study_estimates`, `merchant_revenue_monthly`, `clean_energy_hourly`, `clean_energy_summary`, `cost_of_power_carbon`, `cost_of_power_hourly_profile`, `cost_of_power_monthly`, `datacenter_queue_positions`, `datacenter_facilities`, `ai_power_regions`, `iso_queue_statistics`, `iso_dam_hub_prices`, `iso_rtm_hub_prices`.

What I am asking for:

- Today the ERW is noncommercial and cites SPP as your terms ask; nothing is needed for that.
- Should the ERW ever be part of a commercial publication: SPP's written authorization to publish the values in the tables listed below, and figures computed from them, with SPP cited and a link to each report.
- The same for the ERW's citable dataset on Redivis.

What we offer:

- SPP named as the source beside every figure, in the words you prefer, with a link to SPP's own report.
- No resale or redistribution of SPP's raw files as such: we publish the values in our tables and what we compute from them.
- Any request rate, time of day or file route you set; a bulk file or a key if you prefer.
- A line in our records for your answer, so that every table shows the permission it rests on.

If a license or a fee applies, I would be glad to know its terms.

Thank you,
Samuel [surname]
[email address]

---

## Appendix: the exact tables and fields

Read on 13 November 2026 from each table's file on the data machine (its header's title, its columns, and for a series table the variables and units in SPP's rows, found by the entity, grid or market column). A table whose rows name no grid holds a figure computed across grids.

### `spp_as_prices`

- Energy Research Warehouse (ERW): SPP day-ahead operating reserve market clearing prices, hourly, the system rows
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- SPP's rows: 159,432; variables: `as_price_dam_rampdn` (USD/MW-hour); `as_price_dam_rampup` (USD/MW-hour); `as_price_dam_regdn` (USD/MW-hour); `as_price_dam_regup` (USD/MW-hour); `as_price_dam_spin` (USD/MW-hour); `as_price_dam_supp` (USD/MW-hour); `as_price_dam_uncup` (USD/MW-hour)

### `spp_as_quantities`

- Energy Research Warehouse (ERW): SPP day-ahead operating reserve quantities cleared, hourly, the system rows (session 100)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- SPP's rows: 159,768; variables: `quantity_mw_dam_rampdn` (MW); `quantity_mw_dam_rampup` (MW); `quantity_mw_dam_regdn` (MW); `quantity_mw_dam_regup` (MW); `quantity_mw_dam_spin` (MW); `quantity_mw_dam_supp` (MW); `quantity_mw_dam_uncup` (MW)

### `spp_curtailment_daily`

- Energy Research Warehouse (ERW): SPP wind and solar curtailment by balancing authority area, daily, MWh
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- SPP's rows: 38,632; variables: `curtailed_solar_economic_mwh` (MWh); `curtailed_solar_manual_mwh` (MWh); `curtailed_solar_mwh` (MWh); `curtailed_solar_redispatch_mwh` (MWh); `curtailed_wind_economic_mwh` (MWh); `curtailed_wind_manual_mwh` (MWh); `curtailed_wind_mwh` (MWh); `curtailed_wind_redispatch_mwh` (MWh)

### `spp_dam_cleared_energy`

- Energy Research Warehouse (ERW): SPP, demand cleared in the day-ahead market by hour and balancing authority area (Marketplace portal, Market Clearing, DA-MC files, Total Demand) (session 136)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- SPP's rows: 15,024; variables: `dam_cleared_energy` (MW)

### `spp_interconnection_queue`

- Energy Research Warehouse (ERW): SPP interconnection queue
- Columns: entity_id, entity_type, name, geo, lat, lon, capacity_mw, status, status_date, operator, source, source_url, retrieved_at, vintage, queue_id, county, state, poi, zone, transmission_owner, fuel_technology, iso_status, queue_date, proposed_in_service_date, actual_in_service_date, withdrawn_date

### `energy_projects`

- Energy Research Warehouse (ERW): Energy projects for the project map: EIA-860M generators and ISO interconnection queue positions (derived, platform tool 3)
- Columns: entity_id, entity_type, name, geo, lat, lon, capacity_mw, status, status_date, operator, source, source_url, retrieved_at, vintage, project_id, kind, technology_group, mw, state, county, geo_precision, geo_note, operator_role, date, date_kind, technology, source_status, source_table

### `iso_curtailment_monthly`

- Energy Research Warehouse (ERW): Wind and solar curtailment by ISO, monthly, MWh (derived from the daily curtailment tables; platform tool 22)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- SPP's rows: 1,698; variables: `curtailed_solar_economic_mwh` (MWh); `curtailed_solar_manual_mwh` (MWh); `curtailed_solar_mwh` (MWh); `curtailed_solar_redispatch_mwh` (MWh); `curtailed_wind_economic_mwh` (MWh); `curtailed_wind_manual_mwh` (MWh); `curtailed_wind_mwh` (MWh); `curtailed_wind_redispatch_mwh` (MWh); `share_curtailed_mwh` (MWh); `share_curtailed_pct` (pct); `share_hours_held` (count); `share_hours_in_month` (count); `share_output_mwh` (MWh)

### `iso_queue_snapshot_summary`

- Energy Research Warehouse (ERW): the ISO interconnection queues summarized from their own snapshots: MW and requests by grid, status and fuel group; entered, completed and withdrawn by year; months from request to in-service (derived, session 2953)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_grid, x_fuel_group, x_snapshot
- SPP's rows: 72; variables: `active_count` (count); `active_mw` (MW); `completed_count` (count); `completed_mw` (MW); `suspended_count` (count); `suspended_mw` (MW); `unknown_count` (count); `unknown_mw` (MW); `withdrawn_count` (count); `withdrawn_mw` (MW)

### `price_years_by_window`

- Energy Research Warehouse (ERW): the price years, each economics page's figure under every window of years held (derived, session 357)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_tool, x_grid, x_config, x_window, x_window_kind, x_left_out, x_from, x_to, x_months, x_complete
- SPP's rows: 138; variables: `battery_dayahead_2h_all` (USD/kW-year); `battery_dayahead_2h_last_12` (USD/kW-year); `battery_dayahead_2h_year_2024` (USD/kW-year); `battery_dayahead_2h_year_2025` (USD/kW-year); `battery_dayahead_2h_year_2026` (USD/kW-year); `battery_dayahead_4h_all` (USD/kW-year); `battery_dayahead_4h_last_12` (USD/kW-year); `battery_dayahead_4h_year_2024` (USD/kW-year); `battery_dayahead_4h_year_2025` (USD/kW-year); `battery_dayahead_4h_year_2026` (USD/kW-year); `battery_dayahead_8h_all` (USD/kW-year); `battery_dayahead_8h_last_12` (USD/kW-year); `battery_dayahead_8h_year_2024` (USD/kW-year); `battery_dayahead_8h_year_2025` (USD/kW-year); `battery_dayahead_8h_year_2026` (USD/kW-year); `battery_foresight_2h_all` (USD/kW-year); `battery_foresight_2h_last_12` (USD/kW-year); `battery_foresight_2h_year_2024` (USD/kW-year); `battery_foresight_2h_year_2025` (USD/kW-year); `battery_foresight_2h_year_2026` (USD/kW-year); `battery_foresight_4h_all` (USD/kW-year); `battery_foresight_4h_last_12` (USD/kW-year); `battery_foresight_4h_year_2024` (USD/kW-year); `battery_foresight_4h_year_2025` (USD/kW-year); `battery_foresight_4h_year_2026` (USD/kW-year); `battery_foresight_8h_all` (USD/kW-year); `battery_foresight_8h_last_12` (USD/kW-year); `battery_foresight_8h_year_2024` (USD/kW-year); `battery_foresight_8h_year_2025` (USD/kW-year); `battery_foresight_8h_year_2026` (USD/kW-year); `datacenter_flat_da_all` (USD/MWh); `datacenter_flat_da_avg_3y` (USD/MWh); `datacenter_flat_da_avg_7y` (USD/MWh); `datacenter_flat_da_last_12` (USD/MWh); `datacenter_flat_da_year_2019` (USD/MWh); `datacenter_flat_da_year_2020` (USD/MWh); `datacenter_flat_da_year_2021` (USD/MWh); `datacenter_flat_da_year_2022` (USD/MWh); `datacenter_flat_da_year_2023` (USD/MWh); `datacenter_flat_da_year_2024` (USD/MWh); `datacenter_flat_da_year_2025` (USD/MWh); `datacenter_flat_da_year_2026` (USD/MWh); `datacenter_flat_rt_all` (USD/MWh); `datacenter_flat_rt_last_12` (USD/MWh); `datacenter_flat_rt_year_2024` (USD/MWh); `datacenter_flat_rt_year_2025` (USD/MWh); `datacenter_flat_rt_year_2026` (USD/MWh); `datacenter_hours_da_all` (USD/MWh); `datacenter_hours_da_avg_3y` (USD/MWh); `datacenter_hours_da_avg_7y` (USD/MWh); `datacenter_hours_da_last_12` (USD/MWh); `datacenter_hours_da_year_2019` (USD/MWh); `datacenter_hours_da_year_2020` (USD/MWh); `datacenter_hours_da_year_2021` (USD/MWh); `datacenter_hours_da_year_2022` (USD/MWh); `datacenter_hours_da_year_2023` (USD/MWh); `datacenter_hours_da_year_2024` (USD/MWh); `datacenter_hours_da_year_2025` (USD/MWh); `datacenter_hours_da_year_2026` (USD/MWh); `datacenter_hours_rt_all` (USD/MWh); `datacenter_hours_rt_last_12` (USD/MWh); `datacenter_hours_rt_year_2024` (USD/MWh); `datacenter_hours_rt_year_2025` (USD/MWh); `datacenter_hours_rt_year_2026` (USD/MWh); `datacenter_share_da_all` (USD/MWh); `datacenter_share_da_avg_3y` (USD/MWh); `datacenter_share_da_avg_7y` (USD/MWh); `datacenter_share_da_last_12` (USD/MWh); `datacenter_share_da_year_2019` (USD/MWh); `datacenter_share_da_year_2020` (USD/MWh); `datacenter_share_da_year_2021` (USD/MWh); `datacenter_share_da_year_2022` (USD/MWh); `datacenter_share_da_year_2023` (USD/MWh); `datacenter_share_da_year_2024` (USD/MWh); `datacenter_share_da_year_2025` (USD/MWh); `datacenter_share_da_year_2026` (USD/MWh); `datacenter_share_rt_all` (USD/MWh); `datacenter_share_rt_last_12` (USD/MWh); `datacenter_share_rt_year_2024` (USD/MWh); `datacenter_share_rt_year_2025` (USD/MWh); `datacenter_share_rt_year_2026` (USD/MWh); `datacenter_shift_da_all` (USD/MWh); `datacenter_shift_da_avg_3y` (USD/MWh); `datacenter_shift_da_avg_7y` (USD/MWh); `datacenter_shift_da_last_12` (USD/MWh); `datacenter_shift_da_year_2019` (USD/MWh); `datacenter_shift_da_year_2020` (USD/MWh); `datacenter_shift_da_year_2021` (USD/MWh); `datacenter_shift_da_year_2022` (USD/MWh); `datacenter_shift_da_year_2023` (USD/MWh); `datacenter_shift_da_year_2024` (USD/MWh); `datacenter_shift_da_year_2025` (USD/MWh); `datacenter_shift_da_year_2026` (USD/MWh); `datacenter_shift_rt_all` (USD/MWh); `datacenter_shift_rt_last_12` (USD/MWh); `datacenter_shift_rt_year_2024` (USD/MWh); `datacenter_shift_rt_year_2025` (USD/MWh); `datacenter_shift_rt_year_2026` (USD/MWh); `generator_battery_all` (USD/kW-year); `generator_battery_last_12` (USD/kW-year); `generator_battery_year_2024` (USD/kW-year); `generator_battery_year_2025` (USD/kW-year); `generator_battery_year_2026` (USD/kW-year); `generator_peaker_all` (USD/kW-year); `generator_peaker_last_12` (USD/kW-year); `generator_peaker_year_2024` (USD/kW-year); `generator_peaker_year_2025` (USD/kW-year); `generator_peaker_year_2026` (USD/kW-year); `generator_solar_all` (USD/kW-year); `generator_solar_last_12` (USD/kW-year); `generator_solar_year_2024` (USD/kW-year); `generator_solar_year_2025` (USD/kW-year); `generator_solar_year_2026` (USD/kW-year); `generator_wind_all` (USD/kW-year); `generator_wind_last_12` (USD/kW-year); `generator_wind_year_2024` (USD/kW-year); `generator_wind_year_2025` (USD/kW-year); `generator_wind_year_2026` (USD/kW-year)

### `battery_stack_review_monthly`

- Energy Research Warehouse (ERW): the battery revenue stack on the grids in review (NYISO, SPP), energy and ancillary services co-optimized, per MW, by market, hub, duration (2, 4, 8 hours), strategy and local month (derived, session 86)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_strategy, x_duration_hours, x_metric
- SPP's rows: 2,028; variables: `dayahead_2h_days_held` (count); `dayahead_2h_days_in_month` (count); `dayahead_2h_days_left_out` (count); `dayahead_2h_days_left_out_ancillary` (count); `dayahead_2h_days_left_out_energy` (count); `dayahead_2h_discharged_mwh_per_mw` (MWh/MW); `dayahead_2h_revenue_ancillary_usd_per_mw` (USD/MW); `dayahead_2h_revenue_energy_usd_per_mw` (USD/MW); `dayahead_2h_revenue_regdn_usd_per_mw` (USD/MW); `dayahead_2h_revenue_regup_usd_per_mw` (USD/MW); `dayahead_2h_revenue_spin_usd_per_mw` (USD/MW); `dayahead_2h_revenue_supp_usd_per_mw` (USD/MW); `dayahead_2h_revenue_total_usd_per_mw` (USD/MW); `dayahead_4h_days_held` (count); `dayahead_4h_days_in_month` (count); `dayahead_4h_days_left_out` (count); `dayahead_4h_days_left_out_ancillary` (count); `dayahead_4h_days_left_out_energy` (count); `dayahead_4h_discharged_mwh_per_mw` (MWh/MW); `dayahead_4h_revenue_ancillary_usd_per_mw` (USD/MW); `dayahead_4h_revenue_energy_usd_per_mw` (USD/MW); `dayahead_4h_revenue_regdn_usd_per_mw` (USD/MW); `dayahead_4h_revenue_regup_usd_per_mw` (USD/MW); `dayahead_4h_revenue_spin_usd_per_mw` (USD/MW); `dayahead_4h_revenue_supp_usd_per_mw` (USD/MW); `dayahead_4h_revenue_total_usd_per_mw` (USD/MW); `dayahead_8h_days_held` (count); `dayahead_8h_days_in_month` (count); `dayahead_8h_days_left_out` (count); `dayahead_8h_days_left_out_ancillary` (count); `dayahead_8h_days_left_out_energy` (count); `dayahead_8h_discharged_mwh_per_mw` (MWh/MW); `dayahead_8h_revenue_ancillary_usd_per_mw` (USD/MW); `dayahead_8h_revenue_energy_usd_per_mw` (USD/MW); `dayahead_8h_revenue_regdn_usd_per_mw` (USD/MW); `dayahead_8h_revenue_regup_usd_per_mw` (USD/MW); `dayahead_8h_revenue_spin_usd_per_mw` (USD/MW); `dayahead_8h_revenue_supp_usd_per_mw` (USD/MW); `dayahead_8h_revenue_total_usd_per_mw` (USD/MW); `foresight_2h_days_held` (count); `foresight_2h_days_in_month` (count); `foresight_2h_days_left_out` (count); `foresight_2h_days_left_out_ancillary` (count); `foresight_2h_days_left_out_energy` (count); `foresight_2h_discharged_mwh_per_mw` (MWh/MW); `foresight_2h_revenue_ancillary_usd_per_mw` (USD/MW); `foresight_2h_revenue_energy_usd_per_mw` (USD/MW); `foresight_2h_revenue_regdn_usd_per_mw` (USD/MW); `foresight_2h_revenue_regup_usd_per_mw` (USD/MW); `foresight_2h_revenue_spin_usd_per_mw` (USD/MW); `foresight_2h_revenue_supp_usd_per_mw` (USD/MW); `foresight_2h_revenue_total_usd_per_mw` (USD/MW); `foresight_4h_days_held` (count); `foresight_4h_days_in_month` (count); `foresight_4h_days_left_out` (count); `foresight_4h_days_left_out_ancillary` (count); `foresight_4h_days_left_out_energy` (count); `foresight_4h_discharged_mwh_per_mw` (MWh/MW); `foresight_4h_revenue_ancillary_usd_per_mw` (USD/MW); `foresight_4h_revenue_energy_usd_per_mw` (USD/MW); `foresight_4h_revenue_regdn_usd_per_mw` (USD/MW); `foresight_4h_revenue_regup_usd_per_mw` (USD/MW); `foresight_4h_revenue_spin_usd_per_mw` (USD/MW); `foresight_4h_revenue_supp_usd_per_mw` (USD/MW); `foresight_4h_revenue_total_usd_per_mw` (USD/MW); `foresight_8h_days_held` (count); `foresight_8h_days_in_month` (count); `foresight_8h_days_left_out` (count); `foresight_8h_days_left_out_ancillary` (count); `foresight_8h_days_left_out_energy` (count); `foresight_8h_discharged_mwh_per_mw` (MWh/MW); `foresight_8h_revenue_ancillary_usd_per_mw` (USD/MW); `foresight_8h_revenue_energy_usd_per_mw` (USD/MW); `foresight_8h_revenue_regdn_usd_per_mw` (USD/MW); `foresight_8h_revenue_regup_usd_per_mw` (USD/MW); `foresight_8h_revenue_spin_usd_per_mw` (USD/MW); `foresight_8h_revenue_supp_usd_per_mw` (USD/MW); `foresight_8h_revenue_total_usd_per_mw` (USD/MW)

### `iso_hub_prices_history`

- Energy Research Warehouse (ERW): main-hub day-ahead and real-time prices, history from 2023-07-06 (session 49 from 2025-09-01; session 64 the year before, from 2024-09-01): CAISO SP15 and NP15, MISO Indiana Hub, NYISO N.Y.C., ISO-NE .H.INTERNAL_HUB, SPP SPPNORTH_HUB
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- SPP's rows: 94,249; variables: `lmp_dam` (USD/MWh); `lmp_rtm_15m_mean` (USD/MWh)

### `iso_zone_prices_history`

- Energy Research Warehouse (ERW): zone and hub prices, history from 2019 (session 140): NYISO's eleven load zones, CAISO ZP26 (TH_ZP26_GEN-APND) and SPP South (SPPSOUTH_HUB), day-ahead and real-time. ISO-NE's eight load zones are in isone_zone_prices_history: the same columns, internal (ISO-NE's noti
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- SPP's rows: 68,135; variables: `lmp_dam` (USD/MWh)

### `iso_trader_daily`

- Energy Research Warehouse (ERW): the trader view, daily metrics per hub, every ISO (derived; platform tool 24)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- SPP's rows: 574; variables: `da_mean_usd` (USD/MWh); `da_offpeak_mean_usd` (USD/MWh); `da_onpeak_mean_usd` (USD/MWh); `da_volatility_30d_usd` (USD/MWh); `implied_heat_rate` (MMBtu/MWh)

### `hub_price_comparison`

- Energy Research Warehouse (ERW): where power is cheap, every public hub and zone price held, compared over twelve months and over the last whole month (session 96)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- SPP's rows: 35; variables: `dam_above_200_hours_share_pct` (pct); `dam_avg_price` (USD/MWh); `dam_day_spread_top4_bottom4` (USD/MWh); `dam_hours_held` (count); `dam_hours_in_window` (count); `dam_negative_hours_share_pct` (pct); `grid_carbon_days_held` (count); `grid_carbon_intensity` (kgCO2/MWh); `rtm_above_200_hours_share_pct` (pct); `rtm_avg_price` (USD/MWh); `rtm_day_spread_top4_bottom4` (USD/MWh); `rtm_hours_held` (count); `rtm_hours_in_window` (count); `rtm_negative_hours_share_pct` (pct)

### `price_board_latest`

- Energy Research Warehouse (ERW): price board, latest day per hub and zone, day-ahead and real-time (derived)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- SPP's rows: 152; variables: `da_avg_30d` (USD/MWh); `da_avg_7d` (USD/MWh); `da_daily_mean` (USD/MWh); `da_day_change` (USD/MWh); `da_day_change_pct` (pct); `da_days_30d` (count); `da_days_7d` (count); `da_intervals_30d` (count); `da_latest_day_mean` (USD/MWh); `da_latest_interval` (USD/MWh); `da_max_30d` (USD/MWh); `da_min_30d` (USD/MWh); `da_minus_rt` (USD/MWh); `da_previous_day_mean` (USD/MWh); `rt_avg_30d` (USD/MWh); `rt_avg_7d` (USD/MWh); `rt_daily_mean` (USD/MWh); `rt_day_change` (USD/MWh); `rt_day_change_pct` (pct); `rt_days_30d` (count); `rt_days_7d` (count); `rt_intervals_30d` (count); `rt_latest_day_mean` (USD/MWh); `rt_latest_interval` (USD/MWh); `rt_max_30d` (USD/MWh); `rt_min_30d` (USD/MWh); `rt_previous_day_mean` (USD/MWh)

### `price_board_peak_offpeak`

- Energy Research Warehouse (ERW): price board, peak and off-peak means per ISO main hub (derived)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- SPP's rows: 519; variables: `da_all_mean` (USD/MWh); `da_offpeak_intervals` (count); `da_offpeak_mean` (USD/MWh); `da_peak_intervals` (count); `da_peak_mean` (USD/MWh); `da_peak_minus_offpeak` (USD/MWh); `rt_all_mean` (USD/MWh); `rt_offpeak_intervals` (count); `rt_offpeak_mean` (USD/MWh); `rt_peak_intervals` (count); `rt_peak_mean` (USD/MWh); `rt_peak_minus_offpeak` (USD/MWh)

### `price_board_spreads`

- Energy Research Warehouse (ERW): price board, spark spreads, implied heat rates, Henry Hub and Brent minus WTI, daily (derived)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_gas_date
- SPP's rows: 216; variables: `da_daily_mean` (USD/MWh); `implied_heat_rate` (MMBtu/MWh); `spark_spread_7` (USD/MWh)

### `scarcity_hours_by_grid`

- Energy Research Warehouse (ERW): each grid's own scarcity signal beside the USD 1,000 price count, hour by hour (derived, session 254)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_detail
- SPP's rows: none found by entity or grid column (the grid enters through a derived figure)

### `grid_stress_days`

- Energy Research Warehouse (ERW): stress days of the grids by one rule (session 306); docs/methods/stress_days.md; the rule docs/methods/battery_stress_days.md
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_reason, x_event, x_trailing_p98, x_trailing_days, x_notices
- SPP's rows: 17; variables: `stress_day` (USD/MWh)

### `event_window_daily`

- Energy Research Warehouse (ERW): event windows, daily figures around an event and the same calendar days of earlier years (Historical Event Analyzer v0, derived, session 36B)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba, event
- SPP's rows: 128; variables: `da_max` (USD/MWh); `da_mean` (USD/MWh); `rt_max` (USD/MWh); `rt_mean` (USD/MWh)

### `event_study_estimates`

- Energy Research Warehouse (ERW): event studies, the estimated effect of each event on each grid's daily demand served and ERCOT's daily hub price (derived, research, session 47)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba, event, x_std_error, x_ci_low, x_ci_high, x_n, x_spec, x_term
- SPP's rows: 13; variables: `rt_mean_counterfactual_mean` (USD/MWh); `rt_mean_effect_day` (USD/MWh); `rt_mean_effect_pooled` (USD/MWh)

### `merchant_revenue_monthly`

- Energy Research Warehouse (ERW): merchant revenue per MW at each ISO's main hub, by asset type and month (derived, session 51, the seller's side of the cost of power)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba
- SPP's rows: 962; variables: `battery_2h_capture_price` (USD/MWh); `battery_2h_capture_rate` (pct); `battery_2h_energy_per_mw` (MWh/MW); `battery_2h_flat_price` (USD/MWh); `battery_2h_hours` (count); `battery_2h_revenue_per_mw` (USD/MW); `battery_2h_sales_per_mw` (USD/MW); `battery_4h_capture_price` (USD/MWh); `battery_4h_capture_rate` (pct); `battery_4h_energy_per_mw` (MWh/MW); `battery_4h_flat_price` (USD/MWh); `battery_4h_hours` (count); `battery_4h_revenue_per_mw` (USD/MW); `battery_4h_sales_per_mw` (USD/MW); `flat_price` (USD/MWh); `hours_in_month` (count); `peaker_capture_price` (USD/MWh); `peaker_capture_rate` (pct); `peaker_energy_per_mw` (MWh/MW); `peaker_flat_price` (USD/MWh); `peaker_hours` (count); `peaker_revenue_per_mw` (USD/MW); `peaker_sales_per_mw` (USD/MW); `solar_capture_price` (USD/MWh); `solar_capture_rate` (pct); `solar_energy_per_mw` (MWh/MW); `solar_flat_price` (USD/MWh); `solar_hours` (count); `solar_revenue_per_mw` (USD/MW); `solar_sales_per_mw` (USD/MW); `wind_capture_price` (USD/MWh); `wind_capture_rate` (pct); `wind_energy_per_mw` (MWh/MW); `wind_flat_price` (USD/MWh); `wind_hours` (count); `wind_revenue_per_mw` (USD/MW); `wind_sales_per_mw` (USD/MW)

### `clean_energy_hourly`

- Energy Research Warehouse (ERW): the carbon-free share of each grid's generation by hour, the seven ISO grids (derived, session 122)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_carbon_free_mwh, x_generation_mwh, x_side
- SPP's rows: none found by entity or grid column (the grid enters through a derived figure)

### `clean_energy_summary`

- Energy Research Warehouse (ERW): how clean each grid's generation is by month and year, what an annual clean purchase covers hour by hour, and what moving load into the cleanest hours changes (derived, session 122)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- SPP's rows: none found by entity or grid column (the grid enters through a derived figure)

### `cost_of_power_carbon`

- Energy Research Warehouse (ERW): load-weighted real-time price and carbon intensity per ISO and month (cost-of-power model v0, derived, session 37)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba
- SPP's rows: 67; variables: `intensity_demand` (kgCO2/MWh); `intensity_generation` (kgCO2/MWh); `rt_load_weighted` (USD/MWh)

### `cost_of_power_hourly_profile`

- Energy Research Warehouse (ERW): average real-time price by local hour of day and month, per ISO main hub (cost-of-power model v0, derived, session 37)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba
- SPP's rows: 624; variables: `rt_days_h00` (count); `rt_days_h01` (count); `rt_days_h02` (count); `rt_days_h03` (count); `rt_days_h04` (count); `rt_days_h05` (count); `rt_days_h06` (count); `rt_days_h07` (count); `rt_days_h08` (count); `rt_days_h09` (count); `rt_days_h10` (count); `rt_days_h11` (count); `rt_days_h12` (count); `rt_days_h13` (count); `rt_days_h14` (count); `rt_days_h15` (count); `rt_days_h16` (count); `rt_days_h17` (count); `rt_days_h18` (count); `rt_days_h19` (count); `rt_days_h20` (count); `rt_days_h21` (count); `rt_days_h22` (count); `rt_days_h23` (count); `rt_mean_h00` (USD/MWh); `rt_mean_h01` (USD/MWh); `rt_mean_h02` (USD/MWh); `rt_mean_h03` (USD/MWh); `rt_mean_h04` (USD/MWh); `rt_mean_h05` (USD/MWh); `rt_mean_h06` (USD/MWh); `rt_mean_h07` (USD/MWh); `rt_mean_h08` (USD/MWh); `rt_mean_h09` (USD/MWh); `rt_mean_h10` (USD/MWh); `rt_mean_h11` (USD/MWh); `rt_mean_h12` (USD/MWh); `rt_mean_h13` (USD/MWh); `rt_mean_h14` (USD/MWh); `rt_mean_h15` (USD/MWh); `rt_mean_h16` (USD/MWh); `rt_mean_h17` (USD/MWh); `rt_mean_h18` (USD/MWh); `rt_mean_h19` (USD/MWh); `rt_mean_h20` (USD/MWh); `rt_mean_h21` (USD/MWh); `rt_mean_h22` (USD/MWh); `rt_mean_h23` (USD/MWh)

### `cost_of_power_monthly`

- Energy Research Warehouse (ERW): cost of power per ISO main hub and month, load-weighted and simple averages of the real-time and day-ahead price (cost-of-power model v0, derived, session 37)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba
- SPP's rows: 234; variables: `da_hours` (count); `da_load_weighted` (USD/MWh); `da_shape_premium` (USD/MWh); `da_simple_mean` (USD/MWh); `hours_in_month` (count); `rt_hours` (count); `rt_load_weighted` (USD/MWh); `rt_shape_premium` (USD/MWh); `rt_simple_mean` (USD/MWh)

### `datacenter_queue_positions`

- Energy Research Warehouse (ERW): ISO queue positions that name a datacenter or a large load (session 22)
- Columns: entity_id, entity_type, name, geo, lat, lon, capacity_mw, status, status_date, operator, source, source_url, retrieved_at, vintage, queue_id, county, state, poi, zone, transmission_owner, fuel_technology, iso_status, queue_date, proposed_in_service_date, actual_in_service_date, withdrawn_date, matched

### `datacenter_facilities`

- Energy Research Warehouse (ERW): Datacenter facilities from the news, the operators and the ISO queues (the datacenter power tracker, platform tool 4; session 22)
- Columns: entity_id, entity_type, name, geo, lat, lon, capacity_mw, status, status_date, operator, source, source_url, retrieved_at, vintage, kind, kinds, site_type, developer, state, county, city, country, mw, mw_span, mw_from, queue_mw, project_status, phase, planned_year, power_source, utility, confidence, first_story_at, geo_precision, geo_note, n_members, member_ids, source_urls, grid, grid_basis, mw_basis, power_kind, energized_year, utility_eia861, utility_eia861_number, utilities_in_county

### `ai_power_regions`

- Energy Research Warehouse (ERW): where the next gigawatts for AI can come from, one row of measures per ISO region (derived, session 62)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_window, x_note
- SPP's rows: none found by entity or grid column (the grid enters through a derived figure)

### `iso_queue_statistics`

- Energy Research Warehouse (ERW): interconnection queue statistics by ISO and entry year (derived, session 348)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_iso, x_entry_year, x_rule, x_input_run
- SPP's rows: 342; variables: `mw_entered` (MW); `mw_operating` (MW); `mw_status_not_stated` (MW); `mw_waiting` (MW); `mw_withdrawn` (MW); `positions_entered` (count); `positions_operating` (count); `positions_status_not_stated` (count); `positions_waiting` (count); `positions_withdrawn` (count); `wait_positions` (count); `wait_years_mean` (year); `wait_years_median` (year); `withdrawal_rate` (ratio)

### `iso_dam_hub_prices`

- Energy Research Warehouse (ERW): day-ahead hub prices, CAISO, ERCOT, MISO and SPP
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- SPP's rows: 3,458; variables: `lmp_dam` (USD/MWh)

### `iso_rtm_hub_prices`

- Energy Research Warehouse (ERW): real-time hub prices, CAISO, ERCOT, MISO and SPP
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- SPP's rows: 5,760; variables: `lmp_rtm_15m_mean` (USD/MWh)

---

## The first draft (session 378), kept as it was

# Draft: SPP's written authorization, should the ERW ever be a commercial publication

Written by session 378 (20 October 2026) for Samuel to send himself, from his own address. Nothing here was sent. Fill what stands in brackets first.

Why it is needed: SPP's terms (read 6 of `warehouse/metadata/license_reads.csv`, https://www.spp.org/terms-conditions/, 12 October 2026) allow the ERW as it is today: "Permission is implicitly granted to copy and distribute (via computer network or printed form) in whole or in part (with appropriate citation) EXCEPT when such materials will be used, in whole or in part, within a commercial publication (printed or otherwise) or when the author(s) or SPP will be quoted in commercial materials, forums or publications. Any commercial use of these materials requires prior, express written authorization from the author(s) or a duly authorized officer of SPP." So the letter is needed only if the ERW sells anything: 30 tables would then need it (`docs/licenses.md`, "If the ERW sells anything"). The page names its contact: SPP Communications, 201 Worthen Drive, Little Rock, AR 72223-4936, (501) 614-3200; communication@spp.org is on the same page.

---

**To:** SPP Communications, communication@spp.org (201 Worthen Drive, Little Rock, AR 72223-4936)

**Subject:** Written authorization for SPP's public market data in a research data warehouse

Hello,

I am Samuel [surname], [role and affiliation]. I run the Energy Research Warehouse (ERW), an open record of the US energy system: prices, flows, projects and policy, each number traced to its source. The code and the documentation are public at github.com/SamuelEnrique/erw. Today the ERW is noncommercial and cites SPP as your terms ask; I write ahead of any commercial use, as your terms require written authorization for it.

What we hold of yours, all from SPP's public pages and reports:

- SPP's own tables: ancillary service prices and quantities (`spp_as_prices`, `spp_as_quantities`), day-ahead cleared energy (`spp_dam_cleared_energy`), daily curtailment (`spp_curtailment_daily`) and the interconnection queue (`spp_interconnection_queue`).
- SPP's rows in tables that compare grids: `iso_dam_hub_prices`, `iso_rtm_hub_prices`, `iso_hub_prices_history`, `iso_zone_prices_history`, `iso_trader_daily`, `iso_curtailment_monthly`, `hub_price_comparison`, `price_board_latest`, `price_board_peak_offpeak`, `price_board_spreads`, `price_years_by_window`, `scarcity_hours_by_grid`, `grid_stress_days`, `event_window_daily`, `event_study_estimates`, `merchant_revenue_monthly`, `battery_stack_review_monthly`, `clean_energy_hourly`, `clean_energy_summary`, `cost_of_power_carbon`, `cost_of_power_hourly_profile`, `cost_of_power_monthly`, `datacenter_queue_positions`, `energy_projects`, `ai_power_regions`.

What I am asking for:

- Written authorization to publish the values as SPP states them, and figures computed from them, in tables, charts and downloads of a product that may be sold, with SPP cited and a link to the report.
- The same for a citable archive of those tables (the ERW's dataset on Redivis).

What we offer:

- Citation of SPP beside every figure, in the words you prefer.
- A link to SPP's own report for every series.
- No resale of SPP's raw files. We publish what we compute from them.
- Any request rate, time of day or file route you set.

If a license or a fee applies, I would be glad to know its terms.

Thank you,
Samuel [surname]
[email address]
