* Expected: 2005 0.0, 2024 157428.861588, change 157428.861588 (MW); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate requested_by_type for us_req_battery from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "lbnl_interconnection_queue.csv", varnames(1) stringcols(_all) clear

destring mw_1 q_year, replace force

generate long qd = daily(substr(q_date, 1, 10), "YMD")

generate long od = daily(substr(on_date, 1, 10), "YMD")

generate long wd = daily(substr(wd_date, 1, 10), "YMD")

keep if type_clean == "Battery" & !missing(mw_1) & !missing(q_year)

keep if inrange(q_year, 2005, 2024)

collapse (sum) measure = mw_1, by(q_year)

rename q_year year

generate byte n = 1

* A year with no request is a year of zero MW, as the Python prints it.

sort year

list year measure n, noobs
