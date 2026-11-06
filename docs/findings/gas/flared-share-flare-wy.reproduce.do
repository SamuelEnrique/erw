* Expected: 2001 0.456395, 2024 4.462246, change 4.005851 (percent of gross withdrawals); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate flared_share for flare_WY from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_gas_production_state_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double num = value if regexm(entity, "^eia_gas_production:SWY:") & (variable == "vented_flared")

egen byte num_month = tag(ts_utc) if !missing(num)

generate double den = value if regexm(entity, "^eia_gas_production:SWY:") & (variable == "gross_withdrawals")

collapse (sum) num (sum) den (sum) n = num_month, by(year)

keep if n > 0 & den != 0

generate double measure = num * 100.0 / den

sort year

list year measure n, noobs
