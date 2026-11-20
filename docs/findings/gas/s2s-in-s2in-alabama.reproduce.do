* Expected: 1990 11.997, 2025 28.425, change 16.428 (bcf a day); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate s2s_in for s2in_alabama from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_state_to_state_capacity.csv", varnames(1) stringcols(_all) clear

keep if x_state_to == "Alabama"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

collapse (sum) measure = value, by(year)

generate byte n = 1

sort year

list year measure n, noobs
