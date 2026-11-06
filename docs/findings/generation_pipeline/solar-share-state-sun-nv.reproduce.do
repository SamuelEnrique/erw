* Expected: 2001 0.0, 2025 30.786025, change 30.786025 (percent of net generation); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate solar_share for state_sun_NV from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_state_generation_monthly.csv", varnames(1) stringcols(_all) clear

keep if (entity == "eia:generation:NV:ALL" | entity == "eia:generation:NV:SUN") & variable == "net_generation"

destring value, replace force

drop if missing(value)

generate str4 src = cond(entity == "eia:generation:NV:ALL", "ALL", "SRC")

keep ts_utc src value

reshape wide value, i(ts_utc) j(src) string

drop if missing(valueALL) | valueALL <= 0

capture confirm variable valueSRC

if _rc generate double valueSRC = 0

replace valueSRC = 0 if missing(valueSRC)

generate int year = real(substr(ts_utc, 1, 4))

collapse (sum) src = valueSRC (sum) all = valueALL (count) n = valueALL, by(year)

generate double measure = 100 * src / all

sort year

list year measure n, noobs
