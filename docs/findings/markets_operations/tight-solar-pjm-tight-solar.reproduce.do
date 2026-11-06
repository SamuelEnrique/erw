* Expected: 2019 19.33, 2025 34.355, change 15.025 (percent of solar capacity); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 166): reproduce candidate tight_solar for pjm_tight_solar from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "grid_stress_yearly.csv", varnames(1) stringcols(_all) clear

keep if entity == "iso:pjm" & (variable == "tight_solar_share_of_capacity_pct")

destring value, replace force

drop if missing(value)

duplicates drop entity variable ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

keep year variable value

reshape wide value, i(year) j(variable) string

drop if missing(valuetight_solar_share_of_capacity_pct)

generate double measure = valuetight_solar_share_of_capacity_pct * 1.0

generate byte n = 1

sort year

list year measure n, noobs
