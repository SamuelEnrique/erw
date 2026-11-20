* Expected: 2019 -9.487626, 2025 6.072736, change 15.560362 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate energy_vs_5y for xe5_pjm from the ERW's public tables (eia930_ba_demand_hourly, ferc714_planning_area_forecasts).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "ferc714_planning_area_forecasts.csv", varnames(1) stringcols(_all) clear

keep if entity == "ferc714:119"

keep if variable == "net_energy_forecast_mwh"

destring value x_report_year, replace force

drop if missing(value) | missing(x_report_year)

generate int year = real(substr(ts_utc, 1, 4))

duplicates drop variable year x_report_year, force

keep if year - x_report_year == 5

collapse (first) fc = value, by(year)

tempfile fc

save `fc'

import delimited "eia930_ba_demand_hourly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:PJM" & variable == "demand_mw"

keep ts_utc value

destring value, replace force

rename value demand

drop if missing(demand) | demand <= 0

generate int year = real(substr(ts_utc, 1, 4))

bysort year: egen double med = median(demand)

drop if demand > 3 * med

collapse (sum) act = demand (count) hrs = demand, by(year)

keep if hrs >= 0.98 * cond(mod(year, 4) == 0, 8784, 8760)

drop hrs

merge 1:1 year using `fc', keep(match) nogenerate

keep if year >= 2019 & year <= 2025 & fc > 0 & act / fc >= 0.5 & act / fc <= 2

generate double measure = (act / fc - 1) * 100

generate byte n = 1

sort year

list year measure n, noobs
