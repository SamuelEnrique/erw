# The balancing authority areas (`ba_boundaries`)

Session 8000, chain 501 step B2, 19 November 2026. Connector: `warehouse/connectors/hifld_control_areas.py`. Table: `ba_boundaries` (entities, `entity_type` `balancing_authority`, Decision 80 of `docs/datastandard.md`). Web file: `site/data/regions/ba_boundaries.json`, its shape in `docs/state/page_files_regions.md`.

## The source

"Control Areas", a layer of the Homeland Infrastructure Foundation-Level Data (HIFLD) open catalog, compiled by Oak Ridge, Los Alamos and Idaho National Laboratories with NGA's HSIP team. Its metadata: "Limitations of use: None (Public Use)". It draws the area each balancing authority balances, from the retail service territories of the utilities in it, as of its source date (21 June 2021 for most polygons; 2018 and 2017 for three).

HIFLD's own open catalog was retired on 26 August 2025, and session 180b found its hub gone and its former ArcGIS host refusing its robots file. The same national layer, 71 polygons, is served by Penn State's PASDA (Pennsylvania Spatial Data Access, the state's geospatial clearinghouse, which states "free public access"), map service `HIFLD_FEMA`, layer 26: `https://mapservices.pasda.psu.edu/server/rest/services/pasda/HIFLD_FEMA/MapServer/26`.

The reads of 19 November 2026, in order (each host's robots file first):

| Host | Answer | Taken |
|---|---|---|
| `maps.nccs.nasa.gov` (NASA's HIFLD mirror) | the name resolves to an IPv6 address only; no connection from this machine | not read |
| `www.datacommons.psu.edu` | robots 404 (no rule); the layer's ISO metadata page read once: its distribution is the retired ArcGIS host | metadata only |
| `www.datalumos.org` (ICPSR's archive copy) | robots names ClaudeBot and anthropic-ai with `Disallow: /` | not read |
| `mapservices.pasda.psu.edu` | robots 404 (no rule); the service's folder, its layer list, the count (71) and the attributes read; then the layer | read |
| `www.pasda.psu.edu` | robots 404; the "About PASDA" page read for its terms ("free public access to geospatial data") | terms |

The layer was asked whole once and the service answered "Could not access any server machines" (an HTML page, kept as `answer_error.html` in its run folder). It was then asked in nine batches of eight object ids, five seconds apart; every batch came back as a GeoJSON FeatureCollection of the polygons asked, 90.1 MB in all, joined into one file whose sha256 the table records. Each answer is saved as it came, with `requests.csv`.

## The key to EIA-930

HIFLD's `ID` is the authority's EIA entity identifier. EIA-861's annual file `Balancing_Authority_<year>.xlsx`, saved by the eia861 connector for 2015 to 2025, pairs each `BA ID` with its `BA Code`, the code EIA-930 uses. A polygon takes a code only through that pair, newest year first; nothing is matched by name. Of the 71 polygons, 67 are keyed to an EIA-930 code.

Polygons without an EIA-930 balancing authority (kept with `entity_id` `hifld:control_area:<ID>`):

| HIFLD ID | Name in the layer | EIA-861 code | Why |
|---|---|---|---|
| 3522 | Chugach Electric Assn Inc | CEA | Alaska: EIA-930 covers the lower 48 |
| 19547 | Hawaiian Electric Co Inc | HECO | Hawaii: the same |
| 55372 | New Harquahala Generating Company, LLC - HGBA | none | no EIA-861 year pairs the ID with a code (EIA-930 lists HGMA, "New Harquahala Generating Company, LLC", a match by name only, so not made) |
| 56545 | Gridforce South | GRIS | EIA-930 does not list GRIS |

EIA-930 balancing authorities of the United States with no polygon, with EIA's reference dates: BHBA (Black Hills Energy, active from 1 April 2026, after the layer's date), GLHB (GridLiance, generation only, 29 February 2020 to 1 September 2022), HGMA (New Harquahala, generation only, retired 1 June 2025; above), SIKE (Sikeston Board of Municipal Utilities, generation only, active from 1 June 2025), SWPW (Southwest Power Pool West, active from 1 April 2026) and WAUE (WAPA Upper Great Plains East, retired 1 October 2015). A page draws them as points or not at all; nothing is drawn for them from another source.

New Brunswick's system operator (NBSO) is in the layer and in EIA-930's list as a Canadian authority; it is kept.

## The table

One row a polygon. `entity_id` `eia930:<code>`; `name` as HIFLD writes it; `geo` the ISO 3166-2 code of the layer's `STATE` (the authority's address, not its whole area); `lat` and `lon` the polygon's centroid (shapely); `source` `hifld:control_areas`; `vintage` the polygon's source date. `x_area_km2` is the polygon's area on a sphere of radius 6,371.0088 km (the trapezoid rule on the sphere, holes subtracted), before simplification; `x_parts` and `x_vertices` count the raw polygon; `x_peak_load_mw` and `x_total_cap_mw` are HIFLD's figures for its `x_year` as printed (negative codes left blank); `x_raw_sha256` names the joined raw file.

## The web file

The 67 keyed polygons, each simplified by Douglas-Peucker with topology kept (shapely `simplify`, `preserve_topology`), coordinates rounded to three decimals (about 100 m). The tolerance starts at 0.01 degrees and is doubled until the file is under 1.5 MB; it was 0.01 degrees (about 1 km) and 979,100 bytes on the first build. The lists of authorities without a polygon and polygons without an authority are carried in the file.

## Limits

- The areas are as of 2021 (2017 and 2018 for three). Changes since, such as Southwest Power Pool's western expansion of April 2026, are not drawn.
- Two areas may overlap where the source's territories overlap; nothing is clipped.
- The layer is a copy served by a state clearinghouse after HIFLD's own catalog closed. Its content is HIFLD's, as the metadata says; the date of PASDA's copy is not stated by the service.

## Build

    python warehouse/connectors/hifld_control_areas.py get
    python warehouse/lock.py run --task ba_boundaries -- <python> warehouse/connectors/hifld_control_areas.py build

Not in the daily run: the layer has not changed since 2021 and its host is a mirror.
