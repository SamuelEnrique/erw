# ERCOT's resource nodes placed by county and zone

Energy Research Warehouse (ERW), method note written in session 901 (chain 049) for a table first written on 23 October 2026.

Tables: `ercot_node_places`

## Publisher and address

Derived by the ERW from two ERW tables, with no request: `node_basis_daily` (ERCOT's settlement points, their resource type and class) and `ercot_cdr_units` (the units of ERCOT's Capacity, Demand and Reserves report of December 2025, with each unit's county and load zone; session 872). Builder: `warehouse/derived/ercot_node_places.py`.

## Vintage and revision

Written by the run whose header line begins "Retrieved"; a run reads the two tables as the machine holds them and writes the table whole. It changes when either input does: a new CDR report, or nodes added to `node_basis_daily`.

## Shape and variables

Entities. `entity_id` `ercot_node:<settlement point>`; `entity_type` `generator` (the resource ERCOT settles at the node); `name` the settlement point; `geo` `US-TX`; the other standard columns empty.

| Column | What it is |
|---|---|
| `x_station` | the settlement point's name up to the first "_" (7RNCHSLR_ALL gives 7RNCHSLR) |
| `x_county` | the county the CDR gives every unit at that station |
| `x_zone` | the load zone the CDR gives every unit at that station (COASTAL, HOUSTON, NORTH, PANHANDLE, SOUTH, WEST) |
| `x_class`, `x_resource_type` | `node_basis_daily`'s class (gas, wind, solar, storage, mixed, other) and ERCOT's resource type |
| `x_cdr_units`, `x_cdr_units_n` | the CDR units matched, joined with ";", and their number |

When written: 569 of the 873 resource nodes placed, in 148 counties (Harris 25, Bexar 21, Brazoria 20, Hidalgo 18, Fort Bend 18). By zone: West 155, North 138, South 138, Coastal 58, Houston 53, Panhandle 27.

## The match

- A CDR unit's station code is its unit code up to the first "_" (7RNCHSLR_UNIT1 gives 7RNCHSLR). A node and a unit match when their station codes are equal.
- A node takes the county and zone only when every unit at its station gives the same county and the same zone. When written, 9 nodes' stations had units in two counties or zones and are left out; no match is guessed.
- 295 nodes have no CDR unit at their station (the CDR lists units by its own codes, which do not always begin with the settlement point's station code), left out.
- Hubs and load zones (`x_class` hub or zone) are not resources and are left out.

## License

ERCOT's terms (read 2 of `license_reads.csv`) allow its public contents to be used and redistributed unmodified with attribution; the county and zone are copied as the CDR gives them. The match is the ERW's.

## Cross-check (session 901)

The placements are plausible by class: wind nodes fall mostly in the West (61), Coastal (20) and Panhandle (18) zones, gas nodes in the South (42), North (38) and Houston (30). No other public table gives a node's county to compare.

## What it does not hold

- The wires utility (transmission and distribution service provider): the CDR names no EIA plant id, so `eia860_plants_annual`'s owner cannot be joined without a guess.
- The 304 nodes left out (295 with no CDR unit at their station, 9 whose units disagree).
- A node's hub other than `node_basis_daily`'s HB_HUBAVG.
