# ISO-NE's interconnection queue, one row a queue position (Interconnection Request Tracking Tool)

Energy Research Warehouse (ERW), method note written in session 2222 (chain 098) for a table first written on 26 September 2026 (session 8, run `20260926T000645Z`, `archive/sessions/SESSION_8_REPORT.md`). The other grids' queues from the same connector have their own notes (`caiso_interconnection_queue.md`, `ercot_interconnection_queue.md`, `miso_interconnection_queue.md`, `nyiso_interconnection_queue.md`, `spp_interconnection_queue.md`).

Tables: `isone_interconnection_queue`

## Publisher and address

ISO New England (ISO-NE), Interconnection Request Tracking Tool (IRTT) queue, report page `https://irtt.iso-ne.com/reports/external`; the file cited is `https://irtt.iso-ne.com/reports/external?AspxAutoDetectCookieSupport=1`, read with gridstatus 0.36.0 (`ISONE.get_interconnection_queue`). Source id `isone:interconnection_queue`. Raw responses under `warehouse/raw/iso_queues/<run_id>/`.

Connector: `warehouse/connectors/iso_queues.py` (session 8), `[isos ...] [--out-dir DIR]`, one table a grid. ISO-NE's statuses map Active to active, Withdrawn to withdrawn and Completed to completed; a status outside the map fails the grid. A queue id on several rows (units, phases) gets `:<n>` in ISO-NE's row order.

Schedule: the daily run, `warehouse/run_daily.sh`, runs `iso_queues.py` on Mondays (UTC) or any day with `QUEUES=1`, on the GitHub runner (`.github/workflows/daily-prices.yml`). `run_status.csv` records 10 runs of this table from 20260926T000645Z (local) to 20261012T144744Z (github), all ok; the copy here is of the Monday run of 19 October 2026.

## Vintage and revision

Header line 1: "Rebuilt from the ERW archive by warehouse/restore_tables.py (session 305), as of run 20261019T211146Z-github"; the run's own header: "Retrieved: 20261019T203101Z (UTC) ... via gridstatus 0.36.0". Every row has `retrieved_at` 2026-10-19T16:08:12Z and `vintage` 2026-10-19 (the retrieval date; the connector sets `vintage` to `retrieved_at`'s day). A snapshot: each run replaces the rows; earlier queues are in the archive and the raw files.

## Shape and variables

Entities, 1,751 rows, `entity_type` project, `entity_id` `isone_queue:<queue id>[:<n>]`; 1,601 distinct queue ids, 92 of them over 242 rows. Columns: `name` (never blank), `geo` `US-<state>`, `capacity_mw` (ISO-NE's requested MW as gridstatus reads it), `status` and `iso_status`, `status_date`, `operator`, then `queue_id`, `county`, `state`, `poi`, `zone`, `transmission_owner`, `fuel_technology`, and the dates `queue_date`, `proposed_in_service_date`, `actual_in_service_date`, `withdrawn_date` (YYYY-MM-DD).

- Status: withdrawn 1,331 (169,620.1 MW), completed 364 (12,675.6 MW), active 56 (10,800.9 MW); `iso_status` maps one to one.
- Active MW by fuel: BAT 5,432, WND 3,209, blank 1,232, SUN 921, WAT BAT 7.
- States: MA 605, ME 408, CT 323, NH 138, RI 123, VT 109, NY 13, NB 1, blank 31. Load zones: ME 275, SEMA 218, WMA 213, CT 197, RI 155, NH 133, BHE 126, VT 113, SWCT 96, BOST 96, CMA 55, NOR 22, SME 9, blank 43.
- Fuel codes (EIA's): SUN 380, BAT 274, blank 265, WND 245, SUN BAT 139, NG 134, DFO NG 105, WAT 66, and others.
- Queue dates 1996-06-07 to 2025-01-14; the newest active request was queued on 2024-12-12, the oldest on 2017-07-28.

## Placing values in time, and what is filled

Dates are ISO-NE's, written as dates, a time of day dropped. `status_date` is the withdrawn date for a withdrawn row (1,189 of 1,331 have one) and the actual in-service date for a completed row where ISO-NE gives one; it gives none, so no completed row has a `status_date`. Nothing is filled: `capacity_mw` is blank on 278 rows (210 withdrawn, 68 completed) and zero on 152; two are negative, 148:4 (Comerford Unit #1, -17.0 MW, completed) and 438 (Potter Repowering, -21.2 MW, withdrawn), net reductions as ISO-NE states them (session 8, Decision 20). `lat` and `lon` are blank by design.

## License

Header: "License: public (ISO public queue report)." `license_verdicts.csv`, ISO-NE (read 4): "You are also hereby put on notice that the Content is protected by copyright under United States laws. Any duplication of the Content or non-personal use may violate copyright, trademark, and other laws. ...", verdict "needs written permission". `license_status.csv`: "license needed" from 2026-10-21, ISO-NE, "needs written permission". `docs/licenses.md`: verdict "needs written permission", decided by ISO-NE, flag public, "ruled: license needed from 2026-10-21", ERW verdict "unsettled"; its section on held figures still shown lists `/grid?grid=isone` and `/grid/isone` (36 figures each) from this table.

## Checks (session 2222)

The figures in this note were computed from the rows of `warehouse/output/isone_interconnection_queue.csv`, read past its 12 header lines (scripts `runs/c098/s2222/check_isone_queue.py` and `check_isone_queue2.py`).

- 1,751 rows, as the header states; no `entity_id` twice; every status mapped; no active row with a withdrawn or in-service date; no withdrawn date before its queue date.
- Against LBNL's queue (`lbnl_interconnection_queue`, "2026 edition (through 2025)", region ISO-NE, 1,282 rows): every LBNL queue id is here. LBNL's 982 withdrawn are 978 withdrawn and 4 completed here; its 228 operational are 222 completed and 6 withdrawn; its 72 active are 48 active, 10 completed and 14 withdrawn here. Capacity agrees within 0.5 MW for 1,164 of the 1,226 ids where both give one. LBNL's newest queue date is also 2025-01-14.

## Where the description and the data disagree

1. **The license.** The header says "public (ISO public queue report)" and `coverage.csv` flags the table public; the license record rules ISO-NE's data "license needed" from 2026-10-21 (ERW verdict unsettled), and two review pages still show figures from it.
2. **Columns the docstring describes that ISO-NE does not give.** "operator is the interconnecting entity": `operator` is blank in all 1,751 rows. `actual_in_service_date` is blank in all rows, so the docstring's in-service `status_date` never occurs; `transmission_owner` is blank in 1,105.
3. **A Canadian province as a US state.** The connector writes `US-<code>` for any two capital letters: queue id 1093 ("NB TA#1365950 HVDC", county "Salisbury, New Brunswick") has `geo` US-NB, which is not a US code.
4. **Retrieved before the run.** Every row's `retrieved_at` is 2026-10-19T16:08:12Z, 4 hours 23 minutes before the run named in the header (20261019T203101Z); the table does not say why.

Acted on in session 2222, in `warehouse/connectors/iso_queues.py`: only a U.S. state's or DC's code becomes a geo, so New Brunswick's "NB" (and CAISO's "MX", recorded in chain 094's note) leave geo blank, the state column keeping the ISO's word; the queues' next Monday run writes it. The license line, the blank operator and in-service columns and the retrieval times are recorded, not changed; no request to ISO-NE, whose data the license record rules unsettled.

## The session report against the table

`SESSION_8_REPORT.md` gave the ISO-NE queue of 26 September 2026 as 1,751 rows: 59 active, 1,329 withdrawn, 363 completed, "92 queue ids repeat over 242 rows (units)", and named ISO-NE 438 and 148:4 among the negative capacities. The copy of 19 October holds the same 1,751 rows, 92 ids over 242 rows and both negatives, with 56 active, 1,331 withdrawn and 364 completed: the report holds for its day, and the queue has gained no row since (its newest queue date is 2025-01-14).

## What it does not hold

- Coordinates, interconnecting entities and in-service dates (ISO-NE's file gives none to gridstatus); study stages, cluster assignments or costs; ISO-NE's earlier queues (in the archive and raw files); load requests.
