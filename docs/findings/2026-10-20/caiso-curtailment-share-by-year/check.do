* ERW findings hunt of 2026-10-20: caiso-curtailment-share-by-year. Reproduces the headline number from extract.csv.

* Expected headline value: 4.532152 percent of output (share of the year's wind and solar output that was curtailed: curtailed over curtailed plus generated, CAISO, period 2025).

* The comparison period 2015 is in the same file; its value is printed after the headline.

* The CSV's first four lines are comments; its fifth line holds the variable names.

clear all

import delimited "extract.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring period, replace force

destring curtailed, replace force

destring generation, replace force

replace period = . if period == -999

replace curtailed = . if curtailed == -999

replace generation = . if generation == -999

summarize curtailed if period == 2025

scalar part = r(sum)

summarize generation if period == 2025

scalar other = r(sum)

display "headline (period == 2025), percent: " part / (part + other) * 100

summarize curtailed if period == 2015

scalar part = r(sum)

summarize generation if period == 2015

scalar other = r(sum)

display "comparison (period == 2015), percent: " part / (part + other) * 100

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
