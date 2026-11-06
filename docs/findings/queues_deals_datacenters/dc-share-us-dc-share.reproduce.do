* Expected: 2014 0.496812, 2025 6.346093, change 5.849281 (percent of private nonresidential construction); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate dc_share for us_dc_share from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "census_c30_construction_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if (entity == "census_c30:private:data_center" | entity == "census_c30:private:nonresidential") & variable == "value_put_in_place"

generate str3 side = cond(entity == "census_c30:private:data_center", "dc", "all")

keep year ts_utc side value

reshape wide value, i(ts_utc) j(side) string

drop if missing(valuedc) | missing(valueall)

collapse (sum) dc = valuedc (sum) all = valueall (count) n = valuedc, by(year)

generate double measure = 100 * dc / all

sort year

list year measure n, noobs
