* Expected: 2016 0.460962, 2025 4.817932, change 4.356971 (percent of registered light-duty vehicles); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 166): reproduce candidate ev_share for ev_CA from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "afdc_vehicle_registrations_annual.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if entity == "afdc_reg:CA" & substr(variable, 1, 14) == "registrations_"

generate double ev = value if variable == "registrations_ev"

collapse (sum) ev (sum) all = value, by(year)

keep if all > 0

generate double measure = 100 * ev / all

generate byte n = 1

sort year

list year measure n, noobs
