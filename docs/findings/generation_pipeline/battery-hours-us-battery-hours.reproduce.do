* Expected: 2015 0.534192, 2025 2.855958, change 2.321766 (MWh per MW); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate battery_hours for us_battery_hours from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia860m_operating_generators.csv", varnames(1) stringcols(_all) clear

keep if technology == "Batteries"

destring nameplate_mw energy_capacity_mwh operating_year, replace force

drop if missing(nameplate_mw) | missing(energy_capacity_mwh) | missing(operating_year)

keep if inrange(operating_year, 2010, 2025)

collapse (sum) mwh = energy_capacity_mwh (sum) mw = nameplate_mw, by(operating_year)

keep if mw >= 100

generate double measure = mwh / mw

rename operating_year year

generate byte n = 1

sort year

list year measure n, noobs
