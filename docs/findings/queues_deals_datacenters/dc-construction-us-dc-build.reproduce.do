* Expected: 2014 1.797, 2025 49.737, change 47.94 (USD billion); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate dc_construction for us_dc_build from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "census_c30_construction_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if entity == "census_c30:private:data_center" & variable == "value_put_in_place"

collapse (sum) measure = value (count) n = value, by(year)

replace measure = measure / 1000000000

sort year

list year measure n, noobs
