* Expected: 2019 85.397055, 2025 87.9512, change 2.554144 (percent of the all-hours mean); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate sub_night_share for pjm_sub_CE from the ERW's public tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "eia930_subba_demand_hourly_2019.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930_subba:PJM:CE" & variable == "demand_mw"

keep entity ts_utc value

save subba_hours, replace

import delimited "eia930_subba_demand_hourly_2020.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930_subba:PJM:CE" & variable == "demand_mw"

keep entity ts_utc value

append using subba_hours

save subba_hours, replace

import delimited "eia930_subba_demand_hourly_2021.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930_subba:PJM:CE" & variable == "demand_mw"

keep entity ts_utc value

append using subba_hours

save subba_hours, replace

import delimited "eia930_subba_demand_hourly_2022.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930_subba:PJM:CE" & variable == "demand_mw"

keep entity ts_utc value

append using subba_hours

save subba_hours, replace

import delimited "eia930_subba_demand_hourly_2023.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930_subba:PJM:CE" & variable == "demand_mw"

keep entity ts_utc value

append using subba_hours

save subba_hours, replace

import delimited "eia930_subba_demand_hourly_2024.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930_subba:PJM:CE" & variable == "demand_mw"

keep entity ts_utc value

append using subba_hours

save subba_hours, replace

import delimited "eia930_subba_demand_hourly_2025.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930_subba:PJM:CE" & variable == "demand_mw"

keep entity ts_utc value

append using subba_hours

save subba_hours, replace

duplicates drop entity ts_utc, force

destring value, replace force

keep if value > 0 & !missing(value)

generate double t_utc = clock(subinstr(subinstr(ts_utc, "T", " ", 1), "Z", "", 1), "YMDhms")

generate int y_utc = year(dofc(t_utc))

generate int mar1 = mdy(3, 1, y_utc)

generate int dst_start = mar1 + mod(7 - dow(mar1), 7) + 7

generate int nov1 = mdy(11, 1, y_utc)

generate int dst_end = nov1 + mod(7 - dow(nov1), 7)

generate byte dst = t_utc >= cofd(dst_start) + msofhours(7) & t_utc < cofd(dst_end) + msofhours(6)

generate double t_local = t_utc - msofhours(5) + dst * msofhours(1)

generate int year = year(dofc(t_local))

generate int lhour = hh(t_local)

keep if year >= 2019 & year <= 2025

bysort year: egen double med = median(value)

keep if value <= med * 3

generate double night = value if inrange(lhour, 0, 5)

collapse (mean) avg = value (mean) nig = night (count) n = value, by(year)

generate double measure = 100 * nig / avg

sort year

list year measure n, noobs
