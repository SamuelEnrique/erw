* Expected: 2005 0.0, 2024 29.698266, change 29.698266 (percent of requested MW); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate storage_share for us_req_battery_share from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "lbnl_interconnection_queue.csv", varnames(1) stringcols(_all) clear

destring mw_1 q_year, replace force

generate long qd = daily(substr(q_date, 1, 10), "YMD")

generate long od = daily(substr(on_date, 1, 10), "YMD")

generate long wd = daily(substr(wd_date, 1, 10), "YMD")

keep if !missing(mw_1) & !missing(q_year)

keep if inrange(q_year, 2005, 2024)

generate double bat = mw_1 if type_clean == "Battery"

collapse (sum) tot = mw_1 (sum) bat, by(q_year)

keep if tot > 0

generate double measure = 100 * bat / tot

rename q_year year

generate byte n = 1

sort year

list year measure n, noobs
