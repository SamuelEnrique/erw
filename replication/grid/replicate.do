* ERW, the Grid tool (/grid): the figures the page prints, rebuilt in Stata (session 3704, chain 208).

* Method: docs/methods/grid_network.md, "Replication". replicate.py beside this file computes the same figures and more; this file follows it for the network, the carbon months and the Ask panel's plain queries.

* This do-file has not been run: Stata is not installed on the machine that wrote it. replicate.py printed, on 6 November 2026, on the snapshot built 2026-11-05T23:09:35Z and the tables of warehouse/output: 147 of 158 computed figures met, 11 a known difference (Ask answers asked of a newer copy of their table), 22 license needed, 8 not held in the tables given.

* Run it from this folder (replication/grid). snapshot_hour.csv is the network snapshot's hour shown, written by figures_of_the_page.py from the snapshot the page draws; the global tables below is the folder of the warehouse's tables as CSV (warehouse/output on the ERW's machines).

* What it does not compute: the gravity shape's generation and share (eia930_all_generation at the hour shown, not in the tables of 30 September); the network's carbon intensity per grid (the same); the Ask panel's grouped queries and compares (replicate.py); every figure the page prints as "license needed".

clear all

set more off

global tables "../../warehouse/output"

* ---------------------------------------------------------------- 1. The network: the hour shown

* Each tie with a flow appears once in snapshot_hour.csv, as the snapshot stores it: positive when id sent power to other. Each grid sees it from its own side.

import delimited using "snapshot_hour.csv", varnames(1) stringcols(_all) clear

destring value, replace force

gen built = ts_utc if kind == "built"

gsort -built

local built = built[1]

drop if kind != "tie"

local hour = ts_utc[1]

* the age of the hour shown at the snapshot's refresh, in hours, rounded half up (JavaScript's Math.round)

scalar lag = floor((clock(substr("`built'", 1, 19), "YMD#hms") - clock(substr("`hour'", 1, 19), "YMD#hms")) / 3600000 + 0.5)

display "net|lag|`hour'|`built' = " lag

* both sides of every tie: the sender's flow as it is stored, the receiver's with its sign turned

expand 2, generate(other_side)

gen ba = cond(other_side == 0, id, other)

gen nb = cond(other_side == 0, other, id)

gen double mw = cond(other_side == 0, value, -value)

preserve

collapse (sum) net_export = mw, by(ba)

gsort -net_export ba

display "net|topexport|`hour' = " net_export[1] " (" ba[1] ")"

scalar topexport = net_export[1]

restore

gen double absmw = abs(mw)

keep if inlist(ba, "ERCO", "CISO", "PJM", "MISO", "NYIS", "ISNE", "SWPP")

tempfile ties

save `ties'

* each grid's net export, its ties and its largest flow

collapse (sum) net_export = mw (count) ties = mw (max) maxflow = absmw, by(ba)

gen double net_import = -net_export

gen rows = 4

expand rows

bysort ba: gen k = _n

gen check = ""

gen double replication = .

replace check = "net|export|" + ba + "|`hour'" if k == 1

replace replication = net_export if k == 1

replace check = "net|import|" + ba + "|`hour'" if k == 2

replace replication = net_import if k == 2

replace check = "net|ties|" + ba + "|`hour'" if k == 3

replace replication = ties if k == 3

replace check = "net|maxflow|" + ba + "|`hour'" if k == 4

replace replication = maxflow if k == 4

keep check replication

tempfile grids

save `grids'

* each tie, from each grid's side

use `ties', clear

gen check = "net|tie|" + ba + "|" + nb + "|`hour'"

gen double replication = mw

keep check replication

append using `grids'

set obs `=_N + 1'

replace check = "net|lag|`hour'|`built'" in L

replace replication = lag in L

set obs `=_N + 1'

replace check = "net|topexport|`hour'" in L

replace replication = topexport in L

tempfile network

save `network'

* ---------------------------------------------------------------- 2. The Clean tab's carbon months, rebuilt from the hours

* A month is the month's CO2 over its MWh. Each hour's MWh is its CO2 (eia930_all_emissions, co2_emissions_generated, metric tons) times 1,000 over its intensity (carbon_intensity_hourly, intensity_generation, kg CO2 per MWh). A month counts when every UTC day of it holds 24 hours (docs/methods/emissions.md).

* The tables are large (eia930_all_emissions is about 1 GB): only their first four columns are read (entity, variable, ts_utc, value), and every line that begins with # is a comment.

import delimited using "$tables/eia930_all_emissions.csv", varnames(nonames) colrange(1:4) stringcols(_all) clear

drop if substr(v1, 1, 1) == "#" | v1 == "entity"

rename (v1 v2 v3 v4) (entity variable ts_utc value)

keep if variable == "co2_emissions_generated" & inlist(entity, "eia930:ERCO", "eia930:CISO", "eia930:PJM", "eia930:MISO", "eia930:NYIS", "eia930:ISNE", "eia930:SWPP")

destring value, replace force

rename value co2

drop variable

tempfile co2

save `co2'

import delimited using "$tables/carbon_intensity_hourly.csv", varnames(nonames) colrange(1:4) stringcols(_all) clear

drop if substr(v1, 1, 1) == "#" | v1 == "entity"

rename (v1 v2 v3 v4) (entity variable ts_utc value)

keep if variable == "intensity_generation" & inlist(entity, "eia930:ERCO", "eia930:CISO", "eia930:PJM", "eia930:MISO", "eia930:NYIS", "eia930:ISNE", "eia930:SWPP")

destring value, replace force

rename value intensity

drop if intensity >= .

merge 1:1 entity ts_utc using `co2', keep(match master) nogenerate

gen month = substr(ts_utc, 1, 7)

gen day = substr(ts_utc, 1, 10)

bysort entity day: gen hours_of_day = _N

gen double mwh = co2 * 1000 / intensity if co2 < . & intensity > 0

gen bad = hours_of_day != 24 | mwh >= .

gen days_in_month = day(dofm(monthly(month, "YM") + 1) - 1)

bysort entity month day: gen first_of_day = _n == 1

bysort entity month: egen days_held = total(first_of_day)

collapse (sum) co2 mwh (max) bad (first) days_in_month days_held, by(entity month)

keep if bad == 0 & days_held == days_in_month

gen double replication = co2 * 1000 / mwh

gen check = "series|carbon_intensity_monthly|" + entity + "|intensity_generation|" + month + "-01T00:00:00Z"

keep check replication

append using `network'

tempfile computed

save `computed'

* ---------------------------------------------------------------- 3. The comparison with the page

* page_figures.csv holds what the page prints for each figure (its check key, the value, the tolerance: half of the last digit the page shows).

import delimited using "page_figures.csv", varnames(1) stringcols(_all) clear

destring raw, replace force

destring tolerance, replace force

destring held, replace force

merge 1:1 check using `computed', keep(match master) nogenerate

gen double difference = replication - raw

gen str48 status = ""

replace status = "license needed" if held == 1

replace status = "Ask: replicate_ask.do below" if group == "ask" & status == ""

replace status = "not held in the tables given" if replication >= . & status == ""

replace status = "yes" if abs(difference) <= tolerance + 1e-9 & status == ""

replace status = "NO" if status == ""

format replication raw difference %18.4f

list group check raw replication difference status if group != "ask", noobs clean abbreviate(24)

count if status == "yes"

display "met: " r(N)

count if status == "NO"

display "not met: " r(N)

* ---------------------------------------------------------------- 4. The Ask panel's stored answers, the plain queries

do replicate_ask.do
