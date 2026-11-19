* Expected: 2008 7.673689, 2025 2.554363, change -5.119326 (million short tons); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate coal_stocks_dec for cst_mi from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_power_fuel_stocks_monthly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia_power_stocks:MI:98:COL" & substr(ts_utc, 6, 2) == "12"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double measure = value / 1000000

generate byte n = 1

sort year

list year measure n, noobs
