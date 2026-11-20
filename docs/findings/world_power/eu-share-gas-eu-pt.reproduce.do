* Expected: 2017 30.817507, 2025 14.603596, change -16.21391 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate eu_share_gas for eu_pt from the ERW's public table eurostat_electricity_monthly.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eurostat_electricity_monthly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eurostat_elec:PT"

keep if variable == "net_production:G3000" | variable == "net_production:TOTAL"

keep variable ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate str12 v = subinstr(subinstr(variable, "net_production:", "np_", 1), "flow:", "fl_", 1)

collapse (sum) s = value (count) months = value, by(v year)

keep if months == 12

drop months

reshape wide s, i(year) j(v) string

drop if missing(snp_G3000) | missing(snp_TOTAL)

generate double measure = 100 * snp_G3000 / snp_TOTAL

generate byte n = 12

sort year

list year measure n, noobs
