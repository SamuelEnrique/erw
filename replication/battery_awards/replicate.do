* ERW, what Texas's batteries were awarded day-ahead (/cost-of-power/battery/awards): the five headline figures, rebuilt from the monthly rows.

* Method: docs/methods/battery_awards.md, sections 2, 3 and 4. Session 7505, chain 304, 16 November 2026.

* Input: monthly_rows.csv beside this file, the rows of the five public tables that the page reads (written by
* "python replication/battery_awards/replicate.py --tables <dir> --write"). Run this file from its own folder.

* This do-file has not been run: Stata is not installed on the machine that wrote it. "python replicate.py" computes the
* same figures from the same file (page_figures.csv, the column "ours", at the keys named below).

* Expected values, on the tables as retrieved on 5 October 2026 (the awards to 5 August 2026) and 21 October 2026 (the model):

*   1. July 2026, awarded day-ahead, USD per kW of the fleet: 0.68 (0.6815)                    key month|2026-07|total_kw

*   2. January to July 2026, the months held whole: awarded 6.53 (6.5282), the model 30.14 (30.1379), awards as a share of the model 22 percent (21.66)
*                                                                                              keys year|2026|awarded_whole_kw, model_whole_kw, share_of_model_pct

*   3. The gap of 23.61 (23.6097) in three parts: never offered 9.70 (9.7041), offered and not awarded 14.53 (14.5278), price -0.62 (-0.6222)
*                                                                                              keys offers|gap_kw, offers|part|never_kw, unawarded_kw, price_kw

*   4. February to July 2026: day-ahead awards 4.17 (4.1713), real-time deviations at the hub average's price 3.00 (2.9974), together 7.17 (7.1688), the model 18.81 (18.8081)
*                                                                                              keys rt|whole|dayahead_kw, deviation_kw, market_kw, model_kw

*   5. Resource-hours with a day-ahead energy award: 7.0 percent (127,958 of 1,833,357)          keys share|energy_award_pct, with_award, resource_hours

* The figures change when the data machine rebuilds the tables: after a new copy, compare with python replicate.py.

clear all

import delimited using "monthly_rows.csv", delimiter(comma) varnames(1) stringcols(1 2 3 4 6 7) clear

gen month = substr(ts_utc, 1, 7)

gen byte awards = table == "ercot_storage_dam_awards_monthly"

gen byte offers = table == "ercot_storage_dam_offers_monthly"

gen byte rt = table == "ercot_storage_rt_monthly"

gen byte model = table == "battery_stack_monthly"

* A month is held whole by a table when its days held equal the calendar's days. The model's rows are the 2-hour
* battery on the day-ahead schedule (the prefix dayahead_2h_).

bysort table month: egen dh = max(cond(variable == "days_held" | variable == "dayahead_2h_days_held", value, .))

bysort table month: egen dm = max(cond(variable == "days_in_month" | variable == "dayahead_2h_days_in_month", value, .))

gen byte whole = dh == dm & dh < .

bysort month: egen byte a_whole = max(awards & whole)

bysort month: egen byte o_whole = max(offers & whole)

bysort month: egen byte t_whole = max(rt & whole)

bysort month: egen byte m_whole = max(model & whole)

* 1. July 2026: the month's awards over the month's MW, USD per MW in the table, per kW on the page.

quietly summarize value if awards & variable == "revenue_total_usd_per_mw" & month == "2026-07"

display "1. July 2026, awarded day-ahead, USD per kW: " %6.4f r(sum) / 1000

* 2. The year 2026 over its whole months: the months' figures per kW added up, and the model's for the same months.

quietly summarize value if awards & variable == "revenue_total_usd_per_mw" & a_whole & substr(month, 1, 4) == "2026"

scalar awarded = r(sum) / 1000

scalar n_awarded = r(N)

quietly summarize value if model & variable == "dayahead_2h_revenue_total_usd_per_mw" & a_whole & m_whole & substr(month, 1, 4) == "2026"

scalar modelled = r(sum) / 1000

* The model stands beside the year only when it holds every one of those months whole.

assert r(N) == n_awarded

display "2. 2026, " n_awarded " months held whole: awarded " %7.4f awarded ", the model " %7.4f modelled ", share " %5.2f 100 * awarded / modelled " percent"

* 3. The gap in three parts, over the months the awards, the offers and the model all hold whole.

gen byte g = a_whole & o_whole & m_whole

quietly summarize value if model & variable == "dayahead_2h_revenue_total_usd_per_mw" & g

scalar g_model = r(sum) / 1000

quietly summarize value if awards & variable == "revenue_total_usd_per_mw" & g

scalar g_awards = r(sum) / 1000

scalar gap = g_model - g_awards

* Never offered: the model's figure times the share of limit-hours with no day-ahead offer of any kind (an allocation).

quietly summarize value if offers & variable == "limit_mwh_no_offer" & g

scalar no_offer = r(sum)

quietly summarize value if offers & variable == "limit_mwh" & g

scalar never = g_model * no_offer / r(sum)

* Price, energy only: the MWh sold per MW (each month over its own MW) times the difference between the model's net
* USD per MWh discharged and the awards' net USD per MWh sold.

bysort month: egen o_mw = max(cond(offers & variable == "mw", value, .))

gen sold_per_mw = value / o_mw if offers & variable == "energy_sold_mwh" & g

quietly summarize sold_per_mw

scalar sold = r(sum)

quietly summarize value if model & variable == "dayahead_2h_revenue_energy_usd_per_mw" & g

scalar e_model = r(sum)

quietly summarize value if model & variable == "dayahead_2h_discharged_mwh_per_mw" & g

scalar p_model = e_model / r(sum)

quietly summarize value if awards & variable == "revenue_energy_usd_per_mw" & g

scalar p_awards = r(sum) / sold

scalar price = sold * (p_model - p_awards) / 1000

display "3. the gap " %7.4f gap ": never offered " %7.4f never ", offered and not awarded " %7.4f gap - never - price ", price " %7.4f price

* 4. The real-time side, over the months the real-time table holds whole; real time at the hub average's price.

quietly summarize value if rt & variable == "revenue_da_usd_per_mw" & t_whole

scalar rt_da = r(sum) / 1000

quietly summarize value if rt & variable == "revenue_rt_deviation_hub_usd_per_mw" & t_whole

scalar rt_dev = r(sum) / 1000

quietly summarize value if rt & variable == "revenue_market_hub_usd_per_mw" & t_whole

scalar rt_both = r(sum) / 1000

quietly summarize value if model & variable == "dayahead_2h_revenue_total_usd_per_mw" & t_whole & m_whole

display "4. day-ahead awards " %7.4f rt_da ", real-time deviations " %7.4f rt_dev ", together " %7.4f rt_both ", the model " %7.4f r(sum) / 1000

* 5. The share of resource-hours that hold a day-ahead energy award, over every month held.

quietly summarize value if awards & variable == "resource_hours_energy_award"

scalar hit = r(sum)

quietly summarize value if awards & variable == "resource_hours"

display "5. resource-hours with a day-ahead energy award: " %4.1f 100 * hit / r(sum) " percent (" %9.0fc hit " of " %11.0fc r(sum) ")"
