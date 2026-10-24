# SPP interconnection queue

Energy Research Warehouse (ERW), method note written in session 2166 (chain 094) for a table of the queue connector of session 8.

Tables: `spp_interconnection_queue`

## Publisher and address

Southwest Power Pool (SPP), Generation Interconnection Queue summary, `https://opsportal.spp.org/Studies/GenerateSummaryCSV` (page `https://opsportal.spp.org/Studies/GIActive`), read with gridstatus 0.36.0 (`SPP.get_interconnection_queue`). Source id `spp:interconnection_queue`. Connector: `warehouse/connectors/iso_queues.py` (session 8).

Schedule: the daily run, `warehouse/run_daily.sh`, weekly on Mondays (UTC) or with `QUEUES=1` (step `iso_queues`), on the GitHub runner (`.github/workflows/daily-prices.yml`). `run_status.csv` records the SPP queue `ok` on 30 September and 5 and 12 October 2026; the header's run is 19 October.

## How it differs from the NYISO queue note

The shape and rules are those of `docs/methods/nyiso_interconnection_queue.md`. For SPP:

- `iso_status` is SPP's "Status (Original)" text, eleven values mapped to four statuses, the only queue here with `suspended` (IA FULLY EXECUTED/ON SUSPENSION, 22 rows).
- 34 rows have no status in SPP's file (affected-system requests, per the docstring); `status` and `iso_status` stay empty, not guessed.
- `actual_in_service_date` is SPP's Commercial Operation Date, and it equals `proposed_in_service_date` on all 3,078 rows (below).
- `name` and `operator` are empty on every row; `transmission_owner` is filled (SPS 615, OGE 347, AEP 341, NPPD 248, WERE 215, others fewer; empty on 99).

## Vintage and revision

A snapshot, replaced whole by the next run. Header line 1: rebuilt from the ERW archive as of run `20261019T211146Z-github`; the table's header, run `20261019T203101Z`, "File holds 3078 rows". `retrieved_at` is 2026-10-19T16:08:11Z on 3,075 rows and 2026-10-19T20:31:58Z on 3 (GEN-2023-172, GEN-2017-220, GEN-2017-150); `vintage` 2026-10-19 on all.

## Shape and columns

Entities, 3,078 rows, 3,078 queue ids, key `spp_queue:<GEN number>`, 26 columns.

| `status` | Rows | MW | SPP's statuses |
|---|---|---|---|
| withdrawn | 2,056 | 419,282.3 | WITHDRAWN 2,008, TERMINATED 48 |
| active | 627 | 134,998.1 | IA FULLY EXECUTED/ON SCHEDULE 318, DISIS STAGE 134, IA PENDING 82, SPECIAL STUDY 48, FACILITY STUDY STAGE 44, ICS 1 |
| completed | 339 | 51,198.2 | IA FULLY EXECUTED/COMMERCIAL OPERATION |
| (none) | 34 | 1,254.0 | none in the file |
| suspended | 22 | 3,851.9 | IA FULLY EXECUTED/ON SUSPENSION |

- `capacity_mw`: none blank, 10 zero, none negative, the largest 4,000; 610,584.4 MW in all.
- `queue_date`: 1999-09-20 to 2026-08-26; blank on 48.
- `status_date`: the withdrawn date on 1,516 of 2,056 withdrawn rows; the commercial operation date on 297 of 339 completed rows.
- `geo`: US-OK 807, US-KS 614, US-TX 443, US-NE 373, US-NM 231, US-MO 188, US-CO 90, US-ND 88, US-SD 72, US-AR 63, US-LA 33, others fewer; empty on 27 (one with state `TX/OK`).
- `fuel_technology`: Wind 1,199, Solar 586, Battery/Storage 374, Hybrid - Solar/Storage 201, Thermal - Gas 161, others fewer, several of them the same technology under two spellings (Solar and Solar - Photovoltaic; Wind and Wind - Wind; Battery/Storage and Battery/Storage - Battery). Active MW: Battery/Storage 24,220.1 (155 rows), Solar 18,868.6 (105), Hybrid - Solar/Storage 17,221.8 (81), Thermal - Gas 16,973.6 (40), Wind 15,143.3 (78).

## License

Header: "License: public (ISO public queue report)." `license_verdicts.csv` records SPP, read 6: "may be public"; if commercial, "needs written permission". `docs/licenses.md`: "may be public", flag public, "needs written permission" if the ERW sells anything, ERW verdict public.

## Checks (session 2166)

The figures in this note were computed from the rows of `warehouse/output/spp_interconnection_queue.csv`, read past its 12 header lines (scripts in `runs/c094/s2166/`).

- 3,078 rows, as the header states; no `entity_id` twice.
- Against Berkeley Lab (`lbnl_interconnection_queue`, region SPP, requests through 2025): LBNL holds 2,837 SPP requests (withdrawn 1,846, 382,862.9 MW; active 683, 151,152.0 MW; operational 299, 45,090.3 MW; suspended 9, 1,207.8 MW), queue dates 2000-05-31 to 2025-12-19. Every LBNL SPP id is in this table, which holds 241 more. Of the 2,837 matches: withdrawn in both 1,846; active in both 487; operational and completed 298; LBNL active, here withdrawn 155, completed 28, suspended 13; suspended in both 4. Capacity agrees within 0.5 MW in 2,815 of 2,837. Limited to queue dates through 2025, this table holds 2,972 (withdrawn 2,023, 415,671.9 MW; active 579, 126,528.3 MW; completed 322, 50,630.1 MW; suspended 22; no status 26).

## Where the description and the data disagree

1. **"Actual" in-service dates in the future.** The docstring gives `actual_in_service_date` as the actual in-service date and `status_date` as that date for completed rows; for SPP the column is the Commercial Operation Date and equals `proposed_in_service_date` on all 3,078 rows. 551 active rows carry an "actual" date after the retrieval day (for example GEN-2026-SR5, 2027-12-01).
2. **One snapshot, two retrieval times.** The connector stamps every row of a snapshot with one retrieval time; 3 rows carry 2026-10-19T20:31:58Z and 3,075 carry 2026-10-19T16:08:11Z, which is 4 hours 23 minutes before the header's run `20261019T203101Z` began. The file was rebuilt from the archive (header line 1).

Recorded, not changed in session 2166: the actual in-service date equals the proposed one on every row, as the queue connector maps SPP's file; a reader should take neither as a completed project's date.

## What it does not hold

- Names, interconnecting entities, coordinates, zones; a status for the 34 affected-system requests.
