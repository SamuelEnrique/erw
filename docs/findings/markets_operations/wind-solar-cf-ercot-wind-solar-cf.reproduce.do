* Expected: 2019 32.588279, 2025 29.711655, change -2.876625 (percent of capacity); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 166): reproduce candidate wind_solar_cf for ercot_wind_solar_cf from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "grid_stress_yearly.csv", varnames(1) stringcols(_all) clear

keep if entity == "iso:ercot" & (variable == "wind_solar_mean_mw" | variable == "wind_solar_capacity_mw")

destring value, replace force

drop if missing(value)

duplicates drop entity variable ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

keep year variable value

reshape wide value, i(year) j(variable) string

drop if missing(valuewind_solar_mean_mw) | missing(valuewind_solar_capacity_mw) | valuewind_solar_capacity_mw == 0

generate double measure = valuewind_solar_mean_mw * 100.0 / valuewind_solar_capacity_mw

generate byte n = 1

sort year

list year measure n, noobs
