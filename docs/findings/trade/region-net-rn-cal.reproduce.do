* Expected: 2019 22.561817, 2025 15.614078, change -6.947739 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate region_net for rn_cal from the ERW's public tables (eia930_region_hourly, eia930_ba_demand_hourly).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

import delimited "eia930_ba_demand_hourly.csv", varnames(1) stringcols(_all) clear

keep if variable == "demand_mw" & x_region == "CAL"

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

drop year

tempfile dem

save `dem'

import delimited "eia930_region_hourly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:CAL" & variable == "total_interchange_mw"

keep ts_utc value

destring value, replace force

rename value ti

drop if missing(ti)

generate int year = real(substr(ts_utc, 1, 4))

generate double absflow = abs(ti)

bysort year: egen double p99 = pctile(absflow), p(99)

drop if absflow > 3 * p99

drop absflow p99

generate double v = ti * -1

merge 1:1 ts_utc using `dem', keep(match) nogenerate

collapse (sum) v = v (sum) demand = demand (count) n = v, by(year)

generate double measure = 100 * v / demand

sort year

list year measure n, noobs
