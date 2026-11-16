* ERW, the demand growth explorer (/explore/demand-growth): the page's five headline figures, rebuilt from the public table.

* Method: docs/methods/demand_growth.md, "The tool as a reader meets it" (the rule in full, point 6: a growth is computed from the means and peaks as the table writes them). Session 7508, chain 304, 16 November 2026.

* It reads one table as CSV: eia930_demand_growth (the page's own download, or warehouse/output), or table_rows.csv beside this file, which holds the rows the page reads. Set the file in the line "global table" below. Run this file from its own folder.

* This do-file has not been run: Stata is not installed on the machine that wrote it. "python replicate.py --headline" follows it step for step on the same file and printed the lines below.

* Expected values, on eia930_demand_growth as built on 6 November 2026 (24,116 rows; the year to date runs to the end of October 2026):

*   1. ERCOT, average demand, growth 2019 to 2025, percent: 27.22 (2019: 43,797.6 MW; 2025: 55,717.2 MW)

*   2. ERCOT, peak demand (the highest hour), growth 2019 to 2025, percent: 12.16 (2019: 74,533 MW; 2025: 83,597 MW)

*   3. ERCOT, the year so far (January to October 2026) against the same months of 2019, percent: 33.34 (2019: 44,790.7 MW; 2026: 59,723.4 MW)

*   4. Lower 48, average demand, growth 2019 to 2025, percent: 7.03 (2019: 458,599.1 MW; 2025: 490,819.4 MW)

*   5. ERCOT, average demand, growth 2024 to 2025, percent: 5.57 (2024: 52,779.8 MW)

* The figures move when the table is rebuilt (each month the year to date gains a month, and EIA revises its hours): after a new copy, compare with python replicate.py --headline --table=<the new file>, not with the lines above.

clear all

global table "table_rows.csv"

* ---- The table. A standard ERW table opens with comment lines that begin with #, then a line of column names; its first four columns are entity, variable, ts_utc and value.

import delimited using "$table", delimiter(comma) varnames(nonames) stringcols(_all) bindquote(nobind) clear

drop if substr(v1, 1, 1) == "#" | v1 == "entity"

keep v1 v2 v3 v4

rename (v1 v2 v3 v4) (entity variable ts_utc value)

destring value, replace force

gen year = real(substr(ts_utc, 1, 4))

keep if inlist(entity, "eia930:ERCO", "eia930:US48") & inlist(variable, "avg_demand_mw", "peak_demand_mw", "ytd_avg_demand_mw")

* ---- The last whole year is the newest year with an average of the whole year; the newest year is the newest with a year to date.

quietly summarize year if entity == "eia930:ERCO" & variable == "avg_demand_mw"

scalar last_whole = r(max)

quietly summarize year if entity == "eia930:ERCO" & variable == "ytd_avg_demand_mw"

scalar newest = r(max)

* ---- One value: an area, a variable, a year.

capture program drop one

program define one, rclass

    args entity variable year

    quietly summarize value if entity == "`entity'" & variable == "`variable'" & year == `year'

    return scalar v = r(mean)

end

* ---- 1. ERCOT, average demand, growth 2019 to the last whole year. Expected: 27.22

one "eia930:ERCO" "avg_demand_mw" 2019

scalar a0 = r(v)

one "eia930:ERCO" "avg_demand_mw" `=last_whole'

scalar a1 = r(v)

display "1. ERCOT, average demand, growth 2019 to " last_whole ", percent: " %9.2f (a1 / a0 - 1) * 100 "  (2019: " %12.1fc a0 " MW; " last_whole ": " %12.1fc a1 " MW)"

* ---- 2. ERCOT, peak demand (the highest hour), growth 2019 to the last whole year. Expected: 12.16

one "eia930:ERCO" "peak_demand_mw" 2019

scalar p0 = r(v)

one "eia930:ERCO" "peak_demand_mw" `=last_whole'

scalar p1 = r(v)

display "2. ERCOT, peak demand (the highest hour), growth 2019 to " last_whole ", percent: " %9.2f (p1 / p0 - 1) * 100 "  (2019: " %12.0fc p0 " MW; " last_whole ": " %12.0fc p1 " MW)"

* ---- 3. ERCOT, the year so far against the same months of 2019. Expected: 33.34

one "eia930:ERCO" "ytd_avg_demand_mw" 2019

scalar y0 = r(v)

one "eia930:ERCO" "ytd_avg_demand_mw" `=newest'

scalar y1 = r(v)

display "3. ERCOT, the year so far of " newest " against the same months of 2019, percent: " %9.2f (y1 / y0 - 1) * 100 "  (2019: " %12.1fc y0 " MW; " newest ": " %12.1fc y1 " MW)"

* ---- 4. Lower 48, average demand, growth 2019 to the last whole year. Expected: 7.03

one "eia930:US48" "avg_demand_mw" 2019

scalar u0 = r(v)

one "eia930:US48" "avg_demand_mw" `=last_whole'

scalar u1 = r(v)

display "4. Lower 48, average demand, growth 2019 to " last_whole ", percent: " %9.2f (u1 / u0 - 1) * 100 "  (2019: " %12.1fc u0 " MW; " last_whole ": " %12.1fc u1 " MW)"

* ---- 5. ERCOT, average demand, growth on the year before. Expected: 5.57

one "eia930:ERCO" "avg_demand_mw" `=last_whole - 1'

scalar b0 = r(v)

display "5. ERCOT, average demand, growth " last_whole - 1 " to " last_whole ", percent: " %9.2f (a1 / b0 - 1) * 100 "  (" last_whole - 1 ": " %12.1fc b0 " MW)"
