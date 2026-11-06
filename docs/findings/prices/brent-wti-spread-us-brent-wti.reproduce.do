* Expected: 1988 -1.043425, 2025 3.581926, change 4.625351 (USD per barrel); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate brent_wti_spread for us_brent_wti from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_fuel_spot_prices.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate int month = real(substr(ts_utc, 6, 2))

keep if variable == "spot_price" & (entity == "eia:brent" | entity == "eia:wti_cushing")

generate str5 side = cond(entity == "eia:brent", "brent", "wti")

keep ts_utc year side value

reshape wide value, i(ts_utc) j(side) string

drop if missing(valuebrent) | missing(valuewti)

generate double gap = valuebrent - valuewti

collapse (mean) measure = gap (count) n = gap, by(year)

sort year

list year measure n, noobs
