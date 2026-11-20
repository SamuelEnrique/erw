* Expected: 2021 38.403212, 2024 28.100643, change -10.302569 (MW); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate pair_side_gap for rg_cent_midw from the ERW's public tables (eia930_region_pair_hourly).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

import delimited "eia930_region_pair_hourly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:CENT-MIDW"

keep ts_utc x_first_report x_second_report

destring x_first_report x_second_report, replace force

generate int year = real(substr(ts_utc, 1, 4))

generate double absfirst = abs(x_first_report)

bysort year: egen double p99first = pctile(absfirst), p(99)

replace x_first_report = . if absfirst > 3 * p99first

generate double abssecond = abs(x_second_report)

bysort year: egen double p99second = pctile(abssecond), p(99)

replace x_second_report = . if abssecond > 3 * p99second

drop if missing(x_first_report) | missing(x_second_report)

generate double gap = abs(x_first_report - x_second_report)

collapse (mean) measure = gap (count) n = gap, by(year)

sort year

list year measure n, noobs
