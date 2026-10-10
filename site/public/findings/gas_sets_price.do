* ERW finding gas_sets_price: GAS SETS THE PRICE LESS OFTEN?. Reproduces the card's shares from erw_2026_gas_share_hours.csv.

clear all

import delimited "erw_2026_gas_share_hours.csv", varnames(1) stringcols(_all) clear

destring year, replace force

destring n_hours, replace force

destring share_below_hr6p5, replace force

destring share_below_hr7, replace force

destring share_below_hr8, replace force

replace year = . if year == -999

replace n_hours = . if n_hours == -999

replace share_below_hr6p5 = . if share_below_hr6p5 == -999

replace share_below_hr7 = . if share_below_hr7 == -999

replace share_below_hr8 = . if share_below_hr8 == -999

sort grid year

foreach v in share_below_hr6p5 share_below_hr7 share_below_hr8 {
    tabstat `v', by(grid) statistics(mean min max) format(%6.1f)
}

list grid year n_hours share_below_hr7, sepby(grid) noobs
