* ERW findings hunt of 2026-10-20: caiso-curtailment-this-year. Reproduces the headline number from extract.csv.

* Expected headline value: 5115404.251000 MWh (curtailed wind and solar output from 1 January to 30 September, MWh, CAISO, period 2026).

* The comparison period 2025 is in the same file; its value is printed after the headline.

* The CSV's first four lines are comments; its fifth line holds the variable names.

clear all

import delimited "extract.csv", varnames(5) rowrange(6) stringcols(_all) clear

destring period, replace force

destring curtailed_solar_mwh, replace force

destring curtailed_wind_mwh, replace force

destring curtailed, replace force

replace period = . if period == -999

replace curtailed_solar_mwh = . if curtailed_solar_mwh == -999

replace curtailed_wind_mwh = . if curtailed_wind_mwh == -999

replace curtailed = . if curtailed == -999

summarize curtailed if period == 2026

display "headline (period == 2026), sum: " r(sum)

summarize curtailed if period == 2025

display "comparison (period == 2025), sum: " r(sum)

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
