* Expected: 2001 9.387254, 2024 7.47912, change -1.908134 (MMBtu per MWh); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate gas_heat_rate for hr_gas_FL from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia923_plant_fuel_annual.csv", varnames(1) stringcols(_all) clear

generate str8 f2002 = word(subinstr(entity, ":", " ", .), 3)

keep if f2002 == "NG"

keep if geo == "US-FL"

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double gen = value if variable == "net_generation"

generate double fuel = value if variable == "fuel_consumed"

collapse (sum) gen (sum) fuel, by(year)

keep if gen > 0 & fuel > 0

generate double measure = fuel * 1000000 / gen

generate byte n = 1

sort year

list year measure n, noobs
