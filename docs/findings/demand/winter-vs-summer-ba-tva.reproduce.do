* Expected: 2019 101.176554, 2025 113.876102, change 12.699548 (percent of the summer top days); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate winter_vs_summer for ba_tva from the ERW's public tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "eia930_daily_demand.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:TVA" & variable == "demand_mwh"

destring value, replace force

keep if value > 0 & !missing(value)

duplicates drop entity ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

generate int month = real(substr(ts_utc, 6, 2))

bysort year: egen double med = median(value)

keep if value >= med / 3 & value <= med * 3

generate byte season = cond(inlist(month, 1, 2, 12), 1, cond(inlist(month, 6, 7, 8), 2, 0))

bysort year: generate long n = _N

generate double neg_value = -value

bysort year season (neg_value): generate long rank = _n

keep if season > 0 & rank <= 5

collapse (mean) top = value (count) k = value (firstnm) n, by(year season)

keep if k == 5

reshape wide top k, i(year) j(season)

drop if missing(top1) | missing(top2)

generate double measure = 100 * top1 / top2

sort year

list year measure n, noobs
