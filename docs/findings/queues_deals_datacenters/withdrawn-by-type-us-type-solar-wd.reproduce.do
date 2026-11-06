* Expected: 2008 99.983274, 2024 76.03162, change -23.951654 (percent of MW leaving the queue); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate withdrawn_by_type for us_type_solar_wd (us_lbnl_wd from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "lbnl_interconnection_queue.csv", varnames(1) stringcols(_all) clear

destring mw_1 q_year, replace force

generate long qd = daily(substr(q_date, 1, 10), "YMD")

generate long od = daily(substr(on_date, 1, 10), "YMD")

generate long wd = daily(substr(wd_date, 1, 10), "YMD")

keep if type_clean == "Solar"

keep if !missing(mw_1)

generate int yon = year(od)

generate int ywd = year(wd)

preserve

keep if !missing(yon)

collapse (sum) online = mw_1, by(yon)

rename yon year

save lbnl_online, replace

restore

keep if !missing(ywd)

collapse (sum) withdrawn = mw_1, by(ywd)

rename ywd year

merge 1:1 year using lbnl_online, nogenerate

replace online = 0 if missing(online)

replace withdrawn = 0 if missing(withdrawn)

keep if inrange(year, 2005, 2024) & online > 0 & withdrawn > 0

generate double measure = 100 * withdrawn / (online + withdrawn)

generate byte n = 1

sort year

list year measure n, noobs
