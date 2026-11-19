* Expected: 2007 26209.114, 2025 22764.39, change -3444.724 (MW); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate nuc_out_peak for nuc_us from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_nuclear_outages_facility_daily.csv", varnames(1) stringcols(_all) clear

keep if variable == "capacity" | variable == "outage"

keep entity ts_utc variable value

destring value, replace force

reshape wide value, i(entity ts_utc) j(variable) string

drop if missing(valuecapacity) | missing(valueoutage)

collapse (sum) outage = valueoutage, by(ts_utc)

generate int year = real(substr(ts_utc, 1, 4))

collapse (max) measure = outage (count) n = outage, by(year)

sort year

list year measure n, noobs
