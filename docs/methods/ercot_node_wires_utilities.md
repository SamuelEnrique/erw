# The wires utilities in an ERCOT node's county

Energy Research Warehouse (ERW), method note written in session 945 (chain 053) for a table first written on 23 October 2026.

Tables: `ercot_node_wires_utilities`

## Publisher and address

Derived by the ERW from four ERW tables, with no request: `ercot_node_places` (ERCOT's resource nodes placed by the county and load zone of their CDR units; session 901), `utility_service_territories` (Form EIA-861's utility and county pairs; session 667), `eia861_delivery_only` (EIA-861's delivery-only companies, Texas's transmission and distribution utilities; session 853) and `eia861_utility_data` (EIA-861's utility data, with each utility's NERC regions). Builder: `warehouse/derived/ercot_node_wires_utilities.py`.

## Vintage and revision

Written by the run whose header line begins "Retrieved"; a run reads the four tables as the machine holds them and writes the table whole. `vintage` names the EIA-861 year the territories give (2025 when written); the delivery-only companies and the NERC regions are read for the same year. It changes with EIA-861's annual release or a new CDR report.

## Shape and variables

Entities, one row a placed node. `entity_id` `ercot_node:<settlement point>` (the same ids as `ercot_node_places`); `entity_type` `generator`; `name` the settlement point; `geo` `US-TX`; the other standard columns empty.

| Column | What it is |
|---|---|
| `x_county`, `x_zone` | the node's county and load zone, as `ercot_node_places` gives them |
| `x_utilities_n`, `x_utilities` | the utilities EIA-861 lists as serving the county (state TX), each "<name> (<EIA utility number>)", sorted, joined by "; " |
| `x_delivery_only_n`, `x_delivery_only` | the delivery-only companies among them: those `eia861_delivery_only` holds for Texas in the same year (AEP Texas Central, AEP Texas North, CenterPoint, Oncor, Texas-New Mexico Power, Nueces Electric Cooperative and the City of Lubbock when written) |
| `x_outside_tre_n`, `x_outside_tre` | those whose EIA-861 utility data names a NERC region but not Texas RE (Entergy Texas, Southwestern Public Service, El Paso Electric and some cooperatives): the county has a part outside ERCOT's region |
| `x_short_form_n` | those filing EIA's short form, whose utility data gives no region |

When written: 569 nodes in 148 counties. 517 nodes have a delivery-only company in their county, 287 exactly one, 191 two and 39 three; 52 nodes in 18 counties have none (21 of them in Bexar, served by the City of San Antonio and cooperatives, which own their wires). 128 nodes have a utility outside Texas RE in their county. A county lists from 1 to 8 utilities (median 4).

## The join

- A utility serves a node's county when `utility_service_territories` lists the pair for Texas, the county in capitals with runs of spaces made one. Every placed node's county is in the territories; a county in none stops the run.
- EIA gives no share of a county and no boundary: a utility serving the county may not serve the node's site, and where the county lists two delivery-only companies the table does not choose one.
- A transmission-only company (LCRA Transmission Services, Electric Transmission Texas, Sharyland and the others with no customers) is in no territory, so in no row: the table names the utilities that deliver to customers in the county, the ones a load sited there would connect through, not the owner of the line the generator ties into.
- A municipal utility or cooperative in ERCOT owns its wires and is listed among `x_utilities`, not `x_delivery_only`.

## License

EIA's (record 1, public) and ERCOT's terms (read 2 of `license_reads.csv`). The join is the ERW's.

## Cross-check (session 945)

By load zone, the delivery-only companies are the ones the grid's map gives: all 53 Houston nodes have CenterPoint in their county; 127 of 138 North nodes have Oncor; 89 of 138 South nodes have AEP Texas Central; West nodes have Oncor (126), AEP Texas North (87) and Texas-New Mexico Power (52). Bexar, Pecos and Harris read by hand from the territories equal the table: Bexar 5 utilities and no delivery-only company; Pecos 5, three of them delivery-only (AEP Texas North, Oncor, Texas-New Mexico Power); Harris 3, CenterPoint delivery-only and Entergy Texas outside Texas RE.

## What it does not hold

- The utility at the node's site, or a share of the county.
- Transmission-only companies.
- The 304 nodes `ercot_node_places` does not place.
