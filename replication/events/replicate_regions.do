* ERW, the events pages' section "The whole country": five headline figures, rebuilt from the event files' hours.

* Method: docs/methods/events.md ("The whole country"). Session 8470, chain 503, 19 November 2026.

* Input: regions_rows.csv beside this file, written from the event files (site/data/regions/events/*.json, EIA Form
* EIA-930, public domain) by "python replication/events/replicate_regions.py --write-rows replication/events/regions_rows.csv".
* The rows are not kept in the repository: they come from the data machine's files, which land through it. Run this
* file from its own folder.

* This do-file has not been run: Stata is not installed on the machine that wrote it. The expected values below are
* the ones the Python replication gives from the same rows (replicate_regions.py, and the same rule applied to the
* written rows), on the data machine's files built 19 November 2026 (12:04 UTC), which the pages draw the same figures from.

* The rule: a sum or a mean over the hours the event and the baseline both hold; the highest hour is the first hour at
* the highest held value of the window; GWh is MWh over 1,000 (each hour of the files is one hour, step_hours 1).

* Expected values:

*   1. Winter Storm Elliott, Tennessee (EIA region TEN), 2022-12-19 to 2022-12-29: demand 6,075.748 GWh against
*      4,734.390 GWh in the baseline, +28.33 percent, over 267 hours            page: wc|TEN|demand_pct = +28.3

*   2. Winter Storm Elliott, Tennessee: the highest hour 33,225 MW at 2022-12-24T01:00:00Z (19:00 CST on
*      23 December), the baseline at that hour 19,830 MW                         page: wc|TEN|peak_mw, wc|TEN|peak_base_mw

*   3. Winter Storm Uri, Texas (TEX), 2021-02-07 to 2021-02-24: demand +14.72 percent over 435 hours; the highest
*      hour 69,215 MW at 2021-02-15T01:00:00Z (19:00 CST on 14 February)        page: wc|TEX|demand_pct, wc|TEX|peak_mw

*   4. The September 2022 heat, California (CAL), 2022-08-31 to 2022-09-09: net imports averaged +8,992.8 MW against
*      +8,251.4 MW in the baseline, over 243 hours                               page: wc|CAL|imports_mw, imports_base_mw

*   5. The January 2025 cold, the Mid-Atlantic (MIDA): natural gas +1,386.968 GWh and coal +1,962.007 GWh against the
*      baseline, over the 232 hours both hold                                    page: wc|MIDA|gen|natural_gas, gen|coal

clear all

import delimited using "regions_rows.csv", varnames(3) rowrange(4) delimiter(comma) stringcols(1 2 4) clear

save "regions_rows.dta", replace

* ---- 1. Elliott, Tennessee's demand against the baseline

use "regions_rows.dta", clear

keep if event == "elliott_2022" & region == "TEN" & !missing(demand_mw) & !missing(base_demand_mw)

collapse (sum) d = demand_mw b = base_demand_mw (count) n = demand_mw

gen gwh = d / 1000

gen base_gwh = b / 1000

gen pct = (d - b) / abs(b) * 100

list n gwh base_gwh pct

* ---- 2. Elliott, Tennessee's highest hour and the baseline at that hour

use "regions_rows.dta", clear

keep if event == "elliott_2022" & region == "TEN" & !missing(demand_mw)

gsort -demand_mw i

list ts_utc demand_mw base_demand_mw in 1

* ---- 3. Uri, Texas's demand against the baseline and its highest hour

use "regions_rows.dta", clear

keep if event == "uri_2021" & region == "TEX" & !missing(demand_mw)

gsort -demand_mw i

list ts_utc demand_mw base_demand_mw in 1

keep if !missing(base_demand_mw)

collapse (sum) d = demand_mw b = base_demand_mw (count) n = demand_mw

gen pct = (d - b) / abs(b) * 100

list n pct

* ---- 4. The September 2022 heat, California's net imports

use "regions_rows.dta", clear

keep if event == "caiso_heat_2022" & region == "CAL" & !missing(net_imports_mw) & !missing(base_net_imports_mw)

collapse (mean) m = net_imports_mw bm = base_net_imports_mw (count) n = net_imports_mw

list n m bm

* ---- 5. The January 2025 cold, the Mid-Atlantic's natural gas and coal against the baseline

use "regions_rows.dta", clear

keep if event == "cold_2025" & region == "MIDA"

preserve

keep if !missing(gen_natural_gas_mw) & !missing(base_gen_natural_gas_mw)

collapse (sum) g = gen_natural_gas_mw bg = base_gen_natural_gas_mw (count) n = gen_natural_gas_mw

gen diff_gwh = (g - bg) / 1000

list n diff_gwh

restore

keep if !missing(gen_coal_mw) & !missing(base_gen_coal_mw)

collapse (sum) c = gen_coal_mw bc = base_gen_coal_mw (count) n = gen_coal_mw

gen diff_gwh = (c - bc) / 1000

list n diff_gwh
