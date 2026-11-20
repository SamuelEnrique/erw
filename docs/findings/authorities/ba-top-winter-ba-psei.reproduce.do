* Expected: 2019 90.0, 2025 100.0, change 10.0 (percent of the top hours); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate ba_top_winter for ba_psei from the ERW's public tables (eia930_ba_demand_hourly).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

import delimited "eia930_ba_demand_hourly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:PSEI" & variable == "demand_mw"

keep ts_utc value

destring value, replace force

rename value demand

drop if missing(demand)

generate int year = real(substr(ts_utc, 1, 4))

drop if demand <= 0

bysort year: egen double med = median(demand)

drop if demand > 3 * med

drop med

generate double t = date(substr(ts_utc, 1, 10), "YMD") * 24 + real(substr(ts_utc, 12, 2))

sort t

generate double prev = demand[_n-1] if t[_n-1] == t - 1

generate double nxt = demand[_n+1] if t[_n+1] == t + 1

generate double near = max(prev, nxt)

drop if demand > 1.1 * near & !missing(near)

generate int month = real(substr(ts_utc, 6, 2))

bysort year: generate long n = _N

generate double negd = -demand

bysort year (negd t): generate long rank = _n

keep if rank <= 100

generate double winter = 100 * (month == 1 | month == 2 | month == 12)

collapse (mean) measure = winter (first) n = n, by(year)

sort year

list year measure n, noobs
