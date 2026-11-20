* Expected: 2019 51.687958, 2025 57.029667, change 5.341708 (F); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate winter_temp for wt_sw from the ERW's public tables (region_weather_hourly).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

import delimited "region_weather_hourly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:SW" & variable == "temperature_f"

keep ts_utc value

destring value, replace force

rename value temp

drop if missing(temp)

generate int year = real(substr(ts_utc, 1, 4))

generate int month = real(substr(ts_utc, 6, 2))

keep if month == 1 | month == 2 | month == 12

collapse (mean) measure = temp (count) n = temp, by(year)

sort year

list year measure n, noobs
