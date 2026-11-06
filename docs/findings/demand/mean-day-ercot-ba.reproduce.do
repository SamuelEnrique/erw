* Expected: 2019 1051.1418, 2025 1339.171978, change 288.030178 (GWh a day); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate mean_day for ercot_ba from the ERW's public tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "eia930_daily_demand.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:ERCO" & variable == "demand_mwh"

destring value, replace force

keep if value > 0 & !missing(value)

duplicates drop entity ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

generate int month = real(substr(ts_utc, 6, 2))

bysort year: egen double med = median(value)

keep if value >= med / 3 & value <= med * 3

collapse (mean) measure = value (count) n = value, by(year)

replace measure = measure / 1000

sort year

list year measure n, noobs
