* Expected: 2019 48.136986, 2025 69.950685, change 21.813699 (thousand barrels a day); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate exp_crude_dest for xc_nbr from the ERW's public table eia_petroleum_exports_by_destination.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_petroleum_exports_by_destination.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia_petroleum_exports:NUS-NBR:EPC0" & variable == "exports"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

collapse (sum) kbbl = value (count) n = value, by(year)

generate double measure = kbbl / cond(mod(year, 4) == 0, 366, 365)

sort year

list year measure n, noobs
