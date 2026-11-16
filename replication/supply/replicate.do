* ERW, supply and trade (/supply): five headline figures of the week of 6 November 2026, rebuilt from the EIA weekly
* tables (session 7013, chain 301). Method: docs/methods/supply_and_trade.md. The full replication of every figure of the
* page's file is replicate.py beside this file (5,125 of 5,125 equal; the fuel burn's 16 rows apart).
*
* This do-file has not been run: Stata is not installed on the machine that wrote it. Samuel runs it.
* Expected values (site/data/supply.json built 16 November 2026 12:00 UTC):
*   1. Working gas in storage, Lower 48, week of 2026-11-06, Bcf:                 3,862    (week before +61)
*   2. Its five-year average (the values 52, 104, 156, 208 and 260 weeks back):    3,808.6
*   3. Commercial crude oil stocks, million barrels:                               414.417  (week before +4.657)
*   4. Crude oil production, United States, thousand barrels a day:               14,013   (five-year average 12,792.4)
*   5. Refinery utilization, percent:                                              95.2

version 16
clear all
program define readerw
    args f
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
end

readerw "eia_gas_storage_weekly.csv"
keep if entity == "eia:NW2_EPG0_SWO_R48_BCF"
destring value, replace force
gen d = date(substr(ts_utc, 1, 10), "YMD")
quietly summarize value if d == td(06nov2026)
local last = r(mean)
quietly summarize value if d == td(30oct2026)
display "1. working gas, Lower 48: " `last' " (week before " `last' - r(mean) ")"
gen back = 0
foreach k in 1 2 3 4 5 {
    replace back = 1 if d == td(06nov2026) - 364 * `k'
}
quietly summarize value if back
display "2. five-year average: " %8.1f r(mean) " of " r(N) " values"

readerw "eia_petroleum_supply_weekly.csv"
destring value, replace force
gen d = date(substr(ts_utc, 1, 10), "YMD")
quietly summarize value if entity == "eia:WCESTUS1" & d == td(06nov2026)
display "3. commercial crude stocks, million barrels: " %8.3f r(mean) / 1000
quietly summarize value if entity == "eia:WCRFPUS2" & d == td(06nov2026)
display "4. crude production: " r(mean)
quietly summarize value if entity == "eia:WPULEUS3" & d == td(06nov2026)
display "5. refinery utilization: " r(mean)
