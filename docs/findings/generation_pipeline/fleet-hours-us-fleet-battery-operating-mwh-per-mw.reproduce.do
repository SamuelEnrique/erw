* Expected: 2015 0.6127, 2025 2.7708, change 2.1581 (MWh per MW); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate fleet_hours for us_fleet_battery_operating_mwh_per_mw from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "storage_buildout_monthly.csv", varnames(1) stringcols(_all) clear

keep if entity == "us:total" & variable == "battery_operating_mwh_per_mw" & substr(ts_utc, 6, 2) == "12"

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

rename value measure

generate byte n = 1

sort year

list year measure n, noobs
