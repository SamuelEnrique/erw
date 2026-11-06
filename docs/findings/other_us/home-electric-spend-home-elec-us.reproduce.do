* Expected: 1990 65.258972, 2024 73.324614, change 8.065641 (percent of home energy spending); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 166): reproduce candidate home_electric_spend for home_elec_US from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_seds_residential_annual.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if (entity == "eia_seds_res:ESRCV:US" | entity == "eia_seds_res:TERCV:US") & variable == "expenditures"

generate str3 side = cond(strpos(entity, ":ESRCV:") > 0, "ele", "all")

keep year side value

reshape wide value, i(year) j(side) string

drop if missing(valueele) | missing(valueall) | valueall <= 0

generate double measure = 100 * valueele / valueall

generate byte n = 1

sort year

list year measure n, noobs
