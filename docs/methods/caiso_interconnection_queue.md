# CAISO interconnection queue

Energy Research Warehouse (ERW), method note written in session 2166 (chain 094) for a table of the queue connector of session 8.

Tables: `caiso_interconnection_queue`

## Publisher and address

California Independent System Operator (CAISO), Public Queue Report, the workbook `https://www.caiso.com/documents/publicqueuereport.xlsx` (the address every row cites; the header's report page is `http://www.caiso.com/PublishedDocuments/PublicQueueReport.xlsx`), read with gridstatus 0.36.0 (`CAISO.get_interconnection_queue`). Source id `caiso:interconnection_queue`. Connector: `warehouse/connectors/iso_queues.py` (session 8), the connector of `nyiso_interconnection_queue` and four other ISOs' queues.

Schedule: the daily run, `warehouse/run_daily.sh`, runs the connector weekly, on Mondays (UTC), or on any day with `QUEUES=1` (step `iso_queues`), on the GitHub runner (`.github/workflows/daily-prices.yml`). `run_status.csv` on the data machine records the CAISO queue `ok` on 30 September (three runs) and 5 and 12 October 2026; the header's run is 19 October.

## How it differs from the NYISO queue note

The shape, the status map's form and the rules are those of `docs/methods/nyiso_interconnection_queue.md`. For CAISO:

- One sheet, no blank rows dropped, no repeated queue id (no `:<n>` suffix).
- `iso_status` is CAISO's `ACTIVE`, `WITHDRAWN` or `COMPLETED`, mapped one to one; no suspended status.
- `operator` and `zone` are empty on every row; `transmission_owner` is filled (PGAE 1,082, SCE 804, SDGE 320, GLW 25, VEA 22, others fewer; empty on 2).
- `geo` includes `US-MX` on 18 rows: CAISO's state `MX` (Mexico) passes the connector's two-letter test.
- The license is not in question, as NYISO's is.

## Vintage and revision

A snapshot: the next run replaces it whole. Header line 1: "Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261019T211146Z-github"; the table's own header follows, retrieved by run `20261019T203101Z`, and "File holds 2278 rows". Every row has `retrieved_at` 2026-10-19T16:07:19Z and `vintage` 2026-10-19 (the retrieval day, not a date CAISO prints).

## Shape and columns

Entities, 2,278 rows, 2,278 queue ids; key `entity_id` `caiso_queue:<queue id>`; `entity_type` project; 26 columns (the 11 entity columns and 15 extra, as in the NYISO note).

| `status` | Rows | MW |
|---|---|---|
| withdrawn | 1,765 | 382,686.7 |
| active | 261 | 73,847.7 |
| completed | 252 | 35,662.4 |

- `capacity_mw`: none blank, 6 zero, none negative, the largest 3,200; 492,196.8 MW in all.
- `queue_date`: 1999-11-01 to 2023-03-02; by year, 361 in 2021, 2 in 2022 and 4 in 2023.
- `status_date`: the withdrawn date on 1,726 of 1,765 withdrawn rows; the in-service date on 239 of 252 completed rows; empty on every active row.
- `fuel_technology`: Photovoltaic 693, Storage 485, Photovoltaic + Storage 243, Wind Turbine 189, Storage + Photovoltaic 178, Steam Turbine 158, others fewer. Active MW by type: Storage + Photovoltaic 23,529.9 (55 rows), Storage 22,771.5 (85), Photovoltaic + Storage 18,526.0 (81), Wind Turbine 2,705.8 (10).
- `geo`: US-CA 2,076, US-NV 104, US-AZ 72, US-MX 18, US-ID 2, US-NM 1, US-WY 1; empty on 4.
- `lat` and `lon` empty on every row.

## What is and is not filled

Values as gridstatus reads them; dates as CAISO's, YYYY-MM-DD; nothing is filled. A status not in the map, a non-numeric capacity or an unparseable date fails the table.

## License

Header: "License: public (ISO public queue report)." `license_verdicts.csv` records CAISO, read 3: "may be public", for public and for commercial use. `docs/licenses.md`: "may be public", flag public, ERW verdict public.

## Checks (session 2166)

The figures in this note were computed from the rows of `warehouse/output/caiso_interconnection_queue.csv`, read past its 12 header lines (scripts in `runs/c094/s2166/`).

- 2,278 rows, as the header states; no `entity_id` twice.
- Against Berkeley Lab (`lbnl_interconnection_queue`, region CAISO, requests through 2025, retrieved 2026-10-02): LBNL holds 2,868 CAISO requests (withdrawn 2,200, 626,874.4 MW; active 432, 190,717.1 MW; operational 235, 37,806.2 MW; suspended 1, 58.8 MW), queue dates 1999-11-01 to 2023-04-17. Every one of the 2,278 CAISO queue ids is in LBNL; LBNL holds 590 ids CAISO's report no longer lists. Of the 2,278 matched one to one, statuses agree in 2,209 (withdrawn 1,718, active 258, operational and completed 233); 47 LBNL active rows are now withdrawn, 19 now completed, 2 LBNL operational rows are active here and 1 suspended row active. Capacity agrees within 0.5 MW in 1,376 of 2,278 (LBNL's capacity is the sum of its type components, mw_1 to mw_3).

## Where the description and the data disagree

1. **Mexico as a US state.** The connector writes `geo` `US-<state>` for any two-letter state; 18 rows with CAISO's state `MX` carry `geo` `US-MX`, which is not a US subdivision.
2. **Retrieval time before the run.** The header's run is `20261019T203101Z` (20:31 UTC); every row's `retrieved_at` is 2026-10-19T16:07:19Z, 4 hours 24 minutes before that run began. The file was rebuilt from the archive (header line 1), which the header does not reconcile.

Recorded, not changed in session 2166: the 18 rows with `geo` US-MX come from the queue connector's two-letter test, which takes Mexico's code as a state's; the retrieval times are the archive restore's (the header's first line says the table was rebuilt from the archive).

## What it does not hold

- Coordinates, interconnecting entities, zones, and any earlier snapshot in the table itself.
- The 590 requests Berkeley Lab holds that CAISO's current report does not.
