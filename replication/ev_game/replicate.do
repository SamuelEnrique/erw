* ERW, Should your family get an EV? (/play/ev): the five headline figures, the page as every visitor opens it (the
* United States, every default, the credit off). Method: docs/methods/ev_game.md, "The model" (session 7536, chain 304).
*
* The two prices are the rows of the ERW tables the game's file (site/data/ev_prices.json, built 17 November 2026) holds:
*   eia_retail_electricity_prices, eia:retail_price:US:RES, 2026-08-01: 181.6 USD/MWh
*   eia_regional_retail_fuel_prices, eia:EMM_EPMR_PTE_NUS_DPG, 2026-11-09: 3.995 USD a gallon
*
* Expected (python replication/ev_game/replicate.py --headline printed these on 17 November 2026 (session 7052, chain 370); Stata is not on the
* machine that wrote this file, so the do-file was not run):
*
*   1 a year of gasoline (USD): 2219.44
*   2 a year of electricity (USD): 844.44
*   3 saved a year with the EV (USD): 1375.00
*   4 payback (years): 3.6364
*   5 net present value, 8 years at 5 percent (USD): 3886.95
*
* The page shows them as $2,219, $844, $1,375, 3.6 years and $3,887.

clear all
scalar power = 181.6
scalar gas = 3.995
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

assert abs(gasyear - 2219.44) < 0.005
assert abs(evyear - 844.44) < 0.006
assert abs(save - 1375.00) < 0.006
assert abs(payback - 3.6364) < 0.00005
assert abs(npv - 3886.95) < 0.006
