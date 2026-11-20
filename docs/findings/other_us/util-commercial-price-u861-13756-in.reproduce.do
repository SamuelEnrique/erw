* Expected: 2017 132.603805, 2025 192.43409, change 59.830285 (USD per MWh); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate util_commercial_price for u861_13756_in from the ERW's public table eia861m_utility_sales_monthly.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia861m_utility_sales_monthly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia861m:13756:IN" & (variable == "commercial_sales" | variable == "commercial_revenue")

keep ts_utc variable value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double s = value if variable == "commercial_sales"

generate double r = value if variable == "commercial_revenue"

collapse (sum) s = s (sum) r = r (count) ns = s (count) nr = r, by(year)

keep if s > 0

generate double measure = r / s

generate n = min(ns, nr)

sort year

list year measure n, noobs
