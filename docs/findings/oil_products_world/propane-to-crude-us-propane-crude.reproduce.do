* Expected: 1993 71.018373, 2025 48.023539, change -22.994834 (percent of WTI); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate propane_to_crude for us_propane_crude from the ERW's tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "eia_fuel_spot_prices.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia:wti_cushing" & variable == "spot_price"

destring value, replace force

keep if value > 0 & !missing(value)

generate str10 day = substr(ts_utc, 1, 10)

keep day value

rename value wti

duplicates drop day, force

save wti_days, replace

import delimited "eia_product_spot_prices.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia:EER_EPLLPA_PF4_Y44MB_DPG" & variable == "spot_price"

destring value, replace force

drop if missing(value)

generate str10 day = substr(ts_utc, 1, 10)

keep day value

duplicates drop day, force

merge 1:1 day using wti_days, keep(match) nogenerate

generate double ratio = 100 * value * 42 / wti

generate int year = real(substr(day, 1, 4))

collapse (mean) measure = ratio (count) n = ratio, by(year)

sort year

list year measure n, noobs
