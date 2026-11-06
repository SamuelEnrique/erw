* Expected: 2015 67.307692, 2025 13.461538, change -53.846154 (percent of weeks); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate storage_outside for stor_salt from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "gas_balance_weekly.csv", varnames(1) stringcols(_all) clear

keep if entity == "gas_storage:salt" & (variable == "working_gas_bcf" | variable == "five_year_min_bcf" | variable == "five_year_max_bcf")

destring value, replace force

keep ts_utc variable value

reshape wide value, i(ts_utc) j(variable) string

drop if missing(valueworking_gas_bcf) | missing(valuefive_year_min_bcf) | missing(valuefive_year_max_bcf)

generate byte out = valueworking_gas_bcf < valuefive_year_min_bcf | valueworking_gas_bcf > valuefive_year_max_bcf

generate int year = real(substr(ts_utc, 1, 4))

collapse (mean) measure = out (count) n = out, by(year)

replace measure = 100 * measure

sort year

list year measure n, noobs
