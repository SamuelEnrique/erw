* ERW, the interconnection queue explorer (/explore/interconnection): the page's five headline figures, rebuilt.

* Method: docs/methods/interconnection_explorer.md ("What it draws", "How a figure is written") and docs/methods/energy_projects.md ("Queue statistics"). Session 7509, chain 304, 16 November 2026.

* The page does no arithmetic: each figure is one row of iso_queue_statistics. This file reads that table as CSV (replication/interconnection/fetch_rows.py copies it into rows/; the table is held by grid, so it is not in git), prints the five figures three views open on, and checks the two rules of the note that tie the table's rows to each other: the four statuses of an entry year make up its positions entered, and the withdrawn share is the withdrawn positions over the positions entered. Set the folder that holds the table in the line "global tables" below. Run this file from its own folder.

* This do-file has not been run: Stata is not installed on the machine that wrote it. "python replicate.py --headline" reads the same rows and printed the lines below; "python replicate.py" checks the two rules for every queue and entry year (139 of 139).

* Expected values, on iso_queue_statistics as built on 21 October 2026 (1,511 rows; CAISO's, ERCOT's and SPP's queues as pulled on 19 October 2026). Each view opens on the newest entry year that is over:

*   1. CAISO, positions entered 2023: 4

*   2. CAISO, positions entered 2023 that reached operation: 0

*   3. CAISO, withdrawn share of the positions entered 2023: 1.00

*   4. ERCOT, MW entered 2025 and MW of them still waiting: 104,174.94 and 83,226.25

*   5. SPP, positions entered 2025 and the withdrawn share: 421 and 0.48

* The first three are true of CAISO's public queue report and far from the requests made in 2023 (Berkeley Lab's Queued Up counts 594): the note, "What a queue does not hold". All five move when the table is rebuilt from a newer pull of the queues.

clear all

global tables "rows"

* A standard ERW table opens with comment lines that begin with #, then a line of column names; its first four columns are entity, variable, ts_utc and value.

import delimited using "$tables/iso_queue_statistics.csv", delimiter(comma) varnames(nonames) stringcols(_all) bindquote(strict) clear

drop if substr(v1, 1, 1) == "#" | v1 == "entity"

keep v1 v2 v3 v4

rename (v1 v2 v3 v4) (entity variable ts_utc value)

destring value, replace force

gen queue = substr(entity, 1, strpos(entity, ":") - 1)

gen year = real(substr(entity, strpos(entity, "queue_") + 6, 4))

* The page shows CAISO, ERCOT and SPP; NYISO, MISO and ISO-NE are held (license needed) and are not read.

keep if inlist(queue, "caiso", "ercot", "spp")

keep queue year variable value

reshape wide value, i(queue year) j(variable) string

rename value* *

* ---- The five figures, as the page writes them: positions whole, MW and the share with two decimals.

format positions_* %12.0fc

format mw_* %14.2fc

format withdrawal_rate %6.2f

* 1, 2 and 3: expected 4, 0 and 1.00

list queue year positions_entered positions_operating withdrawal_rate if queue == "caiso" & year == 2023, noobs

* 4: expected 104,174.94 and 83,226.25

list queue year mw_entered mw_waiting if queue == "ercot" & year == 2025, noobs

* 5: expected 421 and 0.48

list queue year positions_entered withdrawal_rate if queue == "spp" & year == 2025, noobs

* ---- The note's two rules, on every entry year of the three queues.

* The four statuses make up the positions entered (ERCOT has no withdrawn row: it counts as none).

gen parts = positions_operating + cond(missing(positions_withdrawn), 0, positions_withdrawn) + positions_waiting + positions_status_not_stated

assert parts == positions_entered

* The withdrawn share is withdrawn over entered, by count (the table rounds to six decimals).

assert abs(withdrawal_rate - positions_withdrawn / positions_entered) < 0.000001 if !missing(withdrawal_rate)

* An MW row is absent only where the status has no position that states a capacity: for the three queues, only where the status has no position at all.

foreach s in operating withdrawn waiting status_not_stated {

    count if missing(mw_`s') & positions_`s' > 0 & !missing(positions_`s')

    assert r(N) == 0

}

display "the five figures are listed above; the three rules hold on every entry year of CAISO, ERCOT and SPP"
