# ERCOT interconnection queue (the Generation Interconnection Status report)

Energy Research Warehouse (ERW), method note written in session 2166 (chain 094) for a table of the queue connector of session 8.

Tables: `ercot_interconnection_queue`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), Generation Interconnection Status (GIS) report, PG7-200-ER (`https://www.ercot.com/mp/data-products/data-product-details?id=PG7-200-ER`); the document every row cites is `https://www.ercot.com/misdownload/servlets/mirDownload?doclookupId=1281327706`, read with gridstatus 0.36.0 (`Ercot.get_interconnection_queue`). Source id `ercot:interconnection_queue`. Connector: `warehouse/connectors/iso_queues.py` (session 8).

Schedule: the daily run, `warehouse/run_daily.sh`, weekly on Mondays (UTC) or with `QUEUES=1` (step `iso_queues`), on the GitHub runner (`.github/workflows/daily-prices.yml`). `run_status.csv` records the ERCOT queue `ok` on 30 September and 5 and 12 October 2026; the header's run is 19 October. A run asks nothing while ERCOT is in `paused_sources.csv`.

## How it differs from the NYISO queue note

The shape and rules are those of `docs/methods/nyiso_interconnection_queue.md`. For ERCOT:

- **No withdrawn positions.** ERCOT's status map holds only `Active` and `Completed`, and the file holds no other status (a new one would fail the run). Every row is active or completed.
- `operator` is filled on every row (the interconnecting entity); `transmission_owner` and `zone` are empty on every row.
- `capacity_mw` can be negative: 4 rows, three wind repowers (Sherbino II -18.0, Silver Star -7.2, Trinity Hills -27.0, all completed) and GIGA AUSTIN SOLAR (-53.3, active).
- `geo` is US-TX on every row.

## Vintage and revision

A snapshot, replaced whole by the next run. Header line 1: rebuilt from the ERW archive as of run `20261019T211146Z-github`; the table's own header follows, run `20261019T203101Z`, "File holds 1758 rows". Every row has `retrieved_at` 2026-10-19T16:07:17Z and `vintage` 2026-10-19.

## Shape and columns

Entities, 1,758 rows, 1,758 queue ids, key `ercot_queue:<INR number>`, 26 columns.

| `status` | Rows | MW |
|---|---|---|
| active | 1,169 | 298,606.0 |
| completed | 589 | 139,889.9 |

- `capacity_mw`: none blank, 74 zero, 4 negative, the largest 3,000; 438,495.9 MW in all.
- `queue_date`: 2013-11-27 to 2026-09-30; blank on 1 (28INR0520, solar, 301.49 MW).
- `status_date`: the in-service date on 105 of 589 completed rows only; `actual_in_service_date` is also filled on 6 active rows (2023-07-01 to 2024-11-22). `proposed_in_service_date` is filled on every row.
- `fuel_technology`: Other - Battery Energy Storage 846, Solar - Photovoltaic Solar 609, Wind - Wind Turbine 159, gas combustion turbine 54, combined cycle 45, reciprocating engine 32, nuclear 2, others fewer; blank on 1. Active MW: battery 118,906.0 (628 rows), solar 85,044.3 (353), combined cycle 33,628.6 (36), wind 28,484.9 (77), combustion turbine 16,613.2 (41), reciprocating 10,243.9 (22), nuclear 2,656.5 (2).

## What is and is not filled

Values as gridstatus reads them; nothing is filled. `lat`, `lon`, `zone` and `transmission_owner` are empty.

## License

Header: "License: public (ISO public queue report)." `license_verdicts.csv` records ERCOT, read 2: "may be public", for public and for commercial use. `docs/licenses.md`: "may be public", flag public, ERW verdict public.

## Checks (session 2166)

The figures in this note were computed from the rows of `warehouse/output/ercot_interconnection_queue.csv`, read past its 12 header lines (scripts in `runs/c094/s2166/`).

- 1,758 rows, as the header states; no `entity_id` twice.
- Against Berkeley Lab (`lbnl_interconnection_queue`, region ERCOT, requests through 2025): LBNL holds 3,757 ERCOT requests (active 1,796, 408,002.1 MW; withdrawn 1,158, 261,974.9 MW; operational 613, 95,296.2 MW; suspended 190, 39,322.9 MW), queue dates 2001-09-06 to 2025-12-23. Limited to queue dates through 2025, this table holds 1,582 (active 994, 225,701.3 MW; completed 588, 138,589.9 MW). 1,489 of the 1,758 ERCOT ids are in LBNL; LBNL holds 2,268 ids ERCOT's report does not (LBNL's queue dates begin in 2001, this table's in 2013, and LBNL keeps withdrawn requests). Of the 1,489 matches: LBNL active and active here 912; LBNL active and completed here 566; LBNL suspended, here completed 8 and active 3. Capacity agrees within 0.5 MW in 1,361 of 1,489.

## Where the description and the data disagree

1. **Status vocabulary.** The connector's docstring and the header say `status` is one of "active, withdrawn, completed, suspended"; ERCOT's map can give only active and completed, so a reader comparing grids finds no withdrawn ERCOT positions, and neither the header nor the docstring says the report omits them.
2. **Negative "requested capacity".** The header calls `capacity_mw` "the ISO's requested capacity"; 4 rows carry a negative value (repowers' and one solar project's net change).
3. **Retrieval time before the run.** Every row's `retrieved_at`, 2026-10-19T16:07:17Z, is 4 hours 24 minutes before the header's run `20261019T203101Z` began; the file was rebuilt from the archive.

Recorded, not changed in session 2166: the status vocabulary in the header is the queue connector's general one, of which ERCOT's map uses two words; the negative requested capacities are ERCOT's figures for repowers.

## What it does not hold

- Withdrawn requests (Berkeley Lab holds 1,158 through 2025), coordinates, zones, transmission owners.
- Large loads (`ercot_large_load_status`).
