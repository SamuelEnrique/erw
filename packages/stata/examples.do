* Energy Research Warehouse (ERW): two of the site's charts, reproduced in Stata with erw (session 1004).
* The figures each chart shows are displayed, so they can be checked against the page at the same time.
* Needs: erw installed (README.md), global ERW_LIVE_URL and global ERW_LIVE_KEY set.

version 16

clear all

* 1. The Grid tool, ERCOT (/grid/ercot): hourly demand, the last nine days (site/lib/grid.ts reads the same table,
* entity and variable).
local since = string(date(c(current_date), "DMY") - 9, "%tdCCYY-NN-DD")

erw fetch eia930_all_demand, entity(eia930:ERCO) variable(demand_mw) start(`since') clear

sort ts_utc

summarize value

display as text "ERCOT demand, last hour " %tc ts_utc[_N] " UTC: " %9.0fc value[_N] " MW; the window's peak " %9.0fc r(max) " MW"

twoway line value ts_utc, xtitle("Hour (UTC)") ytitle("MW") title("ERCOT demand, last nine days") note("Source: `: char _dta[erw_version]'")

graph export "erw_ercot_demand.png", replace width(1280)

* 2. The price board (/board): Henry Hub natural gas spot price, the last twelve months (eia_fuel_spot_prices).
local since = string(date(c(current_date), "DMY") - 365, "%tdCCYY-NN-DD")

erw fetch eia_fuel_spot_prices, entity(eia:henry_hub) start(`since') clear

sort ts_utc

display as text "Henry Hub, latest " %tc ts_utc[_N] ": USD " %6.2f value[_N] " per MMBtu"

twoway line value ts_utc, xtitle("Day (UTC)") ytitle("USD per MMBtu") title("Henry Hub spot price, last twelve months") note("Source: `: char _dta[erw_version]'")

graph export "erw_henry_hub.png", replace width(1280)

erw cite eia_fuel_spot_prices
