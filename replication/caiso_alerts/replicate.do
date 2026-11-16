* ERW, the Flex Alert scorecard (/grid/caiso/alerts): the five headline figures, rebuilt from the public rows.

* Method: docs/methods/caiso_alerts.md and docs/methods/flex_alert_scorecard.md, sections 3, 5, 6 and 7.
* Session 7532, chain 304, 16 November 2026.

* Input: public_rows.csv beside this file, the rows of flex_alert_effects, flex_alert_model (without its coefficients) and
* caiso_dam_alert_day_hub_prices (the alert days' hours) that the page reads, written by
* "python replication/caiso_alerts/replicate.py --tables <dir> --figures <page_figures.json> --write". Run this file from
* its own folder.

* This do-file has not been run: Stata is not installed on the machine that wrote it. "python replicate.py" computes the
* same figures from the same file (page_figures.csv, the column "ours", at the keys named below).

* Expected values, on the tables as retrieved on 2 October 2026 (the scorecard) and 13 October 2026 (the notices):

*   1. Alert days and alert hours, pooled: 38 days, 204 hours            keys pooled_days, pooled_hours

*   2. The pooled cut: -503.18 MW (-503.1849), -102,649.73 MWh (-102649.7289), -1.20 percent (-1.2012) of predicted
*      demand (negative: demand ran above the model)                       keys pooled_reduction_mw, _mwh, _pct

*   3. Alert days by year: 2018 2, 2019 2, 2020 11, 2021 8, 2022 11, 2023 3, 2024 1;
*      alert hours by year: 8, 12, 71, 36, 58, 12, 7                       keys year_days, year_hours

*   4. The value at the day-ahead price: USD -5.47 million (-5,469,360.66) over 19 alert hours with both hub prices
*                                                                          keys pooled_value_usd, pooled_value_hours

*   5. The model's check: 128 held-out hot days, bias -239.34 MW (-239.3376); 34 of the 38 alert days at least as hot as
*      the held-out threshold of 87.01 F (87.008)                          keys oos_days, oos_bias_mw, alert_days_hotter_than_threshold

* The figures change when the data machine rebuilds the tables: after a new copy, compare with python replicate.py.

clear all

import delimited using "public_rows.csv", delimiter(comma) varnames(1) stringcols(1 2 3 4 6 7) clear
save rows, replace

* ---- the hourly rows of the alert days: one row an hour, actual, predicted and the alert mark
keep if table == "flex_alert_effects" & freq == "PT1H" & inlist(variable, "actual_mw", "predicted_mw", "alert_hour")
keep ts_utc variable value
reshape wide value, i(ts_utc) j(variable) string
rename valueactual_mw actual
rename valuepredicted_mw predicted
rename valuealert_hour alert
keep if alert == 1
* the Pacific day (daylight time, UTC-7) of each hour
gen double t = clock(substr(ts_utc, 1, 19), "YMD#hms") - 7 * 3600000
gen day = dofc(t)
format day %td
gen cut = predicted - actual
save hours, replace

* ---- 1 and 2: pooled
quietly count
display "1. alert hours: " r(N)
quietly levelsof day
display "1. alert days: " r(r)
quietly summarize cut
display "2. pooled cut, MW: " %12.4f r(mean) "   MWh: " %14.4f r(sum)
quietly summarize predicted
local pred = r(sum)
quietly summarize cut
display "2. percent of predicted: " %9.4f 100 * r(sum) / `pred'

* ---- 3: by year
gen year = year(day)
preserve
bysort year day: keep if _n == 1
display "3. alert days by year:"
tabulate year
restore
display "3. alert hours by year:"
tabulate year

* ---- 4: the value, each alert hour's cut times the mean of the two hubs' day-ahead prices (an hour only with both)
use rows, clear
keep if table == "caiso_dam_alert_day_hub_prices" & variable == "lmp_dam"
gen hub = cond(entity == "caiso:TH_SP15_GEN-APND", "sp15", cond(entity == "caiso:TH_NP15_GEN-APND", "np15", ""))
keep if hub != ""
keep ts_utc hub value
reshape wide value, i(ts_utc) j(hub) string
keep if !missing(valuesp15) & !missing(valuenp15)
gen double price = (valuesp15 + valuenp15) / 2
merge 1:1 ts_utc using hours, keep(match) nogenerate
gen double usd = cut * price
quietly summarize usd
display "4. value, USD: " %16.2f r(sum) "   over " r(N) " alert hours"

* ---- 5: the model's check, from its held-out rows
use rows, clear
keep if table == "flex_alert_model" & inlist(variable, "heldout_error_mw", "heldout_temp_max_f")
keep ts_utc variable value
reshape wide value, i(ts_utc) j(variable) string
quietly summarize valueheldout_error_mw
display "5. held-out days: " r(N) "   bias, MW: " %10.4f r(mean)
quietly summarize valueheldout_temp_max_f
local thr = r(min)
display "5. threshold, F (the coolest held-out day): " %8.3f `thr'
use rows, clear
keep if table == "flex_alert_effects" & freq == "P1D" & variable == "temp_max_f"
quietly count if value >= `thr'
display "5. alert days at least as hot: " r(N) " of " _N

erase rows.dta
erase hours.dta
