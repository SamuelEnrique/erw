* Expected: 1990 20.71, 2025 42.266, change 21.556 (bcf a day); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate s2s_out for s2out_mississippi from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_state_to_state_capacity.csv", varnames(1) stringcols(_all) clear

keep if x_state_from == "Mississippi"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

collapse (sum) measure = value, by(year)

generate byte n = 1

sort year

list year measure n, noobs
