* ERW findings hunt of 2026-10-20: ercot-hb_west-negative-hours-this-year. Reproduces the headline number from extract.csv.

* Expected headline value: 15.948655 percent of intervals (share of the 15-minute intervals from 1 January to 25 August with a real-time price below zero at the West hub, ERCOT, the West hub, period 2026).

* The comparison period 2022 is in the same file; its value is printed after the headline.

* The CSV's first four lines are comments; its fifth line holds the variable names.

clear all

import delimited "extract.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring period, replace force

destring value, replace force

replace period = . if period == -999

replace value = . if value == -999

count if period == 2026 & value < 0

scalar part = r(N)

count if period == 2026

scalar whole = r(N)

display "headline (period == 2026), percent of rows: " part / whole * 100

count if period == 2022 & value < 0

scalar part = r(N)

count if period == 2022

scalar whole = r(N)

display "comparison (period == 2022), percent of rows: " part / whole * 100

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
