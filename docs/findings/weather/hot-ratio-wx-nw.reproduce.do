* Expected: 2021 142.108675, 2024 146.010714, change 3.902039 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate hot_ratio for wx_nw from the ERW's public tables (region_weather_hourly, eia930_ba_demand_hourly).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

import delimited "eia930_ba_demand_hourly.csv", varnames(1) stringcols(_all) clear

keep if variable == "demand_mw" & x_region == "NW"

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

tempfile dem

save `dem'

import delimited "region_weather_hourly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:NW" & variable == "temperature_f"

keep ts_utc value

destring value, replace force

rename value temp

drop if missing(temp)

merge 1:1 ts_utc using `dem', keep(match) nogenerate

bysort year: egen double ymean = mean(demand)

bysort year: generate long n = _N

generate double negt = -temp

bysort year (negt ts_utc): generate long rank = _n

keep if rank <= 50

collapse (mean) ext = demand (first) ymean = ymean (first) n = n, by(year)

generate double measure = 100 * ext / ymean

sort year

list year measure n, noobs
