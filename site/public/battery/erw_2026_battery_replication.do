* ERW, What a battery earns (/cost-of-power/battery): the headline numbers of the default case, rebuilt from erw_2026_battery_dispatch.csv.

* The default case: ERCOT, a 4-hour battery, perfect foresight, 100 MW. Method: docs/methods/battery_earns_algorithm.md.

* Session 263: the defaults are the page's since the owner's ruling of 12 October 2026 (20 percent debt, a hurdle rate of 12 percent), and the file rebuilds scenario A's column too (NPV at the hurdle rate, IRR, breakeven toll, merchant tail), line for line with site/lib/battery/finance.ts. Not run: Stata is not on the machine that wrote it; its Python mirror was run.

* The file has 14 comment lines; the column names are on line 15 and the hours start on line 16.

clear all

import delimited using "erw_2026_battery_dispatch.csv", varnames(15) rowrange(16) stringcols(_all) clear

destring hour_of_day, replace force

destring in_last_twelve, replace force

destring switch_used, replace force

destring price_energy_usd_mwh, replace force

destring price_regup_usd_mw, replace force

destring price_regdn_usd_mw, replace force

destring price_rrs_usd_mw, replace force

destring price_ecrs_usd_mw, replace force

destring price_nspin_usd_mw, replace force

destring charge_mw, replace force

destring discharge_mw, replace force

destring soc_mwh, replace force

destring award_regup_mw, replace force

destring award_regdn_mw, replace force

destring award_rrs_mw, replace force

destring award_ecrs_mw, replace force

destring award_nspin_mw, replace force

destring revenue_energy_usd, replace force

destring revenue_regup_usd, replace force

destring revenue_regdn_usd, replace force

destring revenue_rrs_usd, replace force

destring revenue_ecrs_usd, replace force

destring revenue_nspin_usd, replace force

destring revenue_ancillary_usd, replace force

destring revenue_total_usd, replace force

replace price_regup_usd_mw = . if price_regup_usd_mw == -999

replace price_regdn_usd_mw = . if price_regdn_usd_mw == -999

replace price_rrs_usd_mw = . if price_rrs_usd_mw == -999

replace price_ecrs_usd_mw = . if price_ecrs_usd_mw == -999

replace price_nspin_usd_mw = . if price_nspin_usd_mw == -999

replace award_regup_mw = . if award_regup_mw == -999

replace award_regdn_mw = . if award_regdn_mw == -999

replace award_rrs_mw = . if award_rrs_mw == -999

replace award_ecrs_mw = . if award_ecrs_mw == -999

replace award_nspin_mw = . if award_nspin_mw == -999

replace revenue_regup_usd = . if revenue_regup_usd == -999

replace revenue_regdn_usd = . if revenue_regdn_usd == -999

replace revenue_rrs_usd = . if revenue_rrs_usd == -999

replace revenue_ecrs_usd = . if revenue_ecrs_usd == -999

replace revenue_nspin_usd = . if revenue_nspin_usd == -999

* The reader's inputs at their defaults: size, fixed O&M, and the debt (Lazard LCOE+ June 2025, its storage cases: 1110 USD per kW, 20 percent debt at 8 percent over 20 years; equity's cost of 12 percent is the hurdle rate; degradation 2.6 percent a year; a life of 20 years).

scalar s_mw = 100

scalar s_fom_usd_kw_year = 22

scalar s_capex_usd_kw = 1110

scalar s_debt_share = 0.2

scalar s_debt_rate = 0.08

scalar s_debt_years = 20

scalar s_life_years = 20

scalar s_degradation = 0.026

scalar s_hurdle_pct = 12

scalar s_toll_target = 1.25

* The term of the debt, cut to the project life; the level payment per dollar borrowed; the payments in USD for the size and per kW.

scalar s_debt_years_used = min(s_debt_years, s_life_years)

scalar s_crf = s_debt_rate / (1 - (1 + s_debt_rate)^(-s_debt_years_used))

scalar s_debt_service = round(s_capex_usd_kw * 1000 * s_debt_share * s_crf * s_mw)

scalar s_debt_kw = s_capex_usd_kw * s_debt_share * s_crf

* The NPV to equity, USD per kW, at the rate in s_rate_pct: equity paid in at year 0, then each year's revenue (cut by the degradation each year after the first) less fixed O&M less the debt payment while the debt lasts (finance.ts, flows and npv; no contract).

capture program drop erw_npv

program define erw_npv
    scalar s_npv = -s_capex_usd_kw * (1 - s_debt_share)
    forvalues t = 1/`=s_life_years' {
        scalar s_npv = s_npv + (s_rev_kw * (1 - s_degradation)^(`t' - 1) - s_fom_usd_kw_year - cond(`t' <= s_debt_years_used, s_debt_kw, 0)) / (1 + s_rate_pct / 100)^`t'
    }
end

* Check of the file against itself: revenue is price times megawatts, hour by hour (the largest difference is printed; rounding only).

gen check_energy = abs(revenue_energy_usd - price_energy_usd_mwh * (discharge_mw - charge_mw))

quietly summarize check_energy

display "largest difference, energy revenue against price times megawatts, USD: " %12.8f r(max)

foreach k in regup regdn rrs ecrs nspin {
    gen check_`k' = abs(revenue_`k'_usd - price_`k'_usd_mw * award_`k'_mw)
    quietly summarize check_`k'
    display "largest difference, `k' revenue against price times megawatts, USD: " %12.8f r(max)
}

* One row a local month: the sums of its hours, per MW of rated power, and the days it holds.

gen local_date = date(local_day, "YMD")

gen month = mofd(local_date)

format month %tm

egen day_tag = tag(local_day)

collapse (sum) revenue_energy_usd revenue_regup_usd revenue_regdn_usd revenue_rrs_usd revenue_ecrs_usd revenue_nspin_usd revenue_ancillary_usd revenue_total_usd (sum) days_held = day_tag (max) in_last_twelve, by(month)

gen days_in_month = day(dofm(month + 1) - 1)

gen held = days_held / days_in_month >= 0.9 - 1e-9

gen calendar_year = year(dofm(month))

* The last twelve months: the first headline number, the summary sentence and the first column of Income by stream.

foreach k in energy regup regdn rrs ecrs nspin ancillary total {
    quietly summarize revenue_`k'_usd if in_last_twelve == 1 & held == 1
    scalar s_l12_`k' = r(sum)
    display "last twelve months, `k', USD for 100 MW: " %15.0fc round(s_l12_`k' * s_mw)
}

quietly count if in_last_twelve == 1 & held == 1

display "months in the last twelve that are held: " r(N)

display "last twelve months, all streams, USD per kW: " %9.2f s_l12_total / 1000

display "share from ancillary services, percent: " %3.0f round(100 * s_l12_ancillary / s_l12_total)

display "annual debt payments, USD: " %15.0fc s_debt_service

display "debt coverage, last twelve months, times: " %9.2f (s_l12_total * s_mw - s_fom_usd_kw_year * 1000 * s_mw) / s_debt_service

* Scenario A at its defaults: the last twelve months' revenue every year of the life (finance.ts, resultOf).

scalar s_rev_kw = s_l12_total / 1000

display "scenario A, debt coverage, times: " %9.2f (s_rev_kw - s_fom_usd_kw_year) / s_debt_kw

scalar s_rate_pct = s_hurdle_pct

erw_npv

scalar s_npv_kw = s_npv

display "scenario A, NPV at the hurdle rate, USD per kW: " %9.2f s_npv_kw

display "scenario A, NPV at the hurdle rate, USD for 100 MW: " %15.0fc round(s_npv_kw * 1000 * s_mw)

* The IRR (finance.ts, irr): bisection between -99 and 1,000 percent, at most 200 halvings or until the bracket is 1e-10 wide; none when the NPV has the same sign at both ends.

scalar s_lo = -99

scalar s_hi = 1000

scalar s_rate_pct = s_lo

erw_npv

scalar s_flo = s_npv

scalar s_rate_pct = s_hi

erw_npv

scalar s_fhi = s_npv

scalar s_irr = .

scalar s_done = 0

if s_flo == 0 scalar s_irr = s_lo
else if s_fhi == 0 scalar s_irr = s_hi
else if (s_flo > 0) != (s_fhi > 0) {
    forvalues i = 1/200 {
        if s_done == 0 & s_hi - s_lo > 1e-10 {
            scalar s_mid = (s_lo + s_hi) / 2
            scalar s_rate_pct = s_mid
            erw_npv
            if s_npv == 0 {
                scalar s_irr = s_mid
                scalar s_done = 1
            }
            else if (s_npv > 0) == (s_flo > 0) {
                scalar s_lo = s_mid
                scalar s_flo = s_npv
            }
            else scalar s_hi = s_mid
        }
    }
    if s_done == 0 scalar s_irr = (s_lo + s_hi) / 2
}

if s_irr == . display "scenario A, IRR, percent a year: none"
else display "scenario A, IRR, percent a year: " %9.1f s_irr

display "scenario A, breakeven toll, USD per kW-month: " %9.2f (s_toll_target * s_debt_kw + s_fom_usd_kw_year) / 12

* The merchant tail: the years of the life after the debt's, and the present value at the hurdle rate of their revenue less fixed O&M.

scalar s_tail_years = max(0, s_life_years - s_debt_years_used)

scalar s_tail = 0

forvalues t = 1/`=s_life_years' {
    if `t' > s_debt_years_used scalar s_tail = s_tail + (s_rev_kw * (1 - s_degradation)^(`t' - 1) - s_fom_usd_kw_year) / (1 + s_hurdle_pct / 100)^`t'
}

display "scenario A, merchant tail, years: " s_tail_years ", USD for 100 MW: " %15.0fc round(s_tail * 1000 * s_mw)

* The chart's full calendar years inside the file, USD per kW.

foreach y in 2024 2025 {
    quietly summarize revenue_energy_usd if calendar_year == `y' & held == 1
    scalar s_year_energy = r(sum)
    quietly summarize revenue_ancillary_usd if calendar_year == `y' & held == 1
    display "calendar year `y', months held: " r(N) ", energy USD per kW: " %9.2f s_year_energy / 1000 ", ancillary USD per kW: " %9.2f r(sum) / 1000
}

* A bad month: the 10th percentile of the held months of the 36, by total revenue, nearest rank.

keep if held == 1

sort revenue_total_usd month

scalar s_n36 = _N

scalar s_rank = max(1, ceil(0.1 * s_n36))

display "months held of the 36: " s_n36

display "a bad month: " %tm month[s_rank] ", USD for 100 MW: " %15.0fc round(revenue_total_usd[s_rank] * s_mw)

* Not in this file: the average of every year held, the last three full years, the column without February 2021 and the stress days need the years before the file's first month.
