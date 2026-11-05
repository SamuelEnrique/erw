# ERCOT's transmission projects (Transmission Project and Information Tracking)

Energy Research Warehouse (ERW), method note written in session 862 (chain 046) for a table first written on 23 October 2026.

Tables: `ercot_transmission_projects`

## Publisher and address

Electric Reliability Council of Texas (ERCOT), Transmission Project and Information Tracking report (TPIT), the public
edition without costs. The connector reads ERCOT's planning page, `https://www.ercot.com/gridinfo/planning`, and takes the
one workbook linked there with the title "Transmission Project and Information Tracking". When written:
`https://www.ercot.com/files/docs/2022/03/02/ERCOT-July-Ad-Hoc-TPIT-No-Cost-071326-UPDATE.xlsx`. It reads the four
project sheets: Future, Planned, Completed and Cancelled. Connector: `warehouse/connectors/ercot_tpit.py` (session 852).

ERCOT's robots file (read by session 850) disallows `/misapp` and `/misdownload`. This report comes from `/gridinfo/` (the
page) and `/files/docs/` (the workbook), which it allows.

## Vintage and revision

The workbook titled "JULY BASE FOR TRANSMISSION OWNER SUBMISSION FILE - TRANSMISSION PROJECT INFORMATION TRACKING (TPIT)
FUTURE PROJECTS AS OF 7/13/2026", updated 17 July 2026. The date in the file's address (2022/03/02) is not the edition's.
Retrieved 2026-10-23T01:44:41Z. A snapshot: each run replaces the table whole with the workbook the page names. Ceiling
two requests a run (the page and the workbook). Session 852 made 4 of its 8 requests (the probe's page and workbook, then
the trial's, which the write reused).

## Shape and variables

Events, one row a project phase.

| Column | What it holds | Unit |
|---|---|---|
| `event_id` | `ercot_tpit:<ERCOT project number>:<phase number>`, unique | |
| `event_date` | the actual in-service date where ERCOT gives one, else the projected one | date |
| `event_type` | `transmission_project` | |
| `parties` | the transmission owner as ERCOT names it | |
| `entity_ids`, `mw`, `price`, `currency` | empty | |
| `status` | the sheet the project is on: `future`, `planned`, `completed`, `cancelled` | |
| `source`, `source_url` | `ercot:tpit` and the workbook's address | |
| `x_project_number`, `x_phase` | ERCOT's project and phase numbers | |
| `x_title`, `x_description`, `x_comment` | ERCOT's text (line breaks written as spaces) | |
| `x_from`, `x_to` | the terminal "from" and "to" | |
| `x_ercot_status` | ERCOT's own status text | |
| `x_owner` | the transmission owner (same as `parties`) | |
| `x_projected_in_service`, `x_actual_in_service` | ERCOT's two dates, as given | date |
| `x_kv` | service level | kV |
| `x_new_circuit_miles`, `x_upgraded_circuit_miles` | new and rebuilt or upgraded circuit miles | miles |
| `x_autotransformer_mva` | autotransformer capacity | MVA |
| `x_reactive_mvar` | reactive capability, ERCOT's cell kept as text (some cells hold two figures, such as "0,28.8") | Mvar |
| `x_county_start`, `x_county_end` | the county of the substation or start, and of the end | |
| `x_tier` | ERCOT's planning charter tier | |
| `x_rpg_number`, `x_rtp_number` | ERCOT's RPG and RTP project numbers | |
| `x_date_kind` | `actual` or `projected`: which date `event_date` is | |
| `x_sheet` | the sheet's name | |

ERCOT's `9999-01-01` means no date. It stands where a project has no actual date (19 rows). It is not taken as a date:
`event_date` falls back to the projected date and `x_actual_in_service` keeps ERCOT's cell.

Deliberately not taken: the "TSP/Company Contact" column and the owners' contact sheet. These hold the owners' contact
names, addresses (email or postal) and telephone numbers, which the warehouse has no need of.

Five project phases are given twice with every field the same; each is kept once and counted in the header (chain 030's
rule). Two different rows under one project and phase would stop the run.

When written: 2,122 project phases: 1,424 future, 358 planned, 262 completed, 78 cancelled. 50 transmission owners (or
owner pairs). `event_date` 2023-05-25 to 2033-12-15; 277 actual, 1,845 projected. By kV: 138 kV 1,260; 345 kV 633; 69 kV
185; 765 kV 41; 115 kV 1; none given 2. ERCOT's status text: Planned 1,550, Conceptual 327, In-Service 159, Under
Construction 43, none 43. Tiers: Tier 4 1,410, Tier 1 350, Tier 3 265, Tier 2 97.

## License

Public: ERCOT's terms (record 2 of the license reads, `docs/licenses.md`) let raw data from public portions of the site be
used, reproduced and redistributed in compilations, charts and analyses. Verdict in `docs/licenses.md`: public. Cite
"ERCOT, Transmission Project and Information Tracking".

## Cross-check (session 852)

- 1,930 of the 2,122 rows name a county. Of the 189 county names, 188 are among the 254 Texas counties of
  `utility_service_territories`; the one that is not is ERCOT's spelling "Stonwall" (Stonewall County), kept as given.
- All four wires utilities of `texas_delivery_charges` own projects here. As first owner: Oncor 505, CenterPoint 398,
  AEP Texas Central 248 and North 137, TNMP 62.
- The future list holds 41 phases at 765 kV with 2,667 new circuit miles.

## What it does not hold

- Costs: this public edition carries no cost by project.
- The owners' contact names, addresses and telephone numbers.
- A link to the warehouse's nodes or plants (`entity_ids` is empty), and no coordinates: only ERCOT's counties and
  terminal names.
- Corrected county spellings: ERCOT's are kept ("Stonwall").
- Earlier editions: each run keeps only the workbook the page names.
