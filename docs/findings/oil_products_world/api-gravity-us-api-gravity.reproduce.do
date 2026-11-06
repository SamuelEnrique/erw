* Expected: 1985 32.463333, 2025 33.753333, change 1.29 (degrees API); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate api_gravity for us_api_gravity from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_crude_quality_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

duplicates drop entity variable ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

keep if entity == "eia_crude_quality:MCRAPUS2" & variable == "api_gravity"

collapse (mean) measure = value (count) n = value, by(year)

replace measure = measure * 1.0

sort year

list year measure n, noobs
