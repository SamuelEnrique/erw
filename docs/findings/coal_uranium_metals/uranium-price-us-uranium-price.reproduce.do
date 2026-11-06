* Expected: 2003 10.81, 2025 58.46, change 47.65 (USD per pound U3O8e); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 166): reproduce candidate uranium_price for us_uranium_price from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_uranium_marketing_annual.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

duplicates drop entity variable ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

keep if entity == "eia_uranium:us" & variable == "price_purchased_total"

collapse (mean) measure = value, by(year)

replace measure = measure * 1.0

generate byte n = 1

sort year

list year measure n, noobs
