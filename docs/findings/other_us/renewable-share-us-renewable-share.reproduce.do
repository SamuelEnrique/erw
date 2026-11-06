* Expected: 1973 4.019065, 2025 8.618382, change 4.599317 (percent of primary energy production); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 166): reproduce candidate renewable_share for us_renewable_share from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_primary_energy_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if entity == "eia:REPRBUS" | entity == "eia:TEPRBUS"

duplicates drop entity ts_utc, force

generate str3 side = cond(entity == "eia:REPRBUS", "ren", "all")

keep year ts_utc side value

reshape wide value, i(ts_utc) j(side) string

drop if missing(valueren) | missing(valueall)

collapse (sum) ren = valueren (sum) all = valueall (count) n = valueren, by(year)

generate double measure = 100 * ren / all

sort year

list year measure n, noobs
