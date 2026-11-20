* Expected: 2020 90.054645, 2025 68.517808, change -21.536837 (percent of full power); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate reactor_power for rp_watts_bar_1 from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "nrc_reactor_status.csv", varnames(1) stringcols(_all) clear

keep if entity == "nrc:watts_bar_1" & variable == "power_pct"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

collapse (mean) measure = value (count) n = value, by(year)

sort year

list year measure n, noobs
