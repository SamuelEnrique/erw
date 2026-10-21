* ERW findings hunt of 2026-10-20: pjm-queue-withdrawn-share-by-cohort. Reproduces the headline number from extract.csv.

* Expected headline value: 63.275490 percent of the cohort's MW (share of the MW that entered PJM's queue in the year and had withdrawn by the end of 2025 (cohorts at least six years old), PJM, period 2019).

* The comparison period 2010 is in the same file; its value is printed after the headline.

* The CSV's first four lines are comments; its fifth line holds the variable names.

clear all

import delimited "extract.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring period, replace force

destring value, replace force

destring withdrawn, replace force

replace period = . if period == -999

replace value = . if value == -999

replace withdrawn = . if withdrawn == -999

summarize value if period == 2019 & withdrawn == 1

scalar part = r(sum)

summarize value if period == 2019

scalar whole = r(sum)

display "headline (period == 2019), percent of the sum: " part / whole * 100

summarize value if period == 2010 & withdrawn == 1

scalar part = r(sum)

summarize value if period == 2010

scalar whole = r(sum)

display "comparison (period == 2010), percent of the sum: " part / whole * 100

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
