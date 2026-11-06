* Expected: 2001 35.425, 2025 87.7, change 52.275 (USD per MWh); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate res_over_ind for res_ind_gap_US from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_retail_electricity_prices.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if (entity == "eia:retail_price:US:RES" | entity == "eia:retail_price:US:IND") & variable == "retail_price"

generate str3 sec = substr(entity, -3, 3)

keep year ts_utc sec value

reshape wide value, i(ts_utc) j(sec) string

drop if missing(valueRES) | missing(valueIND)

generate double gap = valueRES - valueIND

collapse (mean) measure = gap (count) n = gap, by(year)

sort year

list year measure n, noobs
