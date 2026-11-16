* ERW, the interconnection queue (/queues): five figures of the whole United States, rebuilt from
* lbnl_interconnection_queue.csv (session 7014, chain 301). Data: Lawrence Berkeley National Laboratory and GridTracker,
* Queued Up: 2026 Edition (CC BY 4.0). Method: docs/methods/interconnection_queue_summary.md. The full replication of
* every figure of the page's file is replicate.py beside this file (17,254 of 17,254 equal on 16 November 2026).
*
* This do-file has not been run: Stata is not installed on the machine that wrote it. Samuel runs it.
* Expected values (site/data/queues.json built 4 October 2026):
*   1. requests in the file:                                           38,201
*   2. MW requested (positive capacities only):                      7,098,748.5
*   3. active requests, and their MW:                                  8,513 and 1,864,963.3
*   4. of the 22,344 requests entered 2000 to 2020 with a known
*      status, the share that reached operation, percent:              18.78
*   5. median years from request to operation (3,098 requests):         3.58

version 16
clear all
local f "lbnl_interconnection_queue.csv"
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
destring capacity_mw q_year, replace force
count
display "1. requests: " r(N)
quietly summarize capacity_mw if capacity_mw > 0
display "2. MW requested: " %12.1f r(sum)
quietly summarize capacity_mw if q_status == "active" & capacity_mw > 0
local mw = r(sum)
count if q_status == "active"
display "3. active: " r(N) " requests, " %12.1f `mw' " MW"
gen known = inlist(q_status, "active", "suspended", "operational", "withdrawn")
count if known & q_year >= 2000 & q_year <= 2020
local past = r(N)
count if known & q_year >= 2000 & q_year <= 2020 & q_status == "operational"
display "4. past requests " `past' ", reached operation: " %5.2f 100 * r(N) / `past' " percent"
gen qd = date(substr(q_date, 1, 10), "YMD")
gen od = date(substr(on_date, 1, 10), "YMD")
gen yrs = (od - qd) / 365.25 if q_status == "operational" & qd < . & od < . & od >= qd
quietly summarize yrs, detail
display "5. median years to operation: " %4.2f r(p50) " of " r(N) " requests"
