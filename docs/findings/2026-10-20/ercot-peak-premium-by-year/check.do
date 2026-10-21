* ERW findings hunt of 2026-10-20: ercot-peak-premium-by-year. Reproduces the headline number from extract.csv.

* Expected headline value: 14.520000 USD per MWh (the year's median evening-peak real-time price minus its median midday price at the hub average (ercot_peak_premium_annual), ERCOT, the hub average, period 2025).

* The comparison period 2015 is in the same file; its value is printed after the headline.

* The CSV's first four lines are comments; its fifth line holds the variable names.

clear all

import delimited "extract.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring period, replace force

destring value, replace force

replace period = . if period == -999

replace value = . if value == -999

summarize value if period == 2025 & variable == "peak_minus_midday_median"

display "headline (period == 2025), the table's own value: " r(mean)

summarize value if period == 2015 & variable == "peak_minus_midday_median"

display "comparison (period == 2015), the table's own value: " r(mean)

* The series the chart draws: one row a period (series.csv, the same four comment lines).

import delimited "series.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring period, replace force

destring value, replace force

destring n_observations, replace force

destring complete, replace force

replace period = . if period == -999

replace value = . if value == -999

replace n_observations = . if n_observations == -999

replace complete = . if complete == -999

sort period

list period value n_observations complete, noobs
