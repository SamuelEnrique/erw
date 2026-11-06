* Expected: 2008 20.0, 2024 152.755203, change 132.755203 (MW); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate request_size for us_type_battery_size from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "lbnl_interconnection_queue.csv", varnames(1) stringcols(_all) clear

destring mw_1 q_year, replace force

keep if type_clean == "Battery" & !missing(mw_1) & !missing(q_year)

keep if inrange(q_year, 2005, 2024)

collapse (median) measure = mw_1 (count) k = mw_1, by(q_year)

keep if k >= 10

rename q_year year

generate byte n = 1

sort year

list year measure n, noobs
