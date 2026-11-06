* Expected: 2010 0.0, 2025 16372.5, change 16372.5 (MW); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate added_mw for add_battery_US from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia860m_operating_generators.csv", varnames(1) stringcols(_all) clear

keep if technology == "Batteries"

destring nameplate_mw operating_year, replace force

drop if missing(nameplate_mw) | missing(operating_year)

keep if inrange(operating_year, 2010, 2025)

collapse (sum) measure = nameplate_mw, by(operating_year)

rename operating_year year

generate byte n = 1

* A year with no unit is a year of zero MW, as the Python prints it.

sort year

list year measure n, noobs
