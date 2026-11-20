* Expected: 2019 155.658122, 2025 128.583006, change -27.075117 (percent); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate ba_gen_ratio for ba_gcpd from the ERW's public tables (eia930_ba_supply_hourly, eia930_ba_demand_hourly).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

import delimited "eia930_ba_demand_hourly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:GCPD" & variable == "demand_mw"

keep ts_utc value

destring value, replace force

rename value demand

drop if missing(demand)

generate int year = real(substr(ts_utc, 1, 4))

drop if demand <= 0

bysort year: egen double med = median(demand)

drop if demand > 3 * med

drop med

drop year

tempfile dem

save `dem'

import delimited "eia930_ba_supply_hourly.csv", varnames(1) stringcols(_all) clear

keep if entity == "eia930:GCPD" & variable == "net_generation_mw"

keep ts_utc value

destring value, replace force

rename value gen

drop if missing(gen)

generate int year = real(substr(ts_utc, 1, 4))

drop if gen <= 0

bysort year: egen double med = median(gen)

drop if gen > 3 * med

drop med

merge 1:1 ts_utc using `dem', keep(match) nogenerate

collapse (sum) gen = gen (sum) demand = demand (count) n = gen, by(year)

generate double measure = 100 * gen / demand

sort year

list year measure n, noobs
