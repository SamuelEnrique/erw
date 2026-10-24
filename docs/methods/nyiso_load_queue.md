# NYISO load interconnection requests (the queue workbook's sheet "Load Projects")

Energy Research Warehouse (ERW), method note written in session 2214 (chain 098) for a table first written in session 140 (approved pull). The generator queue from the same workbook is `docs/methods/nyiso_interconnection_queue.md`.

Tables: `nyiso_load_queue`

## Publisher and address

New York Independent System Operator (NYISO), NYISO Interconnection Queue workbook, `https://www.nyiso.com/documents/20142/1407078/NYISO-Interconnection-Queue.xlsx` (page `https://www.nyiso.com/interconnections`), sheets "Load Projects" (one row a load request, 21 columns, then an End-Use Key and NOTES) and "Load Project Tracking" (NYISO's formulas over the first, kept in the page's file `site/data/nyiso_load_queue.json`, not in the table). Source id `nyiso:load_queue`.

Connector: `warehouse/connectors/nyiso_load_queue.py` (session 140): `--pull` (one request, the workbook; a copy `iso_queues.py` saved within seven days is used instead), `--write` (the table and the page's file, under the data lock), `--site`, `--terms`; ceiling 50,000 rows.

Schedule: weekly, on Mondays (UTC) or with `QUEUES=1`, in `warehouse/run_daily.sh` right after `iso_queues` (`nyiso_load_queue.py --pull --write`), on the GitHub runner (`.github/workflows/daily-prices.yml`, which commits `site/data/nyiso_load_queue.json`). NYISO's host has answered GitHub's runners HTTP 202 with no body since 2026-09-27 (`docs/methods/nyiso_interconnection_queue.md`), and the file here was last built on 7 October 2026.

## How it differs from the generator queue

Same entities shape and column names as `nyiso_interconnection_queue`, with the sheet's extra columns: `entity_id` `nyiso_load_queue:<Queue Number>`; `capacity_mw` "Peak MW load" as printed; `iso_status` the sheet's code and `iso_status_words` the words of its own key; `end_use` and `end_use_words`; `zone` (NYISO's letter) and `zone_entity` (the id of the ERW's NYISO price and load tables); each date twice, `<x>_printed` as the sheet shows it and `<x>_date` only where the cell is a full date; `proposed_initial_backfeed_month` YYYY-MM; `sheet` and `sheet_row`; `workbook_last_modified`. 44 columns.

## Vintage and revision

A snapshot. Header line 1: rebuilt from the ERW archive as of run `20261007T100923Z-local`; the table's header: "Retrieved: 2026-10-07T09:09:14Z (UTC); built 20261007T092931Z", the workbook 475,716 bytes, Last-Modified Fri, 11 Sep 2026 17:26:02 GMT. Every row: `retrieved_at` 2026-10-07T09:09:14Z, `vintage` 2026-10-07, `workbook_last_modified` 2026-09-11T17:26:02Z.

## Shape and columns

Entities, 74 rows, 74 queue numbers, `entity_type` project, `record_type` Load Interconnection and `type_fuel` L on every row.

| `status` | Rows | MW | NYISO's codes |
|---|---|---|---|
| active | 53 | 14,232.9 | 1 Scoping Meeting Pending 3, 4 SRIS/SIS Pending 16, 5 SRIS/SIS in Progress 16, 6 SRIS/SIS Approved 4, 7 FS Pending 2, 8 Rejected Cost Allocation/Next FS Pending 1, 9 FS in Progress 3, 10 Accepted Cost Allocation/IA in Progress 4, 12 Under Construction 4 |
| withdrawn | 17 | 3,078.88 | 0 Withdrawn |
| completed | 4 | 360.2 | 14 In Service Commercial |

- End use: Data Center (general) 24, AI Datacenter 12, Research and Development 5, Cryptocurrency mining 4, Microchip fabrication 2, Consumable Goods 2, Industrial Goods 1, Other 1; blank on 23.
- Zone: C 14, E 13, A 12, F 12, G 8, D 7, B 3, K 3, H 2. Active MW by zone: C 3,692.0, E 2,924.0, D 2,890.0, A 2,016.0, H 1,200.0, B 600.0.
- The largest: St. Lawrence Infrastructure 2 (1,935 MW, active, D), NY-Route 9W Load Center (1,000, withdrawn, F), 1 Gig Data Center East Fishkill (1,000, active, H), St. Lawrence Infrastructure 1 (860, active, E), Micron Fab 3 (606, active, C).
- `geo`: US-NY 71 (one written "New York" in `state`), US-PA 2, US-NJ 1. Queue dates 2005-11-02 to 2026-08-28. `status_date`, `lat` and `lon` are empty on every row.

## License

The header: "License: public, with a caution (sessions 65, 85, 136, 138) ... A person can rule otherwise." `docs/licenses.md`: verdict "needs written permission", decided by NYISO, flag public, "ruled: license needed from 2026-10-21", ERW verdict "unsettled". That ruling of 21 October 2026 governs NYISO's tables (`docs/methods/nyiso_dam_zone_prices.md`). The connector itself, since session 149 (the owner's ruling of 7 October 2026), sets `SHOWN = False` and writes the license line "License: internal ... Not published, in no public dataset, no download and no page"; its page's file holds no request, zone or megawatt.

## Checks (session 2214)

The figures in this note were computed from the rows of `warehouse/output/nyiso_load_queue.csv`, read past its 14 header lines (scripts in `runs/c098/s2214/`).

- 74 rows, as the header states ("the 74 requests of the sheet"); no `entity_id` twice; every capacity a number.
- The header's counts by the page's rule hold: in line 53 requests, 14,232.9 MW; withdrawn 17, 3,078.88 MW; in service 4, 360.2 MW.
- Every `zone_entity` is the zone's: A nyiso:WEST, C nyiso:CENTRL, E nyiso:MHK VL, F nyiso:CAPITL and so on.

## Where the description and the data disagree

1. **The license line.** The file's header says "public, with a caution"; the connector since session 149 writes "License: internal" (`SHOWN = False`), and the license record rules "needs written permission" from 2026-10-21. The header was written by the build of 7 October 2026 and has not been rewritten since.
2. **The status rule in words and in code.** The docstring maps "0 is withdrawn, 14 (In Service Commercial) is completed, every other code of the sheet's key is active"; the code maps by the key's words (any code whose words hold "withdrawn" is withdrawn; only the words "in service commercial" are completed). On this sheet, which holds codes 0, 1, 4 to 10, 12 and 14, the two give the same result; they would differ for a code other than 0 whose words contain "withdrawn", and neither marks as completed a code the page's own count sets apart as in service other than 14 (the docstring names 13 and 15 there).

Acted on in session 2214: the docstring now states the rule the code applies (by the key's words). The license line is recorded, not changed: the next build writes the connector's "License: internal", and the license record governs the table's standing until then.

## What it does not hold

- Generator requests (`nyiso_interconnection_queue`), the tracking sheet's figures (in the page's file), coordinates, and any change to NYISO's sheet after 11 September 2026.
