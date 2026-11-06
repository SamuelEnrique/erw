* Expected: 2001 604.462421, 2022 362.127499, change -242.334922 (kg CO2 per MWh); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 166): reproduce candidate power_co2_per_mwh for co2mwh_US from the ERW's public tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "eia_state_generation_monthly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia:generation:US:ALL" & variable == "net_generation"

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

collapse (sum) mwh = value (count) months = value, by(year)

keep if months == 12 & mwh > 0

save gen_years, replace

import delimited "eia_co2_state_annual.csv", varnames(1) stringcols(_all) clear

keep if variable == "co2"

destring value, replace force

drop if missing(value)

generate str4 st = word(subinstr(entity, ":", " ", .), 2)

generate str4 sec = word(subinstr(entity, ":", " ", .), 3)

generate str4 fuel = word(subinstr(entity, ":", " ", .), 4)

generate int year = real(substr(ts_utc, 1, 4))

keep if year >= 2001

keep if st == "US" & sec == "EC" & fuel == "TO"

collapse (sum) co2 = value, by(year)

merge 1:1 year using gen_years, keep(match) nogenerate

generate double measure = 1000 * co2 / mwh

generate byte n = 1

sort year

list year measure n, noobs
