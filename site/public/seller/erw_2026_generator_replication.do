* ERW, What a generator earns (/cost-of-power/seller): the headline numbers of the default case, rebuilt from erw_2026_generator_hourly.csv.

* The default case: ERCOT, solar, 100 MW, priced at the hub average (HB_HUBAVG) in real time. Method: docs/methods/cost_of_power.md.

* This do-file has not been run: Stata is not installed on the machine that wrote it. erw_2026_generator_replication.py follows it step for step and prints the same lines.

* Expected values (session 304, 19 October 2026): what this file displays at the page's defaults, equal to the page value by value;

* the Python mirror beside it printed these lines on 19 October 2026:

*   revenue, last twelve months, USD per kW: 59.85

*   long-run average of the last three full years, USD per kW a year: 102.24

*   long-run average of every full year held, USD per kW a year: 130.80

*   hours used for the capture price: 8736

*   price received, weighted by generation, USD per MWh: 23.27

*   flat average over the same hours, USD per MWh: 32.17

*   capture rate, percent of the flat average: 72

*   annual debt payments, USD: 7,078,769

*   debt coverage, last twelve months, times: 0.67

*   energy sold, last twelve months, MWh per MW: 2,580

*   contract price at which coverage reaches 1.25 times, USD per MWh: 39.14

*   NPV at the hurdle rate, USD million for 100 MW: -76.66

*   breakeven PPA price, the whole of the energy for the PPA term, USD per MWh: 58.36

*   months held: 99, 2018-07 to 2026-09

*   worst month 1: 2024-02, USD for 100 MW: 139,298.97

* The file has 16 comment lines; the column names are on line 17 and the hours start on line 18.

clear all

import delimited using "erw_2026_generator_hourly.csv", varnames(17) rowrange(18) stringcols(_all) clear

destring price_usd_mwh, replace force

destring solar_mwh, replace force

destring nameplate_mw, replace force

destring in_last_twelve, replace force

replace solar_mwh = . if solar_mwh == -99999

* The reader's inputs at their defaults: size, fixed O&M, and the debt (Lazard LCOE+ June 2025, solar: 1375 USD per kW, 60 percent debt at 8 percent over 35 years).

scalar s_mw = 100

scalar s_fom_usd_kw_year = 12.5

scalar s_capex_usd_kw = 1375

scalar s_debt_share = 0.6

scalar s_debt_rate = 0.08

scalar s_debt_years = 35

* Session 264: scenario A's other defaults on the page (site/lib/seller/finance.ts): the hurdle rate, 12 percent (Lazard's cost of equity, the owner's ruling of 12 October 2026); the project life, 35 years; the PPA term, the eleventh assumption, the asset's life, 35 years; no degradation.

scalar s_hurdle = 0.12

scalar s_life_years = 35

scalar s_ppa_years = 35

scalar s_debt_service = round(s_capex_usd_kw * 1000 * s_debt_share * s_debt_rate / (1 - (1 + s_debt_rate)^(-s_debt_years)) * s_mw)

* The model, hour by hour: output per MW of nameplate is the fleet's generation over the nameplate installed that month; revenue is price times output.

gen double output_mwh_per_mw = solar_mwh / nameplate_mw if nameplate_mw > 0

gen model_hour = output_mwh_per_mw < . & price_usd_mwh < .

gen double revenue_usd_per_mw = price_usd_mwh * output_mwh_per_mw

* The capture price, hour by hour: the same price and the same generation, from January 2019; generation below zero weighs nothing.

gen ym = monthly(local_month, "YM")

format ym %tm

gen capture_hour = solar_mwh < . & price_usd_mwh < . & ym >= tm(2019m1)

gen double capture_price_sum = price_usd_mwh if capture_hour == 1

gen double capture_mwh = max(0, solar_mwh) if capture_hour == 1

gen double capture_usd = price_usd_mwh * capture_mwh

* One row a local month: the sums of its hours.

collapse (sum) revenue_usd_per_mw energy_mwh_per_mw = output_mwh_per_mw hours = model_hour capture_hours = capture_hour capture_price_sum capture_mwh capture_usd (max) in_last_twelve, by(ym)

* The hours in a local month: 24 a day, one fewer in March and one more in November (daylight saving).

gen hours_in_month = 24 * day(dofm(ym + 1) - 1) - (month(dofm(ym)) == 3) + (month(dofm(ym)) == 11)

* A month of the model is held with at least 90 percent of its hours; a month of the capture price counts with at least 95 percent.

gen held = hours / hours_in_month >= 0.9 - 1e-9 & energy_mwh_per_mw > 0

gen capture_counted = capture_hours >= 0.95 * hours_in_month - 1e-9

* The page reads each month from its snapshot, which holds four decimals; the same rounding here, so that every dollar agrees.

replace revenue_usd_per_mw = round(revenue_usd_per_mw * 10000) / 10000

gen double revenue_usd = revenue_usd_per_mw * s_mw

gen double cfads_usd = revenue_usd - s_fom_usd_kw_year * 1000 * s_mw / 12

gen double cover = cfads_usd / (s_debt_service / 12)

gen calendar_year = year(dofm(ym))

* Revenue, last twelve months: the first headline number and the summary sentence.

quietly summarize ym if in_last_twelve == 1

display "the last twelve months: " %tmCCYY-NN r(min) " to " %tmCCYY-NN r(max)

quietly summarize revenue_usd_per_mw if in_last_twelve == 1 & held == 1

scalar s_l12_usd_per_mw = r(sum)

display "months in the last twelve that are held: " r(N)

display "revenue, last twelve months, USD per kW: " %9.2f s_l12_usd_per_mw / 1000

* The long-run averages: a year is full when all twelve of its months are held.

egen months_held_in_year = total(held), by(calendar_year)

gen full_year = months_held_in_year == 12

quietly summarize calendar_year if full_year == 1

scalar s_first_full_year = r(min)

scalar s_last_full_year = r(max)

scalar s_full_years = r(N) / 12

scalar s_three_from = s_last_full_year - 2

quietly summarize revenue_usd_per_mw if full_year == 1 & calendar_year >= s_three_from

display "the last three full years: " s_three_from " to " s_last_full_year ", months held in them: " r(N)

display "long-run average of the last three full years, USD per kW a year: " %9.2f r(sum) / 3 / 1000

quietly summarize revenue_usd_per_mw if full_year == 1

display "full years held: " s_full_years ", " s_first_full_year " to " s_last_full_year

display "long-run average of every full year held, USD per kW a year: " %9.2f r(sum) / s_full_years / 1000

* The price received at the hub average: the second headline number, over the counted months of the last twelve.

quietly count if in_last_twelve == 1 & capture_counted == 1

display "months in the last twelve that count for the capture price: " r(N)

foreach v in capture_usd capture_mwh capture_price_sum capture_hours {
    quietly summarize `v' if in_last_twelve == 1 & capture_counted == 1
    scalar s_`v' = r(sum)
}

scalar s_price_received = s_capture_usd / s_capture_mwh

scalar s_flat_average = s_capture_price_sum / s_capture_hours

display "hours used for the capture price: " s_capture_hours

display "price received, weighted by generation, USD per MWh: " %9.2f s_price_received

display "flat average over the same hours, USD per MWh: " %9.2f s_flat_average

display "difference, USD per MWh: " %9.2f s_price_received - s_flat_average

display "difference, percent of the flat average: " %9.1f 100 * (s_price_received - s_flat_average) / s_flat_average

* Session 264: the capture rate beside the capture price, the price received over the flat average, in whole percent as the page writes it.

display "capture rate, percent of the flat average: " %9.0f 100 * s_price_received / s_flat_average

* Debt coverage, last twelve months: the third headline number; revenue less fixed O&M, over the annual debt payments.

display "annual debt payments, USD: " %15.0fc s_debt_service

display "debt coverage, last twelve months, times: " %9.2f (s_l12_usd_per_mw * s_mw - s_fom_usd_kw_year * 1000 * s_mw) / s_debt_service

* Session 264: is it worth building, scenario A at the defaults, per kW of nameplate (site/lib/seller/finance.ts). The debt's term, the PPA term and the life are all 35 years and there is no degradation, so each year's flow is the same and a sum over the years is the annuity factor (1 - (1 + r)^-n) / r.

quietly summarize energy_mwh_per_mw if in_last_twelve == 1 & held == 1

scalar s_l12_energy = r(sum)

display "energy sold, last twelve months, MWh per MW: " %9.0fc s_l12_energy

scalar s_debt_kw = s_capex_usd_kw * s_debt_share * s_debt_rate / (1 - (1 + s_debt_rate)^(-s_debt_years))

scalar s_annuity = (1 - (1 + s_hurdle)^(-s_life_years)) / s_hurdle

scalar s_ppa_annuity = (1 - (1 + s_hurdle)^(-s_ppa_years)) / s_hurdle

display "contract price at which coverage reaches 1.25 times, USD per MWh: " %9.2f (1.25 * s_debt_kw + s_fom_usd_kw_year) / (s_l12_energy / 1000)

* Session 304: solar's degradation default is 0.7 percent a year since session 298 (NREL ATB 2025; the owner's ruling 7a of 18 October 2026): the market revenue of year t is the last twelve months' times (1 - s_deg)^(t - 1), summed at the hurdle rate (the site's finance.ts, flows and npv)

scalar s_deg = 0.007

scalar s_npv_kw = -s_capex_usd_kw * (1 - s_debt_share)

forvalues t = 1/35 {
    scalar s_npv_kw = s_npv_kw + (s_l12_usd_per_mw / 1000 * (1 - s_deg)^(`t' - 1) - s_fom_usd_kw_year - s_debt_kw) / (1 + s_hurdle)^`t'
}

display "NPV at the hurdle rate, USD million for 100 MW: " %9.2f s_npv_kw * 1000 * s_mw / 1000000

scalar s_npv0_kw = -s_capex_usd_kw * (1 - s_debt_share) + (-s_fom_usd_kw_year - s_debt_kw) * s_ppa_annuity + (s_l12_usd_per_mw / 1000 - s_fom_usd_kw_year) * (s_annuity - s_ppa_annuity)

display "breakeven PPA price, the whole of the energy for the PPA term, USD per MWh: " %9.2f -s_npv0_kw / (s_l12_energy / 1000 * s_ppa_annuity)

* Trailing twelve months: a window ends at each held month whose eleven months before it are all held.

sort ym

gen streak = held

replace streak = streak[_n-1] + 1 if held == 1 & _n > 1 & ym == ym[_n-1] + 1

gen double cum_cfads_usd = sum(cfads_usd)

gen double ttm_cover = (cum_cfads_usd - cond(_n > 12, cum_cfads_usd[_n-12], 0)) / s_debt_service if streak >= 12

quietly summarize ym if ttm_cover < .

scalar s_newest_window = r(max)

quietly summarize ttm_cover if ym == s_newest_window

display "the newest twelve-month window ends " %tmCCYY-NN s_newest_window ", coverage, times: " %9.2f r(mean)

quietly summarize ttm_cover

display "twelve-month windows: " r(N)

display "lowest twelve-month coverage, times: " %9.2f r(min)

quietly count if ttm_cover < 1

display "twelve-month windows under 1.0 times: " r(N)

quietly count if ttm_cover < 1.25

display "twelve-month windows under 1.25 times: " r(N)

* Month by month, for 100 MW: the months held, the months that did not cover a month of debt payments, the year's average.

quietly summarize ym if held == 1

display "months held: " r(N) ", " %tmCCYY-NN r(min) " to " %tmCCYY-NN r(max)

quietly count if held == 1 & cover < 1

display "months held that covered less than 1.0 times: " r(N)

quietly count if held == 1 & cover < 1.25

display "months held that covered less than 1.25 times: " r(N)

quietly summarize revenue_usd if held == 1

display "the year's average, twelve times the mean month, USD for 100 MW: " %15.2fc r(mean) * 12

* The median month, the 10th-percentile month (nearest rank) and the worst three, by revenue.

keep if held == 1

sort revenue_usd ym

scalar s_median_rank = max(1, ceil(0.5 * _N))

scalar s_p10_rank = max(1, ceil(0.1 * _N))

display "median month: " %tmCCYY-NN ym[s_median_rank] ", USD for 100 MW: " %15.2fc revenue_usd[s_median_rank]

display "10th-percentile month, nearest rank: " %tmCCYY-NN ym[s_p10_rank] ", USD for 100 MW: " %15.2fc revenue_usd[s_p10_rank]

forvalues i = 1/3 {
    display "worst month `i': " %tmCCYY-NN ym[`i'] ", USD for 100 MW: " %15.2fc revenue_usd[`i']
}

* Not in this file: the capture price at the other hubs and by year, the other rows of the spans table, the IRR (none at the defaults: every year's flow is below zero), the sensitivity chart, a contract other than the breakeven one, the battery beside the plant and the stress days.
