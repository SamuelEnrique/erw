* Expected: 2001 163.358333, 2025 404.75, change 241.391667 (USD per MWh); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate res_price for res_price_HI from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_retail_electricity_prices.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if entity == "eia:retail_price:HI:RES" & variable == "retail_price"

collapse (mean) measure = value (count) n = value, by(year)

sort year

list year measure n, noobs
