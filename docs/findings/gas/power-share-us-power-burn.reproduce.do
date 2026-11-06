* Expected: 2001 24.022625, 2025 38.949701, change 14.927076 (percent of consumption); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate power_share for us_power_burn from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "gas_balance_weekly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double num = value if regexm(entity, "^gas_balance:US$") & (variable == "power_burn")

egen byte num_month = tag(ts_utc) if !missing(num)

generate double den = value if regexm(entity, "^gas_balance:US$") & (variable == "consumption")

collapse (sum) num (sum) den (sum) n = num_month, by(year)

keep if n > 0 & den != 0

generate double measure = num * 100.0 / den

sort year

list year measure n, noobs
