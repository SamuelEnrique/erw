* Expected: 1980 107.796, 2024 1371.121134, change 1263.325134 (million short tons); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate wc_consumption for wc_ind from the ERW's public table eia_world_coal_annual.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_world_coal_annual.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia_intl:IND:7" & variable == "consumption"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double measure = value / 1000000

generate byte n = 1

sort year

list year measure n, noobs
