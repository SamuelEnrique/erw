* Expected: 2003 18.036497, 2025 7.249467, change -10.78703 (percent of uranium purchased); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 166): reproduce candidate us_origin_uranium for us_uranium_origin from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_uranium_marketing_annual.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

duplicates drop entity variable ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

keep if (entity == "eia_uranium:us" & variable == "purchased_us_origin") | (entity == "eia_uranium:us" & variable == "purchased_total")

generate str3 side = cond(entity == "eia_uranium:us" & variable == "purchased_us_origin", "num", "den")

keep year ts_utc side value

reshape wide value, i(ts_utc) j(side) string

drop if missing(valuenum) | missing(valueden)

collapse (sum) num = valuenum (sum) den = valueden, by(year)

keep if den != 0

generate double measure = num * 100.0 / den

generate byte n = 1

sort year

list year measure n, noobs
