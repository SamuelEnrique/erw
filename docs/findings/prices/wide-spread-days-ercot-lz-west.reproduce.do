* Expected: 2015 28.767123, 2025 84.109589, change 55.342466 (percent of days); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate wide_spread_days for ercot_LZ_WEST from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "ercot_zone_prices_history.csv", varnames(1) stringcols(_all) clear

keep if market == "ercot_rtm" & (node == "LZ_WEST")

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

collapse (max) pmax = rt (min) pmin = rt (count) hours = rt (firstnm) year, by(day)

keep if hours >= 20

generate byte wide = pmax - pmin >= 50

collapse (mean) measure = wide (count) n = wide, by(year)

replace measure = 100 * measure

sort year

list year measure n, noobs
