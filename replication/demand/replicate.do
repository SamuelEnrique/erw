* ERW, demand growth since 2019 (/demand): five figures of ERCOT, rebuilt from EIA-930's ERCOT workbook (session 7014,
* chain 301). Method: docs/methods/demand_growth.md. The full replication of every figure of the page's file is
* replicate.py beside this file (24,241 of 24,245 equal on the workbooks of 2 November 2026; the four others are the
* Lower 48's September and October 2026, which EIA was still filling in: they move with each day's workbook).
*
* This do-file has not been run: Stata is not installed on the machine that wrote it. Samuel runs it.
* Input: ERCO.xlsx from https://www.eia.gov/electricity/gridmonitor/knownissues/xls/ERCO.xlsx, sheet "Published Hourly
* Data". ERCOT has no hour apart from its neighbours since 2019, so an hour is used when its adjusted demand is held and
* above zero. A row's local date is the local date of the hour's start (EIA's hour 24 ends at the next midnight).
* Expected values (site/data/demand_growth.json built 6 November 2026):
*   1. ERCOT 2019 average demand, MW:          43,797.6
*   2. ERCOT 2025 average demand, MW:          55,717.2
*   3. ERCOT 2025 hours used:                   8,736   (EIA's file is blank for 24 hours of December 2025)
*   4. ERCOT 2025 peak hour, MW:               83,597   (the hour from 2025-08-18 22:00 UTC)
*   5. growth of the average since 2019, %:     27.22

version 16
clear all
import excel using "ERCO.xlsx", sheet("Published Hourly Data") firstrow clear
gen y = year(Localdate)
destring Adjusteddemand, replace force
keep if inlist(y, 2019, 2025) & Adjusteddemand < . & Adjusteddemand > 0
quietly summarize Adjusteddemand if y == 2019
local a19 = r(mean)
display "1. 2019 average: " %9.1f `a19'
quietly summarize Adjusteddemand if y == 2025
display "2. 2025 average: " %9.1f r(mean)
display "3. 2025 hours used: " r(N)
display "4. 2025 peak hour: " r(max)
display "5. growth since 2019, percent: " %6.2f (r(mean) / `a19' - 1) * 100
