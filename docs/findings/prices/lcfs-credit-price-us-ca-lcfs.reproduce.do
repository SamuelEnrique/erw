* Expected: 2019 191.602692, 2025 59.258269, change -132.344423 (USD per tCO2); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate lcfs_credit_price for us_ca_lcfs from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "carb_lcfs_credit_prices.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate int month = real(substr(ts_utc, 6, 2))

keep if entity == "carb:lcfs_credit" & variable == "credit_price_weekly_avg"

collapse (mean) measure = value (count) n = value, by(year)

sort year

list year measure n, noobs
