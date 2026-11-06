# Session 2880 report: the wiring, the tab read

5 November 2026, about 22:28 UTC, on lab-desktop (the data machine), chain 147, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **Nothing was wired, because nothing this chain landed fills a cell of the All grids tab:**
  - **Tariffs:** `utility_large_load_tariffs` holds Georgia Power (SOCO, not a grid of the tab), PGE (not a grid of the tab) and Indiana Michigan Power (PJM). The tab's only PJM row is `pjm:grid`, placed in Allegheny County, PA (`siting_page.ROW_COUNTY`: Duquesne Light). MISO's row is in Marion County, IN (AES Indiana). Writing `tariffs.json` and reading it would show the same "not held" in every cell.
  - **A zone's growth:** already drawn for the sub-region rows since session 728 (`headroom.json` `zones`). Replacing it with `subregion_demand_growth` would move figures: the hour screening differs slightly. That is a page change without a ruling.
  - **Substations, reserve margins, the node mapping:** not held (sessions 2876, 2878, 2879).
- **No branch was made and no gate was run.** The tab was not read at 390 and 1280: it does not change.

## Decisions made without you

- **`tariffs.json` not written** until a tab row sits in a held utility's territory. It is the first file to wire once the registry holds a utility under one of the tab's rows (Duquesne Light, AES Indiana, Oncor, CenterPoint, the New York and New England utilities of chain 148's sessions 2895 to 2897).

## For Samuel's ruling

- **Whether the tab's zone growth should switch to `subregion_demand_growth`'s screened means.** Its figures would move by the hours the screen leaves out.

## Files

- New: this report.
