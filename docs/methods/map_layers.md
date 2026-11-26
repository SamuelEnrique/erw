# The project map's line layers (`/map`)

Session 8014, chain 581 (part D), 20 November 2026. Connector: `warehouse/connectors/hifld_lines.py` (`get`, then `build` under the data lock). Tables: `hifld_transmission_lines` and `eia_hgl_pipelines` (entities, Decision 82). Web files: `site/data/map_layers/transmission_230kv.json` and `hgl_pipelines.json`, served by `/map/lines/<name>` and read by the map only when a switch is turned on. License: public.

## What exists, read first (session 8014)

`/map` has three tabs. Projects draws EIA's operating and planned generating units, the public interconnection queues and the datacenter tracker, with switches by kind, grid, technology, status, state, size and distance. Resources draws the natural resource layers (`site/data/resources/`). Queues draws the queue tables. No layer of pipelines, terminals, refineries, storage fields, transmission lines or substations was drawn. Held in the warehouse without coordinates: `eia_gas_pipeline_projects` (EIA's pipeline projects), `eia_lng_liquefaction_projects` (EIA's liquefaction capacity), `eia_refinery_capacity_annual` (refineries and their capacity): none can be placed on a map without a point the source does not give.

## The sources read, in order (20 November 2026; `runs/c581/probe/probe.csv`, each answer kept under `runs/license_reads/c581/`)

| # | Host and request | Answer | Taken |
|---|---|---|---|
| 1 | `atlas.eia.gov/robots.txt` | 200: `User-agent: *`, `Crawl-delay: 60`, six folders disallowed, none read here | the atlas may be read, a minute apart |
| 2 | `mapservices.pasda.psu.edu/robots.txt` | 404: no rule | may be read |
| 3, 4 | PASDA's folder `pasda` and service `HIFLD_FEMA` | the layer list: `Transmission_Lines` (178), `HGL_Pipelines_US_EIA` (47), `POL_Terminals` (126), `Above_Ground_LNG_Storage_Facilities` (3); no natural gas, crude oil or product pipelines, no LNG terminals, refineries, storage fields, compressor stations or substations | 178 and 47 |
| 5 | `atlas.eia.gov/api/feed/dcat-us/1.1.json`, after 61 seconds | 200: the catalogue's first 100 items (the shale plays, the basins, the storage regions, weather); its distributions name EIA's layers at `services7.arcgis.com/FGr1D95XCGALKXqM` | the host of EIA's layers |
| 6 | `atlas.eia.gov/api/search/v1/...`, after 61 seconds | 404 | |
| 7 | `www.eia.gov/robots.txt` | 200: `Allow: /`, a list of disallowed folders, none matching `/maps/` | |
| 8 | `www.eia.gov/maps/layer_info-m.php` | 200, a page that now points to the US Energy Atlas; no layer file | |
| 9 | `services7.arcgis.com/robots.txt` | 403, `Invalid URL` | **not read**: the stricter reading kept, as session 180b did for another ArcGIS host (Python's reader treats a 403 as "nothing may be asked"; RFC 9309 as "no rule") |
| 10 to 13 | PASDA layers 178, 178's count of `VOLTAGE>=230`, 47 and 126 | layer 178: polylines, fields `ID`, `TYPE`, `STATUS`, `OWNER`, `VOLTAGE`, `VOLT_CLASS`, `INFERRED`, `SUB_1`, `SUB_2`, `SOURCE`, `SOURCEDATE`, `VAL_DATE`; 10,692 lines of 230 kV and above. Layer 47: "Major hydrocarbon gas liquids (HGL) pipelines in the United States ... Updated January 2020", copyright text "U.S. Energy Information Administration" | |

Then `hifld_lines.py get`: 30 requests five seconds apart (each layer's object ids, then its features by ranges of object ids: the service answers 404 to a list of 400 ids in the address), 34,806,396 bytes for the transmission lines and 102,842 for the HGL pipelines, kept under `warehouse/raw/hifld_lines/<run>/` with each request's time, size and sha256.

Terms: HIFLD's layers carry "None (Public Use)" in their metadata (the verdict read for HIFLD as PASDA serves it, read 2061 of the license record, on its Control Areas layer); PASDA states "free public access"; EIA's data are in the public domain (EIA's copyright and reuse page). A table's verdict is its publisher's.

## Not pulled, and why (for Samuel's ruling, default not pulled)

- EIA's layers of natural gas interstate and intrastate pipelines, crude oil pipelines, petroleum product pipelines, LNG import and export terminals, petroleum refineries and natural gas underground storage: served from `services7.arcgis.com`, whose robots file answers 403. Not read.
- HIFLD's natural gas compressor stations and electric substations: not in any service the ERW read (HIFLD's open catalog was retired on 26 August 2025; PASDA's mirror does not hold them).

## The tables

`hifld_transmission_lines`: one row a line of 230 kV and above. `entity_id` `hifld:transmission_line:<HIFLD ID>`; `name` "<SUB_1> to <SUB_2>" where HIFLD names both ends; `operator` HIFLD's `OWNER` (NOT AVAILABLE left blank); `status` `operating` for IN SERVICE, `under_construction` for UNDER CONSTRUCTION, else blank, with HIFLD's word in `x_status`; `lat` and `lon` the line's midpoint; `geo` blank (a line crosses states); `x_voltage_kv` HIFLD's `VOLTAGE`; `x_length_km` the drawn line's length on a sphere of radius 6,371.0088 km.

`eia_hgl_pipelines`: one row a pipeline segment of EIA's layer. `entity_id` `eia:hgl_pipeline:<OBJECTID>`; `name` EIA's `Pipename`; `operator` EIA's `Opername`; `x_length_km` as above. EIA gives no capacity.

## The web files and the switches

Each line simplified (Douglas-Peucker) at a tolerance doubled from 0.005 degrees until the file is under 2 MB, coordinates rounded to 3 decimals, in columns (`fields`, `rows`, `names`, `paths`). On `/map`'s Projects tab, under "Lines on the map", each layer is a switch, off as the page opens; turned on, its file is read once and drawn under the marks. A line's hover gives its name (its two ends, or EIA's name), its operator, its size and unit (kV, or km where EIA gives no capacity), "State: not in the source (a line crosses states)", and its source with its table.

**What the drawing does not tell apart (session 10216, the map audit of 26 November 2026, finding 4).** The pull asks for every line whose `VOLTAGE` is 230 or more, with no condition on `STATUS`, and the web file keeps `id`, `kv`, `owner`, `from`, `to` and `km` only. So a line HIFLD lists as under construction, or with a status it does not state, is drawn as a line in service, and a voltage HIFLD marks as inferred (`INFERRED`) is drawn as any other. The date in a line's hover is `retrieved_at`, the day the ERW read PASDA's copy; HIFLD's own dates (`SOURCEDATE`, `VAL_DATE`) are in `hifld_transmission_lines` line by line (`x_source_date`, `x_val_date`), with `x_status` and `x_inferred`, and not in the web file. HIFLD's open catalog was retired on 26 August 2025, so PASDA's copy may be older than the day it was read. The tip of "Lines on the map" says so; how many lines each status, flag and year holds is a data request of the audit.

## Run

`python warehouse/connectors/hifld_lines.py get` (about three minutes), then `build` (about five seconds, under the data lock); `build --out-dir DIR` for a trial.
