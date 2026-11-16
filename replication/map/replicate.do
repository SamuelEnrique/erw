* ERW, the project map (/map, the Projects tab): the tool's five headline figures, rebuilt from EIA's own workbook.

* Method: docs/methods/map.md, sections 3, 5 and 7. Session 7601, chain 305, 16 November 2026.

* Before this file: python replication/map/fetch_rows.py --units-only writes rows/units.csv from EIA's workbook of the
* month the page's file names (Form EIA-860M, public domain; no key is needed). Run this file from its own folder.

* This do-file has not been run: Stata is not installed on the machine that wrote it. "python replicate.py --headline"
* follows it step for step on the same file and prints the same five lines.

* Expected values, on EIA's inventory of September 2026 (the workbook last modified 23 October 2026, read 16 November 2026):

*   1. operating units: 28,712

*   2. operating units, nameplate megawatts: 1,423,491.7

*   3. planned units: 2,361

*   4. planned units, nameplate megawatts: 290,264.2

*   5. batteries (storage units whose prime mover is BA), operating and planned: 1,640

* The figures move with EIA's inventory each month: after a new fetch, compare with python replicate.py --headline, not with the lines above.

clear all

* The file has one comment line; the column names are on line 2 and the units start on line 3. Every column is read as text,
* so that a generator id of "NA" (two units have one) stays the text it is.

import delimited using "rows/units.csv", delimiter(comma) varnames(2) rowrange(3) stringcols(_all) bindquote(strict) clear

destring nameplate_mw, replace

* 1 and 2: the operating units (EIA's sheets Operating and Operating_PR) and their nameplate megawatts

count if kind == "operating"

display "1. operating units: " %9.0fc r(N)

quietly summarize nameplate_mw if kind == "operating"

display "2. operating units, nameplate megawatts: " %13.1fc r(sum)

* 3 and 4: the planned units (EIA's sheets Planned and Planned_PR)

count if kind == "planned"

display "3. planned units: " %9.0fc r(N)

quietly summarize nameplate_mw if kind == "planned"

display "4. planned units, nameplate megawatts: " %13.1fc r(sum)

* 5: a battery is a unit of EIA's four storage technologies whose prime mover code is BA (the note, section 5)

generate byte storage = inlist(technology, "Batteries", "Flywheels", "Hydroelectric Pumped Storage", "Natural Gas with Compressed Air Storage")

count if storage == 1 & prime_mover == "BA"

display "5. batteries, operating and planned: " %9.0fc r(N)
