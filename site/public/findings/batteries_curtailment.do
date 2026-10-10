* ERW finding batteries_curtailment: BY HOW MUCH DO BATTERIES CUT CURTAILMENT. Reproduces the card's three regressions from erw_2026_caiso_curtailment_batteries.csv.

clear all

import delimited "erw_2026_caiso_curtailment_batteries.csv", varnames(1) stringcols(_all) clear

destring curtailed_mwh, replace force

destring curtailed_solar_mwh, replace force

destring curtailed_wind_mwh, replace force

destring charging_mwh, replace force

destring discharging_mwh, replace force

destring solar_mwh, replace force

destring battery_intervals, replace force

destring solar_hours, replace force

replace curtailed_mwh = . if curtailed_mwh == -999

replace curtailed_solar_mwh = . if curtailed_solar_mwh == -999

replace curtailed_wind_mwh = . if curtailed_wind_mwh == -999

replace charging_mwh = . if charging_mwh == -999

replace discharging_mwh = . if discharging_mwh == -999

replace solar_mwh = . if solar_mwh == -999

replace battery_intervals = . if battery_intervals == -999

replace solar_hours = . if solar_hours == -999

gen charging_gwh = charging_mwh / 1000

gen solar_gwh = solar_mwh / 1000

encode month, gen(month_id)

regress curtailed_mwh charging_gwh, vce(robust)

regress curtailed_mwh charging_gwh solar_gwh, vce(robust)

regress curtailed_mwh charging_gwh solar_gwh i.month_id, vce(robust)

summarize charging_mwh, detail

gen high_charging = charging_mwh > r(p50)

tabstat curtailed_mwh, by(high_charging) statistics(mean n) format(%9.0f)
