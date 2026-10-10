* ERW finding who_rescues_whom: WHO RESCUES WHOM. Reproduces the card's counts and flows from erw_2026_event_interchange_flips.csv.

clear all

import delimited "erw_2026_event_interchange_flips.csv", varnames(1) stringcols(_all) clear

destring baseline_net_mwh_day, replace force

destring event_net_mwh_day, replace force

destring swing_mwh_day, replace force

destring baseline_days, replace force

destring event_days, replace force

destring event_grid, replace force

replace baseline_net_mwh_day = . if baseline_net_mwh_day == -999

replace event_net_mwh_day = . if event_net_mwh_day == -999

replace swing_mwh_day = . if swing_mwh_day == -999

replace baseline_days = . if baseline_days == -999

replace event_days = . if event_days == -999

replace event_grid = . if event_grid == -999

gsort -swing_mwh_day

tab flip

foreach v in baseline_net_mwh_day event_net_mwh_day {
    tabstat `v', by(flip) statistics(mean min max n) format(%12.0f)
}

list name baseline_net_mwh_day event_net_mwh_day flip if flip != "same" & flip != "small", noobs
