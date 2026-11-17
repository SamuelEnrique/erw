* ERW, Should your family get an EV? (/play/ev): the five headline figures, the page as every visitor opens it (the
* United States, every default, the credit off). Method: docs/methods/ev_game.md, "The model" (session 7536, chain 304).
*
* The two prices are the rows of the ERW tables the game's file (site/data/ev_prices.json, built 15 October 2026) holds:
*   eia_retail_electricity_prices, eia:retail_price:US:RES, 2026-07-01: 183.1 USD/MWh
*   eia_regional_retail_fuel_prices, eia:EMM_EPMR_PTE_NUS_DPG, 2026-10-05: 4.354 USD a gallon
*
* Expected (python replication/ev_game/replicate.py --headline printed these on 16 November 2026; Stata is not on the
* machine that wrote this file, so the do-file was not run):
*
*   1 a year of gasoline (USD): 2418.89
*   2 a year of electricity (USD): 851.41
*   3 saved a year with the EV (USD): 1567.47
*   4 payback (years): 3.1898
*   5 net present value, 8 years at 5 percent (USD): 5130.92
*
* The page shows them as $2,419, $851, $1,567, 3.2 years and $5,131.

clear all
scalar power = 183.1
scalar gas = 4.354
scalar miles = 15000
scalar mpg = 27
scalar kwhmi = 0.31
scalar gascar = 28600
scalar evcar = 33600
scalar credit = 0
scalar years = 8
scalar rate = 5

scalar gasyear = miles / mpg * gas
scalar evyear = miles * kwhmi * power / 1000
scalar save = gasyear - evyear
scalar extra = evcar - gascar - credit
scalar payback = extra / save
scalar pv = 0
forvalues t = 1/8 {
    scalar pv = pv + save / (1 + rate / 100)^`t'
}
scalar npv = pv - extra

display "1 a year of gasoline (USD): " %9.2f gasyear
display "2 a year of electricity (USD): " %9.2f evyear
display "3 saved a year with the EV (USD): " %9.2f save
display "4 payback (years): " %9.4f payback
display "5 net present value, 8 years at 5 percent (USD): " %9.2f npv

assert abs(gasyear - 2418.89) < 0.005
assert abs(evyear - 851.41) < 0.006
assert abs(save - 1567.47) < 0.006
assert abs(payback - 3.1898) < 0.00005
assert abs(npv - 5130.92) < 0.006
