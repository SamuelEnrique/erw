* ERW, Research (/research, Automated Analysis): the figures the page prints, rebuilt from its public downloads (session 3701, chain 208).

* Method: docs/methods/automated_analysis.md, "Replication". replicate.py beside this file follows it step for step and prints the same comparison.

* This do-file has not been run: Stata is not installed on the machine that wrote it. replicate.py printed, on 6 November 2026: 65 of 66 computed figures inside the tolerance, 1 a known difference (the weekly chart's score, which this file does not compute), 10 license needed, 2 not in a download.

* Run it from this folder (replication/analysis). The cards' CSVs are read from the repository's copies (../../site/public/findings); a reader with the CSVs elsewhere sets the global csv below to that folder. The site serves the same files at https://erw-flame.vercel.app/findings/.

* What it does not compute, and why: the figures the page prints as "license needed" (a callout whose words name ISO-NE, MISO or NYISO, held under their publishers' terms since 21 October 2026); the siting card's months to connect (not in its CSV); the weekly chart's four figures (its file is JSON, which Stata reads only with a package; replicate.py rebuilds them); today's chart (no download of /research holds its rows).

* Each card's CSV has comment lines first (four, or three for the siting cards), then the column names, then the rows. Every column is read as text and each numeric column is destringed with force.

clear all

set more off

global csv "../../site/public/findings"

* The inputs, from this folder's assumptions.csv (assumptions.json holds the same values with their sources and how to change each). Each becomes a scalar a_<stata name>.

import delimited using "assumptions.csv", varnames(1) stringcols(_all) clear

destring value, replace force

forvalues i = 1/`=_N' {
    local n = stata[`i']
    scalar a_`n' = value[`i']
}

* ---------------------------------------------------------------- 1. Batteries and price spikes, five grids (batteries_lunch_grids)

* ERCOT's worst-interval multiple in its first year and in the last year before the newest; its battery fleet in the newest month that holds one. NYISO's figures on the page are "license needed".

import delimited using "$csv/erw_2026_grids_spikes_batteries.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring interval_minutes, replace force

destring n_intervals, replace force

destring median_usd_mwh, replace force

destring p999_usd_mwh, replace force

destring worst_interval_multiple, replace force

destring hours_top1pct, replace force

destring hours_ge_1000, replace force

destring hours_ge_250, replace force

destring battery_mw, replace force

destring load_mean_mw, replace force

destring henry_hub_usd_mmbtu, replace force

destring share_of_year_pct, replace force

gen yr = real(period) if kind == "year"

summarize yr if grid == "ercot"

scalar y_max = r(max)

scalar y_min = r(min)

summarize yr if grid == "ercot" & yr < scalar(y_max)

scalar y_last = r(max)

summarize worst_interval_multiple if grid == "ercot" & yr == scalar(y_min)

scalar blg_ercot_multiple_first = r(mean)

summarize worst_interval_multiple if grid == "ercot" & yr == scalar(y_last)

scalar blg_ercot_multiple_last = r(mean)

preserve

keep if grid == "ercot" & kind == "month" & battery_mw < .

sort period

scalar blg_ercot_fleet_last_mw = battery_mw[_N]

restore

* ---------------------------------------------------------------- 2. Batteries and CAISO's daily curtailment (batteries_curtailment)

* Daily curtailment, MWh, on charging, GWh: alone, then with solar, GWh, and the month fixed; robust (HC1) errors. The days at or below the median charging against those above it.

import delimited using "$csv/erw_2026_caiso_curtailment_batteries.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring curtailed_mwh, replace force

destring curtailed_solar_mwh, replace force

destring curtailed_wind_mwh, replace force

destring charging_mwh, replace force

destring discharging_mwh, replace force

destring solar_mwh, replace force

destring battery_intervals, replace force

destring solar_hours, replace force

gen double charging_gwh = charging_mwh / 1000

gen double solar_gwh = solar_mwh / 1000

encode month, gen(month_id)

regress curtailed_mwh charging_gwh, vce(robust)

scalar bc_charging_coef = _b[charging_gwh]

regress curtailed_mwh charging_gwh solar_gwh i.month_id, vce(robust)

scalar bc_charging_solar_month_coef = _b[charging_gwh]

scalar bc_charging_solar_month_se = _se[charging_gwh]

scalar bc_charging_solar_month_r2 = e(r2)

summarize charging_mwh, detail

scalar med_charging = r(p50)

summarize curtailed_mwh if charging_mwh <= scalar(med_charging)

scalar bc_curtailed_low_charging_days = r(mean)

summarize curtailed_mwh if charging_mwh > scalar(med_charging)

scalar bc_curtailed_high_charging_days = r(mean)

* ---------------------------------------------------------------- 3. Batteries and CAISO's hourly curtailment (batteries_curtailment_hourly)

* What net load alone, with the hour and the month fixed, predicts in the charging hours of 2025, against what was observed; the correlation of curtailment with charging; the hours at the charging ceiling with curtailment on, in 2021 and 2025 (the years the page's callouts name).

import delimited using "$csv/erw_2026_caiso_curtailment_hourly.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring hour, replace force

destring curtailed_mw, replace force

destring charging_mw, replace force

destring net_load_mw, replace force

destring fleet_mw, replace force

destring trail_max_charging_mw, replace force

gen year = real(substr(day, 1, 4))

gen month = substr(day, 1, 7)

encode month, gen(month_id)

gen double nl = net_load_mw / 1000

gen double nl2 = nl^2

regress curtailed_mw nl nl2 i.hour i.month_id

predict double pred, xb

correlate curtailed_mw charging_mw

scalar bch_corr_curtailed_charging = r(rho)

scalar bch_charging_r2 = r(rho)^2

gen is_charging = charging_mw > 0 & charging_mw < .

gen on = curtailed_mw >= scalar(a_bch_on_mw) & curtailed_mw < .

gen at_trail = is_charging == 1 & trail_max_charging_mw < . & charging_mw >= scalar(a_bch_ceiling_pct) / 100 * trail_max_charging_mw

summarize curtailed_mw if year == 2025 & is_charging == 1

scalar bch_y2025_obs_charging_mw = r(mean)

summarize pred if year == 2025 & is_charging == 1

scalar bch_y2025_pred_charging_mw = r(mean)

count if year == 2021 & at_trail == 1 & on == 1

scalar bch_y2021_sat_curt_hours = r(N)

count if year == 2025 & at_trail == 1 & on == 1

scalar bch_y2025_sat_curt_hours = r(N)

* ---------------------------------------------------------------- 4. Hours priced below gas's fuel cost (gas_sets_price)

* ERCOT's share of hours below Henry Hub times 7.0 (and 6.5 and 8.0) in the first year and the last full year. ISO-NE's figures on the page are "license needed".

import delimited using "$csv/erw_2026_gas_share_hours.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring year, replace force

destring n_hours, replace force

destring share_below_hr6p5, replace force

destring share_below_hr7, replace force

destring share_below_hr8, replace force

summarize year

scalar y_max = r(max)

scalar y_min = r(min)

summarize year if year < scalar(y_max)

scalar y_last = r(max)

summarize share_below_hr7 if grid == "ercot" & year == scalar(y_min)

scalar gsp_ercot_first = r(mean)

summarize share_below_hr7 if grid == "ercot" & year == scalar(y_last)

scalar gsp_ercot_last = r(mean)

summarize share_below_hr6p5 if grid == "ercot" & year == scalar(y_last)

scalar gsp_ercot_last_hr6p5 = r(mean)

summarize share_below_hr8 if grid == "ercot" & year == scalar(y_last)

scalar gsp_ercot_last_hr8 = r(mean)

* ---------------------------------------------------------------- 5. The impact of an event on a series (impact_study)

* The series' mean before and from the event, the difference in differences against the control, and the Newey-West error of the daily difference on the after dummy, L = floor(4 (n / 100) ^ (2 / 9)). The control's own means are "license needed" on the page (NYISO) and are not displayed.

import delimited using "$csv/erw_2026_impact_event_control.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring t, replace force

destring after, replace force

destring in_window, replace force

destring series_value, replace force

destring control_value, replace force

destring diff, replace force

keep if in_window == 1 & diff < .

summarize series_value if after == 0

scalar imp_series_pre = r(mean)

summarize series_value if after == 1

scalar imp_series_post = r(mean)

summarize control_value if after == 0

scalar c_pre = r(mean)

summarize control_value if after == 1

scalar c_post = r(mean)

scalar imp_did = (scalar(imp_series_post) - scalar(imp_series_pre)) - (scalar(c_post) - scalar(c_pre))

gen tt = _n

tsset tt

local nw_lags = floor(4 * (_N / 100)^(2 / 9))

newey diff after, lag(`nw_lags')

scalar imp_reg_did_se = _se[after]

* ---------------------------------------------------------------- 6. Negative prices in the West (negative_prices_west)

import delimited using "$csv/erw_2026_negative_hours_hubs.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring year, replace force

destring n_hours, replace force

destring negative_hours, replace force

destring share_pct, replace force

destring negative_intervals, replace force

destring n_intervals, replace force

summarize year

scalar y_max = r(max)

scalar y_min = r(min)

summarize year if year < scalar(y_max)

scalar y_last = r(max)

summarize negative_hours if hub == "ercot_west" & year == scalar(y_min)

scalar npw_ercot_west_first = r(mean)

summarize negative_hours if hub == "ercot_west" & year == scalar(y_last)

scalar npw_ercot_west_last = r(mean)

summarize negative_hours if hub == "ercot_houston" & year == scalar(y_min)

scalar npw_ercot_houston_first = r(mean)

summarize negative_hours if hub == "ercot_houston" & year == scalar(y_last)

scalar npw_ercot_houston_last = r(mean)

summarize share_pct if hub == "ercot_west" & year == scalar(y_min)

scalar npw_ercot_west_first_share = r(mean)

summarize share_pct if hub == "ercot_west" & year == scalar(y_last)

scalar npw_ercot_west_last_share = r(mean)

* ---------------------------------------------------------------- 7. The peak hour moved, by grid (peak_hour_grids)

* ERCOT's share of days peaking 17:00 to 21:59 in its first year held and its last full year held, and its solar fleet at the end of that year; the rows of hour 0 hold each year's figures. NYISO's figures on the page are "license needed".

import delimited using "$csv/erw_2026_grids_peak_hour_solar.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring year, replace force

destring hour, replace force

destring share_days_pct, replace force

destring n_days, replace force

destring median_peak_hour, replace force

destring share_evening_pct, replace force

destring share_midday_pct, replace force

destring solar_mw_yearend, replace force

summarize year

scalar y_this = r(max)

keep if grid == "ercot" & hour == 0 & n_days < . & n_days != 0

summarize year

scalar y_min = r(min)

summarize year if year < scalar(y_this)

scalar y_last = r(max)

summarize share_evening_pct if year == scalar(y_min)

scalar phg_ercot_first_evening_pct = r(mean)

summarize share_evening_pct if year == scalar(y_last)

scalar phg_ercot_last_evening_pct = r(mean)

summarize solar_mw_yearend if year == scalar(y_last)

scalar phg_ercot_last_solar_mw = r(mean)

* ---------------------------------------------------------------- 8. The interconnection queue's divorce rate (queue_divorce)

import delimited using "$csv/erw_2026_queue_outcomes_technology.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring projects, replace force

destring requested_gw, replace force

destring withdrawn_gw, replace force

destring withdrawn_pct, replace force

destring operational_gw, replace force

destring operational_pct, replace force

destring active_gw, replace force

destring active_pct, replace force

destring suspended_gw, replace force

destring suspended_pct, replace force

destring unknown_gw, replace force

destring unknown_pct, replace force

destring cdc_marriage_rate_per_1000, replace force

destring cdc_divorce_rate_per_1000, replace force

summarize withdrawn_pct if technology == "All technologies"

scalar qd_withdrawn_pct = r(mean)

summarize requested_gw if technology == "All technologies"

scalar qd_requested_gw = r(mean)

summarize operational_pct if technology == "All technologies"

scalar qd_operational_pct = r(mean)

summarize withdrawn_pct if technology != "All technologies"

scalar qd_worst_withdrawn_pct = r(max)

scalar qd_best_withdrawn_pct = r(min)

summarize cdc_divorce_rate_per_1000 if technology == "All technologies"

scalar qd_cdc_divorce_rate = r(mean)

summarize cdc_marriage_rate_per_1000 if technology == "All technologies"

scalar qd_cdc_marriage_rate = r(mean)

scalar qd_cdc_ratio_pct = scalar(qd_cdc_divorce_rate) / scalar(qd_cdc_marriage_rate) * 100

* ---------------------------------------------------------------- 9. Who rescues whom in an event (who_rescues_whom)

import delimited using "$csv/erw_2026_event_interchange_flips.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring baseline_net_mwh_day, replace force

destring event_net_mwh_day, replace force

destring swing_mwh_day, replace force

destring baseline_days, replace force

destring event_days, replace force

destring event_grid, replace force

count if flip == "import_to_export"

scalar wrw_n_to_export = r(N)

count if flip == "export_to_import"

scalar wrw_n_to_import = r(N)

summarize baseline_net_mwh_day if event_grid == 1

scalar wrw_grid_baseline_abs = abs(r(mean))

summarize event_net_mwh_day if event_grid == 1

scalar wrw_grid_event_abs = abs(r(mean))

summarize event_net_mwh_day if flip == "import_to_export"

scalar big_event = r(max)

summarize baseline_net_mwh_day if flip == "import_to_export" & event_net_mwh_day == scalar(big_event)

scalar wrw_big_exp_baseline_abs = abs(r(mean))

scalar wrw_big_exp_event_abs = abs(scalar(big_event))

* ---------------------------------------------------------------- 10. Where a battery's day swings most (siting_battery_swing)

import delimited using "$csv/siting_battery_swing.csv", varnames(4) rowrange(5) stringcols(_all) clear

destring swing_mean_usd_mwh, replace force

destring swing_p10_usd_mwh, replace force

destring swing_p90_usd_mwh, replace force

destring days, replace force

keep if days >= scalar(a_sbs_min_days)

sort swing_mean_usd_mwh node

scalar sbs_narrowest = swing_mean_usd_mwh[1]

scalar sbs_widest = swing_mean_usd_mwh[_N]

scalar sbs_widest_p10 = swing_p10_usd_mwh[_N]

scalar sbs_widest_p90 = swing_p90_usd_mwh[_N]

scalar sbs_nodes = _N

summarize swing_mean_usd_mwh, detail

scalar sbs_median = r(p50)

* ---------------------------------------------------------------- 11. What stepping off saves (siting_flexible)

* The saving all-in, flat less flexible, at each ERCOT row; the hours given up; both all-in figures at the hub average (the row ercot:HB_HUBAVG, assumptions.json siting_flexible_hub_row).

import delimited using "$csv/siting_flexible.csv", varnames(4) rowrange(5) stringcols(_all) clear

destring allin_flat_usd_mwh, replace force

destring allin_flexible_usd_mwh, replace force

destring saved_usd_mwh, replace force

destring hours_given_up, replace force

destring hours_run, replace force

gen double saved = allin_flat_usd_mwh - allin_flexible_usd_mwh

sort saved row

scalar sfl_saved_least = saved[1]

scalar sfl_saved_most = saved[_N]

sort hours_given_up row

scalar sfl_lost_fewest = hours_given_up[1]

scalar sfl_lost_most = hours_given_up[_N]

summarize allin_flat_usd_mwh if row == "ercot:HB_HUBAVG"

scalar sfl_hub_flat = r(mean)

summarize allin_flexible_usd_mwh if row == "ercot:HB_HUBAVG"

scalar sfl_hub_flex = r(mean)

* ---------------------------------------------------------------- 12. Where a gigawatt pays least (siting_gigawatt)

* All-in is energy, transmission and capacity; a year is all-in times 1,000 MW x 0.90 x 8,760 hours (assumptions.csv).

import delimited using "$csv/siting_gigawatt.csv", varnames(4) rowrange(5) stringcols(_all) clear

destring energy_usd_mwh, replace force

destring transmission_usd_mwh, replace force

destring capacity_usd_mwh, replace force

destring allin_usd_mwh, replace force

destring year_usd_1gw, replace force

gen double allin = energy_usd_mwh + transmission_usd_mwh + capacity_usd_mwh

sort allin row

scalar year_mwh = scalar(a_sgw_mw) * scalar(a_sgw_load_factor) * scalar(a_sgw_hours)

scalar sgw_least_allin = allin[1]

scalar sgw_most_allin = allin[_N]

scalar sgw_least_year_usd = allin[1] * scalar(year_mwh)

scalar sgw_most_year_usd = allin[_N] * scalar(year_mwh)

* ---------------------------------------------------------------- the comparison with the page

* page_figures.csv holds what the page prints for each figure, the figure of the card's numbers it is, and the tolerance (half of the last shown digit).

import delimited using "page_figures.csv", varnames(1) stringcols(_all) clear

destring callout, replace force

destring part, replace force

destring page, replace force

destring decimals, replace force

destring tolerance, replace force

destring held, replace force

gen double replication = .

replace replication = scalar(blg_ercot_multiple_first) if card == "batteries_lunch_grids" & field == "ercot_multiple_first"

replace replication = scalar(blg_ercot_multiple_last) if card == "batteries_lunch_grids" & field == "ercot_multiple_last"

replace replication = scalar(blg_ercot_fleet_last_mw) if card == "batteries_lunch_grids" & field == "ercot_fleet_last_mw"

replace replication = scalar(bc_curtailed_low_charging_days) if card == "batteries_curtailment" & field == "curtailed_low_charging_days"

replace replication = scalar(bc_curtailed_high_charging_days) if card == "batteries_curtailment" & field == "curtailed_high_charging_days"

replace replication = scalar(bc_charging_coef) if card == "batteries_curtailment" & field == "charging_coef"

replace replication = scalar(bc_charging_solar_month_coef) if card == "batteries_curtailment" & field == "charging_solar_month_coef"

replace replication = scalar(bc_charging_solar_month_se) if card == "batteries_curtailment" & field == "charging_solar_month_se"

replace replication = scalar(bc_charging_solar_month_r2) if card == "batteries_curtailment" & field == "charging_solar_month_r2"

replace replication = scalar(bch_y2025_pred_charging_mw) if card == "batteries_curtailment_hourly" & field == "y2025_pred_charging_mw"

replace replication = scalar(bch_y2025_obs_charging_mw) if card == "batteries_curtailment_hourly" & field == "y2025_obs_charging_mw"

replace replication = scalar(bch_corr_curtailed_charging) if card == "batteries_curtailment_hourly" & field == "corr_curtailed_charging"

replace replication = scalar(bch_charging_r2) if card == "batteries_curtailment_hourly" & field == "charging_r2"

replace replication = scalar(bch_y2021_sat_curt_hours) if card == "batteries_curtailment_hourly" & field == "y2021_sat_curt_hours"

replace replication = scalar(bch_y2025_sat_curt_hours) if card == "batteries_curtailment_hourly" & field == "y2025_sat_curt_hours"

replace replication = scalar(gsp_ercot_first) if card == "gas_sets_price" & field == "ercot_first"

replace replication = scalar(gsp_ercot_last) if card == "gas_sets_price" & field == "ercot_last"

replace replication = scalar(gsp_ercot_last_hr6p5) if card == "gas_sets_price" & field == "ercot_last_hr6p5"

replace replication = scalar(gsp_ercot_last_hr8) if card == "gas_sets_price" & field == "ercot_last_hr8"

replace replication = scalar(imp_series_pre) if card == "impact_study" & field == "series_pre"

replace replication = scalar(imp_series_post) if card == "impact_study" & field == "series_post"

replace replication = scalar(imp_did) if card == "impact_study" & field == "did"

replace replication = scalar(imp_reg_did_se) if card == "impact_study" & field == "reg_did_se"

replace replication = scalar(npw_ercot_west_first) if card == "negative_prices_west" & field == "ercot_west_first"

replace replication = scalar(npw_ercot_west_last) if card == "negative_prices_west" & field == "ercot_west_last"

replace replication = scalar(npw_ercot_houston_first) if card == "negative_prices_west" & field == "ercot_houston_first"

replace replication = scalar(npw_ercot_houston_last) if card == "negative_prices_west" & field == "ercot_houston_last"

replace replication = scalar(npw_ercot_west_first_share) if card == "negative_prices_west" & field == "ercot_west_first_share"

replace replication = scalar(npw_ercot_west_last_share) if card == "negative_prices_west" & field == "ercot_west_last_share"

replace replication = scalar(phg_ercot_first_evening_pct) if card == "peak_hour_grids" & field == "ercot_first_evening_pct"

replace replication = scalar(phg_ercot_last_evening_pct) if card == "peak_hour_grids" & field == "ercot_last_evening_pct"

replace replication = scalar(phg_ercot_last_solar_mw) if card == "peak_hour_grids" & field == "ercot_last_solar_mw"

replace replication = scalar(qd_withdrawn_pct) if card == "queue_divorce" & field == "withdrawn_pct"

replace replication = scalar(qd_requested_gw) if card == "queue_divorce" & field == "requested_gw"

replace replication = scalar(qd_operational_pct) if card == "queue_divorce" & field == "operational_pct"

replace replication = scalar(qd_worst_withdrawn_pct) if card == "queue_divorce" & field == "worst_withdrawn_pct"

replace replication = scalar(qd_best_withdrawn_pct) if card == "queue_divorce" & field == "best_withdrawn_pct"

replace replication = scalar(qd_cdc_divorce_rate) if card == "queue_divorce" & field == "cdc_divorce_rate"

replace replication = scalar(qd_cdc_marriage_rate) if card == "queue_divorce" & field == "cdc_marriage_rate"

replace replication = scalar(qd_cdc_ratio_pct) if card == "queue_divorce" & field == "cdc_ratio_pct"

replace replication = scalar(wrw_n_to_export) if card == "who_rescues_whom" & field == "n_to_export"

replace replication = scalar(wrw_n_to_import) if card == "who_rescues_whom" & field == "n_to_import"

replace replication = scalar(wrw_grid_baseline_abs) if card == "who_rescues_whom" & field == "grid_baseline_abs"

replace replication = scalar(wrw_grid_event_abs) if card == "who_rescues_whom" & field == "grid_event_abs"

replace replication = scalar(wrw_big_exp_baseline_abs) if card == "who_rescues_whom" & field == "big_exp_baseline_abs"

replace replication = scalar(wrw_big_exp_event_abs) if card == "who_rescues_whom" & field == "big_exp_event_abs"

replace replication = scalar(sbs_narrowest) if card == "siting_battery_swing" & field == "narrowest"

replace replication = scalar(sbs_widest) if card == "siting_battery_swing" & field == "widest"

replace replication = scalar(sbs_median) if card == "siting_battery_swing" & field == "median"

replace replication = scalar(sbs_nodes) if card == "siting_battery_swing" & field == "nodes"

replace replication = scalar(sbs_widest_p10) if card == "siting_battery_swing" & field == "widest_p10"

replace replication = scalar(sbs_widest_p90) if card == "siting_battery_swing" & field == "widest_p90"

replace replication = scalar(sfl_saved_least) if card == "siting_flexible" & field == "saved_least"

replace replication = scalar(sfl_saved_most) if card == "siting_flexible" & field == "saved_most"

replace replication = scalar(sfl_lost_fewest) if card == "siting_flexible" & field == "lost_fewest"

replace replication = scalar(sfl_lost_most) if card == "siting_flexible" & field == "lost_most"

replace replication = scalar(sfl_hub_flat) if card == "siting_flexible" & field == "hub_flat"

replace replication = scalar(sfl_hub_flex) if card == "siting_flexible" & field == "hub_flex"

replace replication = scalar(sgw_least_allin) if card == "siting_gigawatt" & field == "least_allin"

replace replication = scalar(sgw_most_allin) if card == "siting_gigawatt" & field == "most_allin"

replace replication = scalar(sgw_least_year_usd) if card == "siting_gigawatt" & field == "least_year_usd"

replace replication = scalar(sgw_most_year_usd) if card == "siting_gigawatt" & field == "most_year_usd"

gen double difference = replication - page

gen str60 status = ""

replace status = "license needed" if held == 1

replace status = "not in the download" if not_in_download != ""

replace status = "not computed here (the week's chart: replicate.py)" if card == "chart_of_the_week"

replace status = "yes" if status == "" & replication < . & abs(difference) <= tolerance + 1e-9

replace status = "NO" if status == ""

format replication difference %18.4f

list card field page_text replication difference status, noobs clean abbreviate(24)

count if status == "yes"

display "inside the tolerance: " r(N)

count if status == "NO"

display "outside the tolerance: " r(N)
