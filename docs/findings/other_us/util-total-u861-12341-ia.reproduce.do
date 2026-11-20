* Expected: 2017 22.365099, 2025 30.810704, change 8.445606 (TWh); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate util_total for u861_12341_ia from the ERW's public table eia861m_utility_sales_monthly.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia861m_utility_sales_monthly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia861m:12341:IA" & variable == "total_sales"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

collapse (sum) measure = value (count) n = value, by(year)

replace measure = measure / 1000000

sort year

list year measure n, noobs
