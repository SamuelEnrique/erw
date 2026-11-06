# EIA natural gas pipeline projects

Energy Research Warehouse (ERW), method note written in session 905 (chain 049) for tables first written on 23 October 2026.

Tables: `eia_gas_pipeline_projects`

## Publisher and address

U.S. Energy Information Administration (EIA), the natural gas pipeline projects tracker: the newest workbook the natural
gas data page `https://www.eia.gov/naturalgas/data.php` links (`/naturalgas/pipelines/EIA-NaturalGasPipelineProjects<Mon><year>.xlsx`),
sheets "Natural Gas Pipeline Projects" and "Historical Projects (1996-...)". When written, the tracker of August 2026:
`https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjectsAug2026.xlsx` (retrieved 2026-10-23T06:35:49Z).
The address `/naturalgas/pipelines/` answers 403, a folder with no page. EIA's robots file allows these paths. The page
and the workbook are saved in `warehouse/raw/eia_gas_pipeline_projects/` and reused offline. Connector:
`warehouse/connectors/eia_gas_pipeline_projects.py`.

## Vintage and revision

The tracker of August 2026 when written (run `20261023T063743Z`). A run reads the page, takes the newest workbook it
links, chosen by the month and year in its name, and writes the table whole: two requests. EIA dates its own changes to a
record in `x_last_updated`.

## Shape and variables

Events, one row a project, from both sheets.

- `event_id` `eia_gas_pipeline:<project name slug>:<year in service slug>`. A slug is the text in lower case, other
  characters as `_`: `none` where EIA gives no year (29 ids), `na` where EIA writes na (39), and EIA's "2020-2027
  (phased)" as `2020_2027_phased`. The first write (session 899) kept the year's text whole; session 905 made it a slug.
- `event_date` and `x_date_basis`:

| `x_date_basis` | `event_date` | Projects when written |
|---|---|---|
| `completed` | EIA's completed date | 1,127 (1,126 historical, 1 current) |
| `year_in_service` | the year in service's 1 January, where no completed date | 139 (125 current, 14 historical) |
| `last_updated` | the date EIA last updated the record, where neither | 68 (57 historical, 11 current) |

- `event_type` `pipeline_project`. `parties` the pipeline operator. `status` EIA's status in lower case. `entity_ids`,
  `mw`, `price` and `currency` are empty.
- `x_*` EIA's columns:

| Column | Unit | What it is |
|---|---|---|
| `x_project_name` | | the project's name as EIA writes it |
| `x_project_type` | | Expansion, Lateral, New Pipeline, Reversal, Upgrade, Conversion, Abandonment when written |
| `x_completed_date`, `x_year_in_service` | | as EIA gives them, the completed date as YYYY-MM-DD (the first write carried a time, `1996-06-01 00:00:00`, in it and in `x_last_updated`; session 905 removed it) |
| `x_states`, `x_beg_state`, `x_end_state` | | EIA's list of states, the first and the last |
| `x_regions`, `x_beg_region`, `x_end_region`, `x_thru_region` | | EIA's list of regions, the first, the last and the regions passed through |
| `x_cost_million_usd` | million USD | the cost as EIA writes it; a range stays a range (70-100, 13000-17000) |
| `x_miles` | miles | length |
| `x_capacity_mmcfd` | MMcf/d | added capacity |
| `x_diameter_inches` | inches | pipeline diameter |
| `x_pipeline_type` | | Interstate, Intrastate, Foreign, Cross-border when written |
| `x_authority`, `x_docket` | | the authority and its docket |
| `x_crosses_state_border` | | Yes, No or empty |
| `x_notes` | | EIA's Notes or Project Notes |
| `x_demand_served`, `x_website` | | as EIA gives them |
| `x_last_updated` | | when EIA last updated the record, with a time |
| `x_sheet` | | `current` or `historical` |
| `x_date_basis` | | as above |

When written: 1,334 projects, 137 current and 1,197 historical. The current sheet's statuses: 34 applied, 31
construction, 30 approved, 13 announced, 10 on hold, 10 pre-applied, 4 completed, 3 part completed, 2 proposed. The
historical sheet's: 1,136 completed, 44 cancelled, 11 on hold, 3 denied, 1 approved, 1 construction, 1 cancelled/on
hold. Two project names appear in both sheets: Guardian Pipeline Project and Wright Interconnect Project.

## Reading the sheets

- The sheets are found by name: the one named "Natural Gas Pipeline Projects" and the one whose name begins "Historical
  Projects". Either missing stops the run.
- The heading row is the one, among the first five, with a cell "Project Name". Every column is found by its heading,
  not by position. A heading the map does not know stops the run.
- A row with no project name is read past.
- `event_date` is the completed date where it reads as a date, else the year in service where it is four digits, else
  the last updated date. A project with none of the three is left out and counted in the header: none when written.
- A row given twice the same is kept once. A project given twice under one id with two different rows has no key: both
  are left out and named in the header (chain 030's rule). When written, three: Columbia to Eastover Pipeline 2016, East
  Side Expansion Project 2015, TETCO Capacity Expansion Project 2016.
- Nothing is filled. One historical project, SONAT South Sys Expansion II Phase 1A*, carries EIA's completed date
  1903-11-05 with a year in service of 2003; it is kept as EIA gives it, so the table's first `event_date` is
  1903-11-05.

## License

Public: a work of the U.S. government (EIA, record 1 of `license_reads.csv`). Cite "U.S. Energy Information
Administration, natural gas pipeline projects".

## Cross-check (session 899)

The cross-check the queue file named does not apply: `eia_gas_interstate_annual` holds flows between states, not
capacity. Checked instead within the tracker: the current sheet's statuses (above), the two project names in both
sheets, the historical capacity completed each year (25,165 MMcf/d in 2018, 4,231 in 2022, 18,696 in 2024) and the
current projects' capacity by year in service (28,814 MMcf/d in 2027, 25,579 in 2028).

## What it does not hold

- The three projects EIA gives twice with different rows under one name and year.
- A project's route or map: only its states and regions.
- Links to ERW entities (`entity_ids` is empty), and capacity as a series.
- Trackers older than the newest the page links.
