* run_top40: run the reproduce.do files of the findings sheet one after another and print one table.

* Energy Research Warehouse (ERW), written by session 8905 (chain 590) on 19 November 2026 by docs/findings/_top40/build_runners.py. Read, not run: the machine that wrote it has no Stata. The README beside it says what to do if a line fails.

* The sheet: https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/findings-shortlist-2026-11-19.md

* Set this one line: the folder of your copy of the ERW repository (forward slashes).

global erw "C:/Users/samuel/Documents/erw"

* The folder that holds the tables' CSVs, variable names on the first line (README, step 2). Change it only if your CSVs are elsewhere.

global tables "$erw/docs/findings/_top40/tables"

set more off

set linesize 200

capture log close top

log using "$tables/run_top40.log", replace text name(top)

cd "$tables"

* The forty, in the sheet's order. For each: its number on the sheet, a short name, its do-file, the two years, the sheet's two figures. Finding 18 is a summary (median, lowest, highest, filings) and is checked on all four.

global n 40

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

global num5 5

global name5 "ERCOT South hub, evening price (pct)"

global f5 "docs/findings/prices/evening-premium-ercot-hb-south.reproduce.do"

global kind5 "years"

global y0_5 2015

global y1_5 2025

global e0_5 109.549

global e1_5 160.994

global num6 6

global name6 "ERCOT North hub, cheapest hour (hour)"

global f6 "docs/findings/prices/cheapest-hour-ercot-hb-north.reproduce.do"

global kind6 "years"

global y0_6 2015

global y1_6 2025

global e0_6 6.03562

global e1_6 10.674

global num7 7

global name7 "Omaha PPD, commercial sales (TWh)"

global f7 "docs/findings/other_us/util-commercial-u861-14127-ne.reproduce.do"

global kind7 "years"

global y0_7 2017

global y1_7 2025

global e0_7 3.66636

global e1_7 7.87521

global num8 8

global name8 "Canada to New York, mean flow (MW)"

global f8 "docs/findings/trade/pair-flow-rp-can-ny.reproduce.do"

global kind8 "years"

global y0_8 2019

global y1_8 2025

global e0_8 1991.6

global e1_8 211.028

global num9 9

global name9 "New England, hours exporting (pct)"

global f9 "docs/findings/trade/region-against-rn-ne.reproduce.do"

global kind9 "years"

global y0_9 2019

global y1_9 2025

global e0_9 0.045662

global e1_9 27.7803

global num10 10

global name10 "CAISO batteries against peak (pct)"

global f10 "docs/findings/cross_family/battery-per-peak-caiso-bat-peak.reproduce.do"

global kind10 "years"

global y0_10 2019

global y1_10 2025

global e0_10 0.554036

global e1_10 46.5676

global num11 11

global name11 "ERCOT load factor (pct)"

global f11 "docs/findings/authorities/ba-load-factor-ba-erco.reproduce.do"

global kind11 "years"

global y0_11 2019

global y1_11 2025

global e0_11 58.762

global e1_11 66.6477

global num12 12

global name12 "US data center construction (USD bn)"

global f12 "docs/findings/queues_deals_datacenters/dc-construction-us-dc-build.reproduce.do"

global kind12 "years"

global y0_12 2014

global y1_12 2025

global e0_12 1.797

global e1_12 49.737

global num13 13

global name13 "Virginia commercial electricity (TWh)"

global f13 "docs/findings/demand/seds-elec-comm-sd-va.reproduce.do"

global kind13 "years"

global y0_13 1990

global y1_13 2024

global e0_13 28.0818

global e1_13 78.7107

global num14 14

global name14 "US gas fleet heat rate (MMBtu per MWh)"

global f14 "docs/findings/generation_pipeline/gas-heat-rate-hr-gas-us.reproduce.do"

global kind14 "years"

global y0_14 2001

global y1_14 2024

global e0_14 10.8409

global e1_14 8.2976

global num15 15

global name15 "LNG share of US dry gas (pct)"

global f15 "docs/findings/gas/lng-share-us-lng.reproduce.do"

global kind15 "years"

global y0_15 2015

global y1_15 2025

global e0_15 0.104861

global e1_15 14.0222

global num16 16

global name16 "Henry Hub median daily move (pct)"

global f16 "docs/findings/prices/henry-hub-volatility-us-henry-hub.reproduce.do"

global kind16 "years"

global y0_16 1997

global y1_16 2025

global e0_16 2.01344

global e1_16 3.18841

global num17 17

global name17 "Gulf Coast gasoline crack (USD per bbl)"

global f17 "docs/findings/oil_products_world/gasoline-crack-crack-gasoline.reproduce.do"

global kind17 "years"

global y0_17 1987

global y1_17 2025

global e0_17 2.03697

global e1_17 19.33

global num18 18

global name18 "Large-load minimum bill, median (pct)"

global f18 "docs/findings/large_load/tariff-min-bill-pct.reproduce.do"

global kind18 "summary"

global e0_18 11

global e1_18 80

global emin_18 75

global emax_18 100

global num19 19

global name19 "ERCOT CO2 per MWh (kg)"

global f19 "docs/findings/authorities/ba-co2-intensity-ba-erco.reproduce.do"

global kind19 "years"

global y0_19 2019

global y1_19 2025

global e0_19 408.475

global e1_19 315.408

global num20 20

global name20 "ERCOT West, wide-spread days (pct)"

global f20 "docs/findings/prices/wide-spread-days-ercot-lz-west.reproduce.do"

global kind20 "years"

global y0_20 2015

global y1_20 2025

global e0_20 28.7671

global e1_20 84.1096

global num21 21

global name21 "Texas, January 2026 cold peak (MW)"

global f21 "docs/findings/events/cold-2026-tex.reproduce.do"

global kind21 "years"

global y0_21 2019

global y1_21 2026

global e0_21 54656

global e1_21 75599

global num22 22

global name22 "Carolinas, Elliott peak (MW)"

global f22 "docs/findings/events/elliott-2022-car.reproduce.do"

global kind22 "years"

global y0_22 2018

global y1_22 2022

global e0_22 33078

global e1_22 44630

global num23 23

global name23 "US reactor uranium price (USD per lb)"

global f23 "docs/findings/coal_uranium_metals/uranium-price-us-uranium-price.reproduce.do"

global kind23 "years"

global y0_23 2003

global y1_23 2025

global e0_23 10.81

global e1_23 58.46

global num24 24

global name24 "US-origin uranium share (pct)"

global f24 "docs/findings/coal_uranium_metals/us-origin-uranium-us-uranium-origin.reproduce.do"

global kind24 "years"

global y0_24 2003

global y1_24 2025

global e0_24 18.0365

global e1_24 7.24947

global num25 25

global name25 "India coal consumption (million st)"

global f25 "docs/findings/coal_uranium_metals/wc-consumption-wc-ind.reproduce.do"

global kind25 "years"

global y0_25 1980

global y1_25 2024

global e0_25 107.796

global e1_25 1371.12

global num26 26

global name26 "US power CO2 per MWh (kg)"

global f26 "docs/findings/emissions_climate/power-co2-per-mwh-co2mwh-us.reproduce.do"

global kind26 "years"

global y0_26 2001

global y1_26 2022

global e0_26 604.462

global e1_26 362.127

global num27 27

global name27 "US-origin enrichment share (pct)"

global f27 "docs/findings/coal_uranium_metals/us-enrichment-share-us-enrich-origin.reproduce.do"

global kind27 "years"

global y0_27 2003

global y1_27 2025

global e0_27 13.8831

global e1_27 22.8346

global num28 28

global name28 "Georgia and Alabama coal share (pct)"

global f28 "docs/findings/regions/coal-share-st-se-cow.reproduce.do"

global kind28 "years"

global y0_28 2001

global y1_28 2025

global e0_28 60.2307

global e1_28 14.4272

global num29 29

global name29 "Florida gas share (pct)"

global f29 "docs/findings/regions/gas-share-st-fla-ng.reproduce.do"

global kind29 "years"

global y0_29 2001

global y1_29 2025

global e0_29 22.8179

global e1_29 72.9527

global num30 30

global name30 "Arizona and New Mexico solar share (pct)"

global f30 "docs/findings/regions/solar-share-st-sw-sun.reproduce.do"

global kind30 "years"

global y0_30 2001

global y1_30 2025

global e0_30 0.000396

global e1_30 13.9626

global num31 31

global name31 "US commercial retail sales (TWh)"

global f31 "docs/findings/tariffs_policy/commercial-sales-com-sales-us.reproduce.do"

global kind31 "years"

global y0_31 2001

global y1_31 2025

global e0_31 1083.07

global e1_31 1503.31

global num32 32

global name32 "Greece coal share (pct)"

global f32 "docs/findings/world_power/eu-share-coal-eu-el.reproduce.do"

global kind32 "years"

global y0_32 2017

global y1_32 2025

global e0_32 31.8315

global e1_32 5.29206

global num33 33

global name33 "Texas cooling degree days a day"

global f33 "docs/findings/weather/cdd-wd-tex.reproduce.do"

global kind33 "years"

global y0_33 2019

global y1_33 2024

global e0_33 8.93395

global e1_33 9.9366

global num34 34

global name34 "EU27 solar share (pct)"

global f34 "docs/findings/world_power/eu-share-solar-eu-eu27-2020.reproduce.do"

global kind34 "years"

global y0_34 2017

global y1_34 2025

global e0_34 3.79508

global e1_34 13.0051

global num35 35

global name35 "Portugal net imports (pct)"

global f35 "docs/findings/world_power/eu-net-imports-eu-pt.reproduce.do"

global kind35 "years"

global y0_35 2016

global y1_35 2025

global e0_35 -9.97587

global e1_35 17.6645

global num36 36

global name36 "Finland wind share (pct)"

global f36 "docs/findings/world_power/eu-share-wind-eu-fi.reproduce.do"

global kind36 "years"

global y0_36 2016

global y1_36 2025

global e0_36 4.6214

global e1_36 27.9164

global num37 37

global name37 "US share of world liquids (pct)"

global f37 "docs/findings/oil_products_world/us-liquids-share-us-world-liquids.reproduce.do"

global kind37 "years"

global y0_37 1993

global y1_37 2025

global e0_37 14.4734

global e1_37 22.3223

global num38 38

global name38 "US dry gas exports (bcf)"

global f38 "docs/findings/gas/wog-gas-exports-wog-usa.reproduce.do"

global kind38 "years"

global y0_38 1980

global y1_38 2024

global e0_38 48.731

global e1_38 7707.04

global num39 39

global name39 "US reactor fleet power level (pct)"

global f39 "docs/findings/markets_operations/reactor-power-rp-us.reproduce.do"

global kind39 "years"

global y0_39 2020

global y1_39 2025

global e0_39 89.4421

global e1_39 91.0813

global num40 40

global name40 "Indonesia coal exports (million st)"

global f40 "docs/findings/coal_uranium_metals/wc-exports-wc-idn.reproduce.do"

global kind40 "years"

global y0_40 1980

global y1_40 2024

global e0_40 0.423883

global e1_40 614.82

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
