* Expected: 2001 26.28184, 2025 32.526127, change 6.244287 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate nuclear_share for st_se_nuc from the ERW's public tables (eia_state_generation_monthly).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

import delimited "eia_state_generation_monthly.csv", varnames(1) stringcols(_all) clear

keep if variable == "net_generation"

keep if entity == "eia:generation:GA:ALL" | entity == "eia:generation:GA:NUC" | entity == "eia:generation:AL:ALL" | entity == "eia:generation:AL:NUC"

keep entity ts_utc value

destring value, replace force

drop if missing(value)

generate str2 state = substr(entity, 16, 2)

generate str4 fuel = substr(entity, 19, .)

generate int year = real(substr(ts_utc, 1, 4))

generate double allgen = value if fuel == "ALL"

generate double fuelgen = value if fuel == "NUC"

generate byte allrow = fuel == "ALL"

bysort year state allrow: generate long nmonths = _N if allrow

bysort year: egen long minmonths = min(nmonths)

bysort year state: generate byte firststate = _n == 1

bysort year: egen long nstates = total(firststate)

keep if minmonths >= 12 & nstates == 2

collapse (sum) allgen = allgen (sum) fuelgen = fuelgen, by(year)

generate double measure = 100 * fuelgen / allgen

generate byte n = 12

sort year

list year measure n, noobs
