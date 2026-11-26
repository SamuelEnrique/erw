* ERW forecast (/forecast): the regression of docs/methods/predict.md, section 3 (c), for one place and one target day, rebuilt from the public demand.

* Session 10600, chain 730, 26 November 2026. Inputs: runs/predict_replication/<place>_days.csv and <place>_<day>_python.csv, written by replication/predict/export.py from eia930_ba_demand_hourly (Form EIA-930, public).

* For each local hour k: the log of the hour's demand on day T, regressed on the log of the same hour on day A = T - h, the log of day A's mean, the log of the same hour on T-7, the log of the mean of the seven days ending on A, the weekday of T and of A, the holidays and bridge days of T, A and T-7, and two yearly waves; fit on target days T-h-729 to T-h; the forecast is the exponential of the fitted value.

* Not run: Stata is not on the machine that wrote it (the desktop). The Python it mirrors is warehouse/predict/demand.py; the do-file sets its forecast beside the Python one, hour by hour, and prints the largest difference in percent. Expect differences near 1e-6 percent (the two solve the same least squares by different arithmetic).

clear all
set type double

global place "region-tex"
global day "2026-11-20"
global h 2
global dir "../../runs/predict_replication"

import delimited using "$dir/${place}_days.csv", varnames(1) clear
gen d = date(day, "YMD")
format d %td
tsset d

* a lone missing hour inside a day: the mean of its two neighbours, for the regressors only
forvalues k = 0/23 {
    gen double f`k' = v`k'
}
forvalues k = 1/22 {
    local a = `k' - 1
    local b = `k' + 1
    replace f`k' = (v`a' + v`b') / 2 if missing(v`k') & !missing(v`a') & !missing(v`b')
}
forvalues k = 0/23 {
    gen double lf`k' = ln(f`k') if f`k' > 0
    gen double ly`k' = ln(v`k') if v`k' > 0
}

* the day's mean, only when every hour is there; the mean of the seven days ending on a day, when at least five are held
egen double dm = rowmean(f0-f23)
egen nm = rowmiss(f0-f23)
replace dm = . if nm > 0
gen double lmean = ln(dm)
gen double wsum = 0
gen wn = 0
forvalues j = 0/6 {
    replace wsum = wsum + cond(missing(L`j'.dm), 0, L`j'.dm)
    replace wn = wn + !missing(L`j'.dm)
}
gen double lweek = ln(wsum / wn) if wn >= 5

* the calendar: weekday 0 Monday to 6 Sunday (Sunday the base); holidays and bridge days as exported
forvalues j = 0/5 {
    gen dT`j' = (dow == `j')
    gen dA`j' = (L$h.dow == `j') if !missing(L$h.dow)
}
gen hT = hol
gen bT = bridge
gen hA = L$h.hol
gen bA = L$h.bridge
gen h7 = L7.hol
gen b7 = L7.bridge
gen double s1 = sin(2 * _pi * doy / 365.25)
gen double c1 = cos(2 * _pi * doy / 365.25)
gen double s2 = sin(4 * _pi * doy / 365.25)
gen double c2 = cos(4 * _pi * doy / 365.25)
gen double xmean = L$h.lmean
gen double xweek = L$h.lweek

local T = date("$day", "YMD")
local lo = `T' - $h - 729
local hi = `T' - $h
matrix R = J(24, 3, .)
forvalues k = 0/23 {
    capture drop xA x7 yhat
    gen double xA = L$h.lf`k'
    gen double x7 = L7.lf`k'
    quietly regress ly`k' xA xmean x7 xweek dT0-dT5 dA0-dA5 hT bT hA bA h7 b7 s1 c1 s2 c2 if d >= `lo' & d <= `hi'
    predict double yhat, xb
    quietly summarize yhat if d == `T'
    matrix R[`k' + 1, 1] = `k'
    matrix R[`k' + 1, 2] = exp(r(mean))
    matrix R[`k' + 1, 3] = e(N)
}

* beside the Python forecast
preserve
import delimited using "$dir/${place}_${day}_python.csv", varnames(1) clear
svmat double R, names(st)
gen double diff_pct = 100 * (st2 - forecast) / forecast
list hour forecast st2 st3 diff_pct, noobs
summarize diff_pct
display "largest difference, percent: " max(abs(r(min)), abs(r(max)))
restore
