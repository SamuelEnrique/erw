* Expected: 1973 30.906473, 2025 63.413382, change 32.506908 (percent of US crude imports); tolerance 0.5 percent of the change.

* ERW findings hunt (chain 164): reproduce candidate import_share for imp_CA from the ERW's public tables.

* Input: the tables' CSVs as the public download holds them (Redivis: the variable names on the first line). From the ERW's own files, delete the lines that begin with # first.

clear all

import delimited "eia_crude_imports_by_country.csv", varnames(1) stringcols(_all) clear

keep if (entity == "eia:MCRIMUS2" | entity == "eia:MCRIMUSCA2") & variable == "imports"

destring value, replace force

drop if missing(value)

duplicates drop entity ts_utc, force

generate int year = real(substr(ts_utc, 1, 4))

generate double tot = value if entity == "eia:MCRIMUS2"

generate double one = value if entity == "eia:MCRIMUSCA2"

egen byte has = tag(ts_utc) if !missing(one)

collapse (sum) tot (sum) one (sum) n = has, by(year)

keep if tot > 0 & n > 0

generate double measure = 100 * one / tot

sort year

list year measure n, noobs
