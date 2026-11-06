* Expected: 2004 55.394, 2024 374.936, change 319.542 (USD billion); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate hosting_revenue for us_rev518 from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "census_qss_utilities_hosting_quarterly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if entity == "census_qss:518" & variable == "total_revenue"

collapse (sum) measure = value (count) n = value, by(year)

replace measure = measure / 1000000000

sort year

list year measure n, noobs
