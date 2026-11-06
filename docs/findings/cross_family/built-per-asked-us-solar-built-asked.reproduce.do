* Expected: 2010 0.998334, 2024 26.751742, change 25.753408 (percent of MW requested); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate built_per_asked for us_solar_built_asked from the ERW's public tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "eia860m_operating_generators.csv", varnames(1) stringcols(_all) clear

keep if technology == "Solar Photovoltaic"

destring nameplate_mw operating_year, replace force

drop if missing(nameplate_mw) | missing(operating_year)

collapse (sum) built = nameplate_mw, by(operating_year)

rename operating_year year

save built_years, replace

import delimited "lbnl_interconnection_queue.csv", varnames(1) stringcols(_all) clear

keep if type_clean == "Solar"

destring mw_1 q_year, replace force

drop if missing(mw_1) | missing(q_year)

collapse (sum) asked = mw_1, by(q_year)

rename q_year year

merge 1:1 year using built_years, keep(master match) nogenerate

replace built = 0 if missing(built)

keep if inrange(year, 2010, 2024) & asked > 0

generate double measure = 100 * built / asked

generate byte n = 1

sort year

list year measure n, noobs
