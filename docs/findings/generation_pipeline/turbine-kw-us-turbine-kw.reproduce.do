* Expected: 2005 1512.371506, 2025 3804.358172, change 2291.986666 (kW); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate turbine_kw for us_turbine_kw from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "uswtdb_wind_turbines.csv", varnames(1) stringcols(_all) clear

keep if offshore == "0" | offshore == "0.0" | offshore == "False" | offshore == "false"

destring project_year turbine_capacity_kw, replace force

drop if missing(project_year) | missing(turbine_capacity_kw)

keep if inrange(project_year, 2005, 2025)

collapse (mean) measure = turbine_capacity_kw, by(project_year)

rename project_year year

generate byte n = 1

sort year

list year measure n, noobs
