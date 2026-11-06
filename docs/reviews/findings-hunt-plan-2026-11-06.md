# The findings hunt over the whole warehouse: the plan (6 November 2026)

Written by session 3000 (chain 164, lab-desktop's second window) from origin's main at 847dc7de9. Each session of chains 164 and 166 marks the families it hunted in the last section. Nothing here is approved; nothing reaches `/research` or `/analysis` until the owner approves a draft at `/internal/findings`, having run its Stata.

## The hunt as it exists

- **Two writers, one review list.** The daily scanner (`warehouse/analysis/findings/findings_scanner.py`, session 181; method `docs/methods/automated_analysis_scanner.md`) flags five kinds of news on every public series table: record, negative, spike, weekly, pair. The weekly hunt (`warehouse/analysis/findings/hunt.py`, session 233, with `hunt_measures.py` since session 251) asks 20 patterns of every public grid and region, by year, under its tests (holds in more than one year, survives a change of window, sample large enough, half the change remains without the first year, at least one typical yearly move). Both write rows of `public.scanner_drafts` (migrations 029 and 031): the scanner under its five rules, the hunt under rule `hunt`.
- **The review page.** `/internal/findings` (`site/app/internal/findings/page.tsx`) reads the list through `scanner_drafts_list` (`site/lib/scanner.ts`), answered only when the server's token equals the secret. A hunt row shows its card (chart, callouts, footnote), its tests and its files (CSV, Stata do-file, Python mirror, two LinkedIn pictures, the caption) from the row itself. Approved, a draft appears on `/analysis` and can be picked for the Roundup (`roundup_pick.py`).
- **What stands today** (read over `SUPABASE_DB_URL`, 6 November 2026 11:00 UTC): 66 rows. Rule `hunt`: 40 drafts (flag years 2024 and 2025). Rule `record`: 13 drafts, 1 dismissed, 1 with its full card asked. Rule `weekly`: 9 drafts. Rule `spike`: 1 draft, 1 approved. The 40 hunt drafts by pattern: da_rt_spread 4, implied_heat_rate 4, negative_hours_zones 4, evening_ramp 3, demand_growth_weather_adjusted 3, peak_hour_carbon 3, negative_prices 3, wind_night_share 3, stress_day_imports 2, spikes_against_median 2, and one each of battery_evening_discharge, record_days, peak_hour_midday, solar_capture_rate, spikes_against_median_grids, peak_hour_evening, scarcity_hours, hours_above_1000, curtailment_share.
- **What the hunt already asks** (`hunt.py --list`, so this chain does not draft them again): the dearest interval against the median; hours above USD 1,000; hours gas sets the price (7.0 heat rate times Henry Hub); negative-price hours by hub and by zone; the day's peak hour in the evening or at midday; solar's capture rate; the evening net-load ramp; battery discharge in the evening; the implied heat rate; the day-ahead to real-time spread (median hour); ERCOT's scarcity adder hours; curtailment's share; imports on stress days; weather-adjusted demand growth; the evening's carbon intensity; wind's night share; record demand days. Not yet patterns: queue_divorce, who_rescues_whom, the two battery curtailment regressions, impact_study.
- **Only public grids are drafted.** A region of a grid marked "license needed" (ISO-NE, MISO, NYISO) or held by a ruling (NYISO, SPP; `daily_chart.HELD`) is never drafted by the hunt. This chain keeps the rule for prices and drafts a held table's finding only as the chain file says: with "license needed" on its figure and the table named.

## Where this chain's drafts go (session 3000's decision)

- **The store:** rows of `public.scanner_drafts` under rule `hunt`, written by the hunt's own loader (`hunt.load_drafts`, the service key from `.env`; no data lock, no warehouse table). The store takes more than the scanner's form: a hunt row carries a card of any chart kind the site draws, its tests and its files, and `/internal/findings` lists it with them. Every row is state `draft`; nothing is approved by a machine.
- **The card:** the one sentence as the subtitle (every figure in it computed by code); the chart as a card chart the site already draws (`line`, `bar`, `flag_line`, with hover values), in the brand's style (`docs/brand.md`); callouts for the claim, the comparison and the strength; the limits sentence and the tables in the footnote. `hunt.pattern` names the chain's family and candidate, so a later session can tell them from the weekly hunt's.
- **The files of each draft:** the CSV of the rows the figure rests on (the tables and the keys the tracers read), `reproduce.py` and `reproduce.do` that recompute the figure from the tables as the public downloads hold them (the owner's Stata rules: no line continuation, one empty line between commands outside loops and none inside, every variable destringed with `force`), the two pictures and the caption the hunt writes.
- **The document of each draft:** `docs/findings/<family>/<slug>.md` beside the row, with the sentence, the figure, the tables and rows, the strength, the limits, and the commands; the chart's PNG beside it. The row is what the owner reviews; the document is what the git history keeps.
- **The code:** one module per family under `warehouse/analysis/findings/deep/` (session 3001 writes the shared builder), each candidate a function that returns its rows by year or by group, tested by the hunt's own tests (`hunt.py`'s claim and tests), with a test of its own under `tests/`.
- **The model:** Opus through the repository's client, for proposing candidates from a family's table list and for wording sentences around figures computed by code; USD 3 a session and USD 35 the chain; every call's cost in the session's report.

## The ranking rubric (for session 3020)

Each draft is scored 1 to 3 on three counts, and ranked by the sum, ties by strength.

- **Consequence:** 3 when the figure moves money or reliability at a grid's scale (a price shape, a spread worth more than USD 1 per MWh over a year, a peak or a pipeline in GW), 2 at a region's or a technology's scale, 1 a curiosity.
- **Novelty:** 3 when no draft, card, periodical or method note of the ERW states it; 2 when one states it for another grid, region or year; 1 when it restates one.
- **Strength:** 3 when every test of the hunt passes and the change is at least two typical yearly moves (or the family's own test is significant at 1 percent); 2 when every test passes; 1 when one test is marginal and the draft says so.

## The order

Prices (3001 to 3003), demand (3004), generation and the pipeline (3005 to 3007), gas (3008), queues, deals and datacenters (3009 to 3011), tariffs and policy (3012), oil, products and the world prices (3013 to 3015), the cross-family findings (3016), the check (3017 to 3019), the ranking (3020), the Stata read (3021), the records (3022), the note (3023). The landing service begins sessions 3004, 3008, 3012, 3016 and 3020. Chain 166 takes what is left, then coal, uranium and metals, emissions and climate, and the rest of the US tables.

## The questions each family can answer

- **prices:** where a grid's daily price shape changed (the midday trough, the evening peak, the shoulder hours) by year; hub-to-hub spreads by year; the spark spread against Henry Hub at a standard heat rate; ERCOT's node basis; the share of a year's spread value carried by its top days; the regional gas basis; carbon prices against power. (The median hour's day-ahead to real-time spread is already a hunt pattern.)
- **markets_operations:** scarcity and shoulder hours by grid and year; stress days; node basis by node and year; batteries' awards by hour.
- **demand:** the grids and sub-regions whose peak grew fastest by year; the weekday and hour of new peaks; winter peaks that rival summer; the US48 peak against its year before.
- **generation_pipeline:** shares that crossed a line (solar's midday share, gas's evening share, coal's exit by grid); the pipeline's slippage by fuel and grid; reactors' outage days against their decade; the fleet's uprates.
- **gas:** weeks outside the five-year range; LNG feedgas as a share of demand by year; regions whose storage position diverged; basis blowouts.
- **queues_deals_datacenters:** withdrawal rates by fuel and grid; months to in-service by year; disclosed deal prices by technology and year; AI-power deals' MW by quarter; datacenter MW by grid against each grid's peak.
- **tariffs_policy:** what a 500 MW load's delivery charge spans across the utilities held; which rules state a duration; the policy actions scored highest by month.
- **oil_products_world:** crack spreads by year; import origins that moved; chokepoint transits against price (PortWatch is internal: license needed); retail products against crude.

## The families

| Family | Tables | Rows | Public | Internal | Newest date held | Sessions |
|---|---:|---:|---:|---:|---|---|
| prices | 54 | 15,218,268 | 44 | 10 | 2026-11-07 | 3001 to 3003 |
| markets_operations | 40 | 5,977,110 | 37 | 3 | 2026-11-06 | 3001 to 3003 (with prices), 3016 |
| demand | 63 | 32,028,056 | 37 | 26 | 2026-11-05 | 3004 |
| generation_pipeline | 100 | 8,841,860 | 96 | 4 | 2026-11-05 | 3005 to 3007 |
| gas | 24 | 826,072 | 22 | 2 | 2026-10-23 | 3008 |
| queues_deals_datacenters | 27 | 177,704 | 23 | 4 | 2026-11-05 | 3009 to 3011 |
| tariffs_policy | 38 | 4,663,082 | 26 | 12 | 2026-11-05 | 3012 |
| oil_products_world | 52 | 6,681,602 | 50 | 2 | 2026-11-05 | 3013 to 3015 |
| coal_uranium_metals | 12 | 392,758 | 12 | 0 | 2026-10-23 | after 3016 (chain 166) |
| emissions_climate | 29 | 9,993,229 | 28 | 1 | 2026-11-05 | after 3016 (chain 166) |
| other_us | 37 | 5,882,460 | 36 | 1 | 2026-10-23 | after 3016 (chain 166) |
| outside_us | 156 | 8,632,715 | 110 | 46 | 2026-10-25 | not hunted (US first) |
| platform_news | 5 | 53,465 | 2 | 3 | 2026-11-05 | not hunted |
| all | 637 | 99,368,381 | 523 | 114 | | |

Newest date held: the newest `ts_max` at or before 7 November 2026 (a forecast's or a rule's future date is left out of this column).

## The tables of each family

Each line: the table, its rows, its license, its newest `ts_max`. Families by the table's name (session 3000's rules, approximate: a table can answer another family's question, and the sessions read across).

### prices (sessions 3001 to 3003)

The ISO hub and zone prices (day-ahead, real-time), the spreads, ancillary services, the fuel spot closes, carbon allowances, capacity prices.

- `ercot_all_hub_prices_history`: 3,109,938 rows, public, 2026-10-31
- `ercot_zone_prices_history`: 2,489,448 rows, public, 2026-11-01
- `iso_zone_prices_history`: 1,667,330 rows, public, 2026-11-03
- `ercot_rtm_node_prices`: 1,150,968 rows, public, 2026-11-05
- `isone_zone_prices_history`: 1,075,024 rows, internal, 2026-09-01
- `ercot_zone_load_hourly`: 926,838 rows, public, 2026-10-01
- `nyiso_zone_load_hourly`: 753,291 rows, public, 2026-10-24
- `iso_hub_prices_history`: 604,773 rows, public, 2026-11-07
- `ercot_rtm_price_adders`: 602,482 rows, public, 2026-11-01
- `ercot_node_prices_hourly`: 496,176 rows, internal, 2026-11-05
- `ercot_hub_prices_daily`: 347,814 rows, public, 2026-11-06
- `ercot_as_prices`: 339,332 rows, public, 2026-10-31
- `nyiso_as_prices`: 293,376 rows, public, 2026-10-05
- `caiso_as_prices`: 231,944 rows, public, 2026-11-06
- `spp_as_quantities`: 159,768 rows, public, 2026-10-05
- `spp_as_prices`: 159,432 rows, public, 2026-10-04
- `isone_zone_load_hourly`: 137,799 rows, internal, 2026-10-01
- `nyiso_rtm_zone_prices`: 73,964 rows, public, 2026-11-05
- `iso_rtm_hub_prices`: 73,380 rows, public, 2026-11-05
- `eia_product_spot_prices`: 72,178 rows, public, 2026-11-03
- `ercot_as_prices_daily`: 70,695 rows, public, 2026-10-30
- `isone_as_prices`: 55,964 rows, internal, 2026-10-05
- `miso_as_prices`: 54,936 rows, internal, 2026-10-04
- `isone_rtm_zone_prices`: 51,876 rows, public, 2026-11-05
- `eia_fuel_spot_prices`: 27,796 rows, public, 2026-11-03
- `iso_dam_hub_prices`: 26,723 rows, public, 2026-11-07
- `ercot_peak_premium_monthly`: 23,856 rows, public, 2026-10-01
- `eia_all_futures_prices`: 21,240 rows, internal, 2024-04-05
- `nyiso_dam_zone_prices`: 19,283 rows, public, 2026-11-07
- `isone_dam_zone_prices`: 15,777 rows, public, 2026-11-07
- `frb_utility_output_monthly`: 15,365 rows, public, 2026-09-01
- `isone_rtm_zone_prices_hourly`: 14,481 rows, public, 2026-11-05
- `cftc_cot_positions`: 9,856 rows, public, 2026-10-20
- `merchant_revenue_monthly`: 8,853 rows, public, 2026-10-01
- `frb_treasury_yields`: 5,886 rows, public, 2026-11-04
- `ercot_as_quantities`: 4,800 rows, public, 2026-10-13
- `price_board_peak_offpeak`: 4,572 rows, public, 2026-11-06
- `price_board_latest`: 3,250 rows, public, 2026-11-07
- `caiso_dam_alert_day_hub_prices`: 3,024 rows, public, 2025-08-25
- `price_board_spreads`: 2,697 rows, public, 2026-11-06
- `ercot_as_prices_monthly`: 2,325 rows, public, 2026-10-01
- `ercot_storage_node_basis`: 2,064 rows, public, 2026-09-28
- `ercot_peak_premium_annual`: 2,016 rows, public, 2026-01-01
- `carb_lcfs_credit_prices`: 1,124 rows, public, 2026-09-14
- `iso_all_capacity_prices`: 814 rows, internal, 2028-06-01
- `hub_price_comparison`: 575 rows, public, 2026-09-01
- `ercot_node_transmission`: 569 rows, public, 2026-11-06
- `ercot_node_wires_utilities`: 569 rows, public, 2026-10-23
- `ercot_node_planned_generation`: 569 rows, public, 2026-10-23
- `ercot_node_places`: 569 rows, public, 2026-10-23
- `carb_auction_allowance_prices`: 336 rows, public, 2026-08-01
- `rggi_auction_allowance_prices`: 304 rows, internal, 2026-09-09
- `pjm_rpm_capacity_prices`: 234 rows, internal, 2028-06-01
- `price_board_carbon`: 15 rows, internal, 2026-09-09

### markets_operations (sessions 3001 to 3003 (with prices), 3016)

The grids' own operating tables: node basis, scarcity and shoulder hours, stress days, cleared energy, ERCOT's battery awards and forecasts, the network.

- `ercot_dam_esr_awards`: 2,026,149 rows, public, 2026-08-30
- `ercot_sced_esr_hourly`: 1,637,727 rows, public, 2026-08-28
- `node_basis_daily`: 997,839 rows, public, 2026-11-04
- `clean_energy_hourly`: 476,129 rows, public, 2026-11-02
- `caiso_wind_solar_forecast`: 348,361 rows, public, 2026-11-05
- `scarcity_hours_by_grid`: 201,579 rows, public, 2026-10-31
- `ercot_wind_solar_output_hourly`: 52,608 rows, public, 2026-01-01
- `event_window_daily`: 29,953 rows, public, 2026-02-02
- `clean_energy_summary`: 27,834 rows, public, 2026-10-01
- `shoulder_hours_monthly`: 27,489 rows, public, 2026-10-17
- `grid_network_links`: 25,488 rows, public, 2026-11-03
- `caiso_reliability_daily`: 20,726 rows, public, 2026-10-30
- `iso_trader_daily`: 20,100 rows, public, 2026-11-06
- `spp_dam_cleared_energy`: 15,024 rows, public, 2026-10-25
- `ercot_wind_solar_hsl_hourly`: 13,932 rows, public, 2026-11-05
- `nyiso_dam_cleared_energy`: 10,080 rows, public, 2026-10-26
- `caiso_dam_cleared_energy`: 10,063 rows, public, 2026-10-25
- `cost_of_power_hourly_profile`: 4,368 rows, public, 2026-10-01
- `ercot_wind_solar_forecast`: 3,978 rows, public, 2026-11-12
- `event_study_estimates`: 3,040 rows, public, 2026-02-02
- `flex_alert_effects`: 2,973 rows, public, 2024-07-25
- `price_years_by_window`: 2,754 rows, public, 2026-01-01
- `grid_stress_yearly`: 2,394 rows, public, 2026-01-01
- `cost_of_power_monthly`: 2,304 rows, public, 2026-10-01
- `ercot_transmission_projects`: 2,203 rows, public, 2033-12-15
- `caiso_grid_emergencies`: 1,906 rows, public, 2026-10-08
- `ercot_cdr_units`: 1,772 rows, public, 2026-10-23
- `ercot_cdr_reserve_margins`: 1,600 rows, public, 2030-12-01
- `node_basis_summary`: 1,344 rows, public, 2026-11-01
- `isone_dam_cleared_energy`: 1,296 rows, internal, 2026-10-25
- `flex_alert_model`: 881 rows, public, 2025-08-24
- `texas_transmission_matrix`: 855 rows, internal, 2026-03-16
- `isone_ddg_undelivered_monthly`: 840 rows, internal, 2026-09-01
- `ercot_dam_cleared_energy`: 624 rows, public, 2026-10-25
- `grid_stress_days`: 282 rows, public, 2026-10-08
- `ercot_wind_solar_hsl_daily`: 258 rows, public, 2026-11-04
- `ercot_grid_notices`: 178 rows, public, 2026-10-15
- `grid_network_nodes`: 84 rows, public, 2026-11-02
- `iso_rt_top_intervals`: 50 rows, public, 2026-11-04
- `ercot_wind_solar_hsl_monthly`: 45 rows, public, 2026-10-01

### demand (sessions 3004)

EIA-930 and the ISOs' load, the sub-regions, degree days and the state climate; the large-load tariffs and rules sit here by name and are hunted in 3012.

- `eia930_all_emissions`: 4,367,376 rows, public, 2026-11-02
- `ferc714_area_demand_2006`: 1,532,108 rows, internal, 2006-12-31
- `ferc714_area_demand_2007`: 1,375,404 rows, internal, 2007-12-31
- `ferc714_area_demand_2008`: 1,326,412 rows, internal, 2008-12-31
- `ferc714_area_demand_2009`: 1,100,955 rows, internal, 2009-12-31
- `ferc714_area_demand_2010`: 1,098,623 rows, internal, 2010-12-31
- `ferc714_area_demand_2012`: 1,062,839 rows, internal, 2012-12-31
- `ferc714_area_demand_2011`: 1,059,978 rows, internal, 2011-12-31
- `ferc714_area_demand_2013`: 1,054,827 rows, internal, 2013-12-31
- `eia930_daily_interchange`: 956,116 rows, public, 2026-11-03
- `ferc714_area_demand_2014`: 884,855 rows, internal, 2014-12-31
- `ferc714_area_demand_2016`: 869,616 rows, internal, 2016-12-31
- `ferc714_area_demand_2015`: 867,248 rows, internal, 2015-12-31
- `ferc714_area_demand_2017`: 858,484 rows, internal, 2017-12-31
- `ferc714_area_demand_2018`: 849,724 rows, internal, 2018-12-31
- `ferc714_area_demand_2020`: 834,384 rows, internal, 2020-12-31
- `ferc714_area_demand_2019`: 832,185 rows, internal, 2019-12-31
- `ferc714_area_demand_2021`: 796,348 rows, internal, 2021-12-31
- `ferc714_area_demand_2022`: 784,264 rows, internal, 2022-12-31
- `ferc714_area_demand_2024`: 781,703 rows, internal, 2024-12-31
- `ferc714_area_demand_2023`: 779,627 rows, internal, 2023-12-31
- `ferc714_area_demand_2025`: 770,886 rows, internal, 2025-12-31
- `eia930_subba_demand_hourly_2024`: 726,716 rows, public, 2024-12-31
- `eia930_subba_demand_hourly_2025`: 723,617 rows, public, 2025-12-31
- `eia930_subba_demand_hourly_2020`: 719,312 rows, public, 2020-12-31
- `eia930_subba_demand_hourly_2023`: 717,332 rows, public, 2023-12-31
- `eia930_subba_demand_hourly_2022`: 712,831 rows, public, 2022-12-31
- `eia930_subba_demand_hourly_2021`: 710,831 rows, public, 2021-12-31
- `eia930_subba_demand_hourly_2019`: 687,952 rows, public, 2019-12-31
- `eia930_all_interchange`: 395,016 rows, public, 2026-11-03
- `caiso_area_load_hourly`: 268,356 rows, public, 2026-10-24
- `eia930_event_hourly_interchange`: 266,833 rows, public, 2025-06-29
- `eia930_daily_total_interchange`: 213,373 rows, public, 2026-11-04
- `eia930_daily_demand`: 192,582 rows, public, 2026-11-04
- `eia930_subba_demand_hourly`: 186,177 rows, public, 2026-10-21
- `eia930_all_generation`: 141,000 rows, public, 2026-11-04
- `noaa_cpc_degree_days_daily`: 118,900 rows, public, 2026-10-21
- `eia861_demand_response`: 77,073 rows, public, 2025-01-01
- `eia930_all_storage`: 74,784 rows, public, 2026-11-04
- `eia930_all_history`: 60,084 rows, public, 2018-07-01
- `nspower_ns_load_hourly`: 40,308 rows, internal, 2026-09-01
- `ieso_ontario_demand_hourly`: 31,680 rows, public, 2026-10-23
- `noaa_climdiv_state_monthly`: 31,458 rows, public, 2026-09-01
- `eia930_all_demand`: 26,208 rows, public, 2026-11-04
- `eia930_demand_growth`: 24,116 rows, public, 2026-01-01
- `bchydro_ba_load_hourly`: 24,095 rows, internal, 2026-10-01
- `subregion_demand_growth`: 3,918 rows, public, 2026-01-01
- `large_load_waits`: 2,622 rows, internal, 2026-10-08
- `eia930_generation_latest`: 2,485 rows, public, 2026-11-05
- `eia930_demand_weather`: 1,057 rows, public, 2026-01-01
- `emi_nz_generation_demand_monthly`: 846 rows, public, 2026-09-01
- `large_load_statements`: 798 rows, internal, 2026-10-08
- `egrid_subregions_annual`: 540 rows, public, 2023-01-01
- `large_load_document_verdicts`: 427 rows, internal, 2026-10-14
- `large_load_public`: 341 rows, public, 2026-09-30
- `large_load_rule_reads`: 87 rows, public, 2026-10-07
- `large_load_rules_internal`: 75 rows, internal, 2026-10-30
- `nyiso_load_queue`: 74 rows, public, 2026-10-07
- `grid_peak_vs_capacity`: 56 rows, public, 2025-01-01
- `large_load_rules`: 44 rows, public, 2026-10-28
- `large_load_connection_rules`: 39 rows, public, 2027-04-09
- `ercot_large_load_status`: 38 rows, public, 2026-06-19
- `utility_large_load_tariffs`: 13 rows, public, 2026-05-07

### generation_pipeline (sessions 3005 to 3007)

EIA-930 generation, EIA-860M and EIA-923, the nuclear fleet, LBNL's solar and wind, the hydropower tables, the plant inventories.

- `eia_nuclear_outages_generator_daily`: 2,141,406 rows, public, 2026-10-21
- `eia_nuclear_outages_facility_daily`: 1,312,872 rows, public, 2026-10-21
- `eia923_plant_fuel_annual`: 872,492 rows, public, 2024-01-01
- `eia923_plant_fuel_monthly`: 660,531 rows, public, 2025-12-01
- `caiso_curtailment_intervals`: 486,469 rows, public, 2026-11-02
- `caiso_battery_storage`: 375,840 rows, public, 2026-11-05
- `ieso_generation_fuel_hourly`: 371,781 rows, public, 2026-10-23
- `usbr_crsp_reservoirs_daily`: 330,293 rows, public, 2026-10-22
- `nrc_reactor_status`: 236,240 rows, public, 2026-11-05
- `eia_state_generation_monthly`: 201,076 rows, public, 2026-08-01
- `usbr_mead_powell_daily`: 192,508 rows, public, 2026-10-22
- `eia861_distributed_generation`: 179,161 rows, public, 2025-01-01
- `generation_mix_hourly_profile`: 164,724 rows, public, 2026-10-01
- `ba_supply_monthly`: 158,503 rows, public, 2026-09-01
- `state_generation_mix_monthly`: 108,125 rows, public, 2026-08-01
- `nlr_atb_electricity_costs`: 95,000 rows, public, 2060-01-01
- `usace_nid_dams`: 92,788 rows, public, 2026-10-23
- `uswtdb_wind_turbines`: 77,839 rows, public, 2026-10-21
- `eia_state_capacity_annual`: 56,719 rows, public, 2024-01-01
- `eia_gas_storage_state_monthly`: 55,015 rows, public, 2026-07-01
- `eia_power_fuel_stocks_monthly`: 48,702 rows, public, 2026-07-01
- `energy_projects`: 39,917 rows, public, 2026-11-05
- `spp_curtailment_daily`: 38,632 rows, public, 2026-11-04
- `epa_needs_units`: 38,030 rows, public, 2026-10-24
- `eia_state_source_disposition_annual`: 37,738 rows, public, 2024-01-01
- `eia923_fuel_receipts`: 36,733 rows, public, 2025-12-01
- `usbr_hydropower_monthly`: 31,702 rows, public, 2025-10-01
- `eia860m_operating_generators`: 28,712 rows, public, 2026-11-05
- `caiso_curtailment_daily`: 25,228 rows, public, 2026-11-04
- `eia_gas_storage_capacity_monthly`: 23,980 rows, public, 2026-07-01
- `eia_nuclear_outages_daily`: 21,702 rows, public, 2026-10-21
- `storage_buildout_monthly`: 21,382 rows, public, 2026-09-01
- `ercot_storage_dam_offers_daily`: 20,826 rows, public, 2026-08-29
- `storage_owners_monthly`: 19,180 rows, public, 2026-09-01
- `nrc_rop_findings`: 18,240 rows, public, 2025-05-12
- `eia860_plants_annual`: 17,349 rows, public, 2026-10-23
- `nuclear_fleet_status`: 15,048 rows, public, 2026-01-01
- `storage_daily_cycle`: 14,836 rows, public, 2026-11-04
- `eia_power_plant_fuel_costs`: 13,160 rows, public, 2026-08-01
- `egrid_power_plants`: 12,612 rows, public, 2026-10-21
- `battery_stack_monthly`: 11,556 rows, public, 2026-10-01
- `lbnl_tracking_the_sun`: 8,762 rows, public, 2024-01-01
- `eia860_solar_generators`: 8,520 rows, public, 2026-10-23
- `eia_gas_storage_type_monthly`: 8,367 rows, public, 2026-07-01
- `cence_costarica_generation_monthly`: 7,731 rows, internal, 2026-08-01
- `eia860m_retired_generators_all`: 7,334 rows, public, 2026-10-06
- `eia_gas_storage_weekly`: 7,016 rows, public, 2026-10-16
- `uspvdb_solar_facilities`: 6,611 rows, public, 2026-10-23
- `caiso_curtailment_profile`: 6,240 rows, public, 2026-10-01
- `eia860_generator_owners`: 5,680 rows, public, 2026-10-23
- `nlr_jedi_multipliers`: 5,562 rows, public, 2017-01-01
- `eia860_emission_controls`: 5,375 rows, public, 2026-10-23
- `ornl_eha_hydropower_units`: 5,362 rows, public, 2026-10-23
- `generator_pipeline_by_grid`: 5,147 rows, public, 2026-09-01
- `eia860_boilers`: 4,384 rows, public, 2026-10-23
- `eia860_multifuel_generators`: 3,785 rows, public, 2026-10-23
- `battery_stack_review_monthly`: 3,744 rows, public, 2026-10-01
- `iso_curtailment_monthly`: 3,256 rows, public, 2026-10-01
- `eia_lng_storage_annual`: 3,074 rows, public, 2024-01-01
- `eia411_capacity_margins_annual`: 2,924 rows, public, 2027-10-01
- `eia860m_planned_generators`: 2,361 rows, public, 2026-11-05
- `ornl_eha_hydropower_plants`: 2,257 rows, public, 2026-10-23
- `battery_stack_stress_daily`: 1,890 rows, public, 2026-10-08
- `eia860_cooling_systems`: 1,797 rows, public, 2026-10-23
- `eia860_storage_generators`: 1,782 rows, public, 2026-10-23
- `lbnl_solar_projects`: 1,775 rows, public, 2026-10-23
- `eia860_wind_generators`: 1,745 rows, public, 2026-10-23
- `storage_capacity`: 1,648 rows, public, 2026-11-05
- `eia_capacity_factors_monthly`: 1,224 rows, public, 2025-12-01
- `lbnl_wind_capacity_factors`: 1,210 rows, public, 2025-01-01
- `lbnl_ppa_prices`: 1,133 rows, public, 2025-06-13
- `lbnl_hybrid_plants`: 1,068 rows, internal, 2026-10-23
- `statec_lu_electricity_generation_annual`: 942 rows, public, 2024-01-01
- `ercot_storage_dam_offers_monthly`: 819 rows, public, 2026-08-01
- `cec_total_system_generation_annual`: 795 rows, public, 2025-01-01
- `ornl_tedb_transportation_annual`: 674 rows, internal, 2024-01-01
- `ornl_npd_potential`: 597 rows, public, 2026-10-23
- `ornl_hydropower_relicensing`: 559 rows, public, 2025-12-23
- `eia_annual_generation_ba`: 515 rows, public, 2025-01-01
- `sne_panama_generation_monthly`: 504 rows, public, 2021-12-01
- `eia_capacity_factors_annual`: 374 rows, public, 2025-01-01
- `ercot_storage_rt_monthly`: 329 rows, public, 2026-08-01
- `generation_mix_records`: 306 rows, public, 2026-10-31
- `eia860m_retired_generators`: 260 rows, public, 2026-11-05
- `ercot_storage_dam_awards_monthly`: 252 rows, public, 2026-08-01
- `nrc_license_actions`: 236 rows, public, 2026-04-02
- `ornl_hydropower_pipeline`: 196 rows, public, 2026-10-23
- `eia_annual_crosscheck_ba`: 144 rows, public, 2025-01-01
- `nrc_power_reactors`: 130 rows, public, 2026-10-23
- `lbnl_wind_turbine_orders`: 122 rows, public, 2016-07-01
- `lbnl_wind_costs`: 119 rows, public, 2025-06-30
- `lbnl_hybrid_ppa_prices`: 113 rows, public, 2025-06-13
- `doe_grip_selections`: 105 rows, public, 2024-10-18
- `battery_sourced_ranges`: 90 rows, public, 2025-01-01
- `zimstat_zimbabwe_generation_monthly`: 85 rows, internal, 2026-03-01
- `blm_ca_renewable_rows`: 57 rows, public, 2026-10-23
- `boem_renewable_leases`: 52 rows, public, 2026-10-21
- `nrc_advanced_reactor_preapplicants`: 43 rows, public, 2026-10-23
- `nrc_event_notifications`: 25 rows, public, 2026-10-17
- `nrc_new_reactor_applications`: 6 rows, public, 2026-05-05

### gas (sessions 3008)

The gas balance, storage by region and by week, production, consumption, prices by state, LNG and the pipeline projects.

- `eia_world_oil_gas_annual`: 448,267 rows, public, 2025-01-01
- `eia_gas_prices_state_monthly`: 72,550 rows, public, 2026-07-01
- `eia_gas_consumption_state_monthly`: 63,420 rows, public, 2026-07-01
- `eia_gas_production_state_monthly`: 47,805 rows, public, 2026-07-01
- `gas_balance_weekly`: 40,507 rows, public, 2026-10-16
- `eia_gas_trade_country_monthly`: 30,337 rows, public, 2026-07-01
- `eia_gas_interstate_annual`: 29,470 rows, public, 2024-01-01
- `eia_gas_reserves_annual`: 19,232 rows, public, 2021-01-01
- `eia_gas_consumers_state_annual`: 12,864 rows, public, 2024-01-01
- `blm_oil_gas_statistics_annual`: 12,500 rows, public, 2024-10-01
- `eia_gas_balance_annual`: 11,274 rows, public, 2025-01-01
- `eia_gas_for_others_annual`: 9,245 rows, public, 2024-01-01
- `eia_gas_heat_content_monthly`: 8,476 rows, public, 2026-07-01
- `eia_gas_plant_processing_annual`: 5,829 rows, public, 2025-01-01
- `eia_shale_gas_reserves_annual`: 4,455 rows, public, 2021-01-01
- `eia_gas_other_uses_state_annual`: 3,838 rows, public, 2025-01-01
- `eia_gas_trade_monthly`: 1,979 rows, public, 2026-07-01
- `eia_gas_pipeline_projects`: 1,334 rows, public, 2031-01-01
- `eia_lng_exports_monthly`: 1,100 rows, public, 2026-08-01
- `eia_gas_wells_annual`: 1,062 rows, public, 2020-01-01
- `gastat_saudi_electricity_annual`: 177 rows, internal, 2024-01-01
- `instat_madagascar_electricity_monthly`: 168 rows, internal, 2026-06-01
- `doe_lng_export_applications`: 135 rows, public, 2026-10-23
- `eia_lng_liquefaction_projects`: 48 rows, public, 2026-10-23

### queues_deals_datacenters (sessions 3009 to 3011)

The ISO queue snapshots and LBNL's Queued Up, the deals and companies, the datacenter projects, facilities and sites, the large-load status lists.

- `census_c30_construction_monthly`: 82,760 rows, public, 2026-08-01
- `lbnl_interconnection_queue`: 38,201 rows, public, 2026-10-02
- `interconnection_queue_summary`: 17,246 rows, public, 2025-01-01
- `treasury_1603_awards`: 10,012 rows, internal, 2017-11-10
- `miso_interconnection_queue`: 3,881 rows, public, 2026-09-30
- `interconnection_durations`: 3,098 rows, public, 2026-10-02
- `spp_interconnection_queue`: 3,079 rows, public, 2026-11-05
- `interconnection_agreements_signed`: 2,522 rows, public, 2026-10-02
- `caiso_interconnection_queue`: 2,278 rows, public, 2026-11-05
- `census_cbp_hosting_annual`: 1,836 rows, public, 2023-01-01
- `nyiso_interconnection_queue`: 1,814 rows, public, 2026-09-26
- `isone_interconnection_queue`: 1,751 rows, public, 2026-11-05
- `ercot_interconnection_queue`: 1,736 rows, public, 2026-11-05
- `iso_queue_statistics`: 1,511 rows, public, 2026-01-01
- `interconnection_durations_summary`: 1,365 rows, public, 2025-01-01
- `census_qss_utilities_hosting_quarterly`: 784 rows, public, 2024-10-01
- `energy_deals_evidence`: 585 rows, internal, 2026-11-05
- `iso_queue_snapshot_summary`: 570 rows, public, 2026-10-26
- `energy_deals`: 529 rows, public, 2026-11-05
- `energy_companies`: 504 rows, public, 2026-11-05
- `interconnection_agreements_by_grid`: 438 rows, public, 2025-01-01
- `datacenter_facilities`: 428 rows, public, 2026-11-05
- `datacenter_operator_sites`: 264 rows, public, 2026-11-05
- `datacenter_projects_evidence`: 183 rows, internal, 2026-11-05
- `datacenter_projects`: 163 rows, public, 2026-11-05
- `usaspending_doe_obligations`: 163 rows, internal, 2026-08-01
- `datacenter_queue_positions`: 3 rows, public, 2026-11-05

### tariffs_policy (sessions 3012)

The utility large-load tariffs and connection rules (listed under demand by name), EIA-861, retail sales and costs, the policy actions and reads.

- `eia861m_utility_sales_monthly`: 1,051,488 rows, public, 2026-07-01
- `ferc_eqr_contracts_history`: 571,115 rows, internal, 2223-01-01
- `eia861_net_metering`: 507,206 rows, public, 2025-01-01
- `eia861_advanced_meters`: 497,838 rows, public, 2025-01-01
- `eia861_utility_sales`: 433,115 rows, public, 2025-01-01
- `eia861_operational_data`: 367,768 rows, public, 2025-01-01
- `eia_retail_sales_monthly`: 228,947 rows, public, 2026-08-01
- `eia861_energy_efficiency`: 187,850 rows, public, 2025-01-01
- `ferc_eqr_contract_terms`: 186,873 rows, internal, 2223-01-01
- `ferc_eqr_contracts`: 186,873 rows, internal, 2223-01-01
- `eia_retail_electricity_prices`: 114,574 rows, public, 2026-08-01
- `eia861_utility_reliability`: 90,705 rows, public, 2025-01-01
- `eia861_short_form`: 44,170 rows, public, 2025-01-01
- `eia861_distribution_systems`: 34,947 rows, public, 2025-01-01
- `eia861_dynamic_pricing`: 33,157 rows, public, 2025-01-01
- `eia861_utility_data`: 22,716 rows, public, 2026-10-21
- `eia_energy_efficiency_state_annual`: 19,740 rows, public, 2024-01-01
- `ferc_eqr_buyer_names`: 17,955 rows, internal, 2026-10-04
- `eia_net_metering_state_annual`: 16,226 rows, public, 2024-01-01
- `ferc_eqr_party_totals`: 12,290 rows, internal, 2026-10-04
- `utility_service_territories`: 11,893 rows, public, 2026-10-21
- `eia_meters_state_annual`: 8,578 rows, public, 2024-01-01
- `eia_ice_electricity_daily`: 7,056 rows, internal, 2026-10-14
- `policy_reads_evidence`: 3,559 rows, internal, 2026-11-05
- `policy_actions`: 2,020 rows, public, 2026-11-05
- `ferc_eqr_buyer_doubtful`: 1,281 rows, internal, 2026-06-30
- `ferc_eqr_party_mw`: 812 rows, internal, 2026-10-05
- `eia_power_costs_annual`: 550 rows, public, 2025-01-01
- `eia861_delivery_only`: 546 rows, public, 2025-01-01
- `policy_reads`: 408 rows, public, 2026-11-05
- `wapa_energy_sales_annual`: 307 rows, public, 2024-10-01
- `ferc714_respondents`: 219 rows, internal, 2026-10-21
- `texas_delivery_charges`: 73 rows, internal, 2026-10-07
- `ferc_eqr_quarter_changes`: 68 rows, internal, 2026-04-01
- `impact_tax_rules`: 49 rows, public, 2026-10-20
- `eia_heat_rates_annual`: 44 rows, public, 2025-01-01
- `policy_action_tags`: 38 rows, public, 2026-09-04
- `ercot_4cp_intervals`: 28 rows, public, 2025-09-04

### oil_products_world (sessions 3013 to 3015)

Petroleum supply and disposition, crude imports by origin, the PADD flows, refinery tables, retail fuels, the world oil tables, PortWatch's chokepoints.

- `boem_ogor_lease_production_monthly`: 1,131,562 rows, public, 2026-06-01
- `caiso_fuel_supply_history`: 782,808 rows, public, 2025-06-01
- `eia_world_oil_monthly`: 541,215 rows, public, 2026-07-01
- `eia_petroleum_snd_monthly`: 523,835 rows, public, 2026-07-01
- `eia_world_electricity_annual`: 332,254 rows, public, 2024-01-01
- `eia_refinery_production_monthly`: 326,819 rows, public, 2026-07-01
- `eia_world_coal_annual`: 317,307 rows, public, 2024-01-01
- `msha_coal_production_quarterly`: 294,323 rows, public, 2026-04-01
- `svk_sweden_production_hourly`: 274,176 rows, internal, 2025-03-18
- `eia_world_energy_co2_annual`: 246,988 rows, public, 2025-01-01
- `eia_refinery_inputs_monthly`: 216,010 rows, public, 2026-07-01
- `rrc_lease_production_monthly`: 212,252 rows, public, 2026-07-01
- `eia_crude_imports_detail_monthly`: 183,393 rows, public, 2026-07-01
- `caiso_fuel_supply`: 160,992 rows, public, 2026-11-05
- `eia_padd_rail_barge_movements_monthly`: 120,742 rows, public, 2026-07-01
- `portwatch_chokepoint_transits`: 119,910 rows, internal, 2026-10-25
- `eia_petroleum_exports_by_destination`: 112,478 rows, public, 2026-07-01
- `eia_ngl_production_monthly`: 110,896 rows, public, 2026-07-01
- `eia_petroleum_stocks_state_monthly`: 73,997 rows, public, 2026-07-01
- `eia_coal_mine_production_annual`: 72,852 rows, public, 2024-01-01
- `eia_product_supplied_monthly`: 71,938 rows, public, 2026-07-01
- `eia_refinery_capacity_annual`: 62,804 rows, public, 2026-01-01
- `eia_refinery_weekly`: 50,753 rows, public, 2026-10-16
- `eia_heating_fuel_prices_weekly`: 48,534 rows, public, 2026-10-19
- `eia_refinery_utilization_monthly`: 36,672 rows, public, 2026-07-01
- `eia_petroleum_supply_weekly`: 26,178 rows, public, 2026-10-16
- `eia_crude_production_state_monthly`: 25,644 rows, public, 2026-07-01
- `eia_crude_imports_by_country`: 22,657 rows, public, 2026-08-01
- `eia_coal_production_annual`: 22,630 rows, public, 2024-01-01
- `eia_petroleum_stocks_monthly`: 18,247 rows, public, 2026-07-01
- `eia_petroleum_stocks_weekly`: 16,847 rows, public, 2026-10-30
- `eia_regional_retail_fuel_prices`: 16,359 rows, public, 2026-11-02
- `eia_crude_quality_monthly`: 15,968 rows, public, 2026-07-01
- `onrr_production_annual`: 15,068 rows, public, 2025-01-01
- `eia_crude_reserves_annual`: 13,931 rows, public, 2021-01-01
- `eia_petroleum_trade_weekly`: 12,607 rows, public, 2026-10-30
- `wb_commodity_prices_monthly`: 11,139 rows, public, 2026-09-01
- `fhwa_motor_fuel_monthly`: 7,998 rows, public, 2026-05-01
- `eia_oxygenate_production_monthly`: 6,006 rows, public, 2026-07-01
- `eia_retail_fuel_prices`: 5,340 rows, public, 2026-11-02
- `eia_padd_crude_pipeline_flows`: 4,566 rows, public, 2026-08-01
- `eia_crude_tank_farm_stocks_monthly`: 3,553 rows, public, 2026-07-01
- `eia_crude_stream_prices`: 3,013 rows, public, 2026-09-01
- `onrr_production_monthly`: 2,264 rows, public, 2026-07-01
- `eia_basin_production_monthly`: 1,668 rows, public, 2026-07-01
- `epa_rfs_rins_monthly`: 1,632 rows, public, 2026-09-01
- `eia_crude_first_purchase_prices`: 862 rows, public, 2026-08-01
- `epa_rfs_fuel_annual`: 568 rows, public, 2026-01-01
- `eia_biofuel_plants`: 511 rows, public, 2026-10-23
- `imf_commodity_prices`: 465 rows, public, 2026-09-01
- `statbel_be_electricity_production_annual`: 200 rows, public, 2025-01-01
- `eia_uranium_production_quarterly`: 171 rows, public, 2026-04-01

### coal_uranium_metals (sessions after 3016 (chain 166))

Coal production, prices and receipts, MSHA's mines, uranium, the USGS minerals.

- `eia_coal_receipts_annual`: 270,547 rows, public, 2025-01-01
- `msha_coal_mines`: 35,736 rows, public, 2026-10-23
- `usgs_streamflow_daily`: 33,421 rows, public, 2026-10-22
- `eia_coal_trade_price_annual`: 24,623 rows, public, 2025-01-01
- `usgs_comcat_earthquakes_south_central`: 16,000 rows, public, 2026-10-22
- `eia_coal_delivered_price_annual`: 3,213 rows, public, 2025-01-01
- `eia_coal_price_rank_annual`: 2,843 rows, public, 2024-01-01
- `eia_coal_prices_annual`: 2,781 rows, public, 2024-01-01
- `usgs_mcs_critical_minerals`: 1,600 rows, public, 2025-01-01
- `eia_coal_distribution_quarterly`: 1,207 rows, public, 2024-10-01
- `eia_uranium_marketing_annual`: 763 rows, public, 2025-01-01
- `eia_uranium_facilities`: 24 rows, public, 2026-10-23

### emissions_climate (sessions after 3016 (chain 166))

Emissions inventories and the carbon intensity tables, the weather and hazards (drought, wildfire, storms, disasters).

- `noaa_station_weather_hourly`: 4,761,203 rows, public, 2026-10-26
- `noaa_grid_weather_hourly`: 1,913,253 rows, public, 2026-10-26
- `carbon_intensity_hourly`: 1,132,545 rows, public, 2026-11-02
- `noaa_isd_hourly`: 412,435 rows, public, 2025-08-27
- `noaa_ncei_storm_events`: 411,139 rows, public, 2026-07-01
- `epa_tri_energy_releases_annual`: 384,483 rows, public, 2023-01-01
- `gfz_kp_index_3h`: 277,032 rows, public, 2026-10-22
- `usdm_drought_state_weekly`: 177,696 rows, public, 2026-10-20
- `noaa_grid_weather_daily`: 118,990 rows, public, 2026-10-25
- `nrcs_snotel_swe_daily`: 86,241 rows, internal, 2026-10-22
- `epa_ghgrp_facility_emissions`: 70,338 rows, public, 2023-01-01
- `eia_co2_state_annual`: 66,144 rows, public, 2022-01-01
- `carbon_intensity_daily`: 47,171 rows, public, 2026-11-02
- `nhc_hurdat2_track_points`: 27,812 rows, public, 2025-11-01
- `fema_disaster_declarations`: 26,199 rows, public, 2026-10-17
- `epa_ghgrp_power_co2`: 17,035 rows, public, 2023-01-01
- `weather_forecast_hourly`: 15,108 rows, public, 2026-11-12
- `weather_obs_hourly`: 15,068 rows, public, 2026-11-05
- `eia_power_co2_state_annual`: 10,640 rows, public, 2024-01-01
- `wfigs_wildfires`: 6,222 rows, public, 2026-10-21
- `epa_ghg_inventory_annual`: 5,016 rows, public, 2022-01-01
- `doe_oe417_events`: 3,313 rows, public, 2025-12-30
- `noaa_uscrn_solar_monthly`: 2,025 rows, public, 2026-09-01
- `noaa_cpc_oni_monthly`: 1,840 rows, public, 2026-08-01
- `scripps_co2_mlo_monthly`: 1,636 rows, public, 2026-09-01
- `carbon_intensity_monthly`: 1,285 rows, public, 2026-10-01
- `cost_of_power_carbon`: 712 rows, public, 2026-10-01
- `noaa_ncei_billion_disasters`: 403 rows, public, 2024-10-09
- `noaa_grid_weather_stations`: 245 rows, public, 2019-01-01

### other_us (sessions after 3016 (chain 166))

Consumption by sector and state, the forecasts (STEO, AEO), buildings and households, transport, federal revenue; five Energy-Charts tables of Europe fall here by name.

- `energy_charts_central_europe`: 1,419,805 rows, public, 2026-10-23
- `energy_charts_italy_power`: 1,329,375 rows, public, 2026-10-22
- `energy_charts_belgium_hourly`: 908,600 rows, public, 2026-10-23
- `energy_charts_portugal_power`: 725,799 rows, public, 2026-10-22
- `onrr_revenue_monthly`: 413,554 rows, public, 2026-08-01
- `bpa_ba_hourly`: 400,261 rows, public, 2026-10-23
- `doe_lead_energy_burden`: 160,419 rows, public, 2022-01-01
- `energy_charts_southeast_europe_daily`: 128,530 rows, public, 2026-10-22
- `eia_aeo_emm_regions`: 75,712 rows, public, 2050-01-01
- `eia_net_imports_monthly`: 65,501 rows, public, 2026-07-01
- `eia_seds_state_energy`: 49,140 rows, public, 2024-01-01
- `eia_aeo_electricity`: 34,034 rows, public, 2050-01-01
- `eia_seds_residential_annual`: 20,020 rows, public, 2024-01-01
- `eia_state_to_state_capacity`: 19,311 rows, public, 2025-01-01
- `eia_ieo_projections`: 17,856 rows, public, 2050-01-01
- `eia_primary_energy_monthly`: 15,180 rows, public, 2026-07-01
- `afdc_station_counts_annual`: 13,520 rows, public, 2025-01-01
- `ntd_transit_energy_annual`: 10,161 rows, public, 2025-01-01
- `eia_sector_energy_consumption_monthly`: 9,002 rows, public, 2026-07-01
- `boem_offshore_platforms`: 7,092 rows, public, 2026-10-23
- `census_bps_state_annual`: 6,732 rows, public, 2025-01-01
- `afdc_vehicle_registrations_annual`: 6,240 rows, public, 2025-01-01
- `eia_cbecs_commercial_buildings`: 5,944 rows, public, 2018-01-01
- `eia_mecs_manufacturing`: 5,363 rows, public, 2022-01-01
- `eia_steo_forecasts`: 5,088 rows, public, 2027-12-01
- `bsee_offshore_incidents`: 4,818 rows, public, 2024-12-31
- `eia_international_electricity_annual`: 4,131 rows, public, 2024-01-01
- `eia_drilling_monthly`: 3,431 rows, public, 2026-02-01
- `epa_lmop_landfill_projects`: 3,399 rows, public, 2026-10-23
- `doe_useer_employment`: 3,311 rows, public, 2025-01-01
- `afdc_ev_charging_state_annual`: 3,060 rows, public, 2025-01-01
- `eia_recs_households`: 2,802 rows, public, 2020-01-01
- `eia_wood_pellets_monthly`: 2,090 rows, public, 2026-05-01
- `census_metro_population`: 1,650 rows, public, 2025-07-01
- `irs_soi_energy_credits_annual`: 1,074 rows, public, 2023-01-01
- `dbedt_hawaii_electricity_annual`: 268 rows, internal, 2025-01-01
- `ai_power_regions`: 187 rows, public, 2026-09-30

### outside_us (sessions not hunted (US first))

The statistics offices and operators outside the US. Coverage is US first: this chain drafts no finding whose claim is about another country, and reads these only as a comparison a US finding names.

156 tables; not listed here (coverage.csv holds them).

### platform_news (sessions not hunted)

The news index and scores, the cost ledger, the known faults: the platform's records, not the energy system's.

5 tables; not listed here (coverage.csv holds them).


## State by family

| Family | State | Session | Drafts kept |
|---|---|---|---:|
| prices | hunted: ERCOT hourly shape, spreads, volatility, reserves (not drafted), Henry Hub, gas by state, world gas, carbon, Brent and WTI | 3001 to 3003 | 33 |
| markets_operations | not hunted | | 0 |
| demand | hunted: EIA-930 daily by authority and hourly by sub-region | 3004 | 12 |
| generation_pipeline | hunted in part: the mix by state and by grid hour; nuclear; heat rates | 3005, 3006 | 24 |
| gas | not hunted | | 0 |
| queues_deals_datacenters | not hunted | | 0 |
| tariffs_policy | not hunted | | 0 |
| oil_products_world | not hunted | | 0 |
| coal_uranium_metals | not hunted | | 0 |
| emissions_climate | not hunted | | 0 |
| other_us | not hunted | | 0 |
