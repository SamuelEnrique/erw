* Expected: 2020 -17.941117, 2025 -14.514296, change 3.426821 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate util_vs_3y for xu3_195 from the ERW's public tables (eia861m_utility_sales_monthly, ferc714_planning_area_forecasts).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "ferc714_planning_area_forecasts.csv", varnames(1) stringcols(_all) clear

keep if entity == "ferc714:2" & variable == "net_energy_forecast_mwh"

destring value x_report_year, replace force

drop if missing(value) | missing(x_report_year)

generate int year = real(substr(ts_utc, 1, 4))

duplicates drop year x_report_year, force

keep if year - x_report_year == 3

collapse (first) fc = value, by(year)

tempfile fc

save `fc'

import delimited "eia861m_utility_sales_monthly.csv", varnames(1) stringcols(_all) clear

keep if variable == "total_sales" & x_utility_number == "195"

keep ts_utc x_state value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

collapse (sum) sales = value (count) months = value, by(x_state year)

bysort year: generate byte nstates = _N

bysort year: egen byte minmonths = min(months)

keep if nstates == 1 & minmonths == 12

collapse (sum) act = sales, by(year)

merge 1:1 year using `fc', keep(match) nogenerate

keep if year >= 2019 & year <= 2025 & fc > 0 & act / fc >= 0.5 & act / fc <= 2

generate double measure = (act / fc - 1) * 100

generate byte n = 1

sort year

list year measure n, noobs
