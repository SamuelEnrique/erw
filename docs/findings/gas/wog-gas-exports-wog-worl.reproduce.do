* Expected: 1990 10898.187515, 2024 43810.117244, change 32911.929729 (billion cubic feet); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate wog_gas_exports for wog_worl from the ERW's public table eia_world_oil_gas_annual.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_world_oil_gas_annual.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia_intl:WORL:26" & variable == "exports"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if year >= 1980

rename value measure

generate byte n = 1

sort year

list year measure n, noobs
