* Expected: 1992 20.351275, 2024 200.601697, change 180.250422 (million short tons); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate wc_exports for wc_rus from the ERW's public table eia_world_coal_annual.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_world_coal_annual.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia_intl:RUS:7" & variable == "exports"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double measure = value / 1000000

generate byte n = 1

sort year

list year measure n, noobs
