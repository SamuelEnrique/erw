* ERW, where power is cheap (/prices/compare): five figures of the twelve months to September 2026, rebuilt from the
* warehouse's ERCOT hub price history (session 7012, chain 301). Method: docs/methods/hub_price_comparison.md. The full
* replication of every figure of the page's file is replicate.py beside this file (578 of 578 equal).
*
* This do-file has not been run: Stata is not installed on the machine that wrote it. Samuel runs it.
* The window is 1 October 2025 to 1 October 2026 in Central time; both ends fall in daylight time (UTC-5), so it runs
* from 2025-10-01 05:00 UTC to 2026-10-01 05:00 UTC: 8,760 hours, the clock changes inside it cancelling.
* Expected values (site/data/price_compare.json built 16 November 2026 11:36 UTC), day-ahead:
*   1. ERCOT hub average, mean price, USD per MWh:          34.30
*   2. ERCOT hub average, hours held:                       8,760
*   3. ERCOT West, share of hours below zero, percent:       7.42
*   4. ERCOT West, share of hours above USD 200, percent:    0.78
*   5. ERCOT Houston, mean price, USD per MWh:              35.22

version 16
clear all
local f "ercot_all_hub_prices_history.csv"
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

keep if market == "ercot_dam" & inlist(entity, "ercot:HB_HUBAVG", "ercot:HB_WEST", "ercot:HB_HOUSTON")
destring value, replace force
gen double t = clock(substr(ts_utc, 1, 19), "YMD#hms")
keep if t >= clock("2025-10-01 05:00:00", "YMD hms") & t < clock("2026-10-01 05:00:00", "YMD hms")
duplicates drop entity ts_utc, force
gen neg = value < 0
gen high = value > 200
collapse (mean) avg = value neg high (count) hours = value, by(entity)
replace neg = 100 * neg
replace high = 100 * high
format avg neg high %9.2f
* the five figures: HB_HUBAVG's avg (1) and hours (2), HB_WEST's neg (3) and high (4), HB_HOUSTON's avg (5)
list entity avg hours neg high, noobs
