* Expected: 1991 0.462322, 2025 1.080384, change 0.618062 (USD per gallon); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate pump_over_spot for us_pump_spot from the ERW's public tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "eia_product_spot_prices.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia:EER_EPMRU_PF4_RGC_DPG" & variable == "spot_price"

destring value, replace force

drop if missing(value)

generate str10 day = substr(ts_utc, 1, 10)

keep day value

rename value base

duplicates drop day, force

save base_prices, replace

import delimited "eia_retail_fuel_prices.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia:EMM_EPMR_PTE_NUS_DPG" & variable == "retail_price"

destring value, replace force

drop if missing(value)

generate str10 day = substr(ts_utc, 1, 10)

keep day value

duplicates drop day, force

generate int year = real(substr(day, 1, 4))

collapse (mean) retail = value (count) n = value, by(year)

save retail_years, replace

use base_prices, clear

generate int year = real(substr(day, 1, 4))

collapse (mean) base, by(year)

merge 1:1 year using retail_years, keep(match) nogenerate

generate double measure = retail - base

sort year

list year measure n, noobs
