# Landfills and landfill gas energy projects, as of September 2024 (EPA's Landfill Methane Outreach Program)

Energy Research Warehouse (ERW), method note written in session 2129 (chain 079) for a table first written on 23 October 2026 (session 2127, `archive/sessions/SESSION_2127_REPORT.md`).

Tables: `epa_lmop_landfill_projects`

## Publisher and address

U.S. Environmental Protection Agency (EPA), Landfill Methane Outreach Program (LMOP), the LMOP Landfill and Project Database page, `https://www.epa.gov/lmop/lmop-landfill-and-project-database`, which links the composite data file `https://www.epa.gov/system/files/documents/2024-09/lmopcompositedata.xlsx` (1,465,367 bytes; sheets "Summary", "LMOP Database" with 3,399 rows and 69 columns, "Field Descriptions"). Source id `epa:lmop`. Files saved under `warehouse/raw/epa_lmop/`.

Connector: `warehouse/connectors/epa_lmop.py` (session 2127): `[--offline] [--out-dir DIR]`, two requests (the page, for the file's address, and the file). The counts on EPA's Summary sheet (unique landfills, unique operational projects) are checked against the rows; a difference stops the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. `coverage.csv` gives the sectors power and gas.

## Vintage and revision

One run, `20261023T231339Z`, from the file retrieved at 2026-10-23T23:11:19Z; `vintage` 2024-09-20T16:32:56Z, the file's last-modified time, in every row. The table is a snapshot, replaced whole by each run; each run takes the file's address from the database page.

## Shape and columns

Entities, 3,399 rows, one a landfill and project as EPA lists them, 79 columns. `entity_id` `lmop:<Landfill ID>:<Project ID>` (3,399 distinct); `entity_type` project; `name` the landfill's name, then ": " and the project's name where it has one; `geo` US-<state> (53 values, Guam, Puerto Rico and the Virgin Islands among them; none blank); `lat` and `lon` as EPA gives them (blank on 321 rows; 13.43 to 64.80 and -166.51 to 144.75, Guam included); `capacity_mw` EPA's "Rated MW Capacity" (784 rows, 0.0 to 50.0); `status`; `status_date` blank in every row; `operator` "Project Owner(s)"; then EPA's other 65 columns in snake case, "Current Project Status" as `lmop_status`. The sheet's 69 columns are all present: four under the standard's names (`lat`, `lon`, `capacity_mw`, `operator`) and 65 under their own.

| EPA's status (`lmop_status`) | Rows | `status` |
|---|---|---|
| Low Potential | 967 | blank |
| Shutdown | 712 | retired |
| Operational | 669 | operating |
| Candidate | 444 | blank |
| Unknown | 316 | blank |
| Future Potential | 158 | blank |
| Planned | 100 | planned |
| Construction | 33 | under_construction |

2,641 landfills, 3,365 project ids. 30 project ids appear on more than one row (64 rows): a project fed by several landfills, with the same capacity and status on each (project 1016-0, 22.5 MW, on Middlesex County LF, Edison Township SLF and Industrial Land Reclaiming (ILR) LF, New Jersey). Operational rows: 669, 652 project ids, 542 projects once a project's expansions (the id's suffix after "-") are counted with it.

## Placing values in time

The table is a list, not a series: `status_date` is blank. EPA's `project_start_date` runs from 1974-04-01 to 2027-12-31 (planned projects); `project_shutdown_date` is given on 707 of the 712 Shutdown rows.

## What is and is not filled

- Every row of EPA's sheet is kept, landfills without a project included (each has a project id of its own and a status such as Candidate or Low Potential).
- Capacity is repeated on each landfill's row of a shared project, so it is never summed over rows: one row a project id counts it once.
- Values as published; blanks stay blank; nothing is filled. A status not EPA's eight, a missing column or a landfill and project twice stops the run.

## License

Header: "License: public (a work of the U.S. government). Cite: U.S. EPA, Landfill Methane Outreach Program (LMOP) Database." `license_verdicts.csv` records EPA, read 55: "may be public", for public and for commercial use. `docs/licenses.md`: "may be public", flag public, ERW verdict public.

## Checks (session 2129)

The figures in this note were computed from the rows of `warehouse/output/epa_lmop_landfill_projects.csv`, read past its 10 header lines, and from the saved workbook (scripts in `runs/c079/s2129/`).

- 3,399 rows, as the header states; the workbook's sheet has 3,399 rows. No `entity_id` twice; no row without a project id.
- EPA's Summary sheet: "Count of Unique Landfills in this File" 2,641 and "Count of Unique Operational Projects in this File" 542; the rows give 2,641 landfill ids and 542 operational base project ids.
- `status` and `lmop_status` agree in every row (the table above). Within each of the 30 shared project ids, capacity and status are the same on every row.
- Operational projects counted once a project id: 1,745.4 MW of rated capacity, as the header states. By type: Electricity 450 rows, Renewable Natural Gas 123, Direct 96.
- Session 2127's cross-check (`runs/c079/s2127/cross.py`), run again: its output is identical to the saved `cross.out`. LMOP's 437 operational electricity project ids are rated at 1,737.5 MW, against 1,584.5 MW of nameplate at 1,210 operating landfill gas generators at 285 plants in `eia860m_operating_generators` (LMOP 1.097 of EIA). Of the 1,331 GHGRP ids in LMOP, 1,120 (84.1 percent) report direct emissions to the GHGRP in 2023 (`epa_ghgrp_facility_emissions`).

## Where the description and the data disagree

1. **"Landfills, not projects."** The docstring and header give `status` blank for Candidate, Future Potential, Low Potential and Unknown, "which are landfills, not projects". Of those 1,885 rows, 20 carry a project name (Low Potential 11, Future Potential 7, Candidate 2), and one carries a capacity: `lmop:2400:180761-1`, Low Potential, 0.06 MW, "Chittenden County LF: Project #1, Expansion #1".

## The session report against the table

Every figure of `SESSION_2127_REPORT.md` checked against the table, the saved workbook and the rerun cross-check holds: 3,399 rows, 2,641 landfills, 542 operational projects, EPA's eight statuses with their counts, project 1016-0's 22.5 MW on three New Jersey landfills, 1,745.4 MW counted once a project id, all 69 of EPA's columns kept (four under the standard's names), the 1.5 MB file, 437 electricity projects at 1,737.5 MW against 1,584.5 MW at 1,210 generators and 285 plants (1.097), and 1,120 of 1,331 GHGRP ids (84.1 percent). None found that does not hold.

Acted on in session 2129: the docstring now says 20 rows without a project in view carry a project name and one a capacity, as EPA gives them; `status` is unchanged.

## What it does not hold

- Landfills or projects EPA's file does not list, any year but the file's (data as of September 2024), and any gas flow or generation series over time.
- A project-level table: a shared project is on each of its landfills' rows.
