* Expected: 1997 826.767, 2024 -608.453, change -1435.22 (Bcf); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate gas_net_receipts for gn_oh from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_gas_interstate_annual.csv", varnames(1) stringcols(_all) clear

keep if variable == "net_receipts" & substr(entity, -8, 8) == ":SOH-Z0S"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double measure = value / 1000

generate byte n = 1

sort year

list year measure n, noobs
