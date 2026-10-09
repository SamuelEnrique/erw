# Method: energy projects for the project map

> **MISO is paused (4 October 2026).** MISO's terms forbid automated access to its site, so every pull of MISO's own servers is paused pending a review; MISO's interconnection queue stays as of its last weekly pull. What is held stays as it is. [`miso_pause.md`](miso_pause.md)

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

## The page: /map, one page (session 167)

Since session 167 the project map is one page at `/map`: the layout and data of version 2 (session 105, `/map/v2`, which now redirects to `/map`) with what version 1 offered (sessions 16 and 22) carried over. Both earlier versions are kept, unrouted, in `site/app/_retired/map-v1` and `map-v2`. This section is the page's Method note; the page itself carries one source line.

### What the page reads

The site's own copy of four tables, `site/data/map.json`, written by `warehouse/derived/project_map.py` (`build_page`). The page asks no server for anything, the unit card included. The file is rebuilt with the monthly job (`warehouse/run_monthly.sh`, step `project_map`) and by hand after a write of one of the four tables; a rebuild that changes nothing but the built stamp leaves the file as it was.

| Kind | Rows of | Which |
|---|---|---|
| Operating units | `eia860m_operating_generators` | every row (EIA status OP, SB, OA, OS) |
| Planned units | `eia860m_planned_generators` | every row (EIA status P, L, T, U, V, TS, OT) |
| Queue positions | `energy_projects`, kind `queue` | not withdrawn (as version 1: a withdrawn position is not on the map), and only the queues whose rows may be drawn (below) |
| Datacenters | `datacenter_facilities` | the rows the table places in a US state |

- **Queues held back.** The list of queues whose rows may be drawn is `QUEUE_GRIDS` in `site/lib/resources.ts` (one list, switched by a person; `QUEUE_SHOWN` and `QUEUE_HELD` in `project_map.py` follow it, and a test holds the two equal). MISO: every pull of MISO's servers is paused since 4 October 2026 while a person reviews MISO's terms ([`miso_pause.md`](miso_pause.md)); MISO's queue rows are not written to the file and the page reads "MISO queue positions: paused while terms are reviewed". NYISO: its site's legal notice confers no license, so its queue rows are not shown either (energy_projects held none of them on 9 October 2026). The file counts the rows held back (`counts.queue_rows_held`). EIA's units in MISO's and NYISO's footprints are EIA's and are on the map.
- **Datacenters in no US state.** A facility the tracker places in no US state (a facility abroad, or one the news names no state for) is counted in `counts.datacenters_without_state` and not written: the map is a map of the United States.
- **The rest of the inventory.** These notes stood on version 2's face, as "What the inventory leaves out" and "How to read it":
  - Plants under 1 megawatt are not in EIA's inventory. EIA describes the form as covering "existing and proposed generating units at electric power plants with 1 megawatt or greater of combined nameplate capacity". Rooftop solar and other small generators at homes and businesses are not in it. Units smaller than 1 MW that are in it (`counts.under_1_mw`) are each at a plant that passes the threshold.
  - Retired units: the inventory lists them; this map does not. They are in the table `eia860m_retired_generators`.
  - Projects that have told no one but a grid operator: a planned unit is one its owner has reported to EIA. A request in an interconnection queue is not a planned unit until then, which is why the queue positions far outnumber the planned units. A queue position is a request, not a plant; most are withdrawn before they are built, and a completed position may be a unit the inventory already lists. That is why the page never adds a queue position's MW to a unit's.
  - The grid of a unit is EIA's balancing authority for it. The seven ISOs are named; every other balancing authority, and a blank one (`counts.without_balancing_authority` units), is "Outside the seven ISOs". A queue position's grid is the ISO whose queue it is. A datacenter's grid is "Grid not stated": the tracker names none, and none is guessed from the state.
  - A row is a generating unit, not a plant: a plant with four turbines is four units. MW is the unit's nameplate capacity.
  - Batteries are the storage units whose prime mover is a battery (EIA prime mover BA); pumped storage and the other kinds are "Other storage". A queue's storage request does not say what kind of storage it is: it is "Storage (queue positions)", in the storage color.
  - Energy for planned batteries: the inventory gives a planned battery its power in MW and no energy in MWh.
  - Puerto Rico's units are in the totals and the table; the drawing's projection (Albers, the lower 48 with Alaska and Hawaii) has no place for them. A row with no location in its source is not drawn either. The map's line says how many of the rows chosen are not drawn.
  - The inventory is monthly and published about a month after the month it describes: nothing since its vintage is in it.
- **From version 1's face** ("What the map holds" and the line under its table): MW is as each source states it: EIA's nameplate capacity; for a queue position, the MW requested; for a datacenter, the MW a story or the operator states, where one does. A queue position is drawn at its county's internal point from the Census Bureau's gazetteer (above), as a triangle, not at a site. A datacenter is placed at the operator's coordinates or at the stated county or city. Colors are the site's eight fuel colors; petroleum, biomass, geothermal, hybrid, transmission, other and "Not stated" share the color of "Everything else". Hybrid is a queue position naming more than one technology (solar and storage, for example).

### Statuses

As many as the sources give. A proposed unit keeps EIA's own status code (the connector's `eia_status` column, kept beside the folded `status` since session 8: the folded column is not used by the page and stays in the table), in plain words: "Planned, regulatory approvals not started" (P), "Regulatory approvals pending" (L), "Regulatory approvals received, not under construction" (T), "Under construction, half or less complete" (U), "Under construction, more than half complete" (V), "Construction complete, not yet operating" (TS), "Other" (OT). An operating unit is "Operating"; its card names EIA's own label when EIA's code is not OP (standby, or out of service). A queue position shows the table's standard status (active, suspended, completed, or not stated) and its card the ISO's own words. A datacenter shows the tracker's cleaned status, never the raw field of an operator's list. A status of a kind appears in the panel only while that kind is chosen.

### Totals

The sentence and the totals follow every choice. MW is never added across kinds: a unit's nameplate, a queue position's request and a datacenter's stated load are different things, so the sentence gives each kind its own count and MW, and the totals are by status, grouped by kind. A datacenter's MW is summed over the facilities that state one, and the count of those is given. A row whose source states no MW is left out as soon as a size is asked for: it cannot be said to fit one. "By technology" counts the operating units, planned units and queue positions chosen, by technology group and kind; datacenters have no technology and are not in it.

### The marks

A dot is an operating unit; a ring a planned unit (a heavier ring: under construction, EIA's U, V and TS); a triangle a queue position at its county's point; a diamond a datacenter. A mark's color is its technology and its area grows with its MW. The key under the map is plain: it toggles nothing (version 2's legend toggled statuses; the lists of the panel do that now).

### The address

Every list (kind, grid, technology, status, state) is a multi-select with "Select all" and "Clear", and the address keeps the choice: `?kind=operating,planned&grid=ercot,caiso&tech=solar,battery&status=u,v&state=CA,TX&min=100&max=500`. A list is the options' slugs with commas between them, in the page's own order; a parameter that is absent or empty means every one, and `none` means none. A slug the page does not know is passed over, so an address written today reads the same after the file gains a grid, a status or a state. A click on a state on the drawing chooses that state alone when every state is shown, then adds or takes away a state; taking the last one away shows every state again. Reset empties the address.

### The unit card

A click on a unit opens version 1's card: name and entity id, kind, technology group (with the source's own technology text), MW, status, state, county, city, grid, operator or developer, developer, date, power, location, the source table, the stories (datacenters) and the line naming the ERW table it was read from with its vintage. Version 1 read the card from Supabase through `/api/entity`, one request a click; the one page reads it from its own file. Measured on the file of 9 October 2026 (gzip): the page's data without the card is 430 KB; with the entity ids a request per click would need, 582 KB; with the card's fields, 835 KB (3.3 MB before compression). The file costs a phone about 250 KB more than the ids would, once a load, and they keep the card of the same vintage as the map, with no request that can fail (the ids of the datacenter tracker change when its merge rule does). Session 167 chose the file.
