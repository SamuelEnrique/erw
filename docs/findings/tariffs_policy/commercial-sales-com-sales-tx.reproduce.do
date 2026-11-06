* Expected: 2001 87.912113, 2025 174.683009, change 86.770896 (TWh); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate commercial_sales for com_sales_TX from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia_retail_sales_monthly.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if entity == "eia:retail_sales:TX:COM" & variable == "retail_sales"

collapse (sum) measure = value (count) n = value, by(year)

replace measure = measure / 1000000

sort year

list year measure n, noobs
