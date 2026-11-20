* Expected: 2019 1.534491, 2025 229.367539, change 227.833048 (MW); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 502): reproduce candidate tie_side_gap for bg_ciso_srp from the ERW's public tables (eia930_ba_interchange_hourly_2018, eia930_ba_interchange_hourly_2019, eia930_ba_interchange_hourly_2020, eia930_ba_interchange_hourly_2021, eia930_ba_interchange_hourly_2022, eia930_ba_interchange_hourly_2023, eia930_ba_interchange_hourly_2024, eia930_ba_interchange_hourly_2025, eia930_ba_interchange_hourly_2026).

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

* Faults: an hour whose absolute flow is more than three times its year's 99th percentile of absolute flows is dropped; an hour of demand at or below zero or above three times its year's median is dropped. Stata's percentile rule differs from numpy's in the last place, which moves no hour of these series across the line.

clear all

tempfile all

save `all', emptyok

foreach y of numlist 2018/2026 {
import delimited "eia930_ba_interchange_hourly_`y'.csv", varnames(1) stringcols(_all) clear
keep if entity == "eia930:CISO-SRP" | entity == "eia930:SRP-CISO"
keep entity ts_utc value
append using `all'
save `all', replace
}

use `all', clear

destring value, replace force

drop if missing(value)

generate int year = real(substr(ts_utc, 1, 4))

generate double v = cond(entity == "eia930:CISO-SRP", value, -value)

generate str1 side = cond(entity == "eia930:CISO-SRP", "a", "b")

generate double absflow = abs(v)

bysort side year: egen double p99 = pctile(absflow), p(99)

drop if absflow > 3 * p99

drop absflow p99

keep ts_utc year side v

reshape wide v, i(ts_utc year) j(side) string

drop if missing(va) | missing(vb)

generate double gap = abs(va - vb)

collapse (mean) measure = gap (count) n = gap, by(year)

sort year

list year measure n, noobs
