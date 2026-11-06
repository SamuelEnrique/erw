* Expected: 1993 14.47344, 2025 22.322314, change 7.848874 (percent of world production); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate us_liquids_share for us_world_liquids from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_world_oil_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

duplicates drop entity variable ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

keep if (entity == "eia_intl:USA:53" & variable == "production") | (entity == "eia_intl:WORL:53" & variable == "production")

generate str3 side = cond(entity == "eia_intl:USA:53", "num", "den")

keep year ts_utc side value

reshape wide value, i(ts_utc) j(side) string

drop if missing(valuenum) | missing(valueden)

collapse (sum) num = valuenum (sum) den = valueden (count) n = valuenum, by(year)

keep if den != 0

generate double measure = num * 100.0 / den

sort year

list year measure n, noobs
