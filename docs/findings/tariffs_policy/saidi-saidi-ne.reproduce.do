* Expected: 2015 67.933313, 2025 542.784914, change 474.851601 (minutes a customer); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate saidi for saidi_NE from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "eia861_utility_reliability.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if geo == "US-NE"

keep if variable == "ieee_saidi_with_med" | variable == "ieee_customers"

keep entity year variable value

reshape wide value, i(entity year) j(variable) string

drop if missing(valueieee_saidi_with_med) | missing(valueieee_customers) | valueieee_customers <= 0

generate double minutes = valueieee_saidi_with_med * valueieee_customers

collapse (sum) minutes (sum) cust = valueieee_customers, by(year)

generate double measure = minutes / cust

generate byte n = 1

sort year

list year measure n, noobs
