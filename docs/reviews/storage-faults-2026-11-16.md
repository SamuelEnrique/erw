# Storage (/storage): faults found by its replication, 16 November 2026

Energy Research Warehouse (ERW), chain 301, session 7014 (data machine). Found by `replication/storage/replicate.py`, which compares every row the page reads from the live set with the warehouse's own tables. States: `open`, `fixed (<commit>)`, `ruling`, `not a fault`.

| # | Where | The figure | The fault | The fix | State |
|---|---|---|---|---|---|
| 1 | The fleet tab's CAISO battery output and the daily cycle (`caiso_battery_storage`, `storage_daily_cycle`) | 53 values, 9, 17 and 20 October and 11 November 2026 (e.g. 2026-10-17 09:45 UTC: 428 MW in the live set, 427 in the warehouse) | The live set held CAISO's revised values (re-read on 5 November by the runner and loaded on 6 November); the data machine's copy and the archive held the values read on 20 October: the revision was lost with the refused runs of 6 to 13 November and never reached the tables of record | CAISO's history files of the last 40 days read again under the data lock (`caiso_outlook.py --days 40`), the daily cycle rebuilt, validated, archived (900 rows), both tables loaded (13 November's newer revision too); snapshots before and after, 0 differences; the replication 63,075 of 63,075 | fixed (session 7014, wip/c301-tail) |
