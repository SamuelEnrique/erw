* Expected: 2019 83192.446105, 2020 76468.831522, change -6723.614583 (MW); tolerance 0.5 percent of the change.

* The claim: 2020 against the mean of the other years, 83417.466033 MW.

* ERW findings hunt (chain 502): reproduce candidate covid_2020 for MIDA from the ERW's public tables (eia930_ba_demand_hourly).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

import delimited "eia930_ba_demand_hourly.csv", varnames(1) stringcols(_all) clear

keep if variable == "demand_mw" & x_region == "MIDA"

keep entity ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate str7 ym = substr(ts_utc, 1, 7)

bysort ym entity: generate byte firstba = _n == 1

bysort ym: egen nset = total(firstba)

drop if value <= 0

bysort entity year: egen double med = median(value)

drop if value > 3 * med

collapse (sum) demand = value (count) nba = value (first) nset year, by(ts_utc)

keep if nba == nset

drop nba nset

generate str5 md = substr(ts_utc, 6, 5)

keep if md >= "03-01" & md <= "05-31"

generate double need = 24 * (date(string(year) + "-05-31", "YMD") - date(string(year) + "-03-01", "YMD") + 1)

collapse (mean) measure = demand (count) n = demand (first) need = need, by(year)

keep if n >= 0.9 * need

drop need

sort year

list year measure n, noobs
