* Expected: 2016 -9.97587, 2025 17.664467, change 27.640336 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate eu_net_imports for eu_pt from the ERW's public table eurostat_electricity_monthly.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eurostat_electricity_monthly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eurostat_elec:PT"

keep if variable == "flow:IMP" | variable == "flow:EXP" | variable == "flow:AIM"

keep variable ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate str12 v = subinstr(subinstr(variable, "net_production:", "np_", 1), "flow:", "fl_", 1)

collapse (sum) s = value (count) months = value, by(v year)

keep if months == 12

drop months

reshape wide s, i(year) j(v) string

drop if missing(sfl_IMP) | missing(sfl_EXP) | missing(sfl_AIM)

generate double measure = 100 * (sfl_IMP - sfl_EXP) / sfl_AIM

generate byte n = 12

sort year

list year measure n, noobs
