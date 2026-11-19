* Expected: 2006 2.897089, 2025 7.335731, change 4.438642 (percent a year); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate energy_growth for pa_16 from the ERW's public table ferc714_planning_area_forecasts.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "ferc714_planning_area_forecasts.csv", varnames(1) stringcols(_all) clear

keep if entity == "ferc714:16" & variable == "net_energy_forecast_mwh"

keep ts_utc value x_report_year

destring value x_report_year, replace force

drop if missing(value) | missing(x_report_year)

generate int fy = real(substr(ts_utc, 1, 4))

rename x_report_year year

duplicates drop fy year, force

generate double first = value if fy == year + 1

generate double tenth = value if fy == year + 10

collapse (max) first = first (max) tenth = tenth, by(year)

drop if missing(first) | missing(tenth) | first <= 0

keep if tenth / first >= 0.5 & tenth / first <= 3

generate double measure = ((tenth / first) ^ (1 / 9) - 1) * 100

generate byte n = 1

sort year

list year measure n, noobs
