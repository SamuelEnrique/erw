* Expected: 2001 2.250653, 2025 56.508213, change 54.25756 (percent of delivered gas); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate state_power_share for burn_NH from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_gas_consumption_state_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double num = value if regexm(entity, ":SNH$") & (variable == "consumption_electric_power")

egen byte num_month = tag(ts_utc) if !missing(num)

generate double den = value if regexm(entity, ":SNH$") & (variable == "consumption_residential" | variable == "consumption_commercial" | variable == "consumption_industrial" | variable == "consumption_electric_power")

collapse (sum) num (sum) den (sum) n = num_month, by(year)

keep if n > 0 & den != 0

generate double measure = num * 100.0 / den

sort year

list year measure n, noobs
