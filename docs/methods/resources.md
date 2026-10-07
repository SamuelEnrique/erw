# Where the resources are: the natural resource layers

Session 146 (7 October 2026). The page `/resources` draws the natural resource itself, not what is built on it.
Every layer is a publisher's own file, reduced to a size a browser can draw. The file as downloaded keeps the
full resolution in the warehouse's raw store (`warehouse/raw/resources/`, with `downloads.csv`: the address,
the bytes, the hash and the retrieval time of every file and of every terms page). The connector is
`warehouse/connectors/resource_layers.py`; the layers it writes are in `site/public/resources-data/` and are
described, one entry a layer, in `site/data/resources/manifest.json`.

## What holds for every layer

- **Nothing is filled, smoothed or interpolated.** Where the source has no value the layer has none, and the
  page says "no value in the source here".
- **Units are the source's own**, as the source writes them. Nothing is converted.
- **The vintage is what the source states** (the years averaged, the assessment's date, the file's date). Where
  the source states none, the layer says so and gives the file's own date.
- **A grid layer** is a regular grid of longitude and latitude (WGS84) at 0.2, 0.1, 0.05 and 0.025 degrees, and
  never finer than the source: a level whose cell would be smaller than the source's own cell is not built. A
  cell's value is the mean of the source's own valid cells whose centres fall inside it. A cell in which fewer
  than half of the source's cells hold a value is empty. For each level the connector prints the level's mean,
  weighted by the number of source cells in each cell, beside the source's mean over the same cells: the two
  agree to the last stored digit, and the build stops if they do not.
- **A shapes layer** is the source's polygons in WGS84 with each polygon simplified to a stated tolerance
  (topology kept, one feature at a time) and its coordinates written to 3 decimals (about 100 m). No feature
  is dropped; each keeps the source's own fields.
- **A points layer** holds the source's rows, each at the source's own longitude and latitude. None is placed
  by hand.
- **The ceiling.** All downloads together stay under 4 GB. The connector asks the size of a file before it
  reads it and refuses a download that would pass the ceiling.
- **A resource layer is not a siting study.** It says nothing of land that may be used, of the grid, of permits
  or of cost.

<!-- The sections below are written from the manifest by resource_layers.py --method-doc -->

## Sedimentary basins (`oil_gas_basins`)

- **What it is.** EIA's words: "Sedimentary basins associated with the EIA shale plays as of 5-6-2011. Sedimentary basin which do not have shale plays as of publication date are not included in this file. Sources for the basins are mostly from the US Geological Survey and state agencies such as the WY Geological Survey." It is an outline of where the basins lie, not a measure of oil or gas in place or of what can be recovered. The file's own limit: "These data and related graphics, if available, are not legal documents and are not intended to be used as such. The information contained in these data is dynamic and may change over time."
- **Publisher.** U.S. Energy Information Administration (EIA). U.S. Sedimentary Basins (SedimentaryBasins_US_May2011_v2.shp).
- **File.** `eia/SedimentaryBasins_US_EIA.zip` in the raw store, 440,871 bytes, sha256 `02a017ccb84bdcc1`, retrieved 2026-10-07T21:26:20Z from <https://www.eia.gov/maps/map_data/SedimentaryBasins_US_EIA.zip>.
- **Vintage.** as of 5-6-2011 (the file's metadata: "Sedimentary basins associated with the EIA shale plays as of 5-6-2011"); file modified 10 March 2016.
- **Extent.** contiguous United States. Source resolution: polygons, no scale stated by the source.
- **Reduction.** each polygon simplified to 0.01 degrees with its topology kept (Douglas-Peucker, one feature at a time); coordinates to 3 decimals; no feature dropped.
- **Web file.** `oil_gas_basins.json`, 68,698 bytes, 32 features. area of the basin (the source's Area_sq_mi), in square miles: minimum 1,289, mean 35,363, maximum 160,408 over 32 features.
- **Terms.** <https://www.eia.gov/about/copyrights_reuse.php> (saved as `eia/terms/eia_copyrights_reuse.html`, sha256 `a9747722112b2c55`): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service. However, if you use or reproduce any of our information products, you should use an acknowledgment, which includes the publication date, such as: "Source: U.S. Energy Information Administration (Oct 2008).""
- **Acknowledgment.** Source: U.S. Energy Information Administration (May 2011).

## Tight oil and shale gas plays (`oil_gas_plays`)

- **What it is.** EIA's words: "General areas for shale plays in the U.S. Source: EIA based on Enverus DrillingInfo Inc., the U.S. Geological Survey, publicly available peer-reviewed research papers, academic theses, and publications of State Geological Agencies. Updated December 2021 with addition of Spraberry and Wolfcamp Plays in the Permian Basin." A play's outline is a general area, not a reserve estimate and not a lease map. The file's own limit: "None (public use). Users are advised to thoroughly review the metadata to understand the appropriate use and limitations of the data."
- **Publisher.** U.S. Energy Information Administration (EIA). Tight Oil and Shale Gas Plays in the U.S. (ShalePlays_US_EIA_Dec2021.shp).
- **File.** `eia/TightOil_ShaleGas_Plays_Lower48_EIA.zip` in the raw store, 323,424 bytes, sha256 `c09b3bd2982754cf`, retrieved 2026-10-07T21:26:20Z from <https://www.eia.gov/maps/map_data/TightOil_ShaleGas_Plays_Lower48_EIA.zip>.
- **Vintage.** updated December 2021 (the file's metadata: "Updated December 2021 with addition of Spraberry and Wolfcamp Plays in the Permian Basin").
- **Extent.** contiguous United States (the source's Lower 48). Source resolution: polygons, "General areas for shale plays in the U.S.".
- **Reduction.** each polygon simplified to 0.01 degrees with its topology kept (Douglas-Peucker, one feature at a time); coordinates to 3 decimals; no feature dropped.
- **Web file.** `oil_gas_plays.json`, 55,755 bytes, 50 features. area of the play (the source's Area_sq_mi), in square miles: minimum 184.8, mean 10,280, maximum 59,054 over 50 features.
- **Terms.** <https://www.eia.gov/about/copyrights_reuse.php> (saved as `eia/terms/eia_copyrights_reuse.html`, sha256 `a9747722112b2c55`): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service. However, if you use or reproduce any of our information products, you should use an acknowledgment, which includes the publication date, such as: "Source: U.S. Energy Information Administration (Oct 2008).""
- **Acknowledgment.** Source: U.S. Energy Information Administration (Dec 2021).

## Offshore wind lease areas (`offshore_wind_leases`)

- **What it is.** BOEM's words: "Boundaries of renewable energy lease areas, wind planning areas, and marine hydrokinetic planning areas (last file update on 02/05/2025)." These are the outlines of leases, easements and research leases BOEM has issued; a lease is a right to propose a project, not a wind farm and not a measure of the wind. A lease's status may have changed since the file's date. Where the source's ACRES field is 0 (some easements and cable routes) no area is shown: the field is kept as the source wrote it and the value is left empty.
- **Publisher.** Bureau of Ocean Energy Management (BOEM). Renewable Energy Leases and Planning Areas, All Shapefile (Offshore_Wind_Leases_outlines.shp).
- **File.** `boem/boem-renewable-energy-shapefiles.zip` in the raw store, 1,031,812 bytes, sha256 `47c5f33f5d16cede`, retrieved 2026-10-07T21:26:22Z from <https://www.boem.gov/renewable-energy/boem-renewable-energy-shapefiles>.
- **Vintage.** last file update on 02/05/2025 (BOEM's page); the archive on BOEM's server is dated 6 August 2025.
- **Extent.** US Outer Continental Shelf: Atlantic, Gulf and Pacific. Source resolution: lease outlines built from Outer Continental Shelf blocks.
- **Reduction.** coordinates to 3 decimals (about 100 m); no other simplification; no feature dropped.
- **Web file.** `offshore_wind_leases.json`, 78,536 bytes, 51 features. area of the lease (the source's ACRES), in acres: minimum 578, mean 75,124, maximum 176,505 over 46 features.
- **Terms.** <https://www.boem.gov/renewable-energy/mapping-and-data/renewable-energy-gis-data> (saved as `boem/terms/boem_renewable_energy_gis_data.html`, sha256 `f337e0627c8370d8`): "Note to users: Data downloaded from this site is to be used for informational and planning purposes only."

## Offshore wind planning areas (rescinded July 30, 2025) (`offshore_wind_planning_areas`)

- **What it is.** BOEM's words: "These data are an outline version of BOEM's offshore wind planning areas. These areas represent the current investigations by BOEM for new areas of interest in wind energy development. Individual blocks within each wind planning area dissolved into single polygons to generate the area outlines." BOEM's own name for the layer is "Offshore Wind Planning Area Outlines (Rescinded July 30, 2025)": the planning areas were rescinded, and are shown as the record of where BOEM had been looking, not as areas open to leasing. The archive BOEM offers for download holds the leases only; the planning areas come from BOEM's public map service, which BOEM's page links. The service holds 19 rows; one has no shape and no name and is not drawn. Each area's AREA_STATUS (Active or Inactive) is the source's own field and was last edited before the rescission.
- **Publisher.** Bureau of Ocean Energy Management (BOEM). Offshore Wind Planning Area Outlines (Rescinded July 30, 2025).
- **File.** `boem/Wind_Planning_Area_Boundaries_layer0.geojson` in the raw store, 131,232 bytes, sha256 `bc0623cee11e64bb`, retrieved 2026-10-07T21:28:41Z from <https://services7.arcgis.com/G5Ma95RzqJRPKsWL/ArcGIS/rest/services/Wind_Planning_Area_Boundaries__BOEM_/FeatureServer/0/query?where=1%3D1&outFields=*&outSR=4326&f=geojson>.
- **Vintage.** data last edited 2025-02-20 (the service's own date); BOEM names the layer "Offshore Wind Planning Area Outlines (Rescinded July 30, 2025)".
- **Extent.** US Outer Continental Shelf. Source resolution: planning area outlines built from Outer Continental Shelf blocks.
- **Reduction.** coordinates to 3 decimals (about 100 m); no other simplification; no feature dropped.
- **Web file.** `offshore_wind_planning_areas.json`, 28,458 bytes, 18 features.
- **Terms.** <https://www.boem.gov/renewable-energy/mapping-and-data/renewable-energy-gis-data> (saved as `boem/terms/boem_renewable_energy_gis_data.html`, sha256 `f337e0627c8370d8`): "Note to users: Data downloaded from this site is to be used for informational and planning purposes only."

## Not held

- **Wind speed at 100 m** (`wind_speed_100m`): not built yet
- **Wind capacity factor** (`wind_capacity_factor`): not built yet
- **Global horizontal irradiance** (`solar_ghi`): not built yet
- **Direct normal irradiance** (`solar_dni`): not built yet
- **Identified hydrothermal sites** (`geothermal_hydrothermal_sites`): not built yet
- **Deep enhanced geothermal favorability** (`geothermal_egs_favorability`): not built yet
- **Hydropower potential** (`hydropower_potential`): not built yet
- **Biomass resource** (`biomass`): not built yet
