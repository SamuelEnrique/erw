* Expected: 1996 1752.0, 2025 526.0, change -1226.0 (leases); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate gulf_leases for gulf from the ERW's public table boem_ogor_lease_production_monthly.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "boem_ogor_lease_production_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

keep if value > 0 & !missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate str7 ym = substr(ts_utc, 1, 7)

bysort year entity: generate byte firstl = _n == 1

bysort year ym: generate byte firstm = _n == 1

collapse (sum) measure = firstl (sum) n = firstm, by(year)

sort year

list year measure n, noobs
