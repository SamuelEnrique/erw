* ERW, What a datacenter pays (/cost-of-power): the headline numbers of the default case, rebuilt from erw_2026_datacenter_hourly.csv.

* The default case: ERCOT, the North load zone (LZ_NORTH), a flat load of 100 MW, bought in real time. Method: docs/methods/datacenter_pays_algorithm.md.

* This do-file has not been run: Stata is not installed on the machine that wrote it. erw_2026_datacenter_replication.py follows it step for step and prints the same lines.

* The file has 15 comment lines; the column names are on line 16 and the hours start on line 17.

clear all

import delimited using "erw_2026_datacenter_hourly.csv", delimiter(comma) varnames(16) rowrange(17) stringcols(_all) clear

destring rt_usd_mwh, replace force

destring da_usd_mwh, replace force

destring hub_rt_usd_mwh, replace force

destring in_last_twelve, replace force

replace rt_usd_mwh = . if rt_usd_mwh == -99999

replace da_usd_mwh = . if da_usd_mwh == -99999

replace hub_rt_usd_mwh = . if hub_rt_usd_mwh == -99999

* The reader's inputs at their defaults: the size, the power per GPU (NVIDIA DGX H100: 8 GPUs and 10.2 kW) and the facility overhead ratio (Uptime Institute, Global Data Center Survey 2024).

scalar s_mw = 100

scalar s_gpu_kw = 1.3

scalar s_pue = 1.56

* Hour by hour: a flat MW pays the price of every hour that is held. An hour that is not held is in no sum.

gen ym = monthly(std_month, "YM")

format ym %tm

gen rt_hour = rt_usd_mwh < .

gen da_hour = da_usd_mwh < .

gen hub_hour = hub_rt_usd_mwh < .

gen double rt_usd_per_mw = rt_usd_mwh

gen double da_usd_per_mw = da_usd_mwh

gen double hub_usd_per_mw = hub_rt_usd_mwh

* One row a month of US Central standard time: the hours held and the sum of the prices held, for each of the three prices.

collapse (sum) rt_usd_per_mw da_usd_per_mw hub_usd_per_mw rt_hours = rt_hour da_hours = da_hour hub_hours = hub_hour (max) in_last_twelve, by(ym)

* The hours due in a month: 24 a day, with no daylight saving shift. A month counts when at least 95 percent of them are held.

gen hours_due = 24 * day(dofm(ym + 1) - 1)

gen rt_counted = rt_hours >= 0.95 * hours_due

gen da_counted = da_hours >= 0.95 * hours_due

gen hub_counted = hub_hours >= 0.95 * hours_due

gen double rt_usd_mwh_month = rt_usd_per_mw / rt_hours if rt_hours > 0

gen calendar_year = year(dofm(ym))

* Last twelve months, market energy: the first headline number and the summary sentence.

quietly summarize ym if in_last_twelve == 1

scalar s_l12_first = r(min)

scalar s_l12_last = r(max)

display "the last twelve months: " %tmCCYY-NN s_l12_first " to " %tmCCYY-NN s_l12_last

quietly count if in_last_twelve == 1 & rt_counted == 1

display "months in the last twelve that count: " r(N)

quietly summarize rt_hours if in_last_twelve == 1 & rt_counted == 1

scalar s_l12_hours = r(sum)

quietly summarize rt_usd_per_mw if in_last_twelve == 1 & rt_counted == 1

scalar s_l12_usd_per_mw = r(sum)

scalar s_l12_usd_mwh = s_l12_usd_per_mw / s_l12_hours

display "hours held in the last twelve months: " s_l12_hours

display "market energy, a flat load, last twelve months, USD per MWh: " %9.2f s_l12_usd_mwh

display "cost for 100 MW, USD: " %15.0fc s_l12_usd_per_mw * s_mw

display "energy for 100 MW, MWh: " %15.0fc s_l12_hours * s_mw

* Power per GPU-hour: the third headline number. The price per MWh times the kW of a GPU with its share of the facility's overhead, over 1000.

display "power per GPU-hour, USD: " %9.4f s_l12_usd_mwh * s_gpu_kw * s_pue / 1000

display "GPUs that 100 MW powers: " %15.0fc s_mw * 1000 / (s_gpu_kw * s_pue)

* Beside the zone, over the same twelve months: the trading hub (HB_NORTH) in real time, and the zone itself bought day-ahead. Each a flat load.

foreach v in hub da {
    quietly count if in_last_twelve == 1 & `v'_counted == 1
    scalar s_`v'_months = r(N)
    quietly summarize `v'_hours if in_last_twelve == 1 & `v'_counted == 1
    scalar s_`v'_hours = r(sum)
    quietly summarize `v'_usd_per_mw if in_last_twelve == 1 & `v'_counted == 1
    scalar s_`v'_usd_mwh = r(sum) / s_`v'_hours
}

display "months of the twelve that count at the hub: " s_hub_months

display "the hub beside it, a flat load, USD per MWh: " %9.2f s_hub_usd_mwh

display "the load zone less its hub, USD per MWh: " %9.2f s_l12_usd_mwh - s_hub_usd_mwh

display "months of the twelve that count day-ahead: " s_da_months

display "bought day-ahead, a flat load, the same twelve months, USD per MWh: " %9.2f s_da_usd_mwh

* The months held, and those that count.

quietly summarize ym if rt_hours > 0

display "months held: " r(N) ", " %tmCCYY-NN r(min) " to " %tmCCYY-NN r(max)

quietly count if rt_counted == 1

display "months that count: " r(N)

* By calendar year: the sums of the months that count. A year is complete when all twelve count.

egen year_months = total(rt_counted), by(calendar_year)

egen double year_usd_per_mw = total(rt_usd_per_mw * rt_counted), by(calendar_year)

egen double year_hours = total(rt_hours * rt_counted), by(calendar_year)

quietly levelsof calendar_year, local(years)

foreach y of local years {
    quietly summarize year_usd_per_mw if calendar_year == `y'
    scalar s_year_usd_per_mw = r(mean)
    quietly summarize year_hours if calendar_year == `y'
    scalar s_year_hours = r(mean)
    quietly summarize year_months if calendar_year == `y'
    display "year `y': months that count " r(mean) ", a flat load, USD per MWh: " %9.2f s_year_usd_per_mw / s_year_hours
}

* A bad month, the second headline number: of the months that count among the 36 that end with the last twelve, the month at the top tenth by cost per MWh, nearest rank.

keep if rt_counted == 1 & ym >= s_l12_last - 35 & ym <= s_l12_last

gsort -rt_usd_mwh_month ym

scalar s_bad_rank = max(1, ceil(0.1 * _N))

quietly summarize ym

display "months that count of the 36: " r(N) ", " %tmCCYY-NN r(min) " to " %tmCCYY-NN r(max)

display "a bad month, nearest rank " s_bad_rank ": " %tmCCYY-NN ym[s_bad_rank] ", USD per MWh: " %9.2f rt_usd_mwh_month[s_bad_rank]

display "the bad month's cost for 100 MW, USD: " %15.0fc rt_usd_per_mw[s_bad_rank] * s_mw

* Not in this file: a flexible load (the rule, and the same load if perfectly foreseen; both are rebuilt from da_usd_mwh and rt_usd_mwh by the test), the contract, the delivery and transmission charges, the tight hours, the carbon-free share and the queue figures.
