* Expected: 2015 15.534375, 2025 45.878125, change 30.34375 (USD per MWh); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate spread_4h for ercot_HB_WEST from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "ercot_all_hub_prices_history.csv", varnames(1) stringcols(_all) clear

keep if market == "ercot_rtm" & (node == "HB_WEST")

destring value, replace force

drop if missing(value)

generate double t_utc = clock(subinstr(subinstr(ts_utc, "T", " ", 1), "Z", "", 1), "YMDhms")

generate double hour_utc = floor(t_utc / msofhours(1)) * msofhours(1)

collapse (mean) rt = value, by(node hour_utc)

* Central time: standard is UTC minus 6 hours; daylight time from the second Sunday of March 08:00 UTC to the first Sunday of November 07:00 UTC.

generate int y_utc = year(dofc(hour_utc))

generate int mar1 = mdy(3, 1, y_utc)

generate int dst_start = mar1 + mod(7 - dow(mar1), 7) + 7

generate int nov1 = mdy(11, 1, y_utc)

generate int dst_end = nov1 + mod(7 - dow(nov1), 7)

generate byte dst = hour_utc >= cofd(dst_start) + msofhours(8) & hour_utc < cofd(dst_end) + msofhours(7)

generate double t_local = hour_utc - msofhours(6) + dst * msofhours(1)

generate int year = year(dofc(t_local))

generate int lhour = hh(t_local)

generate long day = dofc(t_local)

bysort day: generate long hours = _N

keep if hours >= 20

bysort day (rt): generate long up = _n

by day: generate long down = _N - _n + 1

generate double low4 = rt if up <= 4

generate double top4 = rt if down <= 4

collapse (mean) low4 (mean) top4 (firstnm) year, by(day)

generate double spread4 = top4 - low4

collapse (median) measure = spread4 (count) n = spread4, by(year)

sort year

list year measure n, noobs
