* Expected: 2012 2097.0, 2023 2698.0, change 601.0 (establishments); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate hosting_sites for est518_CA from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "census_cbp_hosting_annual.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if entity == "census_cbp_518210:ca"

keep if variable == "establishments"

collapse (sum) measure = value, by(year)

generate byte n = 1

sort year

list year measure n, noobs
