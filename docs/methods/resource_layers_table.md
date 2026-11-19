# The natural resource map's layers as a table (`resource_layer_features`), and the coal fields

Session 8006, chain 501 step D1, 19 November 2026. Builder: `warehouse/derived/resource_tables.py`. Table: `resource_layer_features` (entities, `entity_type` `resource`, Decision 81 of `docs/datastandard.md`). New web file: `site/data/resources/coal_fields.json`. The other layers' web files are those the page "Where the resources are" already reads (`site/data/resources/layers/`, described by `site/data/resources/manifest.json`, session 146's `docs/methods/resource_layers.md`); they are not changed.

## What the table holds

One row for every cell, site or area of each layer that describes a resource in the ground, the sun or the wind:

| Layer | Kind | Rows (19 November 2026) | Value |
|---|---|---|---|
| `wind_speed_100m` | grid, 0.05 degrees, the lower 48 | 433,080 | mean wind speed at 100 m, m/s |
| `solar_ghi` | grid, 0.05 degrees | 436,141 | global horizontal irradiance, kWh/m2/day |
| `solar_dni` | grid, 0.05 degrees | 436,141 | direct normal irradiance, kWh/m2/day |
| `wind_capacity_factor` | sites (supply-curve sites) | 56,528 | capacity factor, ratio |
| `geothermal_hydrothermal_sites` | sites | 253 | the publisher's MWe figure |
| `hydropower_npd` | sites (non-powered dams) | 2,616 | potential capacity, MW |
| `geothermal_hydrothermal_favorability` | areas | 10 | favorability class |
| `geothermal_egs_favorability` | areas | 1,007 | favorability class |
| `oil_gas_basins` | areas | 32 | area, square miles |
| `oil_gas_plays` | areas | 50 | area, square miles |
| `hydropower_nsd` | areas (HUC10 watersheds) | 2,027 | potential capacity, MW |
| `biomass` | areas (counties) | 3,141 | solid biomass, dry metric tons a year |
| `coal_fields` | areas | 602 | none: province, field, age and rank in `x_extra` |

A grid cell's value is the layer's value as `warehouse/connectors/resource_layers.py` reduced the publisher's raster (its method), at the finest level the page holds; a site's or an area's is the publisher's own field the manifest names; the publisher's other fields are kept in `x_extra` as JSON. `lat` and `lon` are a cell's center or a feature's centroid; `x_area_km2` an area's size on a sphere of radius 6,371.0088 km. Each row carries its layer's source address, retrieval time and the sha256 of the publisher's file.

Left out: the offshore wind lease areas and planning areas (rights to build and areas planned for leases, not a resource), and the Alaska and Hawaii grids (in their web files, not in the table).

## The coal fields (new)

U.S. Geological Survey Open-File Report 2012-1205: East, J.A., 2013, Coal fields of the conterminous United States, National Coal Resource Assessment updated version (`https://pubs.usgs.gov/of/2012/1205/`). Its `Downloads/GIS.zip` (230 MB, saved with its sha256 in `warehouse/raw/usgs_coal_fields/`), shapefile `Updated Coal Fields/Coal_Fields.shp`: 602 polygons, each with its province, field name, age and coal rank, NAD83, read in WGS 84. Public domain (USGS). `pubs.usgs.gov`'s robots file disallows only `/archive/`.

The web file draws each polygon simplified (Douglas-Peucker with topology kept, coordinates to three decimals): 544,878 bytes at a tolerance of 0.005 degrees on the first build.

## Not pulled, and why (for Samuel's ruling, default "not pulled")

- **Uranium and critical-mineral deposits.** USGS's mineral deposit databases (MRDS, USMIN) are served from `mrdata.usgs.gov`, whose robots file opens with `User-agent: *` and `Disallow: /` (a second group for `*` disallows only some paths; the stricter reading is kept), and from ScienceBase (`www.sciencebase.gov`), whose robots file disallows ClaudeBot, Claude-User and anthropic-ai by name. Neither was read. EIA's U.S. Energy Atlas catalog (read 19 November 2026) lists no uranium or mineral deposit layer. The held `usgs_mcs_critical_minerals` is national commodity statistics, not places, so it draws no layer.
- **The atlas's own copy of the coal fields** (Esri's "USA Coal Fields") is under the Esri Master License Agreement; the USGS report's own files are public domain, so those were read instead.

## Build

    python warehouse/lock.py run --task resources -- <python> warehouse/derived/resource_tables.py
