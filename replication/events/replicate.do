* ERW, /events and its nine event pages: the five headline figures, rebuilt from the rows of event_window_daily.

* Method: docs/methods/events.md ("The figures on the pages, each with its table and rule") and docs/methods/event_study.md
* ("Specification", "Inference"). Session 7531, chain 304, 16 November 2026.

* Input: window_rows.csv beside this file, the rows of the public table event_window_daily (written by
* "python replication/events/replicate.py --tables <dir> --write"). Run this file from its own folder.

* This do-file has not been run: Stata is not installed on the machine that wrote it. "python replicate.py" computes the
* same figures from the same file (page_figures.csv, the column "ours", at the keys named below).

* Expected values, on the table as retrieved on 19 October 2026:

*   1. Uri: the highest 15-minute real-time price at ERCOT's hub average, 2021: 9,051.55 USD/MWh on 2021-02-17
*                                       key series|event_window_daily|ercot:HB_HUBAVG|rt_max|2021-02-17T00:00:00Z|uri_2021

*   2. Winter Storm Elliott: PJM's highest hour of demand served, 2022-12-19 to 2022-12-29: 135,328 MW on 2022-12-23
*                                       key series|event_window_daily|eia930:PJM|demand_max_mw|2022-12-23T00:00:00Z|elliott_2022

*   3. The summer 2023 heat: ERCOT's highest hour, 2023-08-01 to 2023-09-10: 85,432 MW on 2023-08-10
*                                       key series|event_window_daily|eia930:ERCO|demand_max_mw|2023-08-10T00:00:00Z|ercot_heat_2023

*   4. Uri: the pooled effect on ERCOT's daily demand served: 155,794.96 MWh a day, 95 percent interval 53,420.68 to
*      258,169.25 (robust, HC1, normal), 54 days                     key es|uri_2021|eia930:ERCO|demand_mwh|pooled|est, lo, hi

*   5. Elliott: the pooled effect on PJM's daily demand served: 386,999.95 MWh a day, 95 percent interval 256,963.62 to
*      517,036.28, 33 days                                          key es|elliott_2022|eia930:PJM|demand_mwh|pooled|est, lo, hi

* Stata's vce(robust) is HC1, the covariance the note names. Stata's own interval uses the t distribution; the pages use
* the normal 1.96, so the interval is computed below as b +- 1.959964 se.

* The figures change when the data machine rebuilds the table: after a new copy, compare with python replicate.py.

clear all

import delimited using "window_rows.csv", varnames(3) rowrange(4) delimiter(comma) stringcols(1 2 3 5 6 7) clear

gen d = date(substr(ts_utc, 1, 10), "YMD")

format d %td

save "window_rows.dta", replace

* ---- 1. Uri, the highest 15-minute real-time price of 2021's days

use "window_rows.dta", clear

keep if event == "uri_2021" & entity == "ercot:HB_HUBAVG" & variable == "rt_max" & year(d) == 2021

gsort -value d

list d value in 1

* ---- 2. Elliott, PJM's highest hour in the window

use "window_rows.dta", clear

keep if event == "elliott_2022" & entity == "eia930:PJM" & variable == "demand_max_mw" & inrange(d, td(19dec2022), td(29dec2022))

gsort -value d

list d value in 1

* ---- 3. ERCOT 2023, the highest hour in the window

use "window_rows.dta", clear

keep if event == "ercot_heat_2023" & entity == "eia930:ERCO" & variable == "demand_max_mw" & inrange(d, td(01aug2023), td(10sep2023))

gsort -value d

list d value in 1

* ---- 4 and 5. The pooled effect: one window indicator, six weekday indicators (Monday the reference), the two baseline
* years coded to sum to zero (the event days take none), on the event's daily rows of demand served

capture program drop pooled

program define pooled

    args ev ent from to

    use "window_rows.dta", clear

    keep if event == "`ev'" & entity == "`ent'" & variable == "demand_mwh" & inlist(freq, "P1D", "")

    gen byte window = inrange(d, `from', `to')

    gen int dw = dow(d)

    quietly summarize d if window == 0

    gen int y = year(d)

    quietly levelsof y if window == 0, local(years)

    local y1 : word 1 of `years'

    local y2 : word 2 of `years'

    gen z = cond(window, 0, (y == `y1') - (y == `y2'))

    regress value window ib1.dw z, vce(robust)

    display "pooled " %12.2f _b[window] "  interval " %12.2f (_b[window] - 1.959964 * _se[window]) " to " %12.2f (_b[window] + 1.959964 * _se[window]) "  days " e(N)

end

pooled uri_2021 eia930:ERCO td(07feb2021) td(24feb2021)

pooled elliott_2022 eia930:PJM td(19dec2022) td(29dec2022)
