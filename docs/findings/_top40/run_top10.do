* run_top10: run the reproduce.do files of the findings sheet one after another and print one table.

* Energy Research Warehouse (ERW), written by session 8905 (chain 590) on 19 November 2026 by docs/findings/_top40/build_runners.py. Read, not run: the machine that wrote it has no Stata. The README beside it says what to do if a line fails.

* The sheet: https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/findings-shortlist-2026-11-19.md

* Set this one line: the folder of your copy of the ERW repository (forward slashes).

global erw "C:/Users/samuel/Documents/erw"

* The folder that holds the tables' CSVs, variable names on the first line (README, step 2). Change it only if your CSVs are elsewhere.

global tables "$erw/docs/findings/_top40/tables"

set more off

set linesize 200

capture log close top

log using "$tables/run_top10.log", replace text name(top)

cd "$tables"

* The ten of tonight's page, in the sheet's order. For each: its number on the sheet, a short name, its do-file, the two years, the sheet's two figures. Finding 18 is a summary (median, lowest, highest, filings) and is checked on all four.

global n 10

global num1 1

global name1 "Dominion zone, mean hour (MW)"

global f1 "docs/findings/demand/sub-mean-pjm-sub-dom.reproduce.do"

global kind1 "years"

global y0_1 2019

global y1_1 2025

global e0_1 11687

global e1_1 15403

global num2 2

global name2 "Virginia Power, commercial sales (TWh)"

global f2 "docs/findings/other_us/util-commercial-u861-19876-va.reproduce.do"

global kind2 "years"

global y0_2 2017

global y1_2 2025

global e0_2 41.5356

global e1_2 60.0882

global num3 3

global name3 "ERCOT solar in tightest hours (pct)"

global f3 "docs/findings/markets_operations/tight-solar-ercot-tight-solar.reproduce.do"

global kind3 "years"

global y0_3 2019

global y1_3 2025

global e0_3 71.103

global e1_3 5.022

global num4 4

global name4 "ERCOT West, midday price (pct of mean)"

global f4 "docs/findings/prices/midday-discount-ercot-lz-west.reproduce.do"

global kind4 "years"

global y0_4 2015

global y1_4 2025

global e0_4 128.949

global e1_4 48.9315

global num5 10

global name5 "CAISO batteries against peak (pct)"

global f5 "docs/findings/cross_family/battery-per-peak-caiso-bat-peak.reproduce.do"

global kind5 "years"

global y0_5 2019

global y1_5 2025

global e0_5 0.554036

global e1_5 46.5676

global num6 11

global name6 "ERCOT load factor (pct)"

global f6 "docs/findings/authorities/ba-load-factor-ba-erco.reproduce.do"

global kind6 "years"

global y0_6 2019

global y1_6 2025

global e0_6 58.762

global e1_6 66.6477

global num7 14

global name7 "US gas fleet heat rate (MMBtu per MWh)"

global f7 "docs/findings/generation_pipeline/gas-heat-rate-hr-gas-us.reproduce.do"

global kind7 "years"

global y0_7 2001

global y1_7 2024

global e0_7 10.8409

global e1_7 8.2976

global num8 16

global name8 "Henry Hub median daily move (pct)"

global f8 "docs/findings/prices/henry-hub-volatility-us-henry-hub.reproduce.do"

global kind8 "years"

global y0_8 1997

global y1_8 2025

global e0_8 2.01344

global e1_8 3.18841

global num9 17

global name9 "Gulf Coast gasoline crack (USD per bbl)"

global f9 "docs/findings/oil_products_world/gasoline-crack-crack-gasoline.reproduce.do"

global kind9 "years"

global y0_9 1987

global y1_9 2025

global e0_9 2.03697

global e1_9 19.33

global num10 19

global name10 "ERCOT CO2 per MWh (kg)"

global f10 "docs/findings/authorities/ba-co2-intensity-ba-erco.reproduce.do"

global kind10 "years"

global y0_10 2019

global y1_10 2025

global e0_10 408.475

global e1_10 315.408

* Each do-file in turn. A file that fails is caught and the next one runs. The figure Stata got is read from the data the do-file leaves in memory: its measure in the sheet's last year (and first year, for the change).

* A match: the last year's figure and the change both within 0.5 percent of the change, the drafts' stated tolerance (for finding 18, each of its four figures within 0.5 percent of itself).

forvalues i = 1/$n {
display as text _newline "{hline}" _newline "Finding ${num`i'} of the sheet: ${name`i'}" _newline "{hline}"
global got0_`i' = .
global got1_`i' = .
global res`i' "no figure"
capture noisily do "$erw/${f`i'}"
global rc`i' = _rc
if ${rc`i'} != 0 {
global res`i' "failed, error ${rc`i'}"
}
else if "${kind`i'}" == "summary" {
capture summarize value, detail
if _rc == 0 {
global got0_`i' = r(N)
global got1_`i' = r(p50)
global res`i' = cond(abs(r(p50) - ${e1_`i'}) <= 0.005 * abs(${e1_`i'}) & abs(r(min) - ${emin_`i'}) <= 0.005 * abs(${emin_`i'}) & abs(r(max) - ${emax_`i'}) <= 0.005 * abs(${emax_`i'}) & abs(r(N) - ${e0_`i'}) <= 0.005 * abs(${e0_`i'}), "match", "differs")
}
}
else {
capture summarize measure if year == ${y0_`i'}, meanonly
if _rc == 0 & r(N) == 1 {
global got0_`i' = r(mean)
}
capture summarize measure if year == ${y1_`i'}, meanonly
if _rc == 0 & r(N) == 1 {
global got1_`i' = r(mean)
}
if !missing(${got0_`i'}) & !missing(${got1_`i'}) {
global res`i' = cond(abs(${got1_`i'} - (${e1_`i'})) <= 0.005 * abs(${e1_`i'} - (${e0_`i'})) & abs((${got1_`i'} - (${got0_`i'})) - (${e1_`i'} - (${e0_`i'}))) <= 0.005 * abs(${e1_`i'} - (${e0_`i'})), "match", "differs")
}
}
}

* The table: the finding, the figure the sheet gives, the figure Stata got, and whether they match.

clear

set obs $n

generate int number = .

generate str44 finding = ""

generate double sheet = .

generate double stata = .

generate str24 result = ""

forvalues i = 1/$n {
replace number = ${num`i'} in `i'
replace finding = "${name`i'}" in `i'
replace sheet = ${e1_`i'} in `i'
replace stata = ${got1_`i'} in `i'
replace result = "${res`i'}" in `i'
}

format sheet stata %14.6g

list number finding sheet stata result, noobs separator(0) abbreviate(12)

count if result == "match"

display as result r(N) " of $n match within the stated tolerance of the drafts."

log close top
