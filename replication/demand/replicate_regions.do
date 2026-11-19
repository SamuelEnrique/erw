* ERW, /demand, the view "The whole country" (/demand?view=country): five headline figures, rebuilt from the ERW table
* eia930_ba_demand_hourly (EIA's six-month files of Form EIA-930, public domain). Session 8480, chain 503, part E.
* Method: docs/methods/demand_growth.md, "The whole country" and "Every figure, in the view's order"; the files' method:
* docs/methods/regions_pages.md. The full replication of every figure the view prints is replicate_regions.py beside
* this file (449,440 of 449,440 figures over 783 views of 71 places on the files built 19 November 2026).
*
* This do-file has not been run: Stata is not installed on the machine that wrote it. Samuel runs it.
*
* Input: eia930_ba_demand_hourly.csv (Redivis, or warehouse/output on the data machine), columns entity, variable,
* ts_utc, value, ...; entity "eia930:<code>", variable "demand_mw", ts_utc the hour's start in UTC, value EIA's adjusted
* demand where printed. Its "#" header lines are dropped below.
*
* The rules (docs/methods/demand_growth.md, rule 3 of "Every figure"; docs/methods/regions_pages.md):
*  - a region's hour is the sum of its authorities that file demand, written only when every one active that hour holds
*    a value (the Southeast: AEC to its retirement, 2021-09-01 04:00 UTC, and SOCO);
*  - an hour is used when it is held, above zero, within 25 percent of the median of those of the two hours before and
*    the two after that are held and above zero, and from a third of to three times the place's median hour; the test
*    is run once, on the hours as written;
*  - a year is the place's local calendar year (Tennessee, Texas and the Southeast: Central time; the Carolinas:
*    Eastern), daylight saving included; its average is the mean of its used hours.
*
* Expected values (site/data/regions/demand/*.json, built 2026-11-19 between 12:01 and 12:03 UTC):
*   1. Tennessee (TVA) 2025 average demand, MW:            19,490.4   (2019: 18,189.5; growth +7.15 percent)
*   2. Tennessee (TVA) 2025 highest hour, MW:              35,086     (the hour from 2025-01-22 13:00 UTC, 07:00 Central)
*   3. Carolinas 2025 average demand, MW:                  26,272.4   (CPLE, CPLW, DUK, SC, SCEG; 8,711 of 8,760 hours)
*   4. Texas (region) 2025 average demand, MW:             55,717.2   (ERCOT as an authority: 55,717.2; 8,736 hours)
*   5. Southeast 2025 average demand, MW:                  27,554.2   (2019: 27,763.9; growth -0.76 percent)
* The fifth figure named in docs/reviews/demand-regions-read-2026-11-19.md (the Southeast's summer peak of 2025 with
* the weather taken out) is not held in the file: region_weather_hourly holds too few of its hours for the 95 percent
* rule, so the page draws it blank. The Southeast's own average and growth stand in its place.

version 16
clear all
set more off
capture program drop erw_local
capture program drop erw_screen
capture program drop erw_place

program define erw_local
    * args: zone ("central" or "eastern"); makes local_year from ts (UTC, Stata clock)
    args zone
    local std = cond("`zone'" == "central", 6, 5)
    gen int yy = year(dofc(ts))
    * second Sunday of March and first Sunday of November, at 02:00 local standard (start) and daylight (end) time
    gen double mar1 = mdy(3, 1, yy)
    gen double nov1 = mdy(11, 1, yy)
    gen double dst_on = cofd(mar1 + mod(7 - dow(mar1), 7) + 7) + (2 + `std') * 3600000
    gen double dst_off = cofd(nov1 + mod(7 - dow(nov1), 7)) + (2 + `std' - 1) * 3600000
    gen double lt = ts - `std' * 3600000 + cond(ts >= dst_on & ts < dst_off, 3600000, 0)
    gen int local_year = year(dofc(lt))
    drop yy mar1 nov1 dst_on dst_off
end

program define erw_screen
    * the hours used: held, above zero, within 25 percent of the median of the held neighbours, inside the range
    tsset h
    gen double ok = mw if mw < . & mw > 0
    gen double n1 = L2.ok
    gen double n2 = L1.ok
    gen double n3 = F1.ok
    gen double n4 = F2.ok
    egen double med = rowmedian(n1 n2 n3 n4)
    quietly summarize ok, detail
    local mid = r(p50)
    gen byte used = ok < . & (med >= . | abs(ok - med) / med <= 0.25) & ok >= `mid' / 3 & ok <= 3 * `mid'
    drop n1-n4
end

program define erw_place
    * args: list of codes, zone; leaves one row an hour with mw (the sum where every code active that hour holds one)
    args codes zone
    use "`c(tmpdir)'/erw_ba.dta", clear
    gen byte keepme = 0
    foreach c of local codes {
        replace keepme = 1 if code == "`c'"
    }
    keep if keepme
    * the authorities active in each hour: AEC to 2021-09-01 04:00 UTC
    gen byte active = !(code == "AEC" & ts >= clock("2021-09-01 04:00", "YMD hm"))
    keep if active
    gen byte held = value < .
    collapse (sum) mw = value (min) allheld = held (count) n = value, by(ts)
    gen byte nwant = 0
    foreach c of local codes {
        replace nwant = nwant + cond("`c'" == "AEC", ts < clock("2021-09-01 04:00", "YMD hm"), 1)
    }
    replace mw = . if n < nwant | allheld == 0
    * every UTC hour of the span, so that a blank hour is a gap for the neighbours' median
    gen double h = round(ts / 3600000)
    tsset h
    tsfill
    replace ts = h * 3600000 if ts >= .
    erw_local `zone'
    erw_screen
end

* ---- the table, once
import delimited using "eia930_ba_demand_hourly.csv", varnames(nonames) stringcols(_all) clear
drop if substr(v1, 1, 1) == "#"
foreach v of varlist _all {
    local nm = strtoname(`v'[1])
    rename `v' `nm'
}
drop in 1
keep if variable == "demand_mw"
gen code = subinstr(entity, "eia930:", "", 1)
keep if inlist(code, "TVA", "CPLE", "CPLW", "DUK", "SC", "SCEG", "ERCO", "AEC", "SOCO")
gen double ts = clock(substr(ts_utc, 1, 16), "YMD#hm")
destring value, replace force
keep code ts value
save "`c(tmpdir)'/erw_ba.dta", replace

* ---- 1 and 2: Tennessee (TVA alone)
erw_place "TVA" central
quietly summarize ok if used & local_year == 2019
local a19 = r(mean)
quietly summarize ok if used & local_year == 2025
display "1. Tennessee 2025 average, MW: " %9.1f r(mean) "   (2019: " %9.1f `a19' "; growth " %6.2f (r(mean) / `a19' - 1) * 100 " percent)"
display "2. Tennessee 2025 highest hour, MW: " %9.0f r(max)
list ts ok if used & local_year == 2025 & ok == r(max), noobs

* ---- 3: the Carolinas
erw_place "CPLE CPLW DUK SC SCEG" eastern
quietly summarize ok if used & local_year == 2025
display "3. Carolinas 2025 average, MW: " %9.1f r(mean) "   over " r(N) " hours"

* ---- 4: Texas (ERCOT alone)
erw_place "ERCO" central
quietly summarize ok if used & local_year == 2025
display "4. Texas 2025 average, MW: " %9.1f r(mean) "   over " r(N) " hours"

* ---- 5: the Southeast (AEC to its retirement, and SOCO)
erw_place "AEC SOCO" central
quietly summarize ok if used & local_year == 2019
local s19 = r(mean)
quietly summarize ok if used & local_year == 2025
display "5. Southeast 2025 average, MW: " %9.1f r(mean) "   (2019: " %9.1f `s19' "; growth " %6.2f (r(mean) / `s19' - 1) * 100 " percent)"
