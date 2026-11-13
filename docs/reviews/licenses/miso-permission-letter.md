# Draft: permission to read MISO's public market data by script and to republish it in a research warehouse

Written by session 378 (20 October 2026), brought up to date by chain 229, session 4104 (13 November 2026), for Samuel to send himself, from his own address. Nothing here was sent. Fill what stands in brackets first.

Why it is needed: MISO's legal page (https://www.misoenergy.org/meet-miso/legal-and-privacy/, as `warehouse/metadata/paused_sources.csv` holds it from 4 October 2026) says: "You agree not use any automated means, including, without limitation, agents, robots, scripts, or spiders, to access, monitor, or copy any part of this Website or the App." MISO is paused since 4 October 2026 ([`docs/methods/miso_pause.md`](../../methods/miso_pause.md)): no page of MISO was asked by chain 229 either, so the sentence was not read again. The tables below show "license needed" in place of MISO's numbers (the owner's ruling of 12 October 2026), and MISO's own tables are internal.

Who to write to: [MISO's legal or market data contact: no page of MISO's site was read while it is paused, so a person finds the address by hand.]

---

**To:** [MISO's legal or market data contact: no page of MISO's site was read while it is paused, so a person finds the address by hand.]

**Subject:** Permission to read MISO's public market data by script and to republish it in an open research data warehouse

Hello,

I am Samuel [surname], [role] at Stanford University. I run the Energy Research Warehouse (ERW), an open, citable research warehouse of the US energy system at Stanford: prices, flows, projects and policy, each number traced to its source report. Its tables are versioned and citable as a dataset on Redivis, and its code and documentation are public at github.com/SamuelEnrique/erw. A public site shows figures derived from the tables (averages, spreads, comparisons between grids); it is in review and not yet open to visitors. The ERW sells nothing.

What we hold from MISO, all from MISO's public pages and reports (26 tables; the fields of each are listed in the appendix below):

- `miso_as_prices`, `miso_interconnection_queue`, `iso_all_capacity_prices`, `iso_hub_prices_history`, `iso_zone_prices_history`, `iso_trader_daily`, `hub_price_comparison`, `price_board_latest`, `price_board_peak_offpeak`, `price_board_spreads`, `scarcity_hours_by_grid`, `grid_stress_days`, `event_window_daily`, `event_study_estimates`, `merchant_revenue_monthly`, `clean_energy_hourly`, `clean_energy_summary`, `cost_of_power_carbon`, `cost_of_power_hourly_profile`, `cost_of_power_monthly`, `datacenter_queue_positions`, `datacenter_facilities`, `ai_power_regions`, `iso_queue_statistics`, `iso_dam_hub_prices`, `iso_rtm_hub_prices`.

What I am asking for:

- Permission to read MISO's public market reports by script, at the rate, times and route MISO sets (its terms forbid automated access as they stand).
- Permission to publish the values in the tables listed below, as MISO states them, and figures computed from them, with MISO named as the source.
- The same for the ERW's citable dataset on Redivis, version by version.
- [Only if the ERW may sell anything one day: the same in a paid product. Strike this line otherwise.]

What we offer:

- MISO named as the source beside every figure, in the words you prefer, with a link to MISO's own report.
- No resale or redistribution of MISO's raw files as such: we publish the values in our tables and what we compute from them.
- Any request rate, time of day or file route you set; a bulk file or a key if you prefer.
- A line in our records for your answer, so that every table shows the permission it rests on.

If a license or a fee applies, I would be glad to know its terms.

Thank you,
Samuel [surname]
[email address]

---

## Appendix: the exact tables and fields

Read on 13 November 2026 from each table's file on the data machine (its header's title, its columns, and for a series table the variables and units in MISO's rows, found by the entity, grid or market column). A table whose rows name no grid holds a figure computed across grids.

### `miso_as_prices`

- Energy Research Warehouse (ERW): MISO day-ahead ancillary service market clearing prices, hourly, the system
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- MISO's rows: 54,936; variables: `as_price_dam_reg` (USD/MW-hour); `as_price_dam_spin` (USD/MW-hour); `as_price_dam_supp` (USD/MW-hour)

### `miso_interconnection_queue`

- Energy Research Warehouse (ERW): MISO interconnection queue
- Columns: entity_id, entity_type, name, geo, lat, lon, capacity_mw, status, status_date, operator, source, source_url, retrieved_at, vintage, queue_id, county, state, poi, zone, transmission_owner, fuel_technology, iso_status, queue_date, proposed_in_service_date, actual_in_service_date, withdrawn_date

### `iso_all_capacity_prices`

- Energy Research Warehouse (ERW): capacity prices, PJM Base Residual Auction, NYISO ICAP spot auction, ISO-NE Forward Capacity Auction, MISO Planning Resource Auction
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_auction, x_period_end, x_note, x_license
- MISO's rows: 130; variables: `capacity_price` (USD/MW-day)

### `iso_hub_prices_history`

- Energy Research Warehouse (ERW): main-hub day-ahead and real-time prices, history from 2023-07-06 (session 49 from 2025-09-01; session 64 the year before, from 2024-09-01): CAISO SP15 and NP15, MISO Indiana Hub, NYISO N.Y.C., ISO-NE .H.INTERNAL_HUB, SPP SPPNORTH_HUB
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- MISO's rows: 36,600; variables: `lmp_dam` (USD/MWh); `lmp_rtm` (USD/MWh)

### `iso_zone_prices_history`

- Energy Research Warehouse (ERW): zone and hub prices, history from 2019 (session 140): NYISO's eleven load zones, CAISO ZP26 (TH_ZP26_GEN-APND) and SPP South (SPPSOUTH_HUB), day-ahead and real-time. ISO-NE's eight load zones are in isone_zone_prices_history: the same columns, internal (ISO-NE's noti
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- MISO's rows: none found by entity or grid column (the grid enters through a derived figure)

### `iso_trader_daily`

- Energy Research Warehouse (ERW): the trader view, daily metrics per hub, every ISO (derived; platform tool 24)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- MISO's rows: 2,408; variables: `da_mean_usd` (USD/MWh); `da_offpeak_mean_usd` (USD/MWh); `da_onpeak_mean_usd` (USD/MWh); `da_rt_spread_max_usd` (USD/MWh); `da_rt_spread_mean_usd` (USD/MWh); `da_volatility_30d_usd` (USD/MWh); `hours_rt_over_da_50` (count); `implied_heat_rate` (MMBtu/MWh); `rt_mean_usd` (USD/MWh)

### `hub_price_comparison`

- Energy Research Warehouse (ERW): where power is cheap, every public hub and zone price held, compared over twelve months and over the last whole month (session 96)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- MISO's rows: none found by entity or grid column (the grid enters through a derived figure)

### `price_board_latest`

- Energy Research Warehouse (ERW): price board, latest day per hub and zone, day-ahead and real-time (derived)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- MISO's rows: 680; variables: `da_avg_30d` (USD/MWh); `da_avg_7d` (USD/MWh); `da_daily_mean` (USD/MWh); `da_day_change` (USD/MWh); `da_day_change_pct` (pct); `da_days_30d` (count); `da_days_7d` (count); `da_intervals_30d` (count); `da_latest_day_mean` (USD/MWh); `da_latest_interval` (USD/MWh); `da_max_30d` (USD/MWh); `da_min_30d` (USD/MWh); `da_minus_rt` (USD/MWh); `da_previous_day_mean` (USD/MWh); `rt_avg_30d` (USD/MWh); `rt_avg_7d` (USD/MWh); `rt_daily_mean` (USD/MWh); `rt_day_change` (USD/MWh); `rt_day_change_pct` (pct); `rt_days_30d` (count); `rt_days_7d` (count); `rt_intervals_30d` (count); `rt_latest_day_mean` (USD/MWh); `rt_latest_interval` (USD/MWh); `rt_max_30d` (USD/MWh); `rt_min_30d` (USD/MWh); `rt_previous_day_mean` (USD/MWh)

### `price_board_peak_offpeak`

- Energy Research Warehouse (ERW): price board, peak and off-peak means per ISO main hub (derived)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- MISO's rows: 387; variables: `da_all_mean` (USD/MWh); `da_offpeak_intervals` (count); `da_offpeak_mean` (USD/MWh); `da_peak_intervals` (count); `da_peak_mean` (USD/MWh); `da_peak_minus_offpeak` (USD/MWh); `rt_all_mean` (USD/MWh); `rt_offpeak_intervals` (count); `rt_offpeak_mean` (USD/MWh); `rt_peak_intervals` (count); `rt_peak_mean` (USD/MWh); `rt_peak_minus_offpeak` (USD/MWh)

### `price_board_spreads`

- Energy Research Warehouse (ERW): price board, spark spreads, implied heat rates, Henry Hub and Brent minus WTI, daily (derived)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_gas_date
- MISO's rows: 117; variables: `da_daily_mean` (USD/MWh); `implied_heat_rate` (MMBtu/MWh); `spark_spread_7` (USD/MWh)

### `scarcity_hours_by_grid`

- Energy Research Warehouse (ERW): each grid's own scarcity signal beside the USD 1,000 price count, hour by hour (derived, session 254)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_detail
- MISO's rows: none found by entity or grid column (the grid enters through a derived figure)

### `grid_stress_days`

- Energy Research Warehouse (ERW): stress days of the grids by one rule (session 306); docs/methods/stress_days.md; the rule docs/methods/battery_stress_days.md
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_reason, x_event, x_trailing_p98, x_trailing_days, x_notices
- MISO's rows: 16; variables: `stress_day` (USD/MWh)

### `event_window_daily`

- Energy Research Warehouse (ERW): event windows, daily figures around an event and the same calendar days of earlier years (Historical Event Analyzer v0, derived, session 36B)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba, event
- MISO's rows: 164; variables: `da_max` (USD/MWh); `da_mean` (USD/MWh); `rt_max` (USD/MWh); `rt_mean` (USD/MWh)

### `event_study_estimates`

- Energy Research Warehouse (ERW): event studies, the estimated effect of each event on each grid's daily demand served and ERCOT's daily hub price (derived, research, session 47)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba, event, x_std_error, x_ci_low, x_ci_high, x_n, x_spec, x_term
- MISO's rows: 13; variables: `rt_mean_counterfactual_mean` (USD/MWh); `rt_mean_effect_day` (USD/MWh); `rt_mean_effect_pooled` (USD/MWh)

### `merchant_revenue_monthly`

- Energy Research Warehouse (ERW): merchant revenue per MW at each ISO's main hub, by asset type and month (derived, session 51, the seller's side of the cost of power)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba
- MISO's rows: 962; variables: `battery_2h_capture_price` (USD/MWh); `battery_2h_capture_rate` (pct); `battery_2h_energy_per_mw` (MWh/MW); `battery_2h_flat_price` (USD/MWh); `battery_2h_hours` (count); `battery_2h_revenue_per_mw` (USD/MW); `battery_2h_sales_per_mw` (USD/MW); `battery_4h_capture_price` (USD/MWh); `battery_4h_capture_rate` (pct); `battery_4h_energy_per_mw` (MWh/MW); `battery_4h_flat_price` (USD/MWh); `battery_4h_hours` (count); `battery_4h_revenue_per_mw` (USD/MW); `battery_4h_sales_per_mw` (USD/MW); `flat_price` (USD/MWh); `hours_in_month` (count); `peaker_capture_price` (USD/MWh); `peaker_capture_rate` (pct); `peaker_energy_per_mw` (MWh/MW); `peaker_flat_price` (USD/MWh); `peaker_hours` (count); `peaker_revenue_per_mw` (USD/MW); `peaker_sales_per_mw` (USD/MW); `solar_capture_price` (USD/MWh); `solar_capture_rate` (pct); `solar_energy_per_mw` (MWh/MW); `solar_flat_price` (USD/MWh); `solar_hours` (count); `solar_revenue_per_mw` (USD/MW); `solar_sales_per_mw` (USD/MW); `wind_capture_price` (USD/MWh); `wind_capture_rate` (pct); `wind_energy_per_mw` (MWh/MW); `wind_flat_price` (USD/MWh); `wind_hours` (count); `wind_revenue_per_mw` (USD/MW); `wind_sales_per_mw` (USD/MW)

### `clean_energy_hourly`

- Energy Research Warehouse (ERW): the carbon-free share of each grid's generation by hour, the seven ISO grids (derived, session 122)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_carbon_free_mwh, x_generation_mwh, x_side
- MISO's rows: none found by entity or grid column (the grid enters through a derived figure)

### `clean_energy_summary`

- Energy Research Warehouse (ERW): how clean each grid's generation is by month and year, what an annual clean purchase covers hour by hour, and what moving load into the cleanest hours changes (derived, session 122)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- MISO's rows: none found by entity or grid column (the grid enters through a derived figure)

### `cost_of_power_carbon`

- Energy Research Warehouse (ERW): load-weighted real-time price and carbon intensity per ISO and month (cost-of-power model v0, derived, session 37)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba
- MISO's rows: 75; variables: `intensity_demand` (kgCO2/MWh); `intensity_generation` (kgCO2/MWh); `rt_load_weighted` (USD/MWh)

### `cost_of_power_hourly_profile`

- Energy Research Warehouse (ERW): average real-time price by local hour of day and month, per ISO main hub (cost-of-power model v0, derived, session 37)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba
- MISO's rows: 624; variables: `rt_days_h00` (count); `rt_days_h01` (count); `rt_days_h02` (count); `rt_days_h03` (count); `rt_days_h04` (count); `rt_days_h05` (count); `rt_days_h06` (count); `rt_days_h07` (count); `rt_days_h08` (count); `rt_days_h09` (count); `rt_days_h10` (count); `rt_days_h11` (count); `rt_days_h12` (count); `rt_days_h13` (count); `rt_days_h14` (count); `rt_days_h15` (count); `rt_days_h16` (count); `rt_days_h17` (count); `rt_days_h18` (count); `rt_days_h19` (count); `rt_days_h20` (count); `rt_days_h21` (count); `rt_days_h22` (count); `rt_days_h23` (count); `rt_mean_h00` (USD/MWh); `rt_mean_h01` (USD/MWh); `rt_mean_h02` (USD/MWh); `rt_mean_h03` (USD/MWh); `rt_mean_h04` (USD/MWh); `rt_mean_h05` (USD/MWh); `rt_mean_h06` (USD/MWh); `rt_mean_h07` (USD/MWh); `rt_mean_h08` (USD/MWh); `rt_mean_h09` (USD/MWh); `rt_mean_h10` (USD/MWh); `rt_mean_h11` (USD/MWh); `rt_mean_h12` (USD/MWh); `rt_mean_h13` (USD/MWh); `rt_mean_h14` (USD/MWh); `rt_mean_h15` (USD/MWh); `rt_mean_h16` (USD/MWh); `rt_mean_h17` (USD/MWh); `rt_mean_h18` (USD/MWh); `rt_mean_h19` (USD/MWh); `rt_mean_h20` (USD/MWh); `rt_mean_h21` (USD/MWh); `rt_mean_h22` (USD/MWh); `rt_mean_h23` (USD/MWh)

### `cost_of_power_monthly`

- Energy Research Warehouse (ERW): cost of power per ISO main hub and month, load-weighted and simple averages of the real-time and day-ahead price (cost-of-power model v0, derived, session 37)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, ba
- MISO's rows: 234; variables: `da_hours` (count); `da_load_weighted` (USD/MWh); `da_shape_premium` (USD/MWh); `da_simple_mean` (USD/MWh); `hours_in_month` (count); `rt_hours` (count); `rt_load_weighted` (USD/MWh); `rt_shape_premium` (USD/MWh); `rt_simple_mean` (USD/MWh)

### `datacenter_queue_positions`

- Energy Research Warehouse (ERW): ISO queue positions that name a datacenter or a large load (session 22)
- Columns: entity_id, entity_type, name, geo, lat, lon, capacity_mw, status, status_date, operator, source, source_url, retrieved_at, vintage, queue_id, county, state, poi, zone, transmission_owner, fuel_technology, iso_status, queue_date, proposed_in_service_date, actual_in_service_date, withdrawn_date, matched

### `datacenter_facilities`

- Energy Research Warehouse (ERW): Datacenter facilities from the news, the operators and the ISO queues (the datacenter power tracker, platform tool 4; session 22)
- Columns: entity_id, entity_type, name, geo, lat, lon, capacity_mw, status, status_date, operator, source, source_url, retrieved_at, vintage, kind, kinds, site_type, developer, state, county, city, country, mw, mw_span, mw_from, queue_mw, project_status, phase, planned_year, power_source, utility, confidence, first_story_at, geo_precision, geo_note, n_members, member_ids, source_urls, grid, grid_basis, mw_basis, power_kind, energized_year, utility_eia861, utility_eia861_number, utilities_in_county

### `ai_power_regions`

- Energy Research Warehouse (ERW): where the next gigawatts for AI can come from, one row of measures per ISO region (derived, session 62)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_window, x_note
- MISO's rows: none found by entity or grid column (the grid enters through a derived figure)

### `iso_queue_statistics`

- Energy Research Warehouse (ERW): interconnection queue statistics by ISO and entry year (derived, session 348)
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage, x_iso, x_entry_year, x_rule, x_input_run
- MISO's rows: 113; variables: `mw_entered` (MW); `mw_operating` (MW); `mw_waiting` (MW); `mw_withdrawn` (MW); `positions_entered` (count); `positions_operating` (count); `positions_status_not_stated` (count); `positions_waiting` (count); `positions_withdrawn` (count); `withdrawal_rate` (ratio)

### `iso_dam_hub_prices`

- Energy Research Warehouse (ERW): day-ahead hub prices, CAISO, ERCOT, MISO and SPP
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- MISO's rows: 7,488; variables: `lmp_dam` (USD/MWh)

### `iso_rtm_hub_prices`

- Energy Research Warehouse (ERW): real-time hub prices, CAISO, ERCOT, MISO and SPP
- Columns: entity, variable, ts_utc, value, unit, freq, geo, market, node, source, source_url, retrieved_at, vintage
- MISO's rows: 7,104; variables: `lmp_rtm` (USD/MWh)

---

## The first draft (session 378), kept as it was

# Draft: permission to read MISO's public market data by script and to republish it in a research warehouse

Written by session 378 (20 October 2026) for Samuel to send himself, from his own address. Nothing here was sent, and nothing was asked of MISO: MISO is paused since 4 October 2026 (`warehouse/metadata/paused_sources.csv`, [`docs/methods/miso_pause.md`](../../methods/miso_pause.md)). Fill what stands in brackets first.

Why it is needed: MISO's legal page (https://www.misoenergy.org/meet-miso/legal-and-privacy/, as the pause file holds it from 4 October 2026; not asked again, read 7 of `warehouse/metadata/license_reads.csv`) says: "You agree not use any automated means, including, without limitation, agents, robots, scripts, or spiders, to access, monitor, or copy any part of this Website or the App." Every pull from MISO's servers is paused, and by the ruling of 12 October 2026 (session 207) the tables below show "license needed" in place of MISO's numbers from 21 October until a permission is recorded in `warehouse/metadata/license_status.csv`. The contact is not known (the page was not asked).

---

**To:** [MISO's legal or market data contact]

**Subject:** Permission to read MISO's public market data by script and republish it in a research data warehouse

Hello,

I am Samuel [surname], [role and affiliation]. I run the Energy Research Warehouse (ERW), an open, noncommercial record of the US energy system: prices, flows, projects and policy, each number traced to its source. The code and the documentation are public at github.com/SamuelEnrique/erw.

Your site's terms forbid automated access, so since 4 October we have stopped every request to MISO's servers. I write to ask whether we may resume, and on what terms.

What we hold of yours, read before the pause from MISO's public pages and reports:

- MISO's own tables: ancillary service prices (`miso_as_prices`, internal) and the interconnection queue (`miso_interconnection_queue`).
- MISO's rows in tables that compare grids: `iso_dam_hub_prices`, `iso_rtm_hub_prices`, `iso_hub_prices_history`, `iso_trader_daily`, `hub_price_comparison`, `price_board_latest`, `price_board_peak_offpeak`, `price_board_spreads`, `scarcity_hours_by_grid`, `grid_stress_days`, `event_window_daily`, `event_study_estimates`, `merchant_revenue_monthly`, `clean_energy_hourly`, `clean_energy_summary`, `cost_of_power_carbon`, `cost_of_power_hourly_profile`, `cost_of_power_monthly`, `datacenter_queue_positions`, `datacenter_facilities`, `ai_power_regions`.
- MISO's news releases as news items (`news_index`).

What I am asking for:

- Read MISO's public market reports by script, once a day, at the rate, times and file routes MISO sets (or through an API key or a bulk file, if you prefer).
- Publish the values as MISO states them, and figures computed from them, in tables, charts and downloads, with MISO named as the source and a link to the report.
- The same for a citable archive of those tables (the ERW's dataset on Redivis).
- [Only if the ERW may sell anything: the same in a paid product. Strike this line otherwise.]

What we offer:

- Attribution to MISO beside every figure, in the words you prefer.
- A link to MISO's own report for every series.
- No resale of MISO's raw files. We publish what we compute from them.

If a license or a fee applies, I would be glad to know its terms.

Thank you,
Samuel [surname]
[email address]
