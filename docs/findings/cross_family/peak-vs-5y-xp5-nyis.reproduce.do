* Expected: 2019 -10.908878, 2025 1.229743, change 12.13862 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate peak_vs_5y for xp5_nyis from the ERW's public tables (eia930_ba_demand_hourly, ferc714_planning_area_forecasts).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "ferc714_planning_area_forecasts.csv", varnames(1) stringcols(_all) clear

keep if entity == "ferc714:100"

keep if variable == "summer_peak_forecast_mw" | variable == "winter_peak_forecast_mw"

destring value x_report_year, replace force

drop if missing(value) | missing(x_report_year)

generate int year = real(substr(ts_utc, 1, 4))

duplicates drop variable year x_report_year, force

keep if year - x_report_year == 5

collapse (max) fc = value, by(year)

tempfile fc

save `fc'

import delimited "eia930_ba_demand_hourly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:NYIS" & variable == "demand_mw"

keep ts_utc value

destring value, replace force

rename value demand

drop if missing(demand) | demand <= 0

generate int year = real(substr(ts_utc, 1, 4))

bysort year: egen double med = median(demand)

drop if demand > 3 * med

generate double t = date(substr(ts_utc, 1, 10), "YMD") * 24 + real(substr(ts_utc, 12, 2))

sort t

generate double prev = demand[_n-1] if t[_n-1] == t - 1

generate double nxt = demand[_n+1] if t[_n+1] == t + 1

generate double near = max(prev, nxt)

drop if demand > 1.1 * near & !missing(near)

collapse (max) act = demand, by(year)

merge 1:1 year using `fc', keep(match) nogenerate

keep if year >= 2019 & year <= 2025 & fc > 0 & act / fc >= 0.5 & act / fc <= 2

generate double measure = (act / fc - 1) * 100

generate byte n = 1

sort year

list year measure n, noobs
