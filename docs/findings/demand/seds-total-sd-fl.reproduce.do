* Expected: 1990 3275.218, 2024 4357.609, change 1082.391 (TBtu); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate seds_total for sd_fl from the ERW's public table eia_seds_state_energy.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_seds_state_energy.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia_seds:TETCB:FL"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double measure = value

generate byte n = 1

sort year

list year measure n, noobs
