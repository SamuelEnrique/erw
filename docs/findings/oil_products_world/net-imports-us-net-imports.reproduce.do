* Expected: 2010 9439.916667, 2025 -2850.333333, change -12290.25 (thousand barrels a day); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate net_imports for us_net_imports from the ERW's public tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "eia_net_imports_monthly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia_net_imports:MTTNTUS2" & variable == "net_imports_crude_and_products"

destring value, replace force

drop if missing(value)

duplicates drop ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

collapse (mean) measure = value (count) n = value, by(year)

sort year

list year measure n, noobs
