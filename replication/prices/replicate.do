* ERW, power prices (/prices, /prices/<hub>): five prices the pages draw, read from the warehouse's tables (session 7011,
* chain 301). The pages read the live set, which replicate.py compares row by row with these tables (74,258 of 74,258
* equal on 16 November 2026 at 11:25 UTC).
*
* This do-file has not been run: Stata is not installed on the machine that wrote it. Samuel runs it.
* Expected values (the tables of 16 November 2026), USD per MWh:
*   1. ERCOT hub average, day-ahead, the hour starting 2026-11-15 18:00 UTC:          32.29
*   2. CAISO SP15, day-ahead, the same hour:                                          13.34319
*   3. SPP North hub, day-ahead, the same hour:                                       34.2017
*   4. ERCOT hub average, real time, the interval starting 2026-11-14 18:00 UTC:      12.96
*   5. ERCOT West hub, real time, the same interval:                                  11.63

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

readerw "iso_dam_hub_prices.csv"
destring value, replace force
list entity value if ts_utc == "2026-11-15T18:00:00Z" & inlist(entity, "ercot:HB_HUBAVG", "caiso:TH_SP15_GEN-APND", "spp:SPPNORTH_HUB"), noobs

readerw "iso_rtm_hub_prices.csv"
destring value, replace force
list entity value if ts_utc == "2026-11-14T18:00:00Z" & inlist(entity, "ercot:HB_HUBAVG", "ercot:HB_WEST"), noobs
