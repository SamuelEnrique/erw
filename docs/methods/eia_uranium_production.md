# Uranium mined and milled in the U.S. (EIA's Domestic Uranium Production Report)

Energy Research Warehouse (ERW), method note written in session 960 (chain 054) for tables first written on 23 October 2026.

Tables: `eia_uranium_production_quarterly`, `eia_uranium_facilities`

## Publisher and address

U.S. Energy Information Administration (EIA), Domestic Uranium Production Report (Quarterly), Forms EIA-851Q and EIA-851A (`https://www.eia.gov/uranium/production/quarterly/`), its four workbooks `xls/qupd_tbl1.xlsx` to `qupd_tbl4.xlsx`. Connector: `warehouse/connectors/eia_uranium_production.py` (session 958). EIA's robots file allows `/uranium/production/`.

## Vintage and revision

The release of August 2026 (data to the second quarter of 2026; Tables 1 and 2 last modified 13 August, Tables 3 and 4 on 19 August), retrieved 23 October 2026; the next release was due in October. Snapshots (ceiling four requests, the workbooks). Table 1 holds only the latest five quarters: a run replaces them, so earlier quarters leave the table as EIA drops them.

## Shape and variables

`eia_uranium_production_quarterly` (series, 171 rows): `entity` `eia_u3o8:<facility>` (8 facilities) and `eia_u3o8:total`, `variable` production, `unit` lb (pounds of U3O8), `freq` P3M, Q2 2025 to Q2 2026 (Table 1); and `entity` `eia_uranium_facilities:<mills_conventional|mills_other|isr_plants|byproduct_plants|total>`, `variable` facilities_producing, `unit` count, at the end of each year from 2000 (`ts_utc` that year's 1 January, `freq` P1Y) and of the latest quarter (`freq` P3M) (Table 2). `geo` US-<state> for a facility in one state, US for the totals; `x_facility`, `x_location` as EIA writes them.

`eia_uranium_facilities` (entities, 24): 4 mills and heap leach facilities (Table 3) and 20 in-situ recovery plants (Table 4). `entity_id` `eia_uranium_facility:<name>`; `entity_type` `plant`; `geo` US-<state>; `capacity_mw` empty; `status` empty, EIA's operating status of each period in `x_status_2025`, `x_status_first_quarter_2026` and the later quarters (operating, standby, developing, permitted and licensed, partially permitted and licensed, restoration, reclamation, undeveloped, under construction, inactive); `operator` the owner; `x_kind` mill or isr; `x_capacity` and `x_capacity_unit` as EIA gives them (short tons of ore a day for a mill, pounds of U3O8 a year for a plant); `x_location`.

## Reading the workbooks

- Headings must be as read; a quarter label not of the form "Q2 2026" stops the run, as a key given twice does.
- EIA's marks have no row: 8 "-" (no production) and 1 "." (withheld or not available).
- A status "-" (a quarter to come) is written empty. Nothing is filled.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`).

## Cross-checks (sessions 958 and 960)

- The total row equals the facilities summed in all five quarters (Q2 2026: 1,087,504 pounds).
- The six facilities producing in Q2 2026 are Table 2's six (one conventional mill, five in-situ plants), and each has the status "operating"; Burke Hollow and Hobson, also "operating", produce through Hobson's plant, as EIA's note says.
- Session 960, against the code: `KINDS` gives Table 2's five kinds; the counts computed from the rows.

## What they do not hold

- Production before Q2 2025 (EIA's annual report and earlier quarterly releases), drilling, employment and expenditures.
- The facilities' coordinates.
