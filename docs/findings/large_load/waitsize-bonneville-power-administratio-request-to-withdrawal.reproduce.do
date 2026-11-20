* Expected figures: large_at_least 17.051335; large_at_most 27.433265; small_at_least 42.809035; small_at_most 56.213552; tolerance 0.5 percent of each.

* ERW findings hunt (chain 502): reproduce waitsize_bonneville_power_administratio_request_to_withdrawal from the ERW's table large_load_waits.

* Input: the table's CSV as the download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "large_load_waits.csv", varnames(1) stringcols(_all) clear

keep if entity == "Bonneville Power Administration" & interval == "request to withdrawal" & label == "measured"

destring days_at_least days_at_most, replace force

preserve

keep if size_class == "300 MW and over"

duplicates drop request_id, force

quietly summarize days_at_least, detail

display "large_at_least " r(p50) / 30.4375

quietly summarize days_at_most, detail

display "large_at_most " r(p50) / 30.4375

restore

preserve

keep if size_class == "under 20 MW"

duplicates drop request_id, force

quietly summarize days_at_least, detail

display "small_at_least " r(p50) / 30.4375

quietly summarize days_at_most, detail

display "small_at_most " r(p50) / 30.4375

restore

display "done"
