* Expected: 2013 2125.309, 2024 18822.433, change 16697.124 (MW); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate net_metered for nem_CA from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_net_metering_state_annual.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if entity == "eia_net_metering:CA:all_technologies:TOT" & variable == "capacity"

collapse (sum) measure = value, by(year)

generate byte n = 1

sort year

list year measure n, noobs
