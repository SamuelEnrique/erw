* Expected: 2005 80.618231, 2025 141.006826, change 60.388595 (m); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate turbine_rotor for us_turbine_rotor from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "uswtdb_wind_turbines.csv", varnames(1) stringcols(_all) clear

keep if offshore == "0" | offshore == "0.0" | offshore == "False" | offshore == "false"

destring project_year rotor_diameter_m, replace force

drop if missing(project_year) | missing(rotor_diameter_m)

keep if inrange(project_year, 2005, 2025)

collapse (mean) measure = rotor_diameter_m, by(project_year)

rename project_year year

generate byte n = 1

sort year

list year measure n, noobs
