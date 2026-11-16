* ERW, the datacenter power tracker (/datacenters): the tool's five headline figures, rebuilt from the rows.

* Method: docs/methods/datacenter_tracker.md, sections 3, 4 and 8. Session 7403, chain 303, 16 November 2026.

* Before this file: python replication/datacenter_tracker/fetch_rows.py writes rows/facilities_slim.csv and rows/ercot_large_load.csv
* from the live set (the table is held, license needed, so its rows are not in git). Run this file from its own folder.

* This do-file has not been run: Stata is not installed on the machine that wrote it. "python replicate.py --headline"
* follows it step for step on the same two files and prints the same five lines.

* Expected values, on the live set's rows as read on 16 November 2026 at 09:18 UTC (458 rows, vintage 15 November):

*   1. facilities held: 458

*   2. counted in the sums (a named US state, not cancelled): 274

*   3. megawatts stated by the counted facilities: 28,254

*   4. counted facilities that state megawatts: 21

*   5. ERCOT, megawatts approved to energize, newest report (2026-06-19): 8,927

* The figures move with the table each day: after a new fetch, compare with python replicate.py --headline, not with the lines above.

clear all

* Each file has one comment line; the column names are on line 2 and the rows start on line 3.

import delimited using "rows/facilities_slim.csv", delimiter(comma) varnames(2) rowrange(3) stringcols(_all) clear

* Megawatts: the stated capacity, missing where no source states one (never zero).

destring capacity_mw, replace force

* In the United States: the country column says US, or, where it is empty, the state is one of the 50 states, the District of Columbia or Puerto Rico.

local states " AL AK AZ AR CA CO CT DE DC FL GA HI ID IL IN IA KS KY LA ME MD MA MI MN MS MO MT NE NV NH NJ NM NY NC ND OH OK OR PA RI SC SD TN TX UT VT VA WA WV WI WY PR "

gen byte us = country == "US" | (country == "" & state != "" & strpos("`states'", " " + state + " ") > 0)

* Cancelled: the entities vocabulary's withdrawn (the extractor's cancelled).

gen byte cancelled = inlist(lower(status), "withdrawn", "cancelled")

* Counted: in a named US state and not cancelled. Every sum of the page is of these.

gen byte counted = us & !cancelled

quietly count

display "1. facilities held: " %9.0fc r(N)

quietly count if counted

display "2. counted in the sums (a named US state, not cancelled): " %9.0fc r(N)

quietly summarize capacity_mw if counted

display "3. megawatts stated by the counted facilities: " %12.0fc r(sum)

display "4. counted facilities that state megawatts: " %9.0fc r(N)

* ERCOT's large loads: the megawatts approved to energize in the newest report that states them.

import delimited using "rows/ercot_large_load.csv", delimiter(comma) varnames(2) rowrange(3) stringcols(_all) clear

keep if variable == "approved_to_energize_mw"

destring value, replace force

sort day

display "5. ERCOT, megawatts approved to energize, newest report (" day[_N] "): " %9.0fc value[_N]
