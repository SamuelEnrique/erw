* Expected: 2019 89.249952, 2025 100.217724, change 10.967772 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate winter_summer for rd_se from the ERW's public tables (eia930_ba_demand_hourly).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

import delimited "eia930_ba_demand_hourly.csv", varnames(1) stringcols(_all) clear

keep if variable == "demand_mw" & x_region == "SE"

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

generate int month = real(substr(ts_utc, 6, 2))

generate double wdem = demand if month == 1 | month == 2 | month == 12

generate double sdem = demand if month >= 6 & month <= 8

collapse (max) wpeak = wdem (max) speak = sdem (count) n = demand, by(year)

generate double measure = 100 * wpeak / speak

sort year

list year measure n, noobs
