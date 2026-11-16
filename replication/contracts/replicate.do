* ERW, the contracts page (/contracts): the tool's headline figures, rebuilt from the rows.

* Method: docs/methods/contracts.md, sections 3, 5, 6 and 7. Session 7501, chain 304, 16 November 2026.

* Before this file: python replication/contracts/copy_rows.py writes rows/contracts_slim.csv from ferc_eqr_contracts in
* warehouse/output (the table is internal, so its rows are not in git with the replication). Run this file from its own folder.

* This do-file has not been run: Stata is not installed on the machine that wrote it. "python replicate.py --headline"
* follows it step for step on the same table and prints the same lines.

* Expected values, on the table as retrieved on 4 October 2026 at 03:50 UTC (the filings for 2026 Q2, 186,873 rows):

*   1. contract rows filed for the quarter: 186,873

*   2. rows that file their rate as a number: 81,718

*   3. rows that file words and no number: 104,952

*   4. energy contracts in force: 22,808

*   5. energy contracts in force that state megawatts, and the megawatts: 356, 31,402.3

*   6. rows of energy, capacity and tolling executed in 2026 Q2: 227

*   7. tolling rows, and their contracts: 382, 217

* The figures change only when the data machine pulls a new quarter: after a new copy, compare with python replicate.py --headline.

clear all

* The file has one comment line; the column names are on line 2 and the rows start on line 3.

import delimited using "rows/contracts_slim.csv", delimiter(comma) varnames(2) rowrange(3) stringcols(_all) bindquote(strict) clear

* 1. One row is one product of one agreement, as the seller filed it.

quietly count

display "1. contract rows filed for the quarter: " %9.0fc r(N)

* 2 and 3. A rate is a number when the filer gave one; rate_description is 1 when the filer wrote words. A rate that is not a number is missing, never zero.

destring rate, generate(rate_n) force

quietly count if rate_n < .

display "2. rows that file their rate as a number: " %9.0fc r(N)

quietly count if rate_n >= . & rate_description == "1"

display "3. rows that file words and no number: " %9.0fc r(N)

* 6. Signed in 2026 Q2: the execution date, for the three products of a power sale (the names are in capitals in this file).

quietly count if inlist(product, "ENERGY", "CAPACITY", "TOLLING ENERGY") & event_date >= "2026-04-01" & event_date < "2026-07-01"

local signed = r(N)

* 7. The tolling tag: the product name, every row filed, a terminated contract's too.

generate contract = company_id + "|" + contract_id

quietly count if product == "TOLLING ENERGY"

local tolling_rows = r(N)

egen byte first_tolling = tag(contract) if product == "TOLLING ENERGY"

quietly count if first_tolling == 1

local tolling_contracts = r(N)

* 4. In force: no actual termination date filed (status in_force). A contract is the filer's company identifier with its own contract identifier.

keep if status == "in_force" & product == "ENERGY"

egen byte first_row = tag(contract)

quietly count if first_row == 1

display "4. energy contracts in force: " %9.0fc r(N)

* 5. Megawatts stated: the quantity when its units are MW, a thousandth of it when kW; zero is no quantity; any other unit is not megawatts.
*    A row above 6,809 MW (the largest power station operating in the United States, EIA-860M, vintage 2026-08) is left out.
*    Per contract, the largest MW any of its rows states; then the sum.

generate units_u = upper(strtrim(units))

destring quantity, generate(quantity_n) force ignore(",")

generate double mw = quantity_n if units_u == "MW" & quantity_n > 0 & quantity_n < .

replace mw = quantity_n / 1000 if units_u == "KW" & quantity_n > 0 & quantity_n < .

replace mw = . if mw > 6809 & mw < .

collapse (max) mw, by(contract)

quietly summarize mw

display "5. energy contracts in force that state megawatts, and the megawatts: " %9.0fc r(N) ", " %12.1fc r(sum)

display "6. rows of energy, capacity and tolling executed in 2026 Q2: " %9.0fc `signed'

display "7. tolling rows, and their contracts: " %9.0fc `tolling_rows' ", " %9.0fc `tolling_contracts'
