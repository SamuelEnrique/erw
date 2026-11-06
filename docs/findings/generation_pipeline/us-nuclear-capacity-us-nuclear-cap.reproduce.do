* Expected: 2007 101013.246301, 2025 98275.907945, change -2737.338356 (MW); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate us_nuclear_capacity for us_nuclear_cap from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_nuclear_outages_daily.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia_nuclear_outages:US" & variable == "capacity"

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

collapse (mean) measure = value (count) n = value, by(year)

sort year

list year measure n, noobs
