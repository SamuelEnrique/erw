* Expected figures: median_at_least 8.66; median_at_most 10.66; requests 179.0; tolerance 0.5 percent of each.

* ERW findings hunt (chain 502): reproduce wait_alberta_electric_system_operat_request_to_energized from the ERW's table large_load_wait_summary.

* Input: the table's CSV as the download holds it (Redivis: the variable names on the first line). From the ERW's own file, delete the lines that begin with # first.

clear all

import delimited "large_load_wait_summary.csv", varnames(1) stringcols(_all) clear

keep if x_publisher == "Alberta Electric System Operator (Canada)" & x_interval == "request to energized"

destring value, replace force

list variable value, noobs

foreach k in median_at_least median_at_most requests {
quietly summarize value if variable == "`k'"
display "`k' " r(mean)
}

display "done"
