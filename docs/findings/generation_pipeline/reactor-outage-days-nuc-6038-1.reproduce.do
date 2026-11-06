* Expected: 2007 85.0, 2025 26.0, change -59.0 (days); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate reactor_outage_days for nuc_6038_1 from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_nuclear_outages_generator_daily.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia_nuclear_outages_gen:6038:1" & (variable == "capacity" | variable == "outage")

destring value, replace force

drop if missing(value)

keep ts_utc variable value

reshape wide value, i(ts_utc) j(variable) string

drop if missing(valuecapacity) | valuecapacity <= 0

replace valueoutage = 0 if missing(valueoutage)

generate byte out = valueoutage >= 0.5 * valuecapacity

generate int year = real(substr(ts_utc, 1, 4))

collapse (sum) measure = out (count) n = out, by(year)

sort year

list year measure n, noobs
