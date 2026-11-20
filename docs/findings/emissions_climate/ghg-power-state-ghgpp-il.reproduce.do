* Expected: 2015 79.703008, 2023 38.428308, change -41.2747 (million t CO2e); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate ghg_power_state for ghgpp_il from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "epa_ghgrp_facility_emissions.csv", varnames(1) stringcols(_all) clear

keep if variable == "emissions_direct" & strpos(x_sectors, "Power Plants") > 0 & geo == "US-IL"

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

collapse (sum) measure = value, by(year)

replace measure = measure / 1000000

generate byte n = 1

sort year

list year measure n, noobs
