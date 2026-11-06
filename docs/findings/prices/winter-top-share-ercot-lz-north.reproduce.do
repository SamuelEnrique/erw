* Expected: 2015 12.5, 2025 42.045455, change 29.545455 (percent of the dearest hours); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate winter_top_share for ercot_LZ_NORTH from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "ercot_zone_prices_history.csv", varnames(1) stringcols(_all) clear

keep if market == "ercot_rtm" & (node == "LZ_NORTH")

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

generate byte winter = inlist(month(day), 12, 1, 2)

gsort year -rt hour_utc

by year: generate long rank = _n

by year: generate long n = _N

by year: egen double top_winter = mean(cond(rank <= ceil(0.01 * n), winter, .))

by year: keep if _n == 1

generate double measure = 100 * top_winter

sort year

list year measure n, noobs
