* ERW, the company database (/companies): five headline figures rebuilt from the public table company_links.csv
* (session 7005, chain 301). Method: docs/methods/companies.md. The full replication of every figure of the page files
* is replicate.py beside this file.
*
* This do-file has not been run: Stata is not installed on the machine that wrote it. Samuel runs it.
* Expected values (the tables of 16 November 2026, the company tables built at 09:04 UTC; computed with Python's csv
* reader on the same file, which replicate.py's 381,721 comparisons agree with):
*   1. companies listed (with at least one public row):                       12,724
*   2. companies that operate a generator in EIA-860M:                         6,060
*   3. operating nameplate MW of those companies, summed:                      1,423,491.7
*   4. the largest by operating MW: company:eia-6452 (Florida Power & Light),  40,818.1
*   5. NRC reactors with a public licensee or operator link:                  95
*
* Read the file: its header lines begin with "#"; they are counted, then the column names line is read.
* Note: a reader that treats "#" as a comment anywhere in a line (pandas' comment="#") drops rows whose names hold
* one ("Company #2"): 12,714 companies instead of 12,724. Stata's import delimited does not.

version 16
clear all
local f "company_links.csv"

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

keep if license == "public"

* 1. companies listed
preserve
    bysort company_id: keep if _n == 1
    display "1. companies listed: " _N
restore

* 5. reactors
preserve
    keep if input_table == "nrc_power_reactors" & inlist(role, "licensee", "operator")
    bysort input_row: keep if _n == 1
    display "5. NRC reactors linked: " _N
restore

* 2 to 4. operating generators
keep if input_table == "eia860m_operating_generators"
destring mw, replace force
collapse (sum) mw, by(company_id)
display "2. companies that operate a generator: " _N
quietly summarize mw
display "3. operating nameplate MW summed: " %12.1f r(sum)
gsort -mw
display "4. the largest: " company_id[1] ", " %9.1f mw[1] " MW"
