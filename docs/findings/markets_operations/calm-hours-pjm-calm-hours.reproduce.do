* Expected: 2019 1492.0, 2025 1976.0, change 484.0 (hours); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 166): reproduce candidate calm_hours for pjm_calm_hours from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "grid_stress_yearly.csv", varnames(1) stringcols(_all) clear

keep if entity == "iso:pjm" & (variable == "calm_hours")

destring value, replace force

drop if missing(value)

duplicates drop entity variable ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

keep year variable value

reshape wide value, i(year) j(variable) string

drop if missing(valuecalm_hours)

generate double measure = valuecalm_hours * 1.0

generate byte n = 1

sort year

list year measure n, noobs
