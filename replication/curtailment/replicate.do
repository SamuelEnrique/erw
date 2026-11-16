* ERW, curtailment (/curtailment): five figures of California's curtailment, rebuilt from caiso_curtailment_intervals.csv
* (session 7014, chain 301). Method: docs/methods/caiso_curtailment_intervals.md. The full replication of the page's
* California and Texas files is replicate.py beside this file (11,515 of 11,515 equal on 16 November 2026).
*
* This do-file has not been run: Stata is not installed on the machine that wrote it. Samuel runs it.
* To 2025 a row is a five-minute interval's MW (its MWh is MW / 12); from 2026 a row is an hour's MWh by category and
* reason. Months are Pacific; ts_utc is UTC, so a row's Pacific time is ts_utc less 8 hours (standard time) or 7
* (daylight time: from the second Sunday of March 10:00 UTC to the first Sunday of November 09:00 UTC).
* Expected values (site/data/curtailment_profile.json built 16 November 2026 12:47 UTC):
*   1. solar curtailed, 2025, MWh:          3,482,322.8
*   2. wind curtailed, 2025, MWh:             283,305.3
*   3. solar curtailed, October 2026, MWh:    154,267.6
*   4. wind curtailed, October 2026, MWh:      28,197.5
*   5. days held in October 2026:                  31

version 16
clear all
local f "caiso_curtailment_intervals.csv"
tempname fh
file open `fh' using "`f'", read text
local n 0
file read `fh' line
while substr(`"`line'"', 1, 1) == "#" {
    local ++n
    file read `fh' line
}
file close `fh'
local h = `n' + 1
import delimited using "`f'", varnames(`h') rowrange(`=`h' + 1') stringcols(_all) bindquote(strict) encoding("utf-8") clear
destring value, replace force
gen double t = clock(substr(ts_utc, 1, 19), "YMD#hms")
gen y = year(dofc(t))
gen double dst_on = clock(string(y) + "-03-01 10:00:00", "YMD hms") + msofhours(24) * (mod(7 - dow(mdy(3, 1, y)), 7) + 7)
gen double dst_off = clock(string(y) + "-11-01 09:00:00", "YMD hms") + msofhours(24) * mod(7 - dow(mdy(11, 1, y)), 7)
gen double lt = t - msofhours(8) + msofhours(1) * (t >= dst_on & t < dst_off)
gen ld = dofc(lt)
gen ly = year(ld)
gen lm = month(ld)
gen fuel = cond(strpos(variable, "_solar_"), "solar", "wind")
gen kind = cond(strpos(variable, "_day_mwh"), "day", cond(substr(variable, -4, 4) == "_mwh", "hourly", "interval"))
* the interval and hourly rows carry the energy; the day rows mark the days held
gen mwh = cond(kind == "interval", value / 12, value) if kind != "day"
quietly summarize mwh if ly == 2025 & fuel == "solar"
display "1. solar 2025: " %12.1f r(sum)
quietly summarize mwh if ly == 2025 & fuel == "wind"
display "2. wind 2025: " %12.1f r(sum)
quietly summarize mwh if ly == 2026 & lm == 10 & fuel == "solar"
display "3. solar October 2026: " %12.1f r(sum)
quietly summarize mwh if ly == 2026 & lm == 10 & fuel == "wind"
display "4. wind October 2026: " %12.1f r(sum)
* a day row's ts_utc carries the Pacific date itself
count if kind == "day" & fuel == "solar" & substr(ts_utc, 1, 7) == "2026-10"
display "5. days held, October 2026: " r(N)
