* Expected figures: median 80.0; lowest 75.0; highest 100.0; filings 11.0; tolerance 0.5 percent of each.

* ERW findings hunt (chain 502): reproduce tariff_min_bill_pct from the ERW's table utility_large_load_tariffs.

* Input: the table's CSV as the download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "utility_large_load_tariffs.csv", varnames(1) stringcols(_all) clear

keep if variable == "min_bill_pct"

destring value, replace force

drop if missing(value)

summarize value, detail

display "median " r(p50)

display "lowest " r(min)

display "highest " r(max)

display "filings " r(N)
