* ERW, the deal tracker (/deals): the tool's headline figures, rebuilt from the rows.

* Method: docs/methods/deal_tracker.md, sections 3, 4 and 5. Session 7406, chain 303, 16 November 2026.

* Before this file: python replication/deals/fetch_rows.py writes rows/deals_slim.csv from the live set (the table is held,
* license needed, so its rows are not in git with the replication). Run this file from its own folder.

* This do-file has not been run: Stata is not installed on the machine that wrote it. "python replicate.py --headline"
* follows it step for step on the same file and prints the same lines.

* Expected values, on the live set's rows as read on 16 November 2026 at 09:49 UTC (590 rows, the newest deal of 13 November):

*   1. deals held, the register's folded pairs counted once: 585

*   2. deals that state a size in MW: 39

*   3. megawatts stated by them: 43,119

*   4. deals that state a value in US dollars: 298

*   5. deals tagged AI power: 217

*   6. deals that state a price in US dollars per MWh: 0

* and, of the table by year and kind, for the power purchases (kind ppa): 2025, 3 deals, none stating MW; 2026, 29 deals, 10 stating MW, 9,911.5 MW.

* The figures move with the table each day: after a new fetch, compare with python replicate.py --headline, not with the lines above.

clear all

* The file has one comment line; the column names are on line 2 and the rows start on line 3.

import delimited using "rows/deals_slim.csv", delimiter(comma) varnames(2) rowrange(3) stringcols(_all) clear

* One deal, one row: the row the register marks as the duplicate of a folded pair leaves (the tracker, the comparables, the AI view and the charts count the pair once).

drop if folded_duplicate == "1"

* A figure a story does not state is missing, never zero.

destring mw, replace force

destring dollars, replace force

destring usd_per_mwh, replace force

quietly count

display "1. deals held, the register's folded pairs counted once: " %9.0fc r(N)

quietly summarize mw

display "2. deals that state a size in MW: " %9.0fc r(N)

display "3. megawatts stated by them: " %12.2fc r(sum)

quietly count if dollars < .

display "4. deals that state a value in US dollars: " %9.0fc r(N)

* The AI-power tag: "True" and "true" are one flag (the fetch writes it in lower case).

quietly count if ai_power == "true"

display "5. deals tagged AI power: " %9.0fc r(N)

quietly count if usd_per_mwh < .

display "6. deals that state a price in US dollars per MWh: " %9.0fc r(N)

* By year and kind: the deals, those that state MW, and the MW they state (a kind left empty by the extraction is "other").

gen year = substr(date, 1, 4)

replace kind = "other" if kind == ""

gen byte states_mw = mw < .

collapse (count) deals = states_mw (sum) stating_mw = states_mw (sum) mw_stated = mw, by(year kind)

list year kind deals stating_mw mw_stated, noobs clean
