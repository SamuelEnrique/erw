* ERW analysis impact_study: IMPACT OF AN EVENT ON A SERIES. Reproduces the card's means and its regression from the CSV.

* The CSV begins with four comment lines: the names are read from line 5 and the data from line 6.

clear all

import delimited "erw_2026_impact_event_control.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring t, replace force

destring after, replace force

destring in_window, replace force

destring series_value, replace force

destring control_value, replace force

destring diff, replace force

replace t = . if t == -999

replace after = . if after == -999

replace in_window = . if in_window == -999

replace series_value = . if series_value == -999

replace control_value = . if control_value == -999

replace diff = . if diff == -999

keep if in_window == 1 & diff < .

tabstat series_value control_value diff, by(after) statistics(mean n) format(%12.4f)

generate obs = _n

tsset obs

local lags = floor(4 * (_N / 100)^(2 / 9))

newey diff after, lag(`lags')
