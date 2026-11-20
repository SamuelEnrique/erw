* Expected: 2007 -4.104753, 2025 13.487851, change 17.592605 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate energy_revision for pa_16 from the ERW's public table ferc714_planning_area_forecasts.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "ferc714_planning_area_forecasts.csv", varnames(1) stringcols(_all) clear

keep if entity == "ferc714:16" & variable == "net_energy_forecast_mwh"

keep ts_utc value x_report_year

destring value x_report_year, replace force

drop if missing(value) | missing(x_report_year)

generate int fy = real(substr(ts_utc, 1, 4))

rename x_report_year ry

duplicates drop fy ry, force

preserve

rename value prev

replace ry = ry + 1

tempfile p

save `p'

restore

merge 1:1 ry fy using `p', keep(match) nogenerate

keep if fy == ry + 5

keep if prev > 0 & value / prev >= 0.5 & value / prev <= 2

generate double measure = (value / prev - 1) * 100

rename ry year

generate byte n = 1

sort year

list year measure n, noobs
