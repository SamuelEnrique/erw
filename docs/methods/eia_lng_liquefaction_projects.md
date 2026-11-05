# LNG export projects: trains, capacity, authorizations and status (EIA's U.S. Liquefaction Capacity)

Energy Research Warehouse (ERW), method note written in session 2023 (chain 057) for a table first written on 23 October 2026 (session 2021).

Tables: `eia_lng_liquefaction_projects`

## Publisher and address

U.S. Energy Information Administration (EIA), U.S. Liquefaction Capacity, a quarterly workbook listed on `https://www.eia.gov/naturalgas/data.php`: `https://www.eia.gov/naturalgas/importsexports/liquefactioncapacity/U.S.liquefactioncapacity_2026_Q3.xlsx`, its sheets "Existing & Under Construction" and "Approved". EIA names FERC, DOE and the projects' sponsors as its sources. Source id `eia:us_liquefaction_capacity`. Connector: `warehouse/connectors/eia_lng_liquefaction.py` (session 2021).

## Vintage and revision

The 2026 third quarter's file, last modified 1 October 2026 20:44:22 UTC, retrieved 23 October 2026 18:59:44 UTC and written by run `20261023T190257Z` from the saved file (`--offline`).

Each quarter's file has a new name: the connector reads the one named in `FILE` or given with `--file`, from the saved file once a run has saved it. The table is written whole each time, so a project dropped from a later quarter's file leaves the table.

## Shape and variables

Entities, 48 rows, `entity_type` project, each `entity_id` once:

| Sheet (`x_sheet`) | `status` | `x_status` (EIA's words) | Rows | Peak capacity, bcf/d | Baseload, bcf/d |
|---|---|---|---|---|---|
| existing_under_construction | operating | Commercial operation | 20 | 14.27 | 11.42 |
| existing_under_construction | empty | Commissioning (Plaquemines Phases 1 and 2, Corpus Christi Stage 3, Golden Pass Train 1) | 4 | 6.79 | 4.64 |
| existing_under_construction | under_construction | Under construction (13), Under Construction (1), Under constructionH (1) | 15 | 17.65 | 14.96 |
| approved | planned | Proposed, or a sentence on the project's progress | 9 | 10.91 (8 with figures) | per train |

`entity_id` `eia_lng:<project>:<train>` for a train or group of trains, `eia_lng:<project>` for an approved project, each slugged from EIA's words; `name` the project, with its train; `geo` US-LA 21, US-TX 20, US-GA 2, US-AK, US-MD and US-MS 1 each, and US for the 2 offshore rows (Delfin FLNG: its approved project and its Train 1 under construction); `status_date` the in-service date where EIA gives a day (24 rows, the 20 operating and the 4 commissioning, 1 February 2016 to 1 April 2026); `operator` EIA's operator; `capacity_mw`, `lat` and `lon` empty.

| Column | Unit or form |
|---|---|
| x_baseload_bcfd, x_baseload_mtpa, x_peak_bcfd, x_peak_mtpa | bcf/d and million tonnes a year: a train's nameplate; for an approved project the baseload per train and the peak its proposed design capacity in all |
| x_doe_fta_bcfd, x_doe_fta_mtpa, x_doe_nonfta_bcfd, x_doe_nonfta_mtpa, x_ferc_bcfd, x_ferc_mtpa | the authorized export quantities, bcf/d and Mtpa |
| x_doe_fta_docket, x_doe_nonfta_docket, x_ferc_docket | as EIA writes them |
| x_in_service | a day, a year or a half year as EIA writes it (under construction: 2H2026 to 2031) |
| x_commercial_operation_date | a day (the 20 operating rows) |
| x_trains | the approved project's number of trains |
| x_train, x_project_type, x_marks | EIA's train label; Greenfield or Brownfield as written; EIA's footnote marks, "column:mark" |

`x_marks` is filled in 35 rows: ^ 90 times, B 8, D 6, "Note A" 4, "n/a" 3, + 1 and ^+ 1. EIA's notes themselves are in the file.

## Reading the workbook

- Both sheets must be in the file, each with one row, within its first eight, whose first cell is "Project name"; each column read must hold its words in that row or the next, or the run stops. A sheet's projects end at a row beginning "Notes" or "<n> Projects need"; a row whose first cell is empty is passed over.
- A figure is read as a number; one written with a footnote mark of one or two characters (capital letters, ^ or +, as "0.66B", "6.20^", "1.20+") as the number with its mark kept in `x_marks`; "Note A" (any capital letter) and "n/a" have no figure and keep their mark. Any other text where a figure belongs stops the run.
- Status: a project of the Approved sheet is planned; otherwise "Commercial operation" is operating, "Under construction" (in any case) under_construction, and "Commissioning" has no standard status (`status` empty). Any other status stops the run.
- `status_date` is filled only where the in-service cell is a date; a commercial operation date that is neither empty nor a date stops the run.
- A location must be one of the states in the connector's map (AK, AL, FL, GA, LA, MD, MS, OR, TX, WA) or begin "offshore" in any case (geo US), or the run stops.
- Names, train labels and statuses are kept as EIA prints them, footnote letters included ("Train 1B", "Gulf LNGE"). An `entity_id` given twice stops the run. Nothing is filled.
- Ceiling: one request, the quarter's file. EIA's robots file does not disallow `/naturalgas/importsexports/`.

## License

Public: a work of the U.S. government. The table's header: "License: public (EIA: U.S. government publications are in the public domain); EIA names FERC, DOE and the projects' sponsors as its sources." `license_tables.csv` maps it to EIA through the source registry; `license_verdicts.csv` gives EIA (read 1) may be public.

## Cross-checks (sessions 2021 and 2023)

- Session 2021, each terminal's highest month of 2026 in `eia_lng_exports_monthly` against the peak capacity of its trains in operation or commissioning: Sabine Pass 4.51 bcf/d against 4.56 (0.99), Plaquemines 3.82 against 3.85 (0.99), Freeport 2.30 against 2.37 (0.97), Elba Island 0.43 against 0.44 (0.98), Calcasieu Pass 0.90, Cameron 1.06, Cove Point 1.13, and the two still ramping below it, Corpus Christi with Stage 3 0.69 and Golden Pass 0.27. All terminals exported 16.5 bcf/d in July 2026 against 21.1 of peak and 16.1 of baseload capacity in operation and commissioning; session 2023 computed the same 21.06 and 16.06 from the rows.
- Session 2023: the counts above were computed from the rows, read past the header lines; 20 + 4 + 15 + 9 = 48, the header's counts.
- For the eight approved projects with figures, the number of trains times the baseload per train equals the proposed design capacity within 0.01 bcf/d (Alaska LNG: 3 times 0.85 = 2.55).
- Mtpa over bcf/d lies between 6.6 and 9.2 (median 7.6 for baseload, 7.6 for peak) in all 47 rows with both: the two units are read in their own columns throughout.
- The commercial operation date is on or after the in-service date in all 20 operating rows.

## What it does not hold

- Earlier quarters' files, and the history of a project's status or dates.
- A capacity in MW, and the plants' coordinates.
- A standard status for commissioning (four rows, for a person's ruling on the vocabulary).
- Import terminals, small-scale liquefaction and projects not on EIA's two sheets.
- One row on the Approved sheet is not a separate project: "Lake Charles LNG (additional DOE application)", whose capacities are "Note A".
