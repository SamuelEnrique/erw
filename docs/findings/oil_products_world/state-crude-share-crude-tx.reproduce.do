* Expected: 2001 20.041946, 2025 42.166911, change 22.124965 (percent of US crude production); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate state_crude_share for crude_TX from the ERW's public tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "eia_crude_production_state_monthly.csv", varnames(1) stringcols(_all) clear

keep if variable == "field_production_per_day"

destring value, replace force

drop if missing(value)

duplicates drop entity ts_utc, force

generate str4 code = word(subinstr(entity, ":", " ", .), 2)

keep if code == "NUS" | code == "STX"

generate int year = real(substr(ts_utc, 1, 4))

generate double tot = value if code == "NUS"

generate double one = value if code == "STX"

egen byte has = tag(ts_utc) if !missing(one)

collapse (sum) tot (sum) one (sum) n = has, by(year)

keep if tot > 0 & n > 0

generate double measure = 100 * one / tot

sort year

list year measure n, noobs
