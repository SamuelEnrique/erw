* Expected: 1987 2.036968, 2025 19.32996, change 17.292991 (USD per barrel); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate gasoline_crack for crack_gasoline from the ERW's public tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "eia_fuel_spot_prices.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia:wti_cushing" & variable == "spot_price"

destring value, replace force

drop if missing(value)

generate str10 day = substr(ts_utc, 1, 10)

keep day value

rename value base

duplicates drop day, force

save base_prices, replace

import delimited "eia_product_spot_prices.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia:EER_EPMRU_PF4_RGC_DPG" & variable == "spot_price"

destring value, replace force

drop if missing(value)

generate str10 day = substr(ts_utc, 1, 10)

keep day value

duplicates drop day, force

merge 1:1 day using base_prices, keep(match) nogenerate

generate double crack = value * 42 - base

generate int year = real(substr(day, 1, 4))

collapse (mean) measure = crack (count) n = crack, by(year)

sort year

list year measure n, noobs
