* Expected: 2020 89.442116, 2025 91.081251, change 1.639136 (percent of full power); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate reactor_power for rp_us from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "nrc_reactor_status.csv", varnames(1) stringcols(_all) clear

keep if variable == "power_pct"

keep entity ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

bysort year entity: generate byte firstr = _n == 1

collapse (mean) measure = value (count) days = value (sum) reactors = firstr, by(year)

generate double n = days / reactors

sort year

list year measure n, noobs
