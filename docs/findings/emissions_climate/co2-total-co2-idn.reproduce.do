* Expected: 1980 72.18311, 2024 886.784535, change 814.601425 (million t CO2); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate co2_total for co2_idn from the ERW's public table eia_world_energy_co2_annual.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_world_energy_co2_annual.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia_intl:IDN:4008" & variable == "emissions"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if year >= 1980

generate double measure = value / 1000000

generate byte n = 1

sort year

list year measure n, noobs
