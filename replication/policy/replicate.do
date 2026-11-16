* ERW, the policy monitor (/policy?view=monitor): five headline figures rebuilt from policy_actions.csv (session 7006,
* chain 301). Method: docs/methods/policy_monitor.md, sections 14 and 16. The full replication of the monitor's file,
* record by record, is replicate.py beside this file.
*
* This do-file has not been run: Stata is not installed on the machine that wrote it. Samuel runs it.
* Expected values (the table of 16 November 2026, pulled at 09:13 UTC; computed with Python's csv reader on the same
* file):
*   1. documents held:                                              2,063
*   2. documents that state at least one dated step (dates):         1,401
*   3. documents whose body is FERC:                                   959
*   4. documents scored at significance 5 or more (of 2,049 scored):   404
*   5. comment deadlines stated (comments_due steps, all documents): 1,064
* (After the next pull with session 7006's fill_bare, the 27 DOE releases without fields gain theirs; figures 1, 3, 4
* do not move; 2 and 5 can only rise.)

version 16
clear all
local f "policy_actions.csv"

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

display "1. documents held: " _N
count if strtrim(dates) != ""
display "2. documents with a dated step: " r(N)
count if body == "FERC"
display "3. FERC documents: " r(N)
destring significance, gen(sig) force
count if sig >= 5 & !missing(sig)
display "4. documents of significance 5 or more: " r(N)
gen ncd = (strlen(dates) - strlen(subinstr(dates, "comments_due=", "", .))) / strlen("comments_due=")
quietly summarize ncd
display "5. comment deadlines stated: " r(sum)
