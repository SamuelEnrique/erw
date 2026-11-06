* Expected: 2019 0.175299, 2025 7.033629, change 6.85833 (percent of peak-day demand); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate battery_per_peak for us_bat_peak from the ERW's public tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "storage_buildout_monthly.csv", varnames(1) stringcols(_all) clear

keep if entity == "us:total" & variable == "battery_operating_mw" & substr(ts_utc, 6, 2) == "12"

destring value, replace force

generate int year = real(substr(ts_utc, 1, 4))

keep year value

rename value fleet

save fleet_years, replace

import delimited "eia930_daily_demand.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:US48" & variable == "demand_mwh"

destring value, replace force

keep if value > 0 & !missing(value)

duplicates drop entity ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

bysort year: egen double med = median(value)

keep if value >= med / 3 & value <= med * 3

generate double neg_value = -value

bysort year (neg_value): generate long rank = _n

by year: generate long n = _N

by year: egen double top = mean(cond(rank <= 10, value, .))

by year: keep if _n == 1

merge 1:1 year using fleet_years, keep(match) nogenerate

generate double measure = 100 * fleet / (top / 24)

sort year

list year measure n, noobs
