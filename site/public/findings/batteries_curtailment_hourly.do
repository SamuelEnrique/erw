* ERW finding batteries_curtailment_hourly: BY HOW MUCH DO BATTERIES CUT CURTAILMENT, HOUR BY HOUR. Reproduces the card's correlation, regressions and ceiling counts from erw_2026_caiso_curtailment_hourly.csv.

* The CSV begins with four comment lines: the names are on line 5 and the data begin on line 6.

clear all

import delimited "erw_2026_caiso_curtailment_hourly.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring hour, replace force

destring curtailed_mw, replace force

destring charging_mw, replace force

destring net_load_mw, replace force

destring fleet_mw, replace force

destring trail_max_charging_mw, replace force

replace hour = . if hour == -999

replace curtailed_mw = . if curtailed_mw == -999

replace charging_mw = . if charging_mw == -999

replace net_load_mw = . if net_load_mw == -999

replace fleet_mw = . if fleet_mw == -999

replace trail_max_charging_mw = . if trail_max_charging_mw == -999

gen year = real(substr(day, 1, 4))

gen month = substr(day, 1, 7)

encode month, gen(month_id)

encode day, gen(day_id)

gen net_load_gw = net_load_mw / 1000

gen net_load_gw2 = net_load_gw ^ 2

gen charging_hour = charging_mw > 0

correlate curtailed_mw charging_mw

regress curtailed_mw charging_mw, vce(cluster day_id)

regress curtailed_mw charging_mw net_load_gw net_load_gw2, vce(cluster day_id)

regress curtailed_mw charging_mw net_load_gw net_load_gw2 i.hour i.month_id, vce(cluster day_id)

* vce(cluster day_id) is the card's standard errors: hours of one Pacific day are not independent

regress curtailed_mw net_load_gw net_load_gw2 i.hour i.month_id

predict predicted, xb

predict residual, residuals

tabstat curtailed_mw predicted residual if charging_hour == 1, by(year) statistics(mean n) format(%9.1f)

* net load before curtailment: the curtailed MW added back to wind and solar

gen net_load_before_gw = (net_load_mw - curtailed_mw) / 1000

gen net_load_before_gw2 = net_load_before_gw ^ 2

regress curtailed_mw charging_mw net_load_before_gw net_load_before_gw2 i.hour i.month_id, vce(cluster day_id)

gen at_ceiling = charging_hour == 1 & !missing(trail_max_charging_mw) & charging_mw >= 0.90 * trail_max_charging_mw

gen at_nameplate = !missing(fleet_mw) & charging_mw >= 0.90 * fleet_mw

tabstat at_ceiling at_nameplate, by(year) statistics(sum) format(%9.0f)

tabstat curtailed_mw if at_ceiling == 1 & curtailed_mw >= 1, by(year) statistics(n sum) format(%9.0f)
