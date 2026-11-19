* Expected: 2019 90.08, 2025 93.35, change 3.27 (F); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate max_temp for wt_midw from the ERW's public tables (region_weather_hourly).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

import delimited "region_weather_hourly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:MIDW" & variable == "temperature_f"

keep ts_utc value

destring value, replace force

rename value temp

drop if missing(temp)

generate int year = real(substr(ts_utc, 1, 4))

collapse (max) measure = temp (count) n = temp, by(year)

sort year

list year measure n, noobs
