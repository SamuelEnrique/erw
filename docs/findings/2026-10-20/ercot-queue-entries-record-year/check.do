* ERW findings hunt of 2026-10-20: ercot-queue-entries-record-year. Reproduces the headline number from extract.csv.

* Expected headline value: 85405.180000 MW (MW of generation and storage that entered ERCOT's interconnection queue in the year, every status, as LBNL's Queued Up data file records it, ERCOT, period 2024).

* The comparison period 2023 is in the same file; its value is printed after the headline.

* The CSV's first four lines are comments; its fifth line holds the variable names.

clear all

import delimited "extract.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring period, replace force

destring value, replace force

replace period = . if period == -999

replace value = . if value == -999

summarize value if period == 2024

display "headline (period == 2024), sum: " r(sum)

summarize value if period == 2023

display "comparison (period == 2023), sum: " r(sum)

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
