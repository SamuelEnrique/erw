* Expected: 1996 1008.933525, 2025 1947.851329, change 938.917804 (thousand barrels a day); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate gulf_oil for gulf from the ERW's public table boem_ogor_lease_production_monthly.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "boem_ogor_lease_production_monthly.csv", varnames(1) stringcols(_all) clear

keep if variable == "oil_production"

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate str7 ym = substr(ts_utc, 1, 7)

bysort year ym: generate byte firstm = _n == 1

collapse (sum) vol = value (sum) n = firstm, by(year)

generate double measure = vol / cond(mod(year, 4) == 0, 366, 365)

sort year

list year measure n, noobs
