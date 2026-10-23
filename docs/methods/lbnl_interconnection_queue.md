# US interconnection queue requests (Berkeley Lab's Queued Up data file, 2026 edition)

Energy Research Warehouse (ERW), method note written in session 2074 (chain 067) for a table first written on 2 October 2026 (session 62).

Tables: `lbnl_interconnection_queue`

## Publisher and address

Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition (`https://eta-publications.lbl.gov/publications/queued-2026-edition-characteristics`), its data file of requests through the end of 2025: `https://eta-publications.lbl.gov/sites/default/files/2026-05/lbnl_ix_queue_data_file_thru2025.xlsx`, sheet "03. Complete Queue Data" (the codebook is sheet "04. Data Codebook"). emp.lbl.gov answers automated requests with HTTP 403; the same file is on eta-publications.lbl.gov. Source id `lbnl:queued_up`. Connector: `warehouse/connectors/lbnl_queues.py` (session 62). No scheduled job runs it.

## Vintage and revision

One edition: the file retrieved 2 October 2026 at 09:16:25 UTC (Last-Modified 7 May 2026), written by run `20261002T091835Z`; `vintage` "2026 edition (through 2025)" on every row. Header: "File holds 38201 rows, one snapshot; the previous file held 38647 rows." The file on the data machine was rebuilt from the ERW archive by `warehouse/restore_tables.py` (as of run `20261004T023527Z-local`) and restored from the Redivis draft by `scripts/sync.py`.

A run replaces the table (`write_snapshot`). A file an earlier run saved under `warehouse/raw/lbnl_queues/` is read rather than downloaded again, so a new edition needs its address in the connector.

## Shape and variables

Entities, 38,201 rows, one per interconnection request; `entity_type` project; `entity_id` `lbnl:<Berkeley Lab's entity>:<q_id>`, unique. Where an (entity, q_id) pair repeats, the id takes the row number after a colon (276 rows); 9 `q_id` values are dates as Excel turned them ("2009-03-01 00:00:00"). `name` is the project name, else the `q_id` (25,113 rows). `geo` `US-<state>`, empty on the 1,235 rows without a state; `lat` and `lon` empty on every row; `operator` the utility.

| `status` (from `q_status`) | Requests | MW (`capacity_mw`) |
|---|---|---|
| withdrawn | 24,221 | 4,527,734.8 |
| active | 8,513 | 1,864,769.8 |
| operating (`operational`) | 4,789 | 567,536.1 |
| suspended | 668 | 137,204.1 |
| empty (`unknown`) | 10 | 1,167.0 |

`capacity_mw` is `mw_1` + `mw_2` + `mw_3`, filled on every row, 7,098,411.8 MW in all; 16 rows are negative (-336.7 MW together, as the file gives them). `status_date` is `on_date` for operating, `wd_date` for withdrawn, else `q_date`; it is empty on 10,230 rows (8,639 withdrawn without a withdrawal date, 1,500 operating without an online date).

Berkeley Lab's fields follow, renamed only where shown: `q_id`, `q_status`, `q_date` (1995-11-08 to 2025-12-24), `prop_date`, `on_date` (1982-06-30 to 2025-12-31), `wd_date` (1999-06-26 to 2026-01-16), `ia_date`, `ia_phase` (`IA_phase_clean`), `region`, `lbnl_entity` (`entity`, 57 values), `utility`, `state`, `county`, `fips_code`, `poi_name`, `service`, `project_type`, `type_clean`, `type_1` to `type_3`, `mw_1` to `mw_3`, `q_year`, `prop_year`. In the file on the data machine every filled `q_year` (37,536), `prop_year` (32,936) and `fips_code` (36,431) ends in ".0" ("2021.0", "4013.0"), although the connector removes that ending before it writes; read them as numbers. `q_year` is the year of `q_date` wherever both are filled.

By `region`: West 8,097, PJM 7,666, MISO 5,424, Southeast 4,334, ERCOT 3,757, CAISO 2,868, SPP 2,837, NYISO 1,936, ISO-NE 1,282. Active MW by `type_clean`: Solar+Battery 503.8 GW, Solar 396.6 GW, Battery 385.3 GW, Gas 240.0 GW, Wind 177.8 GW.

## Reading the source

- Rows with neither a `q_id` nor an `entity` are dropped. More than 100,000 rows writes nothing.
- A `q_status` outside active, withdrawn, suspended, operational and unknown stops the run; unknown has no ERW status and keeps its `q_status`.
- Text is put on one line (Excel's `_x000D_` and line breaks become spaces); dates are written as YYYY-MM-DD, and a value that is not a date is left empty.

- The code strips a trailing ".0" from `fips_code`, `q_year` and `prop_year` (lines 125 to 129), but the file on this machine keeps it in every filled value (36,431, 37,536 and 32,936 of them, `4013.0`, `2021.0`): it was rebuilt by `restore_tables.py` and restored by `scripts/sync.py`, which may have written the numbers back as floats; the cause is not established (session 2074). A join on these codes should read them as numbers.

## License

`license_verdicts.csv` records Berkeley Lab, read 14: "may be public", for public and for commercial use, with the note "NOT READ: HTTP 403 on 12 October 2026. The verdict rests on an earlier session's reading, in the table's own header: 'The Queued Up data file is licensed CC BY 4.0'." `license_tables.csv` lists the table under Berkeley Lab; `docs/licenses.md` gives "may be public", flag public, ERW verdict public. Attribute: Lawrence Berkeley National Laboratory and GridTracker, Queued Up: 2026 Edition data file.

## Cross-checks (session 2074)

- The counts above were computed from the rows, read past the header lines. `capacity_mw` equals the sum of `mw_1` to `mw_3` in 38,201 of 38,201 rows, and the `status_date` rule holds on all 27,971 dated rows.
- `interconnection_queue_summary` (built from this table on 4 October 2026) gives the same requests by region in all nine regions and 38,201 in all. Its MW are larger by the 16 negative capacities, which it counts as zero: 7,098,748.5 MW in all and 1,864,963.3 active, equal to this table's positive capacities to 0.1 MW.

## What it does not hold

- Coordinates: a request is placed by state, county and `fips_code` only.
- Requests entered after 2025, and any queue change after the file's date; the grids' own current queues are in `caiso_interconnection_queue`, `ercot_interconnection_queue`, `nyiso_interconnection_queue` and the others.
- Berkeley Lab's other sheets (the codebook, the summaries).
