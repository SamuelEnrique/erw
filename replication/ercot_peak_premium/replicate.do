* ERW, the ERCOT peak premium explorer (/explore/ercot-peak-premium): the page's five headline figures, rebuilt.

* Method: docs/methods/ercot_peak_premium.md ("Metrics", and "The tool as a reader meets it"). Session 7507, chain 304, 16 November 2026.

* Part A reads the public table ercot_peak_premium_annual as CSV (the page's own download, or warehouse/output) and prints the five figures the page opens on, each also rebuilt from the table's other rows where the note defines it by them. Part B rebuilds the same figures for one hub and one year from ERCOT's 15-minute prices by the note's rule, with no percentile command of Stata (the note's interpolation is written out). Set the folder that holds the tables in the line "global tables" below. Run this file from its own folder.

* This do-file has not been run: Stata is not installed on the machine that wrote it. "python replicate.py --headline" follows part A step for step on the same file and printed the lines below; "python from_hourly.py" follows part B for every hub and period (25,704 of 25,704 rows of the two tables equal at six decimals).

* Expected values, on ercot_peak_premium_annual as built on 29 September 2026 (2,016 rows; last input interval 2026-09-28T04:45:00Z). The page opens on HB_HUBAVG, the whole year, 2015 against 2025:

*   1. peak-block IQR, USD/MWh: 34.12 in 2025 (7.64 in 2015)

*   2. peak median minus midday median, USD/MWh: 14.52 in 2025 (-0.16 in 2015)

*   3. median of all intervals, USD/MWh: 25.68 in 2025 (20.49 in 2015)

*   4. 99.9th percentile, USD/MWh, and the worst-interval multiple: 311.80 and 12.14 in 2025 (583.96 and 28.50 in 2015)

*   5. intervals at or above 1,000 USD/MWh, and at or below 0: 9 and 959 in 2025 (5 and 297 in 2015)

* Both years are complete (35,040 intervals), so these ten values do not move when the tables are rebuilt, unless ERCOT restates a price. The second year moves to 2026 once 2026 is complete: compare then with python replicate.py --headline.

clear all

global tables "../../warehouse/output"

global hub "ercot:HB_HUBAVG"

global first 2015

global second 2025

* ---- Part A: the figures as the page reads them, one row of the annual table each.

* A standard ERW table opens with comment lines that begin with #, then a line of column names; its first four columns are entity, variable, ts_utc and value.

import delimited using "$tables/ercot_peak_premium_annual.csv", delimiter(comma) varnames(nonames) stringcols(_all) bindquote(nobind) clear

drop if substr(v1, 1, 1) == "#" | v1 == "entity"

keep v1 v2 v3 v4

rename (v1 v2 v3 v4) (entity variable ts_utc value)

destring value, replace force

keep if entity == "$hub"

gen year = real(substr(ts_utc, 1, 4))

keep if inlist(year, $first, $second)

keep year variable value

reshape wide value, i(year) j(variable) string

rename value* *

* The note's definitions on the table's own rows: each must equal the row (to the table's six decimals).

gen iqr_rebuilt = peak_q3 - peak_q1

gen spread_rebuilt = peak_median - midday_median

gen multiple_rebuilt = all_p999 / all_median

assert abs(iqr_rebuilt - peak_iqr) < 0.000002

assert abs(spread_rebuilt - peak_minus_midday_median) < 0.000002

assert abs(multiple_rebuilt - worst_interval_multiple) < 0.00001

assert n_intervals == cond(mod(year, 4) == 0, 35136, 35040)

format peak_iqr peak_minus_midday_median all_median all_p999 worst_interval_multiple %12.2fc

format n_scarcity n_negative n_intervals %12.0fc

sort year

* 1. the peak-block IQR; 2. the peak median less the midday median; 3. the median of all intervals

list year peak_iqr peak_minus_midday_median all_median, noobs

* 4. the 99.9th percentile and the worst-interval multiple; 5. the intervals at or above 1,000 USD/MWh and at or below 0

list year all_p999 worst_interval_multiple n_scarcity n_negative n_intervals, noobs

* Stata prints 37.035 as 37.03 or 37.04 by its own rule; the page rounds a tie away from zero. None of the ten values above is a tie.

* ---- Part B: the second year's figures from the 15-minute prices (the yearly history, about 700 MB as CSV: it needs about 2 GB of memory).

* The rows of ercot_all_hub_prices_history whose market is ercot_rtm are ERCOT's real-time settlement point prices (NP6-785-ER), one row an interval, ts_utc the interval's start in UTC. Columns: entity, variable, ts_utc, value, unit, freq, geo, market.

import delimited using "$tables/ercot_all_hub_prices_history.csv", delimiter(comma) varnames(nonames) stringcols(_all) bindquote(nobind) clear

drop if substr(v1, 1, 1) == "#" | v1 == "entity"

keep if v1 == "$hub" & v8 == "ercot_rtm" & v2 == "spp_rtm"

keep v3 v4

rename (v3 v4) (ts_utc price)

destring price, replace force

gen double t = clock(ts_utc, "YMD#hms#")

* Local time in America/Chicago: six hours behind UTC, five while daylight saving holds, from the second Sunday of March at 08:00 UTC to the first Sunday of November at 07:00 UTC.

gen y_utc = yofd(dofc(t))

gen d1 = mdy(3, 1, y_utc)

gen d2 = mdy(11, 1, y_utc)

gen double dst_on = cofd(d1 + mod(7 - dow(d1), 7) + 7) + 8 * 3600000

gen double dst_off = cofd(d2 + mod(7 - dow(d2), 7)) + 7 * 3600000

gen double local = t - cond(t >= dst_on & t < dst_off, 5, 6) * 3600000

keep if yofd(dofc(local)) == $second

gen h = hh(local)

* The blocks, by the local hour in which the interval starts: peak 16 to 20, midday 12 to 15, overnight the rest.

gen block = cond(h >= 16 & h < 21, "peak", cond(h >= 12 & h < 16, "midday", "overnight"))

count

* The note's percentile: the sorted prices interpolated at position (n - 1) * p / 100, counted from zero.

capture program drop pct

program define pct, rclass

    args p cond

    preserve

    if "`cond'" != "" keep if block == "`cond'"

    sort price

    local n = _N

    local pos = (`n' - 1) * `p' / 100

    local lo = floor(`pos') + 1

    local hi = min(`lo' + 1, `n')

    return scalar v = price[`lo'] + (price[`hi'] - price[`lo']) * (`pos' - floor(`pos'))

    restore

end

pct 25 peak

scalar k_q1 = r(v)

pct 75 peak

scalar k_q3 = r(v)

pct 50 peak

scalar k_med = r(v)

pct 50 midday

scalar m_med = r(v)

pct 50

scalar a_med = r(v)

pct 99.9

scalar a_p999 = r(v)

display "1. peak-block IQR: " %9.2f (k_q3 - k_q1)

display "2. peak median minus midday median: " %9.2f (k_med - m_med)

display "3. median of all intervals: " %9.2f a_med

display "4. 99.9th percentile and the worst-interval multiple: " %9.2f a_p999 " and " %9.2f (a_p999 / a_med)

count if price >= 1000

count if price <= 0

* For 2025 at HB_HUBAVG part B should display 34.12, 14.52, 25.68, 311.80 and 12.14, then count 9 and 959, with 35,040 intervals in all.
