* Expected: 2019 51.428197, 2025 45.100105, change -6.328092 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate ba_coal_co2_share for ba_erco from the ERW's public tables (eia930_all_emissions).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

import delimited "eia930_all_emissions.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:ERCO" & variable == "co2_emissions_coal"

keep ts_utc value

destring value, replace force

rename value coal

drop if missing(coal)

generate int year = real(substr(ts_utc, 1, 4))

drop if coal < 0

drop year

tempfile k

save `k'

import delimited "eia930_all_emissions.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:ERCO" & variable == "co2_emissions_generated"

keep ts_utc value

destring value, replace force

rename value co2

drop if missing(co2)

generate int year = real(substr(ts_utc, 1, 4))

drop if co2 < 0

merge 1:1 ts_utc using `k', keep(match) nogenerate

collapse (sum) co2 = co2 (sum) coal = coal (count) n = co2, by(year)

keep if co2 > 0

generate double measure = 100 * coal / co2

sort year

list year measure n, noobs
