* Expected: 2000 1.240833, 2025 2.6075, change 1.366667 (degrees F above the 1901 to 2000 mean); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 166): reproduce candidate conus_temperature for conus_temp from the ERW's public tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "noaa_climdiv_state_monthly.csv", varnames(1) stringcols(_all) clear

keep if entity == "noaa_climdiv:110" & variable == "temp_avg"

destring value x_mean_1901_2000, replace force

drop if missing(value) | missing(x_mean_1901_2000)

generate int year = real(substr(ts_utc, 1, 4))

keep if year >= 2000

generate double anomaly = value - x_mean_1901_2000

collapse (mean) measure = anomaly (count) n = anomaly, by(year)

sort year

list year measure n, noobs
