* Energy Research Warehouse (ERW), session 7534 (chain 304): five headline figures of the problem sets in Stata.
* Run from the repository's root:  do replication/problem_sets/replicate.do
* It reads replication/problem_sets/live_rows.csv (the rows the five sets were given by the live set at
* 2026-11-16T22:51:27Z) and site/data/bill_rules.json's two numbers typed below with their source. Each figure is
* asserted against the page within half its last shown digit (0.005). Expected, as the pages showed them:
*   1. Know your grid, question 1: ERCOT's peak over CAISO's on 2026-11-15 (UTC)            2.08 times  (54,008 / 25,964 MW)
*   2. Know your grid, question 2: ERCOT's natural gas share of net generation, 2026-11-15  47.74 percent
*   3. Prices and your bill, question 1: ERCOT hub average shape premium, 2026-09            1.12 USD/MWh (39.50 - 38.39)
*   4. Prices and your bill, question 4: the wholesale share of Oncor's 600 kWh bill         24.88 percent (bill 95.27 USD)
*   5. Storage and taxes, question 1: ERCOT's batteries out over in, 2026-11-03 to 11-14     73.06 percent
version 15
clear all
set more off

import delimited using "replication/problem_sets/live_rows.csv", rowrange(3) varnames(2) stringcols(_all) clear
destring value, replace force
gen day = substr(ts_utc, 1, 10)
tempfile all
save `all'

* ---- 1 and 2: the newest UTC day of 2026-11-15, ERCOT and CAISO (the replication finds the day; it is given here)
use `all', clear
keep if variable == "demand_mw" & day == "2026-11-15"
duplicates drop entity ts_utc, force
collapse (max) peak = value (count) n = value, by(entity)
assert n == 24
quietly summarize peak if entity == "eia930:ERCO"
local e = r(mean)
quietly summarize peak if entity == "eia930:CISO"
local c = r(mean)
local ratio = `e' / `c'
display "1. ERCOT's peak over CAISO's: " %9.4f `ratio'
assert abs(`ratio' - 2.08) <= 0.005

use `all', clear
keep if inlist(variable, "net_generation_mw", "net_generation_natural_gas_mw") & entity == "eia930:ERCO" & day == "2026-11-15"
duplicates drop variable ts_utc, force
collapse (sum) mwh = value (count) n = value, by(variable)
assert n == 24
quietly summarize mwh if variable == "net_generation_natural_gas_mw"
local gas = r(mean)
quietly summarize mwh if variable == "net_generation_mw"
local tot = r(mean)
local share = 100 * `gas' / `tot'
display "2. ERCOT's gas share: " %9.4f `share'
assert abs(`share' - 47.74) <= 0.005

* ---- 3 and 4: cost_of_power_monthly, ERCOT's hub average, 2026-09 (complete: rt_hours equal to hours_in_month)
use `all', clear
keep if entity == "ercot:HB_HUBAVG" & day == "2026-09-01" & inlist(variable, "rt_load_weighted", "rt_simple_mean", "rt_hours", "hours_in_month")
duplicates drop variable, force
quietly summarize value if variable == "rt_hours"
local h = r(mean)
quietly summarize value if variable == "hours_in_month"
assert `h' == r(mean)
quietly summarize value if variable == "rt_load_weighted"
local lw = r(mean)
quietly summarize value if variable == "rt_simple_mean"
local sm = r(mean)
display "3. Shape premium: " %9.4f `lw' - `sm'
assert abs((`lw' - `sm') - 1.12) <= 0.005

* Oncor's default bill (site/data/bill_rules.json, TX): 600 kWh at the retailer's 0.0907 USD/kWh, the customer and
* metering charges 1.48 and 2.58 USD, and the per-kWh charges and riders 0.036043 + 0.019046 + 0.001487 + 0.000086
* + 0.001027 + 0.003633 USD/kWh (two more are zero), each quoted from Oncor's tariff in the file
local bill = 600 * 0.0907 + 1.48 + 2.58 + 600 * (0.036043 + 0.019046 + 0.001487 + 0.000086 + 0.001027 + 0.003633)
local wh = 600 * `lw' / 1000
local bshare = 100 * `wh' / `bill'
display "4. Wholesale share of Oncor's bill: " %9.4f `bshare' "  (bill " %7.2f `bill' " USD)"
assert abs(`bshare' - 24.88) <= 0.005

* ---- 5: storage_daily_cycle, ERCOT, the seven latest days held (3 and 9 to 14 November 2026)
use `all', clear
keep if entity == "eia930:ERCO" & inlist(variable, "mwh_discharged", "mwh_charged")
duplicates drop variable ts_utc, force
keep if inlist(day, "2026-11-03", "2026-11-09", "2026-11-10", "2026-11-11", "2026-11-12", "2026-11-13", "2026-11-14")
collapse (sum) mwh = value (count) n = value, by(variable)
assert n == 7
quietly summarize mwh if variable == "mwh_discharged"
local out = r(mean)
quietly summarize mwh if variable == "mwh_charged"
local inn = r(mean)
local rt = 100 * `out' / `inn'
display "5. Out over in, seven days: " %9.4f `rt'
assert abs(`rt' - 73.06) <= 0.005
display "All five headline figures agree."
