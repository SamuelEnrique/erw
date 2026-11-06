* Expected: 2000 -0.45, 2025 8.436667, change 8.886667 (USD per MMBtu); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate europe_gas_premium for us_europe_gas from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "wb_commodity_prices_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate int month = real(substr(ts_utc, 6, 2))

keep if variable == "price" & (entity == "wb_pink:natural_gas_europe" | entity == "wb_pink:natural_gas_us")

keep if year >= 2000

generate str5 side = cond(entity == "wb_pink:natural_gas_us", "us", "other")

keep ts_utc year side value

reshape wide value, i(ts_utc) j(side) string

drop if missing(valueus) | missing(valueother)

generate double gap = valueother - valueus

collapse (mean) measure = gap (count) n = gap, by(year)

sort year

list year measure n, noobs
