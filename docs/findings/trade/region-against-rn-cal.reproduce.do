* Expected: 2019 0.392428, 2025 5.020776, change 4.628347 (percent of hours); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate region_against for rn_cal from the ERW's public tables (eia930_region_hourly).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

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

generate double against = 100 * (v < 0)

collapse (mean) measure = against (count) n = v, by(year)

sort year

list year measure n, noobs
