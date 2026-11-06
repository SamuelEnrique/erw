# The generator pipeline by grid

Energy Research Warehouse (ERW), method note written in session 2951 (chain 157, 6 November 2026) for the table first
written that day.

Table: `generator_pipeline_by_grid` (series, public). Builder: `warehouse/derived/generator_pipeline_by_grid.py`.

## Sources

EIA-860M, the Monthly Update to the Annual Electric Generator Report, as this machine holds it: the current snapshot
(`eia860m_planned_generators` and `eia860m_operating_generators`, vintage 2026-09) and the newest earlier month's workbook
kept in the raw files (`warehouse/raw/eia860m_retired_all/<run>/*_august_generator2026.xlsx`, saved by
`eia860m_retired_all`'s pull of 6 October 2026: the Planned, Planned_PR, Operating and Operating_PR sheets). No request
is made. A month's snapshot replaces its rows in the current tables, so the table holds the months this machine keeps:
on 6 November 2026, August and September 2026.

## What a row is

- **A cell of a snapshot:** `eia860m_pipeline:<balancing authority>:<state>:<energy source code>:<EIA status>:<planned
  year>`, at the snapshot's month. `planned_mw` is the cell's nameplate MW as EIA gives it, `planned_count` its
  generators, `datacenter_mw` the MW of its datacenter-tagged generators.
- **A move between two months**, by balancing authority and for the US (`eia860m_pipeline:<BA>`, `eia860m_pipeline:US`),
  at the later month, each generator keyed by EIA's plant and generator ids:
  - `entered`: planned now, in neither list the month before;
  - `online`: planned the month before, operating now;
  - `left`: planned the month before, in neither list now. Cancelled, postponed and withdrawn are not told apart: this
    month's "Canceled or Postponed" sheet is not held;
  - `status_moved`: planned in both, its EIA status code changed;
  - `slipped`: planned in both, its planned year later now.
  Each has `_mw` (the later month's nameplate MW, or the earlier's for `online` and `left`) and `_count`.

## The datacenter tag

A generator is tagged when its plant's name or its owner's (EIA's entity name) matches
`data ?cent(er|re)|datacenter|\blabs?\b|laborator` (case ignored), the owner's rule: "a plant whose name or owner names
a datacenter or a lab". **On 6 November 2026 no planned generator matches, in either month.** Generators built for a
datacenter are owned and named by utilities and developers, so the column is zero, and it is kept: a match in a later
month will show.

## Checks

- **The months reconcile exactly.** August's planned 288,721.1 MW, plus 7,299.4 entered, less 5,383.4 online and 572.9
  left, plus 200.0 MW of capacity revised in generators held in both months, is September's 290,264.2 MW.
- **"Came online" against EIA's own operating dates:** of the 70 generators that moved to the operating list,
  `eia860m_operating_generators` dates 62 to September 2026 and 8 to August 2026. EIA-923 (`eia923_plant_fuel_monthly`)
  is held to December 2025 only, so it cannot check these months.

## License

Public: EIA-860M is a work of the U.S. government.
