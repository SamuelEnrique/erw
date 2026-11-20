* Expected: 2020 1418.946197, 2025 3711.944391, change 2292.998194 (MW); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate fr_mean_solar for fr from the ERW's public table rte_eco2mix_france_halfhourly.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "rte_eco2mix_france_halfhourly.csv", varnames(1) stringcols(_all) clear

keep if variable == "solar"

keep ts_utc value

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

collapse (mean) measure = value (count) n = value, by(year)

sort year

list year measure n, noobs
