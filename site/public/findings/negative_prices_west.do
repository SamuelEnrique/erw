* ERW finding negative_prices_west: NEGATIVE PRICES MARCH WEST. Reproduces the card's counts from erw_2026_negative_hours_hubs.csv.

clear all

import delimited "erw_2026_negative_hours_hubs.csv", varnames(1) stringcols(_all) clear

destring year, replace force

destring n_hours, replace force

destring negative_hours, replace force

destring share_pct, replace force

destring negative_intervals, replace force

destring n_intervals, replace force

replace year = . if year == -999

replace n_hours = . if n_hours == -999

replace negative_hours = . if negative_hours == -999

replace share_pct = . if share_pct == -999

replace negative_intervals = . if negative_intervals == -999

replace n_intervals = . if n_intervals == -999

sort hub year

foreach v in negative_hours share_pct {
    tabstat `v', by(hub) statistics(mean min max) format(%9.1f)
}

list hub year n_hours negative_hours share_pct, sepby(hub) noobs
