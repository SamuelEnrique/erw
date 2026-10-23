* Energy Research Warehouse (ERW): the Stata package against the conformance file (session 1006).
* Written by packages/conformance/write_runners.py from conformance.json; needs erw installed and
* global ERW_LIVE_URL and global ERW_LIVE_KEY set. Prints one line a call and the count that pass.

version 16

local pass 0

erw fetch eia_fuel_spot_prices, entity(eia:henry_hub) start(2025-01-01) end(2026-01-01) backend(live) clear

capture confirm variable event_date

if _rc == 0 {
    local tvar event_date
}
else {
    capture confirm variable ts_utc
    local tvar = cond(_rc == 0, "ts_utc", "status_date")
}

quietly summarize `tvar'

local t0 = cond("`tvar'" == "status_date", date("2025-01-02", "YMD"), clock("2025-01-02 00:00:00", "YMDhms"))

local t1 = cond("`tvar'" == "status_date", date("2025-12-31", "YMD"), clock("2025-12-31 00:00:00", "YMDhms"))

local ok = (_N == 247) & (r(min) == `t0') & (r(max) == `t1')

display as text cond(`ok', "ok   ", "FAIL ") + "01 fetch eia_fuel_spot_prices"

local pass = `pass' + `ok'

erw fetch eia_fuel_spot_prices, entity(eia:wti_cushing eia:brent) start(2026-09-01) end(2026-10-01) backend(live) clear

capture confirm variable event_date

if _rc == 0 {
    local tvar event_date
}
else {
    capture confirm variable ts_utc
    local tvar = cond(_rc == 0, "ts_utc", "status_date")
}

quietly summarize `tvar'

local t0 = cond("`tvar'" == "status_date", date("2026-09-01", "YMD"), clock("2026-09-01 00:00:00", "YMDhms"))

local t1 = cond("`tvar'" == "status_date", date("2026-09-30", "YMD"), clock("2026-09-30 00:00:00", "YMDhms"))

local ok = (_N == 44) & (r(min) == `t0') & (r(max) == `t1')

display as text cond(`ok', "ok   ", "FAIL ") + "02 fetch eia_fuel_spot_prices"

local pass = `pass' + `ok'

erw fetch carbon_intensity_monthly, entity(eia930:CISO) variable(intensity_demand) backend(live) clear

capture confirm variable event_date

if _rc == 0 {
    local tvar event_date
}
else {
    capture confirm variable ts_utc
    local tvar = cond(_rc == 0, "ts_utc", "status_date")
}

quietly summarize `tvar'

local t0 = cond("`tvar'" == "status_date", date("2018-08-01", "YMD"), clock("2018-08-01 00:00:00", "YMDhms"))

local t1 = cond("`tvar'" == "status_date", date("2026-09-01", "YMD"), clock("2026-09-01 00:00:00", "YMDhms"))

local ok = (_N == 71) & (r(min) == `t0') & (r(max) == `t1')

display as text cond(`ok', "ok   ", "FAIL ") + "03 fetch carbon_intensity_monthly"

local pass = `pass' + `ok'

erw fetch ercot_peak_premium_annual, entity(HB_HUBAVG) end(2026-01-01) backend(live) clear

capture confirm variable event_date

if _rc == 0 {
    local tvar event_date
}
else {
    capture confirm variable ts_utc
    local tvar = cond(_rc == 0, "ts_utc", "status_date")
}

quietly summarize `tvar'

local t0 = cond("`tvar'" == "status_date", date("2015-01-01", "YMD"), clock("2015-01-01 00:00:00", "YMDhms"))

local t1 = cond("`tvar'" == "status_date", date("2025-01-01", "YMD"), clock("2025-01-01 00:00:00", "YMDhms"))

local ok = (_N == 308) & (r(min) == `t0') & (r(max) == `t1')

display as text cond(`ok', "ok   ", "FAIL ") + "04 fetch ercot_peak_premium_annual"

local pass = `pass' + `ok'

erw fetch caiso_grid_emergencies, start(2022-09-01) end(2022-09-15) backend(live) clear

capture confirm variable event_date

if _rc == 0 {
    local tvar event_date
}
else {
    capture confirm variable ts_utc
    local tvar = cond(_rc == 0, "ts_utc", "status_date")
}

quietly summarize `tvar'

local t0 = cond("`tvar'" == "status_date", date("2022-09-01", "YMD"), clock("2022-09-01 00:00:00", "YMDhms"))

local t1 = cond("`tvar'" == "status_date", date("2022-09-09", "YMD"), clock("2022-09-09 00:00:00", "YMDhms"))

local ok = (_N == 40) & (r(min) == `t0') & (r(max) == `t1')

display as text cond(`ok', "ok   ", "FAIL ") + "05 fetch caiso_grid_emergencies"

local pass = `pass' + `ok'

erw fetch eia860m_retired_generators, variable(generator) backend(live) clear

capture confirm variable event_date

if _rc == 0 {
    local tvar event_date
}
else {
    capture confirm variable ts_utc
    local tvar = cond(_rc == 0, "ts_utc", "status_date")
}

quietly summarize `tvar'

local t0 = cond("`tvar'" == "status_date", date("2025-01-01", "YMD"), clock("2025-01-01 00:00:00", "YMDhms"))

local t1 = cond("`tvar'" == "status_date", date("2026-08-01", "YMD"), clock("2026-08-01 00:00:00", "YMDhms"))

local ok = (_N == 249) & (r(min) == `t0') & (r(max) == `t1')

display as text cond(`ok', "ok   ", "FAIL ") + "06 fetch eia860m_retired_generators"

local pass = `pass' + `ok'

erw fetch eia930_all_demand, entity(eia930:ERCO) variable(demand_mw) start(2026-10-18) end(2026-10-19) backend(live) clear

capture confirm variable event_date

if _rc == 0 {
    local tvar event_date
}
else {
    capture confirm variable ts_utc
    local tvar = cond(_rc == 0, "ts_utc", "status_date")
}

quietly summarize `tvar'

local t0 = cond("`tvar'" == "status_date", date("2026-10-18", "YMD"), clock("2026-10-18 00:00:00", "YMDhms"))

local t1 = cond("`tvar'" == "status_date", date("2026-10-18", "YMD"), clock("2026-10-18 23:00:00", "YMDhms"))

local ok = (_N == 24) & (r(min) == `t0') & (r(max) == `t1')

display as text cond(`ok', "ok   ", "FAIL ") + "07 fetch eia930_all_demand"

local pass = `pass' + `ok'

erw fetch state_generation_mix_monthly, entity(eia:TX) start(2025-01-01) end(2026-01-01) backend(live) clear

capture confirm variable event_date

if _rc == 0 {
    local tvar event_date
}
else {
    capture confirm variable ts_utc
    local tvar = cond(_rc == 0, "ts_utc", "status_date")
}

quietly summarize `tvar'

local t0 = cond("`tvar'" == "status_date", date("2025-01-01", "YMD"), clock("2025-01-01 00:00:00", "YMDhms"))

local t1 = cond("`tvar'" == "status_date", date("2025-12-01", "YMD"), clock("2025-12-01 00:00:00", "YMDhms"))

local ok = (_N == 98) & (r(min) == `t0') & (r(max) == `t1')

display as text cond(`ok', "ok   ", "FAIL ") + "08 fetch state_generation_mix_monthly"

local pass = `pass' + `ok'

erw fetch iso_curtailment_monthly, start(2025-01-01) end(2026-01-01) backend(live) clear

capture confirm variable event_date

if _rc == 0 {
    local tvar event_date
}
else {
    capture confirm variable ts_utc
    local tvar = cond(_rc == 0, "ts_utc", "status_date")
}

quietly summarize `tvar'

local t0 = cond("`tvar'" == "status_date", date("2025-01-01", "YMD"), clock("2025-01-01 00:00:00", "YMDhms"))

local t1 = cond("`tvar'" == "status_date", date("2025-12-01", "YMD"), clock("2025-12-01 00:00:00", "YMDhms"))

local ok = (_N == 312) & (r(min) == `t0') & (r(max) == `t1')

display as text cond(`ok', "ok   ", "FAIL ") + "09 fetch iso_curtailment_monthly"

local pass = `pass' + `ok'

erw fetch carbon_intensity_daily, entity(eia930:ERCO) start(2026-10-01) end(2026-10-08) backend(live) clear

capture confirm variable event_date

if _rc == 0 {
    local tvar event_date
}
else {
    capture confirm variable ts_utc
    local tvar = cond(_rc == 0, "ts_utc", "status_date")
}

quietly summarize `tvar'

local t0 = cond("`tvar'" == "status_date", date("2026-10-01", "YMD"), clock("2026-10-01 00:00:00", "YMDhms"))

local t1 = cond("`tvar'" == "status_date", date("2026-10-07", "YMD"), clock("2026-10-07 00:00:00", "YMDhms"))

local ok = (_N == 14) & (r(min) == `t0') & (r(max) == `t1')

display as text cond(`ok', "ok   ", "FAIL ") + "10 fetch carbon_intensity_daily"

local pass = `pass' + `ok'

erw cite eia_fuel_spot_prices

local ok = strpos(`"`r(cite)'"', `"U.S. Energy Information Administration (EIA). Natural Gas Spot and Futures Prices (NYMEX), daily; Spot Prices for Crude Oil and Petroleum Products. Via the Energy Research Warehouse (ERW), table "') == 1

display as text cond(`ok', "ok   ", "FAIL ") + "11 cite eia_fuel_spot_prices"

local pass = `pass' + `ok'

erw cite carbon_intensity_monthly

local ok = strpos(`"`r(cite)'"', `"Energy Research Warehouse (ERW), derived. California's carbon intensity of generation from the join of 16 December 2025 (docs/methods/eia930_caiso_break.md); Carbon intensity per balancing authority (docs/methods/emissions.md). Via the Energy Research Warehouse (ERW), table "') == 1

display as text cond(`ok', "ok   ", "FAIL ") + "12 cite carbon_intensity_monthly"

local pass = `pass' + `ok'

erw cite eia860m_retired_generators

local ok = strpos(`"`r(cite)'"', `"U.S. Energy Information Administration (EIA). Form EIA-860M, Monthly Update to the Annual Electric Generator Report. Via the Energy Research Warehouse (ERW), table "') == 1

display as text cond(`ok', "ok   ", "FAIL ") + "13 cite eia860m_retired_generators"

local pass = `pass' + `ok'

erw cite caiso_grid_emergencies

local ok = strpos(`"`r(cite)'"', `"California Independent System Operator (CAISO). Grid Emergencies History Report (1998 to present). Via the Energy Research Warehouse (ERW), table "') == 1

display as text cond(`ok', "ok   ", "FAIL ") + "14 cite caiso_grid_emergencies"

local pass = `pass' + `ok'

erw license eia_fuel_spot_prices

local ok = ("`r(verdict)'" == "public") & (`"`r(words)'"' == `"Public: every publisher's terms the ERW read allow it to be shared, with credit to the publisher."')

display as text cond(`ok', "ok   ", "FAIL ") + "15 license eia_fuel_spot_prices"

local pass = `pass' + `ok'

erw license iso_rtm_hub_prices

local ok = ("`r(verdict)'" == "unsettled") & (`"`r(words)'"' == `"MISO's terms ask for written permission, which the ERW has not recorded (license needed since 2026-10-21)."')

display as text cond(`ok', "ok   ", "FAIL ") + "16 license iso_rtm_hub_prices"

local pass = `pass' + `ok'

erw license pjm_rpm_capacity_prices

local ok = ("`r(verdict)'" == "internal") & (`"`r(words)'"' == `"The ERW holds it for its own use only (needs a paid license); it is never redistributed."')

display as text cond(`ok', "ok   ", "FAIL ") + "17 license pjm_rpm_capacity_prices"

local pass = `pass' + `ok'

capture erw fetch iso_rtm_hub_prices, start(2026-10-20) backend(live) clear

local ok = (_rc == 498)

display as text cond(`ok', "ok   ", "FAIL ") + "18 refusal iso_rtm_hub_prices"

local pass = `pass' + `ok'

erw standard eia860m_retired_generators, backend(live) clear

local ok = ("`r(shape)'" == "entities") & ("`r(key)'" == "entity_id")

display as text cond(`ok', "ok   ", "FAIL ") + "19 standard eia860m_retired_generators"

local pass = `pass' + `ok'

erw tables, clear

quietly count if table == "eia_fuel_spot_prices" & shape == "series" & verdict == "public" & in_live == "yes"

local ok = (r(N) == 1) & (_N >= 299)

display as text cond(`ok', "ok   ", "FAIL ") + "20 tables eia_fuel_spot_prices"

local pass = `pass' + `ok'

display as text "`pass' of 20 pass"
