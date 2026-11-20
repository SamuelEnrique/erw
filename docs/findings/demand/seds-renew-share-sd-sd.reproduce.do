* Expected: 1990 8.72132, 2024 40.691958, change 31.970638 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate seds_renew_share for sd_sd from the ERW's public table eia_seds_state_energy.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_seds_state_energy.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia_seds:RETCB:SD" | entity == "eia_seds:TETCB:SD"

keep entity ts_utc value

destring value, replace force

generate str5 code = substr(entity, 10, 5)

drop entity

reshape wide value, i(ts_utc) j(code) string

drop if missing(valueRETCB) | missing(valueTETCB)

keep if valueTETCB > 0

generate int year = real(substr(ts_utc, 1, 4))

generate double measure = 100 * valueRETCB / valueTETCB

generate byte n = 1

sort year

list year measure n, noobs
