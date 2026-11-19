* Expected figures: median_at_least 5.22; median_at_most 11.17; requests 57.0; tolerance 0.5 percent of each.

* ERW findings hunt (chain 502): reproduce wait_new_york_iso_in_stage from the ERW's table large_load_wait_summary.

* Input: the table's CSV as the download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "large_load_wait_summary.csv", varnames(1) stringcols(_all) clear

keep if x_publisher == "New York ISO" & x_interval == "in stage"

destring value, replace force

list variable value, noobs

foreach k in median_at_least median_at_most requests {
quietly summarize value if variable == "`k'"
display "`k' " r(mean)
}

display "done"
