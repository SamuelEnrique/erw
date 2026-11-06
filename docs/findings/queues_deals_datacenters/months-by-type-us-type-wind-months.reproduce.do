* Expected: 2005 21.092402, 2024 81.117043, change 60.024641 (months); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate months_by_type for us_type_wind_months (us_lbnl_months from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "lbnl_interconnection_queue.csv", varnames(1) stringcols(_all) clear

destring mw_1 q_year, replace force

generate long qd = daily(substr(q_date, 1, 10), "YMD")

generate long od = daily(substr(on_date, 1, 10), "YMD")

generate long wd = daily(substr(wd_date, 1, 10), "YMD")

keep if type_clean == "Wind"

keep if !missing(qd) & !missing(od) & od >= qd

generate double months = (od - qd) / 30.4375

generate int year = year(od)

keep if inrange(year, 2005, 2024)

collapse (median) measure = months (count) k = months, by(year)

keep if k >= 10

generate byte n = 1

sort year

list year measure n, noobs
