* Expected: 1990 69.681712, 2024 50.687866, change -18.993845 (TWh); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate seds_elec_ind for sd_oh from the ERW's public table eia_seds_state_energy.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_seds_state_energy.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia_seds:ESICB:OH"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double measure = value / 3.412

generate byte n = 1

sort year

list year measure n, noobs
