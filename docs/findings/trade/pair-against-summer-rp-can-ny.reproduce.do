* Expected: 2019 0.0, 2025 49.818841, change 49.818841 (percent of hours); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate pair_against_summer for rp_can_ny from the ERW's public tables (eia930_region_pair_hourly).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

import delimited "eia930_region_pair_hourly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:CAN-NY"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate double v = value * 1

generate int year = real(substr(ts_utc, 1, 4))

generate double absflow = abs(v)

bysort year: egen double p99 = pctile(absflow), p(99)

drop if absflow > 3 * p99

drop absflow p99

generate int month = real(substr(ts_utc, 6, 2))

keep if month == 6 | month == 7 | month == 8

generate double against = 100 * (v < 0)

collapse (mean) measure = against (count) n = v, by(year)

sort year

list year measure n, noobs
