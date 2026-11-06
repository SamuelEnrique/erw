* Expected: 1997 2.013445, 2025 3.188406, change 1.17496 (percent a day); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate henry_hub_volatility for us_henry_hub from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_fuel_spot_prices.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia:henry_hub" & variable == "spot_price"

destring value, replace force

keep if value > 0 & !missing(value)

sort ts_utc

generate double change = abs(value / value[_n - 1] - 1) * 100

drop if missing(change)

generate int year = real(substr(ts_utc, 1, 4))

collapse (median) measure = change (count) n = change, by(year)

sort year

list year measure n, noobs
