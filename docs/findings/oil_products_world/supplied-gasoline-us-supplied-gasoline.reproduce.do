* Expected: 2017 9324.666667, 2025 8933.416667, change -391.25 (thousand barrels a day); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate supplied_gasoline for us_supplied_gasoline from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_product_supplied_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

duplicates drop entity variable ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

keep if entity == "eia_product_supplied:MGFUPUS2" & variable == "product_supplied_per_day"

collapse (mean) measure = value (count) n = value, by(year)

replace measure = measure * 1.0

sort year

list year measure n, noobs
