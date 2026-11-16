* ERW, the severance tax calculator (/severance): the five headline figures of the page as it opens, rebuilt from the
* daily spot prices. Method: docs/methods/severance.md, "The tool as a reader meets it" (session 7502, chain 304).
*
* The file read is rows/spot_slim.csv: entity (wti_cushing or henry_hub), day (the trading day's place in its month),
* month (YYYY-MM) and value, the rows of the public table eia_fuel_spot_prices since January 2023. Write it with
*   python replication/severance/replicate.py --tables DIR --headline
* which also prints the same six lines, so the two can be set side by side.
*
* Not run: Stata is not on the machine that wrote this file. Its Python mirror printed these lines on 16 November 2026,
* for a page drawn that day (the latest complete month held was October 2026, 22 trading days of each series):
*
*   default oil price, WTI Cushing, mean of 2026-10 (USD per bbl): 102.07
*   default gas price, Henry Hub, mean of 2026-10 (USD per MMBtu): 2.99
*   Texas oil, 1,000 bbl, tax at the base rate (USD): 4695.22
*   Texas gas, 10,000 Mcf, tax at the base rate (USD): 2242.50
*   Louisiana oil, 1,000 bbl, well completed before July 1, 2025 (USD): 12758.75
*   New Mexico oil, 1,000 bbl, no district chosen (USD): 7287.80
*
* The page is drawn on a day; the month below is the latest complete month held on 16 November 2026. For another day,
* set the local `month' to the month before the latest month the file holds.

clear all
local month "2026-10"

import delimited using "rows/spot_slim.csv", varnames(1) stringcols(1 3) clear

* 1 and 2: the default prices, each the mean of the month's daily prices, rounded to the cent (half up)
quietly summarize value if entity == "wti_cushing" & month == "`month'"
scalar oil = floor(r(mean) * 100 + 0.5) / 100
display "default oil price, WTI Cushing, mean of `month' (USD per bbl): " %9.2f oil
quietly summarize value if entity == "henry_hub" & month == "`month'"
scalar gas = floor(r(mean) * 100 + 0.5) / 100
display "default gas price, Henry Hub, mean of `month' (USD per MMBtu): " %9.2f gas

* 3: Texas oil, 4.6 percent of market value or 4.6 cents a barrel, whichever is greater (Tax Code Sec. 202.052(a))
display "Texas oil, 1,000 bbl, tax at the base rate (USD): " %12.2f max(1000 * oil * 0.046, 1000 * 0.046)

* 4: Texas gas, 7.5 percent of market value (Sec. 201.052(a)); one Mcf priced as one MMBtu
display "Texas gas, 10,000 Mcf, tax at the base rate (USD): " %12.2f 10000 * gas * 0.075

* 5: Louisiana oil from a well completed before July 1, 2025, 12.5 percent of value (La. R.S. 47:633)
display "Louisiana oil, 1,000 bbl, well completed before July 1, 2025 (USD): " %12.2f 1000 * oil * 0.125

* and New Mexico oil with no district chosen: severance 3.75, emergency school 3.15 and conservation 0.24 percent
display "New Mexico oil, 1,000 bbl, no district chosen (USD): " %12.2f 1000 * oil * (0.0375 + 0.0315 + 0.0024)
