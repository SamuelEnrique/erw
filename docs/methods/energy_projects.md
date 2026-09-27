# Method: energy projects for the project map

Energy Research Warehouse (ERW), session 16. Table: `energy_projects` (entities shape, derived, public). Code: `warehouse/derived/energy_projects.py`. The map that reads it: the site's `/map` (platform tool 3).

## What it is

One table that puts every generator EIA lists and every interconnection queue position the ERW holds on one map. It computes nothing new: each row is one row of an input table, with the fields renamed to one set of columns and, where the source has no coordinates, a county location added.

| kind | Input table | Rows (2026-09-27) | Coordinates |
|---|---|---|---|
| operating | `eia860m_operating_generators` | 28,605 | EIA's plant lat and lon |
| planned | `eia860m_planned_generators` | 2,316 | EIA's plant lat and lon |
| queue | `ercot_`, `caiso_`, `nyiso_`, `miso_`, `spp_`, `isone_interconnection_queue` | 14,567 | none from the ISOs: county internal point |

## Columns

The entities standard columns first (`docs/datastandard.md`), then:

| Column | Meaning |
|---|---|
| `project_id` | the input row's `entity_id` (for example `eia860:10003:GEN1`, `ercot_queue:15INR0064b`) |
| `kind` | operating, planned or queue |
| `technology_group` | see below |
| `mw` | `capacity_mw` as the source states it (EIA: nameplate; queues: the requested MW; a queue may state a negative repowering request) |
| `state`, `county` | as the source states them; the state is reduced to its postal code |
| `geo_precision` | `point` (EIA's coordinates), `county` (the county's internal point), `none` (not placed) |
| `geo_note` | for a county or none row: which county and gazetteer file, or why it was not placed |
| `operator`, `operator_role` | EIA's operator (`operator`), or the queue's interconnection customer (`developer`) |
| `date`, `date_kind` | EIA operating year (`operating_year`), EIA planned operation date (`planned_operation_date`) or the queue date (`queue_date`) |
| `technology`, `source_status` | the source's own technology text and status label |
| `source_table` | the input table |

`status` is the input's standard status (operating, planned, under_construction, active, completed, withdrawn, suspended). `source` is `erw:energy_projects` and `source_url` links this page (Decision 23).

## Coordinates

1. **Point.** Where EIA gives lat and lon, they are used as given. Every EIA-860M row in the 2026-08 vintage has them.
2. **County.** Otherwise the row's county and state are looked up in the U.S. Census Bureau's county gazetteer:
   - the file: 2025 Gazetteer Files, counties, national (`2025_Gaz_counties_national.zip`, https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2025_Gazetteer/), public domain;
   - it is downloaded on each run into `warehouse/raw/census_gazetteer/<run_id>/`, with a `manifest.csv` naming the URL, time and SHA-256;
   - lat and lon are the county's **internal point** (`INTPTLAT`, `INTPTLONG`). The Census Bureau places this point inside the county, at or near its geographic center. The session 16 prompt asked for the centroid; the internal point is the gazetteer's published point, and it is always inside the county, which a centroid is not.
   - **Connecticut:** since 2022 the Census Bureau publishes planning regions instead of Connecticut's eight counties, while the ISO-NE queue still names the counties. For names the 2025 file lacks, the 2020 file (`2020_Gaz_counties_national.zip`) is used; `geo_note` names the file.
   - **Matching:** names are compared without case, accents, punctuation and the words county, parish, borough, census area and municipality; "Saint" and "St." are the same. The whole text is tried first (a county may contain a hyphen, as in Miami-Dade), then each county of a list ("Tioga - Bradford", "Kern/Kings"): the first that matches is used, and `geo_note` says the row listed several.
3. **None.** No fuzzy matching and no city lookup: a misspelled county ("Wocester"), a city named in place of a county ("Oklahoma City") or a row without a state stays unplaced, with the reason in `geo_note`. On 2026-09-27: 1,172 queue positions (286 without a state, 214 without a county, the rest a name the gazetteer does not hold).

A county point is drawn differently from an exact one on the map, and the click card says which it is.

## Technology groups

- **EIA rows:** EIA's technology text grouped by the EIA-860M connector (`TECH_GROUPS` in `warehouse/connectors/eia860.py`): solar, wind, storage (batteries, flywheels, pumped storage), natural_gas, coal, nuclear, hydro, petroleum, biomass, geothermal, other; `unknown` where EIA gives no technology.
- **Queue rows:** the ISO's fuel or technology text is grouped by `QUEUE_TECH` in the script, into the same groups plus:
  - `hybrid`: the text names more than one of solar, wind, storage or another technology ("Photovoltaic + Storage", "SUN BAT", "Hybrid - Solar/Storage");
  - `transmission`: merchant transmission requests (AC, DC, variable frequency transformer);
  - several fossil fuels only ("DFO NG") take the first one named.
  - An ISO that states no technology gives `unknown`; text that matches no group gives `other`.

## Live set

`energy_projects` repeats rows that are already in Supabase in their source tables. To stay under the live set's size limit (`max_mb` in `warehouse/supabase/live_set.yaml`), Supabase holds it without withdrawn queue positions and with only the columns the map uses (the `select` rule in `live_set.yaml`). The CSV and Redivis hold every row and column.

## Refresh

The table is a snapshot (Decision 21), rebuilt by `warehouse/run_daily.sh` after the EIA-860M and queue connectors. In CI the queue tables are on the runner only on Mondays (and on a manual run with `queues` set to 1); on other days the script skips with a warning and the previous load stays in Supabase.
