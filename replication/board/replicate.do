* ERW, the price board (/board): five headline figures rebuilt from iso_dam_hub_prices.csv (session 7010, chain 301).
* Method: docs/methods/price_board.md ("The columns of every row": a daily price is the mean of a complete local day's
* hours). The full replication of every figure of the page's file is replicate.py beside this file.
*
* This do-file has not been run: Stata is not installed on the machine that wrote it. Samuel runs it.
* The days chosen, 9 to 15 November 2026, all fall after the clock change of 1 November, so one fixed offset a grid gives
* the local day: Central Standard Time (UTC-6) for ERCOT and SPP, Pacific Standard Time (UTC-8) for CAISO.
* Expected values (the board's file built 15 November 2026 18:19 UTC; every one equal to the hourly table's mean,
* replicate.py's part two):
*   1. ERCOT hub average, day-ahead, 15 November 2026, USD per MWh:          37.2504
*   2. ERCOT hub average, day-ahead, mean of 9 to 15 November:               39.1464
*   3. CAISO SP15, day-ahead, 15 November:                                   31.3727
*   4. SPP North hub, day-ahead, 15 November:                                37.9086
*   5. ERCOT North less Houston, day-ahead, 15 November:                      2.3117  (37.5371 - 35.2254)

version 16
clear all
local f "iso_dam_hub_prices.csv"

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

keep if inlist(entity, "ercot:HB_HUBAVG", "ercot:HB_NORTH", "ercot:HB_HOUSTON", "caiso:TH_SP15_GEN-APND", "spp:SPPNORTH_HUB")
destring value, replace force
gen double t = clock(substr(ts_utc, 1, 19), "YMD#hms")
gen offset = cond(substr(entity, 1, 5) == "caiso", -8, -6)
gen double local = t + offset * 3600000
gen ldate = dofc(local)
format ldate %td
keep if inrange(ldate, td(09nov2026), td(15nov2026))

* a complete local day: 24 hours (no clock change falls in these days)
bysort entity ldate: gen hours = _N
keep if hours == 24
collapse (mean) value, by(entity ldate)

quietly summarize value if entity == "ercot:HB_HUBAVG" & ldate == td(15nov2026)
display "1. ERCOT hub average, 15 November: " %9.4f r(mean)
quietly summarize value if entity == "ercot:HB_HUBAVG"
display "2. ERCOT hub average, mean of 9 to 15 November: " %9.4f r(mean) " (" r(N) " days)"
quietly summarize value if entity == "caiso:TH_SP15_GEN-APND" & ldate == td(15nov2026)
display "3. CAISO SP15, 15 November: " %9.4f r(mean)
quietly summarize value if entity == "spp:SPPNORTH_HUB" & ldate == td(15nov2026)
display "4. SPP North, 15 November: " %9.4f r(mean)
quietly summarize value if entity == "ercot:HB_NORTH" & ldate == td(15nov2026)
local north = r(mean)
quietly summarize value if entity == "ercot:HB_HOUSTON" & ldate == td(15nov2026)
display "5. ERCOT North less Houston, 15 November: " %9.4f `north' - r(mean)
