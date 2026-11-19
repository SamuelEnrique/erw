* Expected: 2007 8.691008, 2025 3.56712, change -5.123888 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate nuc_out_share for nucf_2589 from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_nuclear_outages_facility_daily.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia_nuclear_outages:2589"

keep if variable == "capacity" | variable == "outage"

keep entity ts_utc variable value

destring value, replace force

reshape wide value, i(entity ts_utc) j(variable) string

drop if missing(valuecapacity) | missing(valueoutage)

keep if valuecapacity > 0

generate double share = 100 * valueoutage / valuecapacity

generate int year = real(substr(ts_utc, 1, 4))

collapse (mean) measure = share (count) n = share, by(year)

sort year

list year measure n, noobs
