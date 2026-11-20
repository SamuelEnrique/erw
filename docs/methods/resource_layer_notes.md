# Notes on three layers of the resource map (`site/data/resources/layer_notes_added.json`)

Energy Research Warehouse (ERW). Session 8013, chain 505, data requests 554 to 556 (`docs/state/data_requests_done_line.md`), asked by the portable laptop's replications of the resource map (chain 504). Builder: `warehouse/derived/resource_layer_notes.py`. Test: `tests/test_session8013.py`.

## Why a new file

The three layers were written in October by `warehouse/connectors/resource_layers.py`, and `site/data/resources/manifest.json` describes them. Chain 505 adds and never changes an existing page file, so the layers and the manifest stay as they are, and the answers are in a new file beside them, in the way data request 553's answer was (`hover_fields_added.json`). The page that wants them reads this file. No figure of any layer is in question: each replication met every figure.

## What the file holds

- **`oil_gas_basins` (request 554).** EIA's field `NAME` is in capitals; the connector writes each word with its first letter a capital (`str.title`). The rule stated here: a word or hyphenated part that is a US state's postal code keeps its capitals; "and", "of", "the" and "in" are small unless first; every other word has its first letter a capital. A basin is listed only where the rule's name differs from the layer's: of 32 basins, two ("TX-LA-MS SALT" as "TX-LA-MS Salt", "VALLEY AND RIDGE" as "Valley and Ridge"). The plays' names keep the publisher's own text (no `str.title`), so none is listed.
- **`wind_capacity_factor` (request 555).** The decimals each column of the web file keeps, measured over all 56,528 rows: coordinates 3, the capacity factor 4, the wind speed 2, the developable area 1 (the capacity is whole megawatts). The key `reduction_all_roundings` is the manifest's sentence naming all four; the manifest's own sentence named two.
- **`offshore_wind_leases` (request 556).** BOEM's archive has two tables: the lease outlines, which the layer draws, and the lease blocks. Every outline whose `LEASE_TYPE` is not among the types the blocks table gives the same lease is listed with both: OCS-A 0497 (Virginia Department of Energy; outline "Commercial", blocks "Easement" and "Research"), OCS-A 0506 (The Narragansett Electric Company; outline "Commercial", blocks "Right-of-Way Grant"), and OCS-G 37334 Provisional (RWE Offshore US Gulf; outline "Commercial", no row in the blocks table). Nothing chooses between BOEM's two tables.

## Limits

The name rule is the ERW's own way of writing a name, applied to EIA's text; EIA's `NAME` stays in the layer beside it. The decimals are what the web file keeps, not what the publisher printed.
