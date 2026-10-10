* ERW finding peak_hour_moved: THE PEAK HOUR MOVED. Reproduces the card's shares and hours from erw_2026_peak_hour_solar.csv.

clear all

import delimited "erw_2026_peak_hour_solar.csv", varnames(1) stringcols(_all) clear

destring year, replace force

destring hour, replace force

destring share_days_pct, replace force

destring n_days, replace force

destring median_peak_hour, replace force

destring share_evening_pct, replace force

destring share_midday_pct, replace force

destring solar_mw_yearend, replace force

replace year = . if year == -999

replace hour = . if hour == -999

replace share_days_pct = . if share_days_pct == -999

replace n_days = . if n_days == -999

replace median_peak_hour = . if median_peak_hour == -999

replace share_evening_pct = . if share_evening_pct == -999

replace share_midday_pct = . if share_midday_pct == -999

replace solar_mw_yearend = . if solar_mw_yearend == -999

sort grid year hour

bysort grid year: egen modal_share = max(share_days_pct)

gen modal_hour = hour if share_days_pct == modal_share

foreach v in median_peak_hour share_evening_pct share_midday_pct solar_mw_yearend {
    tabstat `v' if hour == 0, by(grid) statistics(mean min max) format(%9.1f)
}

list grid year median_peak_hour share_evening_pct share_midday_pct solar_mw_yearend if hour == 0, sepby(grid) noobs
