* Expected: 2019 1082.892237, 2025 1789.384817, change 706.49258 (MW); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate pair_flow for rp_midw_ten from the ERW's public tables (eia930_region_pair_hourly).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

import delimited "eia930_region_pair_hourly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:MIDW-TEN"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate double v = value * 1

generate int year = real(substr(ts_utc, 1, 4))

generate double absflow = abs(v)

bysort year: egen double p99 = pctile(absflow), p(99)

drop if absflow > 3 * p99

drop absflow p99

collapse (mean) measure = v (count) n = v, by(year)

sort year

list year measure n, noobs
