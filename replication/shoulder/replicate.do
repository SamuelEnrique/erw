* ERW, The shoulder hours (/shoulder): the page's five headline figures, rebuilt from the public tables.

* Method: docs/methods/shoulder.md, sections 3 and 4 (the rules are those of docs/methods/shoulder_hours.md). Session 7503, chain 304, 16 November 2026.

* It reads two tables as CSV: shoulder_hours_monthly (the average day's 24 hours of net load and of solar, and the ten ranked days) and storage_buildout_monthly (the battery fleet, EIA-860M). Set the folder that holds them in the line "global tables" below. Run this file from its own folder.

* This do-file has not been run: Stata is not installed on the machine that wrote it. "python replicate.py --headline" follows it step for step on the same two files and printed the lines below.

* Expected values, on shoulder_hours_monthly as built on 3 November 2026 (27,489 rows), the warehouse's copy (session 7022, chain 301, the data machine). ERCOT, September 2026, the month the page opens on:

*   1. the evening shoulder, hours: 6 (from 18:00 to 24:00)

*   2. net load above its daily mean in the shoulder, MWh: 64,370.37

*   3. the fleet's hours at full power (MWh over MW), and the hours of the shoulder it covers: 1.65 and 1.65

*   4. hours the fleet would need to deliver all of it: 3.35

*   5. the same on the ten worst days of 2026, their mean: 6.76 (9 days)

* On the copy of 4 October 2026 (27,201 rows, the fleet as held on 3 October 2026) (the test's small fixture, tests/fixtures/session7503, prints the same lines), ERCOT, August 2026, the month the page opened on then:

*   1. the evening shoulder, hours: 5 (from 19:00 to 24:00)

*   2. net load above its daily mean in the shoulder, MWh: 66,629.88

*   3. the fleet's hours at full power (MWh over MW), and the hours of the shoulder it covers: 1.65 and 1.65

*   4. hours the fleet would need to deliver all of it: 3.66

*   5. the same on the ten worst days of 2026, their mean: 6.58 (10 days)

* The figures move when the table is rebuilt (a newer month, a fleet EIA has since published): after a new copy, compare with python replicate.py --headline, not with the lines above.

clear all

global tables "../../warehouse/output"

* The grid (iso:ercot, iso:caiso or iso:caiso_own) and the month. The fleet of both California entities is iso:caiso's.

global entity "iso:ercot"

global fleet_entity "iso:ercot"

global month "2026-08"

* ---- The fleet, by month: the batteries operating in EIA's monthly generator inventory, MW and MWh.

* A standard ERW table opens with comment lines that begin with #, then a line of column names; its first four columns are entity, variable, ts_utc and value.

import delimited using "$tables/storage_buildout_monthly.csv", delimiter(comma) varnames(nonames) stringcols(_all) bindquote(nobind) clear

drop if substr(v1, 1, 1) == "#" | v1 == "entity"

keep v1 v2 v3 v4

rename (v1 v2 v3 v4) (entity variable ts_utc value)

keep if entity == "$fleet_entity" & inlist(variable, "battery_operating_mw", "battery_operating_mwh")

destring value, replace force

gen ym = substr(ts_utc, 1, 7)

replace variable = substr(variable, 19, .)

keep ym variable value

reshape wide value, i(ym) j(variable) string

rename (valuemw valuemwh) (fleet_mw fleet_mwh)

tempfile fleet

save `fleet'

* ---- The table, the grid's rows.

import delimited using "$tables/shoulder_hours_monthly.csv", delimiter(comma) varnames(nonames) stringcols(_all) bindquote(nobind) clear

drop if substr(v1, 1, 1) == "#" | v1 == "entity"

keep v1 v2 v3 v4

rename (v1 v2 v3 v4) (entity variable ts_utc value)

keep if entity == "$entity"

destring value, replace force

tempfile grid

save `grid'

* ---- The month's average day: net load and solar by local hour, 0 to 23.

keep if substr(ts_utc, 1, 7) == "$month" & (substr(variable, 1, 16) == "avg_net_load_mw_" | substr(variable, 1, 13) == "avg_solar_mw_")

gen hour = real(substr(variable, -2, 2))

gen series = cond(substr(variable, 1, 9) == "avg_solar", "solar", "net")

keep hour series value

reshape wide value, i(hour) j(series) string

sort hour

* Net load's daily mean: the mean of the 24 hourly values.

egen mean_net = mean(valuenet)

* The shoulder starts at the first hour after solar's highest hour (the earliest, on a tie) in which solar is below half of that highest value.

egen top_solar = max(valuesolar)

egen top_hour = min(cond(valuesolar == top_solar, hour, .))

egen start = min(cond(hour > top_hour & valuesolar < top_solar / 2, hour, .))

* It ends at the first hour, after net load has risen above its mean, in which net load is back at or below it; at midnight (24) when it never is.

egen rise = min(cond(hour >= start & valuenet > mean_net, hour, .))

egen back = min(cond(hour > rise & valuenet <= mean_net, hour, .))

gen end = cond(missing(back), 24, back)

* Its energy above the mean counts only the hours in which net load is above the mean.

egen mwh = total(cond(hour >= start & hour < end & valuenet > mean_net, valuenet - mean_net, 0))

gen ym = "$month"

keep in 1

keep ym start end mwh

merge 1:1 ym using `fleet', keep(match) nogenerate

gen hours = end - start

* The fleet's hours are its MWh over its MW, to the table's four decimals; the hours covered are the smaller of the shoulder's length and those hours; the hours needed are the shoulder's energy over the fleet's MW.

gen fleet_hours = round(fleet_mwh / fleet_mw, 0.0001)

gen covered = min(hours, fleet_hours)

gen needed = mwh / fleet_mw

display "$entity, $month"

display "1. the evening shoulder, hours: " hours[1] " (from " %02.0f start[1] ":00 to " %02.0f end[1] ":00)"

display "2. net load above its daily mean in the shoulder, MWh: " %12.2fc mwh[1]

display "3. the fleet's hours at full power (MWh over MW), and the hours of the shoulder it covers: " %4.2f fleet_hours[1] " and " %4.2f covered[1]

display "4. hours the fleet would need to deliver all of it: " %4.2f needed[1]

* ---- The ten worst days of the month's year: each ranked day's energy above its own mean over the fleet's MW of the day's month, and their mean.

* The page gives the mean only when all ten days have a fleet: when the count below is under ten, the page says the figure is not held.

use `grid', clear

keep if substr(ts_utc, 1, 4) == substr("$month", 1, 4) & inlist(variable, "worst_rank", "day_shoulder_mwh_above_mean")

gen day = substr(ts_utc, 1, 10)

keep day variable value

reshape wide value, i(day) j(variable) string

keep if !missing(valueworst_rank)

gen ym = substr(day, 1, 7)

merge m:1 ym using `fleet', keep(master match) nogenerate

gen needed = round(valueday_shoulder_mwh_above_mean / fleet_mw, 0.0001)

quietly count if !missing(needed)

local days = r(N)

quietly summarize needed

display "5. the same on the ten worst days of " substr("$month", 1, 4) ", their mean: " %4.2f r(mean) " (`days' days)"
