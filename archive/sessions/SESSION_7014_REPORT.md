# Session 7014 report: storage, demand, curtailment and queues replicated (the done line's tools 21 to 24); two stale pages fixed at the cause

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0.

## /storage (tool 21)

- **`replication/storage/replicate.py`**: the page reads the live set; the script reads the same rows (the fleet, the daily cycle, EIA-930's and CAISO's battery output, the buildout, the owners) and compares each with the warehouse's tables, and recomputes the fleet's sums: **63,075 of 63,075** after its finding.
- **Its finding** (`docs/reviews/storage-faults-2026-11-16.md` row 1): 53 values of CAISO's battery output and daily cycle (9, 17 and 20 October, 11 November) differed: the live set held CAISO's revised values (read again by the runner on 5 November), the tables of record the values of 20 October. CAISO's history files of the last 40 days read again under the lock (`caiso_outlook.py --days 40`: 32,832 rows replaced), the daily cycle rebuilt, archived (900 rows), both loaded. Snapshots `before-load7014` and `after-load7014`: 0 differences.
- **`replicate.do`**: five sums of the fleet (not run).

## /demand (tool 22)

- **`replication/demand/replicate.py`**: every figure of `demand_growth.json` rebuilt from EIA-930's nine workbooks (openpyxl the one library beyond Python's own): **24,241 of 24,245** on the workbooks of 2 November. The four others are the Lower 48's September and October 2026 and one partly summed last hour, which move with each day's workbook while EIA fills in late hours (October's mean: 460,798.6 MW on 2 November, 460,894.6 in the page, 461,062.9 on 9 November): not a fault.
- Three rules the method note left implicit, now written in it: an hour's four neighbours are the nearest held above zero; the hours left out are counted to the workbook's last row (EIA's blank last day included); California's emptied hour has no row. The change of a cell is the change of the two printed means.
- **`replicate.do`**: five figures of ERCOT (not run).

## /curtailment (tool 23)

- **`replication/curtailment/replicate.py`**: California's profile and Texas's hours and days rebuilt from their tables: **11,515 of 11,515** after its findings (`docs/reviews/curtailment-faults-2026-11-16.md`).
- **Row 1, fixed at the cause**: the profile was built 5 October (months to September) and `/mix/v2` 19 October. The run of 6 November built both on the GitHub runner from restored tables shorter than the history; session 2885 put the files back, while demand growth's file, the monthly mark, stayed, so neither was built again. Both builds left the runner's monthly job (`run_monthly.sh`; `scheduled.py` `DATA_MACHINE`) and are built on the data machine (session 7015 placed them in the weekly table steps). Both rebuilt to October 2026; the profile loaded (6 rows written; snapshots `before-load7014b`, `after-load7014b`: 0 differences); the mix's rows were already in the live set (0 written; `before-load7014c`, `after-load7014c`: 0 differences).
- **Row 2**: the September battery figures followed CAISO's revision (fixed by the rebuild).
- **Row 3, for Samuel**: ERCOT's wind High Sustained Limit at 07:00 UTC on 1 November (the second 01:00 Central) is 11,385.93 MW against about 5,000 around it, and 06:00 has none: it looks like the two hours' limits summed. The posting was read by the runner and is not saved here; ruling 2 allows no new request to ERCOT's MIS. The day is not whole and enters no month.
- **`replicate.do`**: five figures of California (not run). Shares, free energy and worth are not yet replicated.

## /queues (tool 24)

- **`replication/queues/replicate.py`**: every figure of `queues.json` from `lbnl_interconnection_queue`: **17,254 of 17,254** (Berkeley Lab writes the region "ISO-NE"). **`replicate.do`**: five figures of the whole United States (not run).

## Decisions made without you

- The demand mirror compares with the workbooks of 2 November, the nearest held to the page's build of 6 November.

## For Samuel's ruling

- Curtailment row 3 (ERCOT's limit at the autumn hour).
