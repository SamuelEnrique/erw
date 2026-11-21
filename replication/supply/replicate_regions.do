* ERW, supply and trade (/supply), "The whole country": five headline figures of the views for EIA's thirteen regions,
* rebuilt from the page's own files (site/data/regions/, built by the data machine on 19 November 2026 between 12:03
* and 12:16 UTC, on origin/main since af1962719). Session 8490, chain 503, part E. Method: docs/methods/supply_and_trade.md,
* "The whole country" and "The rules above, made exact (session 8460)". The full replication of every figure of the
* views is replicate_regions.py beside this file (43,552 of 43,552 equal on those files).
*
* This do-file has not been run: Stata is not installed on the machine that wrote it. Samuel runs it from the
* repository's root. It needs Stata 16 or later with Python set up (the page files are JSON, which Stata does not read;
* the python block below only flattens the arrays to rows, every sum and percent is Stata's).
*
* Expected values (the page prints the same, drawn with the site's own code on the same files):
*   1. Tennessee, net imports from all its neighbours, 2025, its own report:          +8,309.7 GWh  (12 months)
*   2. The Carolinas and Tennessee, 2025, net imports of the Carolinas from Tennessee:
*        the Carolinas' own report                                                    +91.1 GWh
*        Tennessee's report of the same flow, the Carolinas' sign                     +94.2 GWh
*        the gap in percent of the mean size of the two reports (three sums over the months that hold all three)  0.0
*   3. The Southeast and Tennessee, 2025, in "Who trades with whom": the mean of the two reports   2,877.5 GWh
*        and the gap, Tennessee's report less the Southeast's (Tennessee sent)        +0.3 GWh
*   4. The Northwest, net imports from Canada, 2024, its own report:                  -7,769.7 GWh  (12 months; the sum
*        is exactly -7,769,650 MWh, a half: the page rounds it away from zero; Stata's %9.1f may print -7769.6)
*   5. Texas, solar's share of net generation, 2025:                                  14.1 percent  (over the 11 months
*        the file holds; it holds no December 2025)

version 16
clear all
local files "site/data/regions"
tempfile long

python:
import csv, json, os
from sfi import Macro
root = Macro.getLocal("files")
out = Macro.getLocal("long")
rows = []
def rd(p):
    with open(os.path.join(root, p), encoding="utf-8") as f:
        return json.load(f)
ten = rd("trade/ten.json")
for m, v in zip(ten["months"], ten["net_imports_mwh"]):
    rows.append(["ten_all", m, v, None, None])
car = rd("trade/car.json")
n = car["neighbors"]["TEN"]
for m, a, b, c in zip(car["months"], n["net_imports_mwh"], n["their_report_mwh"], n["gap_mwh"]):
    rows.append(["car_ten", m, a, b, c])
for r in rd("trade_matrix.json")["region_pairs"]:
    if r["a"] == "SE" and r["b"] == "TEN":
        rows.append(["se_ten", str(r["year"]), r["mean_mwh"], r["gap_mwh"], 1 if r["direction"] == "b_to_a" else 0])
nw = rd("trade/nw.json")
for m, v in zip(nw["months"], nw["neighbors"]["CAN"]["net_imports_mwh"]):
    rows.append(["nw_can", m, v, None, None])
for m, r in rd("mix/tex.json")["months"].items():
    rows.append(["tex_mix", m, r.get("solar_mwh"), r.get("net_generation_mwh"), None])
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["fig", "month", "a", "b", "c"])
    for r in rows:
        w.writerow(["" if x is None else x for x in r])
end

import delimited using "`long'", varnames(1) stringcols(1 2) clear
gen year = substr(month, 1, 4)

* 1. a month whose total is not held is left out of the year, never filled
quietly summarize a if fig == "ten_all" & year == "2025" & !missing(a)
display "1. Tennessee, net imports from all neighbours, 2025: " %12.0fc r(sum) " MWh = " %9.1fc r(sum) / 1000 " GWh over " r(N) " months"

* 2. each report summed over its own months; the percent on three sums over the months that hold all three
quietly summarize a if fig == "car_ten" & year == "2025" & !missing(a)
local own = r(sum)
quietly summarize b if fig == "car_ten" & year == "2025" & !missing(b)
local their = r(sum)
gen all3 = fig == "car_ten" & year == "2025" & !missing(a, b, c)
quietly summarize a if all3
local o3 = r(sum)
quietly summarize b if all3
local t3 = r(sum)
quietly summarize c if all3
local g3 = r(sum)
display "2. the Carolinas from Tennessee, 2025: own " %9.1fc `own' / 1000 " GWh, Tennessee's " %9.1fc `their' / 1000 " GWh, gap " %5.1f abs(`g3') / ((abs(`o3') + abs(`t3')) / 2) * 100 " percent"

* 3. the matrix's mean, turned to the direction (times minus one when power ran from the second to the first), and its gap
quietly summarize a if fig == "se_ten" & month == "2025"
local mean = r(mean)
quietly summarize c if fig == "se_ten" & month == "2025"
local turn = cond(r(mean) == 1, -1, 1)
quietly summarize b if fig == "se_ten" & month == "2025"
display "3. the Southeast and Tennessee, 2025: mean " %9.1fc `turn' * `mean' / 1000 " GWh, gap " %7.1f r(mean) / 1000 " GWh"

* 4.
quietly summarize a if fig == "nw_can" & year == "2024" & !missing(a)
display "4. the Northwest from Canada, 2024: " %12.0fc r(sum) " MWh = " %9.1fc r(sum) / 1000 " GWh over " r(N) " months"

* 5. solar's energy over the months that hold it and net generation, over the net generation of those same months
gen both5 = fig == "tex_mix" & year == "2025" & !missing(a, b)
quietly summarize a if both5
local sol = r(sum)
quietly summarize b if both5
display "5. Texas, solar's share of net generation, 2025: " %5.1f `sol' / r(sum) * 100 " percent over " r(N) " months"
