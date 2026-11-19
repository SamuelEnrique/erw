* Expected: 2015 13.557403, 2023 29.218078, change 15.660675 (million t CO2e); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate ghg_onshore_basin for ghgon_430 from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "epa_ghgrp_facility_emissions.csv", varnames(1) stringcols(_all) clear

keep if variable == "emissions_onshore_production" & lower(substr(x_basin, 1, 6)) == "430 - "

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

collapse (sum) measure = value, by(year)

replace measure = measure / 1000000

generate byte n = 1

sort year

list year measure n, noobs
