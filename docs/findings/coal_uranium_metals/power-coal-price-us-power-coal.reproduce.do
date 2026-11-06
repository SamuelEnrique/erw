* Expected: 2001 24.68, 2025 45.85, change 21.17 (USD per short ton); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 166): reproduce candidate power_coal_price for us_power_coal from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_coal_delivered_price_annual.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

duplicates drop entity variable ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

keep if entity == "eia_coal_delivered:US:98" & variable == "price"

collapse (mean) measure = value, by(year)

replace measure = measure * 1.0

generate byte n = 1

sort year

list year measure n, noobs
