* ERW findings hunt of 2026-10-20: ercot-battery-evening-share-by-month. Reproduces the headline number from extract.csv.

* Expected headline value: 85.832479 percent of discharge (share of the month's battery discharge (hourly net battery output above zero) delivered from 5 PM to 10 PM local, ERCOT, period 202609).

* The comparison period 202412 is in the same file; its value is printed after the headline.

* The CSV's first four lines are comments; its fifth line holds the variable names.

clear all

import delimited "extract.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring period, replace force

destring hour, replace force

destring value, replace force

destring evening, replace force

replace period = . if period == -999

replace hour = . if hour == -999

replace value = . if value == -999

replace evening = . if evening == -999

* period is the month as YYYYMM.

summarize value if period == 202609 & evening == 1

scalar part = r(sum)

summarize value if period == 202609

scalar whole = r(sum)

display "headline (period == 202609), percent of the sum: " part / whole * 100

summarize value if period == 202412 & evening == 1

scalar part = r(sum)

summarize value if period == 202412

scalar whole = r(sum)

display "comparison (period == 202412), percent of the sum: " part / whole * 100

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
