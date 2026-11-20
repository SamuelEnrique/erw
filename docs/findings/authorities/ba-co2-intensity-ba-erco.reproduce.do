* Expected: 2019 408.474734, 2025 315.408474, change -93.06626 (kg CO2 per MWh); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate ba_co2_intensity for ba_erco from the ERW's public tables (eia930_all_emissions, eia930_ba_supply_hourly).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

import delimited "eia930_ba_supply_hourly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:ERCO" & variable == "net_generation_mw"

keep ts_utc value

destring value, replace force

rename value gen

drop if missing(gen)

generate int year = real(substr(ts_utc, 1, 4))

drop if gen <= 0

bysort year: egen double med = median(gen)

drop if gen > 3 * med

drop med

drop year

tempfile g

save `g'

import delimited "eia930_all_emissions.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:ERCO" & variable == "co2_emissions_generated"

keep ts_utc value

destring value, replace force

rename value co2

drop if missing(co2)

generate int year = real(substr(ts_utc, 1, 4))

drop if co2 < 0

merge 1:1 ts_utc using `g', keep(match) nogenerate

collapse (sum) co2 = co2 (sum) gen = gen (count) n = co2, by(year)

generate double measure = 1000 * co2 / gen

sort year

list year measure n, noobs
