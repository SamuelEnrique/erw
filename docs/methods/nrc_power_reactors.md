# The NRC's power reactor units

Energy Research Warehouse (ERW), method note written in session 932 (chain 052) for a table first written on 23 October 2026.

Tables: `nrc_power_reactors`

## Publisher and address

U.S. Nuclear Regulatory Commission (NRC): the List of Power Reactor Units (`https://www.nrc.gov/reactors/operating/list-power-reactor-units.html`) and two datasets of the NRC Data page, the operating reactors and the reactors in decommissioning (`.../reading-rm/doc-collections/datasets/reactors-operating.xlsx`, `reactors-decommissioning.xlsx`). Connector: `warehouse/connectors/nrc_reactors.py` (session 925).

## Vintage and revision

The list as read on 23 October 2026 (95 operating units); the datasets' "Year of Update" 2022 (last modified September 2025). A snapshot: each run replaces the table whole, asking for the list again and reusing the saved datasets (ceiling: three requests; `--offline` asks nothing).

## Shape and variables

Entities, one row a reactor unit. `entity_id` `nrc_reactor:<docket number>`; `entity_type` `generator`; `name` the list's name (the dataset's for a retired unit); `geo` `US-<state>` from the location's last two letters; `capacity_mw` the operating dataset's Capacity MWe; `status` `operating` (on the list, 95) or `retired` (in decommissioning, 35; `status_date` the shutdown); `operator` the list's owner and operator.

`x_*`: the list's license number, reactor type, location and NRC region; the datasets' parent company, licensee, containment and steam supply types, architect-engineer, constructor, construction permit, operating license, commercial operation, renewed and subsequent renewed licenses, license expiry, licensed MWt, and for a retired unit its shutdown, license termination, estimated closure, decommissioning method and license status; `x_dataset_year` the datasets' year (2022).

## Reading the documents

- The list's table must have its six headings as read; a row's name cell must end in an eight-digit docket.
- The datasets' columns are found by heading; a docket given twice stops the run. A date cell with words (the NRC's "Application Withdrawn", 2 cells) keeps them as given and is counted in the header.
- A unit on the list but not in the dataset (Palisades, Vogtle 4) keeps its dataset columns empty; the dataset's licenses expiring in the 2020s (7 units) may have been renewed since 2022.
- The datasets' derived columns (age, license remaining, as of 2022) and capacity factors are not taken.

## License

Public: "NRC's website constitutes a U.S. Government Work under federal copyright law and as such, it is not subject to copyright" (read 16 of `license_reads.csv`).

## Cross-checks (sessions 925 and 932)

- Every operating unit is a unit of `nrc_reactor_status`'s last day (95 and 95, matched by name; four spelled apart: Harris 1, LaSalle 1 and 2, River Bend 1).
- Capacity: 95,869 MWe for the 93 units the dataset holds, against EIA-860M's 98,423 MW of net summer capacity for 96 nuclear generators today.
- Session 932, against the table: the 95 operating units are 64 PWR and 31 BWR; the 35 retired are 18 PWR, 2 PWR CE, 10 BWR, 1 BWR Mark 1, 2 HTG, 1 SCF and 1 experimental superheat reactor, as the decommissioning dataset types them.

## What it does not hold

- Research and test reactors, new reactors under review, and the NRC's daily power levels (`nrc_reactor_status` holds those).
