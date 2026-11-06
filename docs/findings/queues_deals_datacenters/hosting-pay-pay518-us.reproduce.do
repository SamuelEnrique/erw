* Expected: 2012 89.983038, 2023 147.665185, change 57.682147 (USD thousand a year); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate hosting_pay for pay518_US from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "census_cbp_hosting_annual.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double pay = value if variable == "annual_payroll"

generate double emp = value if variable == "employment"

collapse (sum) pay (sum) emp, by(year entity)

drop if pay == 0 | emp == 0

collapse (sum) pay (sum) emp, by(year)

generate double measure = pay / emp / 1000

generate byte n = 1

sort year

list year measure n, noobs
