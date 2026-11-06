* Expected: 2019 51.154421, 2025 38.029285, change -13.125135 (percent of generation); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate gas_evening_share for caiso_mix from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "generation_mix_hourly_profile.csv", varnames(1) stringcols(_all) clear

keep if entity == "iso:caiso" & regexm(variable, "^avg_[a-z_]+_mw_h[0-9][0-9]$")

destring value, replace force

drop if missing(value)

generate int hour = real(substr(variable, -2, 2))

generate str20 src = regexs(1) if regexm(variable, "^avg_([a-z_]+)_mw_h[0-9][0-9]$")

keep if inrange(hour, 17, 21)

keep if src == "natural_gas" | src == "coal" | src == "nuclear" | src == "wind" | src == "solar" | src == "hydro" | src == "storage" | src == "other"

replace value = max(value, 0)

collapse (sum) value, by(ts_utc src)

bysort ts_utc: egen double gen = total(value)

keep if src == "natural_gas"

generate double share = 100 * value / gen

generate int year = real(substr(ts_utc, 1, 4))

collapse (mean) measure = share (count) n = share, by(year)

sort year

list year measure n, noobs
