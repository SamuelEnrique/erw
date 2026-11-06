* Expected: 2015 0.0038, 2025 2.1695, change 2.1657 (MWh per MW of solar); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate storage_per_solar for caiso_bat_solar from the ERW's public tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "storage_buildout_monthly.csv", varnames(1) stringcols(_all) clear

keep if entity == "iso:caiso" & variable == "battery_mwh_per_solar_mw" & substr(ts_utc, 6, 2) == "12"

destring value, replace force

generate int year = real(substr(ts_utc, 1, 4))

rename value measure

generate byte n = 1

sort year

list year measure n, noobs
