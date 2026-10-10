* ERW finding batteries_lunch_grids: BATTERIES ATE THEIR OWN LUNCH? FIVE GRIDS. Reproduces each grid's regression from erw_2026_grids_spikes_batteries.csv.

* The CSV begins with four comment lines: the names are on line 5 and the data from line 6.

clear all

import delimited "erw_2026_grids_spikes_batteries.csv", varnames(5) rowrange(6) stringcols(_all) clear

keep if kind == "month"

destring interval_minutes, replace force

destring share_of_year_pct, replace force

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

replace interval_minutes = . if interval_minutes == -999

replace share_of_year_pct = . if share_of_year_pct == -999

replace n_intervals = . if n_intervals == -999

replace median_usd_mwh = . if median_usd_mwh == -999

replace p999_usd_mwh = . if p999_usd_mwh == -999

replace worst_interval_multiple = . if worst_interval_multiple == -999

replace hours_top1pct = . if hours_top1pct == -999

replace hours_ge_1000 = . if hours_ge_1000 == -999

replace hours_ge_250 = . if hours_ge_250 == -999

replace battery_mw = . if battery_mw == -999

replace load_mean_mw = . if load_mean_mw == -999

replace henry_hub_usd_mmbtu = . if henry_hub_usd_mmbtu == -999

gen battery_gw = battery_mw / 1000

gen load_gw = load_mean_mw / 1000

gen month_of_year = real(substr(period, 6, 2))

drop if missing(battery_gw) | missing(load_gw) | missing(henry_hub_usd_mmbtu) | missing(worst_interval_multiple)

foreach g in ercot caiso nyiso isone spp {
    foreach y in worst_interval_multiple hours_ge_1000 hours_top1pct {
        regress `y' battery_gw load_gw henry_hub_usd_mmbtu i.month_of_year if grid == "`g'", vce(robust)
    }
}

* vce(robust) is HC1, the card's standard errors
