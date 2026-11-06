* Expected: 2019 0.998231, 2025 1.312192, change 0.313962 (USD per gallon); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate gas_premium for gasprem_SCA from the ERW's tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "eia_regional_retail_fuel_prices.csv", varnames(1) stringcols(_all) clear

keep if (entity == "eia:EMM_EPMR_PTE_SCA_DPG" | entity == "eia:EMM_EPMR_PTE_NUS_DPG") & variable == "retail_price"

destring value, replace force

drop if missing(value)

generate str10 day = substr(ts_utc, 1, 10)

generate str4 side = cond(entity == "eia:EMM_EPMR_PTE_SCA_DPG", "one", "base")

keep day side value

duplicates drop day side, force

reshape wide value, i(day) j(side) string

drop if missing(valueone) | missing(valuebase)

generate double gap = valueone - valuebase

generate int year = real(substr(day, 1, 4))

collapse (mean) measure = gap (count) n = gap, by(year)

sort year

list year measure n, noobs
