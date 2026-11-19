* Expected: 1990 13.4307, 2024 48.7635, change 35.3328 (billion USD); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate seds_elec_spend for sd_tx from the ERW's public table eia_seds_state_energy.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_seds_state_energy.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia_seds:ESTCV:TX"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double measure = value / 1000000000.0

generate byte n = 1

sort year

list year measure n, noobs
