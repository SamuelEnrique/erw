# The planned generation in an ERCOT node's county

Energy Research Warehouse (ERW), method note written in session 931 (chain 052) for a table first written on 23 October 2026.

Tables: `ercot_node_planned_generation`

## Publisher and address

Derived by the ERW from three ERW tables, with no request: `ercot_node_places` (ERCOT's resource nodes placed by the county and load zone of their CDR units; session 901), `ercot_interconnection_queue` (ERCOT's GIS report: every queue position with its county, fuel and technology, status and dates) and `eia860m_planned_generators` (Form EIA-860M's planned generators with their state and county). Builder: `warehouse/derived/ercot_node_planned_generation.py`.

## Vintage and revision

Written by the run whose header line begins "Retrieved"; a run reads the three tables as the machine holds them and writes the table whole. It changes when any input does: ERCOT's monthly GIS report, EIA-860M's monthly release, a new CDR report.

## Shape and variables

Entities, one row a placed node. `entity_id` `ercot_node:<settlement point>` (the same ids as `ercot_node_places`); `entity_type` `generator`; `name` the settlement point; `geo` `US-TX`; the other standard columns empty.

| Column | What it is |
|---|---|
| `x_county`, `x_zone` | the node's county and load zone, as `ercot_node_places` gives them |
| `x_queue_projects`, `x_queue_mw` | ERCOT's active queue projects in the county (status `active`), their number and capacity (MW) |
| `x_queue_solar_mw`, `x_queue_wind_mw`, `x_queue_storage_mw`, `x_queue_gas_mw`, `x_queue_other_mw` | the same capacity by kind, from the queue's fuel and technology: its first word (Solar, Wind, Gas), "Other - Battery Energy Storage" as storage, everything else other |
| `x_queue_next_in_service` | the earliest proposed in-service date among them (some fall before the table's day: the queue's dates are the developers') |
| `x_eia_planned_generators`, `x_eia_planned_mw` | EIA-860M's planned generators in the county (state TX), their number and nameplate MW |
| `x_eia_<group>_mw` | the same by EIA-860M's technology group (solar, wind, storage, natural_gas, nuclear, petroleum, hydro, biomass, geothermal, other) |

When written: 569 nodes in 148 counties. ERCOT's queue held 1,169 active projects (298,606 MW), 1,031 of them in a node's county; EIA-860M 545 planned generators in Texas, 475 in a node's county. The counties with the most queued capacity: Pecos (36 projects, 16,313 MW), Jack (6,913), Reeves (6,703), Mitchell (6,616), Milam (5,781).

## The join

- A project or generator is in a node's county when its county, in capitals with runs of spaces made one, is the node's.
- A county with no project has zeros: the queue lists every active position in ERCOT, and EIA-860M every planned generator it holds. When written, 10 of the 148 counties had no active queue project.
- A project in the county is not a project at the node: a county is large, and neither table gives a project's bus.
- The two sources count differently. The queue holds every active request, most of which will not be built; EIA-860M holds generators their owners report as planned. In the 148 counties the queue holds 264,182 MW, EIA-860M 76,866; 32 counties have queued capacity and no EIA-860M plan; the two rank the counties alike only loosely (Spearman 0.42).

## License

ERCOT's terms (read 2 of `license_reads.csv`) and EIA's (record 1, public). The counts are the ERW's.

## Cross-check (session 931)

Pecos, Brazoria and Harris counted by hand from the two tables (read past their header lines) equal the table: Pecos 36 queue projects, 16,312.91 MW, and 10 EIA-860M generators, 1,098.5 MW; Brazoria 25, 5,134.22, 13, 2,498.9; Harris 22, 5,356.13, 5, 966.8.

## What it does not hold

- Withdrawn and completed queue positions.
- A project's distance from the node, or its bus.
- The 304 nodes `ercot_node_places` does not place.
