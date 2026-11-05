# NYISO interconnection queue

Energy Research Warehouse (ERW), method note written in session 696 (chain 045) for a table first written on 25 September 2026.

Tables: `nyiso_interconnection_queue`

## Publisher and address

New York Independent System Operator (NYISO), NYISO Interconnection Queue, the workbook
`https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx`, read with gridstatus 0.36.0
(`NYISO.get_interconnection_queue`). Connector: `warehouse/connectors/iso_queues.py` (session 8), which writes the
queues of six ISOs, one table each. Page: `https://www.nyiso.com/interconnections`.

## Vintage and revision

A snapshot: the table holds the queue as retrieved, and the next run replaces it whole (earlier snapshots stay in the
raw files and the archive). The daily run (`warehouse/run_daily.sh`) runs the connector weekly, on Mondays (UTC), or on
any day with `QUEUES=1`. No request ceiling is stated.

Held from coverage.csv: one snapshot, 2026-09-26T00:06:50Z (run 2026-09-26T00:06:45Z). Every row has that
`retrieved_at` and the `vintage` 2026-09-26T00:00:00Z (the retrieval day, not a date NYISO prints). Since 2026-09-27
NYISO's host answers GitHub's runners HTTP 202 with no body (`warehouse/metadata/known_gaps.csv`), so the scheduled run
skips it. Session 216 records that the workbook stays held until NYISO's license is answered. The file on the data
machine was rebuilt from the archive by `warehouse/restore_tables.py`, as of run `20261004T023527Z-local`.

The run log (`iso_queues_20260926T000645Z.log`): 1,350 rows with no queue id and no data dropped (blank rows gridstatus
reads from the withdrawn sheet); 4 rows share 2 queue ids, which get `:<n>` in NYISO's row order.

## Shape and variables

Entities. One row per queue position; `entity_type` `project`; key `entity_id` `nyiso_queue:<queue id>`, with `:<n>`
where an id repeats (`0031` and `0127A`, two rows each). No x_* fields; the extra columns are NYISO's fields.

| Column | Unit or form | From |
|---|---|---|
| `name` | text | Project Name |
| `geo` | `US-<state>` | State; empty where the state is not two letters |
| `lat`, `lon` | degrees | empty on every row |
| `capacity_mw` | MW | Capacity (MW), as gridstatus reads it |
| `status` | `active`, `withdrawn`, `completed` | NYISO's Status, mapped (STATUS_MAP) |
| `status_date` | YYYY-MM-DD | the withdrawn date for withdrawn rows, the in-service date for completed rows |
| `operator` | text | Interconnecting Entity |
| `queue_id`, `county`, `state`, `poi`, `zone`, `transmission_owner`, `fuel_technology` | text | NYISO's columns |
| `iso_status` | NYISO's word | Status |
| `queue_date`, `proposed_in_service_date`, `actual_in_service_date`, `withdrawn_date` | YYYY-MM-DD | NYISO's dates |

As of 23 October 2026: 1,814 rows, 1,812 queue ids.

| Status | Rows | MW |
|---|---|---|
| withdrawn | 1,453 | 320,210.0 |
| active | 210 | 30,874.6 |
| completed | 151 | 16,239.3 |

- Queue dates 1989-09-15 to 2026-08-25.
- `fuel_technology`: Energy Storage 533, Solar 390, Wind 287, AC Transmission 146, DC Transmission 57, other values
  fewer; empty on 212 rows. One value is NYISO's text `=Solid Waste`, kept as published.
- Of the active rows: Energy Storage 96 (13,460.1 MW), Solar 65 (6,678.9 MW), Wind 19 (3,463.6 MW).
- `geo`: US-NY 1,767, US-PA 29, US-NJ 10, US-DE 1, US-CT 1; empty on 6 (state `NY-NJ` 3, `NY-PA` 2, `Quebec` 1).
- `capacity_mw` is 0 on 191 rows; none is negative; the largest is 2,620.
- `operator` is empty on all 210 active rows. `zone` is empty on 363 rows; it holds NYISO's text, sometimes several
  zones (`I, J`).

## License

ERW verdict (docs/licenses.md, "Every table"): verdict today "needs written permission"; decided by NYISO; flag in
coverage.csv "public"; flag and verdict "ruled: license needed from 2026-10-21"; if the ERW sells anything "needs
written permission"; ERW verdict "unsettled". The document lists it: "`nyiso_interconnection_queue`: needs written
permission, by NYISO; license needed from 2026-10-21." The header's own line, "License: public (ISO public queue
report).", predates that ruling. NYISO's page (read 5) names no line to cite; cite "New York Independent System
Operator (NYISO), NYISO Interconnection Queue", with the retrieval date.

## Cross-check

None in the connector. It fails the table on a NYISO status not in its map, a non-numeric capacity, an unparseable date
or a row with data but no queue id; these are gates, not a comparison with another source.

## What it does not hold

- No coordinates: `lat` and `lon` are empty. County and point of interconnection are NYISO's text.
- No load projects: the workbook's sheet "Load Projects" is the table `nyiso_load_queue`.
- Only the columns above: any other field gridstatus reads from the workbook is not kept.
- No queue since 26 September 2026, and no history of earlier snapshots in the table itself.
- No interconnecting entity for an active position.
