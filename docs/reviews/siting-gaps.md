# The All grids tab: the cells the warehouse cannot fill

Started by session 703 (22 October 2026, chain 050). This file lists every cell of `/cost-of-power?view=allgrids` that the warehouse cannot fill, one row each, by grid, with the source that would fill it. Method: `docs/methods/siting.md`. Each later session of the chain adds its column's rows; session 713 completes it with each source's license, as far as the registry and `docs/licenses.md` say without a web request, and the connector it resembles.

| Grid | Column | What is not held | The source that would fill it |
|---|---|---|---|
| CAISO | Transmission and 4CP | the transmission and delivery charge a large load pays | the large-load (transmission-voltage) tariffs of PG&E, SCE and SDG&E, and CAISO's transmission access charge |
| NYISO | Transmission and 4CP | the same | the large-load service classifications of Con Edison, National Grid, NYSEG, RG&E, Central Hudson and O&R |
| ISO-NE | Transmission and 4CP | the same | the large-load rates of Eversource, National Grid and the other New England utilities, and ISO-NE's regional network service rate |
| SPP | Transmission and 4CP | the same | SPP's network integration transmission service rates by zone, and the members' large-load tariffs |
| MISO | Transmission and 4CP | the same (the grid is paused) | MISO's zonal transmission rates (attachment O) and the members' large-load tariffs, once the pause is lifted |
| PJM | Transmission and 4CP | the same | PJM's network integration transmission service rates by zone, and the utilities' large-load tariffs |
| ERCOT | Transmission and 4CP | the four peaks of summer 2026 | ERCOT's Four Coincident Peak calculation (NP9-83-M), published by 1 December 2026 (`warehouse/connectors/ercot_4cp.py`) |
| ERCOT | Transmission and 4CP | the wires utility's own transmission and distribution charges at a node | the node's wires utility (not held, see the node rows) and its tariff; Texas's four large wires utilities' tariffs are held for "Your load" (`texas_delivery.json`) |
| All but ERCOT | Energy, flexible compute | the grid's peak intervals that set a transmission charge | each grid's peak-hour rules (PJM 5CP, ISO-NE and NYISO annual peak), with the hours, not held |
