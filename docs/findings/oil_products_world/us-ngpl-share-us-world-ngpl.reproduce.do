* Expected: 1993 28.394035, 2025 50.545009, change 22.150974 (percent of world NGPL); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate us_ngpl_share for us_world_ngpl from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_world_oil_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

duplicates drop entity variable ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

keep if (entity == "eia_intl:USA:58" & variable == "production") | (entity == "eia_intl:WORL:58" & variable == "production")

generate str3 side = cond(entity == "eia_intl:USA:58", "num", "den")

keep year ts_utc side value

reshape wide value, i(ts_utc) j(side) string

drop if missing(valuenum) | missing(valueden)

collapse (sum) num = valuenum (sum) den = valueden (count) n = valuenum, by(year)

keep if den != 0

generate double measure = num * 100.0 / den

sort year

list year measure n, noobs
