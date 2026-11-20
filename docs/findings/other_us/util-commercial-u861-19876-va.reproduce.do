* Expected: 2017 41.535599, 2025 60.088203, change 18.552603 (TWh); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate util_commercial for u861_19876_va from the ERW's public table eia861m_utility_sales_monthly.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia861m_utility_sales_monthly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia861m:19876:VA" & variable == "commercial_sales"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

collapse (sum) measure = value (count) n = value, by(year)

replace measure = measure / 1000000

sort year

list year measure n, noobs
