* Expected: 2013 12.83, 2025 28.055, change 15.225 (USD per tCO2); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate carb_allowance_price for us_ca_allowance from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "carb_auction_allowance_prices.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate int month = real(substr(ts_utc, 6, 2))

keep if entity == "carb:current_auction" & variable == "settlement_price"

collapse (mean) measure = value (count) n = value, by(year)

sort year

list year measure n, noobs
