* Expected: 2013 6.441291, 2019 92.821785, change 86.380494 (percent of meters); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate ami_share for ami_IL from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_meters_state_annual.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if (entity == "eia_meters:IL:advanced_meter_infrastructure:TOT" | entity == "eia_meters:IL:all_meters:TOT") & variable == "meters"

generate str3 kind = cond(strpos(entity, "advanced") > 0, "ami", "all")

keep year kind value

reshape wide value, i(year) j(kind) string

drop if missing(valueami) | missing(valueall) | valueall <= 0

generate double measure = 100 * valueami / valueall

generate byte n = 1

sort year

list year measure n, noobs
