# Session 2889 report: ERCOT nodes, the wires utility (TSP)

6 November 2026, about 03:26 UTC, on lab-desktop (the data machine), chain 148, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **Held, and not enough for the cell:** `ercot_node_wires_utilities` (session 945) lists, for each of the 569 placed nodes, the utilities EIA-861 names in the node's county: 517 with a delivery-only company in the county, 287 with exactly one. Its header says it: "A utility serving the county may not serve the node's site." The tab's Utility cell for a node therefore stays "not held". A county's utility is not a node's TSP.
- **ERCOT's resource registration** (the TSP a resource connects to) is published through MIS (`/misapp`), which ERCOT's robots file disallows.

## Decisions made without you

- **The county's utilities not drawn as the node's TSP.**

## For Samuel's ruling

- **A node's TSP from ERCOT's MIS lists** (the `/misapp` ruling of chain 147's note, item 1).
