* Expected: 2001 0.901815, 2025 8.327696, change 7.425881 (percent of US marketed production); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate state_production_share for prod_WV from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_gas_production_state_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double num = value if regexm(entity, "^eia_gas_production:SWV:") & (variable == "marketed_production")

egen byte num_month = tag(ts_utc) if !missing(num)

generate double den = value if regexm(entity, "^eia_gas_production:NUS:") & (variable == "marketed_production")

collapse (sum) num (sum) den (sum) n = num_month, by(year)

keep if n > 0 & den != 0

generate double measure = num * 100.0 / den

sort year

list year measure n, noobs
