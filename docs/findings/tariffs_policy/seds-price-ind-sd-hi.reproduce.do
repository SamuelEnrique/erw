* Expected: 1990 75.71228, 2024 341.30236, change 265.59008 (USD per MWh); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate seds_price_ind for sd_hi from the ERW's public table eia_seds_state_energy.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_seds_state_energy.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia_seds:ESICD:HI"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double measure = value / 0.29308323563892147

generate byte n = 1

sort year

list year measure n, noobs
