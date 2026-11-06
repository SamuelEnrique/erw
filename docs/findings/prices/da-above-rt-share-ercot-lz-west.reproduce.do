* Expected: 2015 66.187215, 2025 59.3379, change -6.849315 (percent of hours); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate da_above_rt_share for ercot_LZ_WEST from the ERW's public tables.

* Input: the table's CSV as the public download holds it (Redivis: the variable names on its first line). From the ERW's own file, delete its lines that begin with # first.

clear all

import delimited "ercot_zone_prices_history.csv", varnames(1) stringcols(_all) clear

keep if (market == "ercot_rtm" | market == "ercot_dam") & node == "LZ_WEST"

destring value, replace force

drop if missing(value)

generate double t_utc = clock(subinstr(subinstr(ts_utc, "T", " ", 1), "Z", "", 1), "YMDhms")

generate double hour_utc = floor(t_utc / msofhours(1)) * msofhours(1)

generate str3 kind = substr(market, -3, 3)

collapse (mean) value, by(kind hour_utc)

reshape wide value, i(hour_utc) j(kind) string

drop if missing(valuedam) | missing(valuertm)

generate int y_utc = year(dofc(hour_utc))

generate int mar1 = mdy(3, 1, y_utc)

generate int dst_start = mar1 + mod(7 - dow(mar1), 7) + 7

generate int nov1 = mdy(11, 1, y_utc)

generate int dst_end = nov1 + mod(7 - dow(nov1), 7)

generate byte dst = hour_utc >= cofd(dst_start) + msofhours(8) & hour_utc < cofd(dst_end) + msofhours(7)

generate double t_local = hour_utc - msofhours(6) + dst * msofhours(1)

generate int year = year(dofc(t_local))

generate byte above = valuedam > valuertm

collapse (mean) measure = above (count) n = above, by(year)

replace measure = 100 * measure

sort year

list year measure n, noobs
