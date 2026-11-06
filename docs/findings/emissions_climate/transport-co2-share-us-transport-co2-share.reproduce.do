* Expected: 2001 32.285041, 2022 37.288437, change 5.003397 (percent of US energy CO2); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 166): reproduce candidate transport_co2_share for us_transport_co2_share from the ERW's public tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "eia_co2_state_annual.csv", varnames(1) stringcols(_all) clear

keep if variable == "co2"

destring value, replace force

drop if missing(value)

generate str4 st = word(subinstr(entity, ":", " ", .), 2)

generate str4 sec = word(subinstr(entity, ":", " ", .), 3)

generate str4 fuel = word(subinstr(entity, ":", " ", .), 4)

generate int year = real(substr(ts_utc, 1, 4))

keep if year >= 2001

keep if st == "US"

generate double part = value if sec == "TC" & fuel == "TO"

generate double all = value if sec == "TT" & fuel == "TO"

collapse (sum) part (sum) all, by(year)

keep if all > 0

generate double measure = 100 * part / all

generate byte n = 1

sort year

list year measure n, noobs
