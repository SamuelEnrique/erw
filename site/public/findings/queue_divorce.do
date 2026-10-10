* ERW finding queue_divorce: TILL QUEUE DO US PART. Reproduces the card's shares from erw_2026_queue_outcomes_technology.csv.

clear all

import delimited "erw_2026_queue_outcomes_technology.csv", varnames(1) stringcols(_all) clear

destring projects, replace force

destring requested_gw, replace force

destring withdrawn_gw, replace force

destring operational_gw, replace force

destring active_gw, replace force

destring suspended_gw, replace force

destring unknown_gw, replace force

destring withdrawn_pct, replace force

destring operational_pct, replace force

destring active_pct, replace force

destring suspended_pct, replace force

destring unknown_pct, replace force

destring cdc_marriage_rate_per_1000, replace force

destring cdc_divorce_rate_per_1000, replace force

replace projects = . if projects == -999

replace requested_gw = . if requested_gw == -999

replace withdrawn_gw = . if withdrawn_gw == -999

replace operational_gw = . if operational_gw == -999

replace active_gw = . if active_gw == -999

replace suspended_gw = . if suspended_gw == -999

replace unknown_gw = . if unknown_gw == -999

replace withdrawn_pct = . if withdrawn_pct == -999

replace operational_pct = . if operational_pct == -999

replace active_pct = . if active_pct == -999

replace suspended_pct = . if suspended_pct == -999

replace unknown_pct = . if unknown_pct == -999

replace cdc_marriage_rate_per_1000 = . if cdc_marriage_rate_per_1000 == -999

replace cdc_divorce_rate_per_1000 = . if cdc_divorce_rate_per_1000 == -999

gen cdc_ratio_pct = cdc_divorce_rate_per_1000 / cdc_marriage_rate_per_1000 * 100

gen queue_over_cdc = withdrawn_pct / cdc_ratio_pct

list technology requested_gw withdrawn_pct operational_pct active_pct suspended_pct queue_over_cdc, noobs
