* ERW, storage (/storage): five figures of the fleet, rebuilt from storage_capacity.csv (session 7014, chain 301).
* The page reads the live set; replicate.py compares every live row with the warehouse's tables (63,075 of 63,075 equal on
* 16 November 2026 at 12:25 UTC) and recomputes these sums.
*
* This do-file has not been run: Stata is not installed on the machine that wrote it. Samuel runs it.
* Expected values (storage_capacity of 16 November 2026):
*   1. operating batteries:                       1,156
*   2. operating MW, every grid:                 56,120.7
*   3. operating MWh, every grid:               154,272.4
*   4. operating MW in ERCOT, and in CAISO:      19,194.6 and 17,265.5
*   5. planned MW with a planned year of 2027:   26,847.5

version 16
clear all
local f "storage_capacity.csv"
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
destring capacity_mw energy_capacity_mwh, replace force
count if status == "operating"
display "1. operating batteries: " r(N)
quietly summarize capacity_mw if status == "operating"
display "2. operating MW: " %10.1f r(sum)
quietly summarize energy_capacity_mwh if status == "operating"
display "3. operating MWh: " %10.1f r(sum)
quietly summarize capacity_mw if status == "operating" & iso == "ERCOT"
local e = r(sum)
quietly summarize capacity_mw if status == "operating" & iso == "CAISO"
display "4. operating MW in ERCOT and CAISO: " %9.1f `e' " and " %9.1f r(sum)
quietly summarize capacity_mw if status != "operating" & planned_year == "2027"
display "5. planned MW, 2027: " %9.1f r(sum)
