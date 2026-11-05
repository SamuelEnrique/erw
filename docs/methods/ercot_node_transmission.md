# ERCOT's transmission projects by a resource node's county

Energy Research Warehouse (ERW), method note written in session 917 (chain 051) for a table first written on 23 October 2026.

Tables: `ercot_node_transmission`

## Publisher and address

Derived by the ERW from two ERW tables, with no request: `ercot_node_places` (ERCOT's resource nodes placed by the county and load zone of their CDR units; session 901) and `ercot_transmission_projects` (every project phase of ERCOT's Transmission Project and Information Tracking report, TPIT, the July 2026 base file; session 852). Builder: `warehouse/derived/ercot_node_transmission.py`.

## Vintage and revision

Written by the run whose header line begins "Retrieved"; a run reads the two tables as the machine holds them and writes the table whole. It changes when either input does: a new TPIT edition, a new CDR report, or nodes added to `node_basis_daily`. `x_tpit_edition` names the TPIT workbook the run read.

## Shape and variables

Entities, one row a placed node. `entity_id` `ercot_node:<settlement point>` (the same ids as `ercot_node_places`); `entity_type` `generator`; `name` the settlement point; `geo` `US-TX`; the other standard columns empty.

| Column | What it is |
|---|---|
| `x_county`, `x_zone` | the node's county and load zone, as `ercot_node_places` gives them |
| `x_phases_future`, `x_phases_planned`, `x_phases_completed`, `x_phases_cancelled` | the TPIT project phases on that sheet whose start or end county is the node's county |
| `x_open_projects` | distinct TPIT project numbers among the future and planned phases |
| `x_open_new_circuit_miles`, `x_open_upgraded_circuit_miles` | the new and upgraded circuit miles of those phases, summed |
| `x_open_max_kv` | the highest voltage among them (kV) |
| `x_open_next_in_service` | the earliest projected in-service date among them (some fall before the table's day: TPIT's projected dates are the owners' as of the edition) |
| `x_tpit_edition` | the TPIT workbook's title line |

When written: 569 nodes in 148 counties; 548 nodes are in a county with at least one open phase. The counties with the most open phases: Harris 157, Bexar 79, Brazoria 66, Dallas 52, Cameron 46.

## The join

- A phase touches a county when `x_county_start` or `x_county_end` is that county, compared in capitals with runs of spaces made one. A line from one county to another counts in both; a phase within one county counts once.
- 244 of TPIT's 2,122 phases name no county at either end and touch no node; 315 run between two counties.
- A node's county with no phase has zeros, not blanks: TPIT lists every project the transmission owners report, so a county it does not name has none in the report. When written, 11 of the 148 counties had none (Armstrong, Baylor, Delta, Hale, Kinney, Oldham, Parmer, Randall, Roberts, Swisher, Willacy).
- Circuit miles are summed over phases; a line counted in two counties gives its miles to both. The table answers "how much transmission work touches this node's county", not the network's length.

## License

ERCOT's terms (read 2 of `license_reads.csv`) allow its public contents to be used and redistributed unmodified with attribution; the counts are the ERW's.

## Cross-check (session 917)

Three counties counted by hand from `ercot_transmission_projects` give the table's figures: Harris 101 future, 56 planned, 33 completed; Pecos 22, 2, 2; Bexar 74, 5, 13 and 3 cancelled. TPIT's fields hold '#' in 66 phases (switch and line numbers): a reader must skip the header lines, not pass `comment="#"`, which cuts those rows and loses their counties (the first hand count did, and was one short in Pecos).

## What it does not hold

- A project's distance from the node: TPIT gives counties, not coordinates.
- The 304 nodes `ercot_node_places` does not place.
- Costs: this TPIT edition has none.
