* ERW findings hunt of 2026-10-20: ercot-battery-discharge-by-month. Reproduces the headline number from extract.csv.

* Expected headline value: 770026.000000 MWh (the month's battery discharge, MWh, summed from the daily cycle table, ERCOT, period 202609).

* The comparison period 202412 is in the same file; its value is printed after the headline.

* The CSV's first four lines are comments; its fifth line holds the variable names.

clear all

import delimited "extract.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring period, replace force

destring value, replace force

replace period = . if period == -999

replace value = . if value == -999

* period is the month as YYYYMM.

summarize value if period == 202609

display "headline (period == 202609), sum: " r(sum)

summarize value if period == 202412

display "comparison (period == 202412), sum: " r(sum)

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
