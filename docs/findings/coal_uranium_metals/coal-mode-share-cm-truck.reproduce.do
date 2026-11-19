* Expected: 2008 9.905878, 2025 7.602664, change -2.303214 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate coal_mode_share for cm_truck from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_coal_receipts_annual.csv", varnames(1) stringcols(_all) clear

keep if variable == "quantity" | variable == "sulfur_content"

keep entity ts_utc x_mine_basin x_transport_mode variable value

destring value, replace force

reshape wide value, i(entity ts_utc x_mine_basin x_transport_mode) j(variable) string

drop if missing(valuequantity)

generate int year = real(substr(ts_utc, 1, 4))

generate double mine = valuequantity * (x_transport_mode == "Truck")

collapse (sum) mine = mine (sum) q = valuequantity, by(year)

generate double measure = 100 * mine / q

generate byte n = 1

sort year

list year measure n, noobs
