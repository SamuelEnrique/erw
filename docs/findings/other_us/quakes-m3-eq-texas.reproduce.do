* Expected: 2010 9.0, 2025 67.0, change 58.0 (earthquakes); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate quakes_m3 for eq_texas from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "usgs_comcat_earthquakes_south_central.csv", varnames(1) stringcols(_all) clear

destring x_magnitude, replace force

drop if missing(x_magnitude)

keep if x_magnitude >= 3.0 & x_place_state == "Texas"

duplicates drop event_id, force

generate int year = real(substr(event_date, 1, 4))

generate byte one = 1

collapse (sum) measure = one, by(year)

keep if inrange(year, 2010, 2026)

tempfile got

save `got'

clear

set obs 17

generate int year = 2009 + _n

merge 1:1 year using `got', nogenerate

replace measure = 0 if missing(measure)

generate byte n = 1

* A year with no earthquake is a year of zero, as the Python prints it: the years 2010 to 2026 are added above.

sort year

list year measure n, noobs
