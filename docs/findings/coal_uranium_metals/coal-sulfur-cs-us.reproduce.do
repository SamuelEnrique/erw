* Expected: 2008 0.892194, 2025 1.120865, change 0.22867 (percent sulfur); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate coal_sulfur for cs_us from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "eia_coal_receipts_annual.csv", varnames(1) stringcols(_all) clear

keep if variable == "quantity" | variable == "sulfur_content"

keep entity ts_utc x_mine_basin x_transport_mode variable value

destring value, replace force

reshape wide value, i(entity ts_utc x_mine_basin x_transport_mode) j(variable) string

drop if missing(valuequantity)

generate int year = real(substr(ts_utc, 1, 4))

drop if missing(valuesulfur_content)

generate double ws = valuesulfur_content * valuequantity

collapse (sum) ws = ws (sum) q = valuequantity, by(year)

generate double measure = ws / q

generate byte n = 1

sort year

list year measure n, noobs
