* ERW, the Attention and Friction indices (/attention): five headline figures rebuilt from attention_story_links.csv
* (session 7007, chain 301). Method: docs/methods/attention.md. The full replication of every figure of the page's file
* is replicate.py beside this file.
*
* This do-file has not been run: Stata is not installed on the machine that wrote it. Samuel runs it.
* Expected values (the tables of 16 November 2026, built at 09:24 UTC; computed with Python's csv reader on the same
* file, the one row of week 2026-11-16 left out: a listing dated after it was read, in no week of the corpus):
*   1. classified stories in the weeks of the corpus:                 8,119
*   2. energy stories (seven sectors and other energy):                5,024
*   3. energy stories that report opposition:                            250  (Friction Index 4.98 percent)
*   4. data center stories, and those that report opposition:      798 and 90
*   5. data center Friction Index over the classified weeks:          11.28 percent
* (The memo of 6 November gives 90 of 799, 11.3 percent: the 799th was the listing now left out.)

version 16
clear all
local f "attention_story_links.csv"

tempname fh
file open `fh' using "`f'", read text
local n 0
file read `fh' line
while substr(`"`line'"', 1, 1) == "#" {
    local ++n
    file read `fh' line
}
file close `fh'
local h = `n' + 1
import delimited using "`f'", varnames(`h') rowrange(`=`h' + 1') stringcols(_all) bindquote(strict) encoding("utf-8") clear

drop if week >= "2026-11-16"
display "1. classified stories: " _N
gen energy = inlist(sector, "datacenters", "transmission", "gas", "nuclear", "solar_wind", "storage", "oil_lng", "other_energy")
gen opp = (opposition == "true")
count if energy
local e = r(N)
display "2. energy stories: " `e'
count if energy & opp
display "3. energy opposition stories: " r(N) ", Friction Index " %5.2f 100 * r(N) / `e'
count if sector == "datacenters"
local d = r(N)
count if sector == "datacenters" & opp
local o = r(N)
display "4. data center stories: " `d' ", opposition: " `o'
display "5. data center Friction Index: " %5.2f 100 * `o' / `d'
