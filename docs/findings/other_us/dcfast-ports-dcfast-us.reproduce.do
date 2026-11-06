* Expected: 2014 1494.0, 2025 68599.0, change 67105.0 (ports); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 166): reproduce candidate dcfast_ports for dcfast_US from the ERW's public table.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "afdc_ev_charging_state_annual.csv", varnames(1) stringcols(_all) clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

keep if variable == "ev_dcfast_ports"

generate str2 st = upper(word(subinstr(entity, ":", " ", .), 2))

keep if strpos(" AK AL AR AZ CA CO CT DC DE FL GA HI IA ID IL IN KS KY LA MA MD ME MI MN MO MS MT NC ND NE NH NJ NM NV NY OH OK OR PA RI SC SD TN TX UT VA VT WA WI WV WY ", " " + st + " ") > 0

collapse (sum) measure = value, by(year)

generate byte n = 1

sort year

list year measure n, noobs
