* Expected: 1985 0.911667, 2025 1.299167, change 0.3875 (percent sulfur by weight); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate sulfur_content for us_sulfur from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_crude_quality_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

duplicates drop entity variable ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

keep if entity == "eia_crude_quality:MCRS1US2" & variable == "sulfur_content"

collapse (mean) measure = value (count) n = value, by(year)

replace measure = measure * 1.0

sort year

list year measure n, noobs
