* Expected: 2014 0.274398, 2025 2.102598, change 1.8282 (percent of net generation); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate small_solar_ratio for state_dpv_US from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_state_generation_monthly.csv", varnames(1) stringcols(_all) clear

keep if (entity == "eia:generation:US:ALL" | entity == "eia:generation:US:DPV") & variable == "net_generation"

destring value, replace force

drop if missing(value)

generate str4 src = cond(entity == "eia:generation:US:ALL", "ALL", "SRC")

keep ts_utc src value

reshape wide value, i(ts_utc) j(src) string

drop if missing(valueALL) | valueALL <= 0

drop if missing(valueSRC)

generate int year = real(substr(ts_utc, 1, 4))

collapse (sum) src = valueSRC (sum) all = valueALL (count) n = valueALL, by(year)

generate double measure = 100 * src / all

sort year

list year measure n, noobs
