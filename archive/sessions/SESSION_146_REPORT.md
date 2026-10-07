# Session 146 report: Where the resources are

Run on 7 October 2026 (UTC), unattended, in the chain 146 to 149. Two agents built it in one working copy to written
briefs (`runs/session146/BRIEF_DATA.md`, `BRIEF_PAGE.md`): one pulled and reduced the layers, one built the page.
I moved the layer files out of the public folder, merged, rebuilt and checked. The page is at `/resources`, under
Projects, titled "Where the resources are", locked for visitors (`review`).

## Six things to know first

- **Hydropower is not on the map, and the publisher is not USGS.** USGS publishes no hydropower potential layer
  (searched twice by the agent and once by me). The federal assessments are Oak Ridge's, for the Energy Department,
  on HydroSource, and their download page puts a form (name, e-mail, company, occupation) in front of the files.
  The file addresses answer a plain request, but that is going round the form, and no address may be sent. Nothing
  was pulled. The toggle is greyed, "not held", with the reason on hover. Your ruling: the non-powered dams file is
  one CSV of 1.6 MB (2,616 dams).
- **The capacity factor layer is not a gross capacity factor, and is not called one.** No gross raster downloads
  without a key. What is held is the 2024 wind supply curve's `capacity_factor_ac`, in the source's words "Mean
  capacity factor across 11.5km grid-cell", for a 2035 turbine; the files say neither gross nor net. Shown under
  the title "Wind capacity factor (supply curve sites)".
- **The menu changes on every page, the three live ones included.** Projects gains "Where the resources are"
  (greyed for a visitor), as you asked. To keep the menu's limit of eight entries a group, which a test enforces,
  **"Thesis Builder" moved from Projects to Tools**: not asked for. The landing's snapshot should show those menu
  lines on the live pages and no number.
- **The laboratory's terms are new in kind.** NREL (now at nlr.gov) grants use "provided that this entire notice
  appears in all copies of the Data": the whole notice is carried in each web file made from its data and in the
  Method note. The notice also holds an indemnity clause, the first among this warehouse's sources. Its four files
  are no longer linked from any live page since the site moved; they still answer, and the raw store holds them
  with their hashes.
- **BOEM names its planning layer "Rescinded July 30, 2025".** It is shown under that name; 10 of its 18 shapes
  still read "Active" in the source's own status field.
- **The layer files were open to visitors when the page was handed to me; they are not now.** They sat under the
  public folder. I moved them to `site/data/resources/layers`; a visitor's request for one answers 404, and the page
  reads them through addresses the release gate covers.

## Verdict: ready to open, for what it holds. What a developer would use first

- **First: a resource layer with the queue by county over it.** Irradiance or the wind capacity factor shows where
  the resource is; the county shading shows where others have already asked to connect. "Good resource, and how
  crowded" in two clicks and one hover. Tonight's example: Pecos County, Texas, 56 requests asking 21,364 MW, the
  most of any county drawn.
- Second: planned plants by fuel over the same layer, then datacenters (where load is arriving).
- **What is left, exactly:**
  1. Your ruling on hydropower (the form), and on a gross capacity factor (it needs a key tied to a person).
  2. The queue overlay holds four grids (ERCOT 1,758 rows, SPP 1,023, CAISO 514, ISO-NE 422): the live set holds
     no MISO or NYISO queue row.
  3. Frame time was measured in a headless browser on this laptop's own graphics (the screen was locked). With the
     screen on: `node scripts/frametime-resources.mjs http://localhost:3146`.
  4. Five vector layers as warehouse tables are blocked by the validator: the data standard has no entity type for
     a basin, play, lease area, planning area or geothermal system. A data-standard decision ("To finish").
  5. No pinch zoom on a touch screen; no check at phone width (looked at once at 390 px: no sideways scroll).
  6. The 0.05 degree grid is the finest: no source is finer than about 0.03 degrees, so no 0.025 level exists.

## What is on the map

| Toggle | Kind, as drawn | Unit (the source's) | Vintage (the source's) | Publisher |
|---|---|---|---|---|
| Wind speed at 100 m | grid, 0.2, 0.1 and 0.05 degrees | m/s | 2007 to 2013 | NREL, WIND Toolkit |
| Wind capacity factor (supply curve sites) | 56,528 points at the source's 11.5 km spacing | ratio | 2024 edition, a 2035 turbine | NREL |
| Global horizontal irradiance | grid, three levels; Hawaii and Alaska in files of their own | kWh/m2/day | 1998 to 2016 | NREL, NSRDB |
| Direct normal irradiance | the same | kWh/m2/day | 1998 to 2016 | NREL, NSRDB |
| Identified hydrothermal systems | 253 points | MWe (mean) | the 2008 assessment | USGS |
| Hydrothermal favorability | 10 class shapes, western states | class | the 2008 assessment | USGS |
| Deep enhanced geothermal favorability | 1,007 class shapes | class | 2009 | NREL |
| Sedimentary basins | 32 shapes | square miles | as of 5-6-2011 | EIA |
| Tight oil and shale gas plays | 50 shapes | square miles | updated December 2021 | EIA |
| Solid biomass by county | 3,141 counties | dry metric tons/year | data for 2012 | NREL |
| Offshore wind lease areas | 51 shapes | acres | file of 02/05/2025 | BOEM |
| Offshore wind planning areas (rescinded) | 18 shapes | none | edited 2025-02-20 | BOEM |
| Hydropower potential | greyed, "not held" | | | |

- Hydrothermal and enhanced geothermal are separate layers from separate publishers, as published.
- **Reduction of a grid:** the mean of the source's own cells inside each cell; no interpolation, no filling, no
  smoothing; a cell with fewer than half its source cells is empty. Each level's mean equals the source's over the
  same cells (wind 6.94785 against 6.94785 m/s; GHI 4.60362 against 4.60362).
- **Hover:** the value under the pointer in the source's unit, the cell size or the feature's name, the vintage,
  the publisher; each layer that is on is listed; an empty cell reads "no value in the source here". The check
  computes the value at the pointer independently, at four zooms, for every grid.
- **Overlays, each a toggle:**
  - Plants (EIA-860M of August 2026): 28,605 operating units, 2,316 planned or under construction, by fuel.
  - The queue, by county: 3,446 rows drawn in 536 counties, 271 not drawn (no county), of 3,717. No row has
    coordinates of its own; the hover says a county, not a site.
  - Datacenters: 220 drawn (83 at the operator's coordinates, 116 at a city point, 21 at a county point), 152 not
    drawn (no place stated), of 372.
- **No hub or zone is drawn.** Session 149 found none whose operator publishes a boundary.
- The address holds the view (layers on, zoom, centre). The Method note is collapsed; the face holds no method prose.
- The map is drawn with longitude and latitude straight (not the project map's Albers plane), so a grid cell is a
  rectangle and the hover reads the stored value exactly. Alaska looks wider than on a globe; the note says so.

## Every pull against its ceiling

| Pull | Ceiling | Read |
|---|---|---|
| All resource sources, raw downloads | 4 GB in total | **568,092,783 bytes** (13.2 percent), 29 files |

- The size is asked before each download and a download that would pass the ceiling is refused first (tested).
- **One read outside the ledger, by accident:** the agent's page reader followed BOEM's shapefile link and received
  the 1 MB archive; the connector then pulled it properly.
- **Contact string: exactly "ERW research project, github.com/SamuelEnrique/erw". No address sent anywhere.**
- **No MISO request. No PJM request. No model spend.**
- **Terms, quoted** (each checked against its saved page; all in the Method note):
  - NREL: "The user is granted the right, without any fee or cost, to use or copy the Data, provided that this
    entire notice appears in all copies of the Data. Further, the user agrees to credit the U.S. Department of
    Energy (DOE)/NLR/ALLIANCE in any publication that results from the use of the Data."
  - The wind supply curve (Open Energy Data Initiative): "Content is available under Creative Commons Attribution
    4.0 unless otherwise noted."
  - USGS: "USGS-authored or produced data and information are considered to be in the U.S. Public Domain." and
    "When using information from USGS information products, publications, or websites, we ask that proper credit
    be given."
  - EIA: "U.S. government publications are in the public domain and are not subject to copyright protection. You
    may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information
    products that are on our website or that you receive through our email distribution service."
  - BOEM: "Note to users: Data downloaded from this site is to be used for informational and planning purposes
    only." (the Interior Department's copyright page is quoted beside it in the Method note).
  - The laboratory names itself the National Laboratory of the Rockies (NLR), until 2025 NREL; "NREL" in this
    report is that publisher.
- The solar files' metadata says kWh/m2/year in one line; the values are daily totals. Labelled kWh/m2/day, not
  converted. Flagged.

## Model spend: none

- No model call. No cap was set for this session.

## The landing

- **Not landed when this was written.** `REVIEW_FREEZE` reads frozen through 7 October (UTC) and ends by its own
  dates at 00:00 UTC. The landing follows then, with the snapshot before and after, and a line is added here.
- Expected on the live pages: the menu's lines, no number.

## Checks

- On the fully merged build (sessions 146 to 149 together): `check-resources` 79 of 79; `check-routes` 0 failed (8
  live pages and 127 in review asked as a visitor); the datacenter page 39, the curtailment page 118, the generator
  page 43; `check-values` 7,026 of 7,026.
- `test-resources.mjs` 73 passed; `tests/test_session146.py` and `test_session146_page.py` passed.
- Frame time, every layer and combination: median 17.6 to 17.7 ms, longest 36.0 ms, none over 100 ms (headless).

## Decisions made without you

1. Hydropower left unpulled (the form).
2. The supply curve's capacity factor shown under its own name, as points, not as a "gross" grid.
3. "Thesis Builder" moved to Tools to keep eight entries under Projects.
4. The layer files moved out of the public folder.
5. Plants are read from the project map's own copy of EIA-860M; the queue is shaded by county, completed requests
   with the active ones, as the live set holds them.
6. Biomass takes the teal the site uses for nuclear, and offshore wind the violet of storage: no new colour token.
7. One row of `docs/tools.md` added, since a test requires every menu page in that inventory.

## To finish

```bash
# if you rule that Oak Ridge's file may be taken by its direct address: the commands are in
# runs/session146/agent_report_data.md, "To finish" (one CSV, 1,594,027 bytes, a points layer)

# the five vector layers as entities tables, once the data standard names their entity types:
.venv/Scripts/python.exe warehouse/connectors/resource_layers.py --tables --out-dir runs/session146/tables_trial
.venv/Scripts/python.exe warehouse/validate/erw_validate.py runs/session146/tables_trial/*.csv; echo "exit=$?"
```

## The five most interesting numbers

1. **Pecos County, Texas: 56 queue requests asking 21,364 MW**, the most of 536 counties drawn; Kern County,
   California is next, 89 requests and 17,148 MW.
2. **Planned batteries pass operating ones**: 64,458 MW planned or under construction (482 units) against 54,489 MW
   operating (1,137 units), EIA-860M of August 2026.
3. **The Salton Sea area is 2,210 MWe of the 9,061 MWe** in USGS's 253 identified hydrothermal systems: 24 percent.
4. **The best of 56,528 wind supply curve sites has a capacity factor of 0.5445**, in southern Wyoming (41.457 N,
   106.199 W); the mean is 0.312.
5. **568 MB of 4 GB**: seven kinds of resource, twelve layers, reduced to 16 MB of web files.
