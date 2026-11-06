* Expected: 2002 -0.390833, 2024 -3.2, change -2.809167 (USD per Mcf); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate power_vs_citygate for state_pow_WV from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_gas_prices_state_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate int month = real(substr(ts_utc, 6, 2))

keep if geo == "US-WV" & (variable == "price_electric_power" | variable == "price_citygate")

generate str4 side = cond(variable == "price_citygate", "city", "use")

keep ts_utc year side value

reshape wide value, i(ts_utc) j(side) string

drop if missing(valuecity) | missing(valueuse)

generate double gap = valueuse - valuecity

collapse (mean) measure = gap (count) n = gap, by(year)

sort year

list year measure n, noobs
