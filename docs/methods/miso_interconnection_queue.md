# MISO interconnection queue (held as of 30 September 2026; MISO pulls paused)

Energy Research Warehouse (ERW), method note written in session 2166 (chain 094) for a table of the queue connector of session 8.

Tables: `miso_interconnection_queue`

## MISO is paused

Since 4 October 2026 every pull of MISO's own servers is paused, by Samuel's ruling at the close of session 89, pending a review of MISO's terms by a person (`docs/methods/miso_pause.md`). MISO's terms of use say: "You agree not use any automated means, including, without limitation, agents, robots, scripts, or spiders, to access, monitor, or copy any part of this Website or the App." The pause is held in `warehouse/metadata/paused_sources.csv`; `iso_queues.py` asks `iso_prices.paused("miso")` before MISO and makes no request. **The table stays exactly as it is**: `run_status.csv` records the MISO queue `skipped` ("PAUSED since 2026-10-04 ...") on 5 and 12 October 2026. Only a person lifts the pause.

## Publisher and address

Midcontinent Independent System Operator (MISO), Generator Interconnection Queue, MISO's giqueue API `https://www.misoenergy.org/api/giqueue/getprojects` (page `https://www.misoenergy.org/planning/resource-utilization/GI_Queue/`), read with gridstatus 0.36.0 (`MISO.get_interconnection_queue`). Source id `miso:interconnection_queue`. Connector: `warehouse/connectors/iso_queues.py` (session 8).

Schedule: the step `iso_queues` of `warehouse/run_daily.sh` (weekly on Mondays UTC, or `QUEUES=1`, on the GitHub runner); for MISO it is skipped while the pause stands.

## How it differs from the NYISO queue note

The shape and rules are those of `docs/methods/nyiso_interconnection_queue.md`. For MISO:

- `capacity_mw` is the larger of MISO's summer and winter net MW (gridstatus), not a single requested figure.
- Six MISO statuses map to three: Active 1,085 and Pending Revision Approval 84 and Pending Transfer 7 to active; Done 552 and LEGACY: Done 5 to completed; Withdrawn 2,148 to withdrawn.
- `name` and `operator` are empty on every row; `actual_in_service_date` is empty on every row, so no completed row has a `status_date`.
- One queue id repeats: J2656, as `:1` (180.0 MW) and `:2` (0.0 MW), both active.
- `vintage` is written `2026-09-30T00:00:00Z`, a timestamp, where the other queues carry a day (`2026-10-19`).
- The license is ruled, as NYISO's is (below).

## Vintage and revision

Header line 1: "Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261004T023527Z-local"; then the table's own header, from run `20260926T000645Z` ("File holds 3870 rows"); last, "Restored from the Redivis draft (energy_research_warehouse) by scripts/sync.py". The rows are another run's: every row has `retrieved_at` 2026-09-30T23:33:22Z, the GitHub run `20260930T233227Z` that `run_status.csv` records `ok` for MISO.

## Shape and columns

Entities, 3,881 rows, 3,880 queue ids, key `miso_queue:<project number>`, 26 columns.

| `status` | Rows | MW |
|---|---|---|
| withdrawn | 2,148 | 363,968.4 |
| active | 1,176 | 257,207.1 |
| completed | 557 | 91,822.2 |

- `capacity_mw`: none blank, 87 zero, none negative, the largest 2,220; 712,997.7 MW in all.
- `queue_date`: 2015-04-15 to 2026-09-09; blank on 6.
- `withdrawn_date` on 2,126 of 2,148 withdrawn rows, and on 2 active (S1184, J4194) and 3 completed rows (S1001, R1014, R1009).
- `geo`: US-MI 530, US-IL 494, US-IN 468, US-AR 406, US-LA 387, US-MN 285, US-WI 249, US-IA 229, US-MS 204, US-MO 129, US-TX 91, others fewer; empty on 211.
- `fuel_technology`: Solar 1,781, Battery Storage 745, Wind 523, Hybrid 347, Gas 121, others fewer; blank on 325. Active MW: Solar 71,671.2 (383 rows), blank 54,051.8 (203), Battery Storage 48,806.2 (273), Gas 30,421.8 (53), Wind 29,171.1 (142), Hybrid 20,866.2 (108), Nuclear 2,170.1 (8).

## License

Header: "License: public (ISO public queue report)." `license_verdicts.csv` records MISO, read 7: "needs written permission", for public and for commercial use. `docs/licenses.md`: verdict "needs written permission", decided by MISO, flag public, "ruled: license needed from 2026-10-21", ERW verdict "unsettled".

## Checks (session 2166)

The figures in this note were computed from the rows of `warehouse/output/miso_interconnection_queue.csv`, read past its 13 header lines (scripts in `runs/c094/s2166/`).

- 3,881 rows; no `entity_id` twice.
- Against Berkeley Lab (`lbnl_interconnection_queue`, region MISO, requests through 2025; Berkeley Lab's file, not a pull of MISO's servers, so not paused): LBNL holds 5,424 MISO requests (withdrawn 3,263, 622,888.2 MW; active 1,646, 350,124.6 MW; operational 515, 73,274.0 MW), entities MISO 5,378 and MPC 46, queue dates 1995-11-08 to 2025-12-22. Limited to queue dates through 2025, this table holds 3,728 (withdrawn 2,146, 362,468.4 MW; active 1,028, 213,961.7 MW; completed 554, 91,682.2 MW). 3,616 of the 3,880 MISO ids are in LBNL; LBNL holds 1,808 ids this table does not (LBNL's queue dates begin in 1995, this table's in 2015). Of the matches: withdrawn in both 1,992; active in both 971; LBNL active, here completed 442 and withdrawn 126; LBNL operational, here completed 86. Capacity agrees within 0.5 MW in 3,560 of 3,617.

## Where the description and the data disagree

1. **The header describes another run.** The header's own lines are run `20260926T000645Z`, "File holds 3870 rows"; the file holds 3,881 rows, all retrieved at 2026-09-30T23:33:22Z by the GitHub run `20260930T233227Z`. The restore kept the older header over newer rows.
2. **`vintage`'s form.** The connector writes `vintage` as the retrieval day (`got[:10]`, YYYY-MM-DD); every row here has `2026-09-30T00:00:00Z`.
3. **The license line.** The header says public; the license record rules MISO "needs written permission" (`docs/licenses.md`, "ruled: license needed from 2026-10-21").
4. **Completed without a date.** The docstring gives `status_date` "the actual in-service date for completed rows where the ISO gives one"; MISO's rows carry no in-service date (empty on all 3,881), so no completed row has one, and 5 non-withdrawn rows carry a withdrawn date.

Recorded, not changed in session 2166: MISO is paused (docs/methods/miso_pause.md), so the table is not run again and its header stays as the archive restore left it; the license record governs its standing.

## What it does not hold

- Any change to MISO's queue after 30 September 2026, names, interconnecting entities and coordinates.
