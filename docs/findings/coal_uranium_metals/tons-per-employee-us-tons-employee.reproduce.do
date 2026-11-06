* Expected: 2001 14628.590779, 2024 11632.780844, change -2995.809935 (short tons per employee); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 166): reproduce candidate tons_per_employee for us_tons_employee from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_coal_production_annual.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

duplicates drop entity variable ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

keep if (entity == "eia_coal_production:US:TOT:ALL" & variable == "production") | (entity == "eia_coal_production:US:TOT:ALL" & variable == "employees")

generate str3 side = cond(entity == "eia_coal_production:US:TOT:ALL" & variable == "production", "num", "den")

keep year ts_utc side value

reshape wide value, i(ts_utc) j(side) string

drop if missing(valuenum) | missing(valueden)

collapse (sum) num = valuenum (sum) den = valueden, by(year)

keep if den != 0

generate double measure = num * 1.0 / den

generate byte n = 1

sort year

list year measure n, noobs
