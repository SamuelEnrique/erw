* Expected: 2001 8308.188812, 2023 4150.0, change -4158.188812 (USD per kW DC); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate res_pv_price for tts_res_CA from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "lbnl_tracking_the_sun.csv", varnames(1) stringcols(_all) clear

keep if entity == "tts:ca_res" & (variable == "price_median" | variable == "systems_priced")

destring value, replace force

keep ts_utc variable value

reshape wide value, i(ts_utc) j(variable) string

drop if missing(valueprice_median) | missing(valuesystems_priced)

keep if valuesystems_priced >= 500

generate int year = real(substr(ts_utc, 1, 4))

rename valueprice_median measure

generate byte n = 1

sort year

list year measure n, noobs
