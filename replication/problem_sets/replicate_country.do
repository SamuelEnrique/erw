* Energy Research Warehouse (ERW), session 8901 (chain 507, part C): the four problem sets of the whole country in Stata.
* Run from the repository's root, after the Python:  python replication/problem_sets/replicate_country.py
* then:  do replication/problem_sets/replicate_country.do
* Stata reads no JSON, so the figures are read as the page files give them through the CSV the Python writes:
*   replication/problem_sets/country_inputs.csv   every figure read from a page file (site/data/...), with its file and path;
*                                                 pos is a position of an hourly series (the storms' peak hours)
*   replication/problem_sets/country_answers.csv  every figure of every question: read, calc (op of two figures), max
* Stata checks each read figure against its input, recomputes each max from its series and each calc from its two
* figures, and asserts each within a relative 1e-6 of the Python's value. No number is typed here.
* Samuel's rules: no line continuation; one empty line between commands; every variable destringed with force.
version 15

clear all

set more off

import delimited using "replication/problem_sets/country_inputs.csv", rowrange(3) varnames(2) stringcols(_all) clear

destring pos, replace force

destring value, replace force

rename set setname

rename name figure

tempfile inputs

save `inputs'

import delimited using "replication/problem_sets/country_answers.csv", rowrange(3) varnames(2) stringcols(_all) clear

destring value, replace force

rename set setname

tempfile answers

save `answers'

keep setname question figure value

tempfile values

save `values'

* ---- 1. every read figure equals the figure the page file gives
use `inputs', clear

keep if missing(pos)

rename value input

keep setname question figure input

tempfile reads

save `reads'

use `answers', clear

keep if kind == "read"

merge 1:1 setname question figure using `reads'

assert _merge == 3

assert abs(value - input) <= 1e-6 * max(1, abs(input))

count

display "1. read figures equal to their page files: " r(N)

* ---- 2. every max is the largest of its hourly series
use `inputs', clear

keep if !missing(pos)

collapse (max) top = value, by(setname question figure)

tempfile tops

save `tops'

use `answers', clear

keep if kind == "max"

drop figure

rename a figure

merge 1:1 setname question figure using `tops'

assert _merge == 3

assert abs(value - top) <= 1e-6 * max(1, abs(top))

count

display "2. highest hours recomputed: " r(N)

* ---- 3. every calc is its op of its two figures
use `values', clear

rename value va

rename figure a

tempfile avals

save `avals'

use `values', clear

rename value vb

rename figure b

tempfile bvals

save `bvals'

use `answers', clear

keep if kind == "calc"

merge m:1 setname question a using `avals', keep(master match)

assert _merge == 3

drop _merge

merge m:1 setname question b using `bvals', keep(master match)

assert _merge == 3

generate double again = .

replace again = va / vb if op == "ratio"

replace again = va - vb if op == "diff"

replace again = va / vb * 100 if op == "pct"

assert !missing(again)

assert abs(value - again) <= 1e-6 * max(1, abs(again))

count

display "3. derived figures recomputed: " r(N)
