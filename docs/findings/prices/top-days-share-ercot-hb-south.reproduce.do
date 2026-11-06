* Expected: 2015 57.520017, 2025 36.759829, change -20.760188 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate top_days_share for ercot_HB_SOUTH from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "ercot_all_hub_prices_history.csv", varnames(1) stringcols(_all) clear

keep if market == "ercot_rtm" & (node == "HB_SOUTH")

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

collapse (max) pmax = rt (min) pmin = rt (mean) pmean = rt (count) hours = rt (firstnm) year, by(day)

keep if hours >= 20

generate double spread = pmax - pmin

generate double neg_spread = -spread

bysort year (neg_spread): generate long rank = _n

by year: generate long n = _N

by year: egen double total = total(spread)

by year: egen double top = total(cond(rank <= ceil(0.10 * n), spread, .))

by year: keep if _n == 1

generate double measure = 100 * top / total

sort year

list year measure n, noobs
