* Expected: 1973 14.0, 2025 2422.841, change 2408.841 (Bcf); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate mexico_exports for us_mexico from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_gas_trade_country_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double num = value if regexm(entity, "^eia_gas_trade:N9132MX2$") & (variable == "volume")

egen byte num_month = tag(ts_utc) if !missing(num)

collapse (sum) num (sum) n = num_month, by(year)

keep if n > 0

generate double measure = num * 1.0 / 1000

sort year

list year measure n, noobs
