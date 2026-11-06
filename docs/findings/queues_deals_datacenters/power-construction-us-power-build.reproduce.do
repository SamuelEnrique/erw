* Expected: 1993 16.386, 2025 128.041, change 111.655 (USD billion); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate power_construction for us_power_build from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "census_c30_construction_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if entity == "census_c30:private:electric" & variable == "value_put_in_place"

collapse (sum) measure = value (count) n = value, by(year)

replace measure = measure / 1000000000

sort year

list year measure n, noobs
