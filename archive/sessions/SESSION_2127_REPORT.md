# Session 2127 report: the landfill gas projects (EPA's Landfill Methane Outreach Program), a source of the session's own choosing

23 October 2026, from 23:10 UTC, on lab-desktop (the data machine), the eighth session of `queue/done/079-day-28-october-data-quakes-credits-rates-world-renewables.md`, unattended. Model spend USD 0. Pulls: 3 requests of 20 (below).

## Read these first

- **Why this source:** EPA's Landfill Methane Outreach Program database is the national list of landfill gas energy projects (electricity, renewable natural gas, direct use), a public file the ERW did not hold and that no queue file of chains 057 to 092 plans (`sources.csv` on main and on chains 068, 069 and 090's branches, and their queue files, searched). It joins the ERW at three points: the GHGRP's landfills (by GHGRP id), EIA's landfill gas generators, and the gas side (renewable natural gas into pipelines).
- **One table written, validated, archived, in coverage (sectors power and gas), in the release package, both holds:** `epa_lmop_landfill_projects`, an entities table, one row a landfill and project as EPA lists them (data as of September 2024): 3,399 rows, 2,641 landfills and 542 operational projects. Those are the counts on EPA's own Summary sheet, and the connector stops if the rows ever disagree with them (EPA counts a project's expansions with it).
  - By EPA's status: Low Potential 967, Shutdown 712, Operational 669, Candidate 444, Unknown 316, Future Potential 158, Planned 100, Construction 33. `status` maps the four project stages to the standard's words and is blank for the landfills without a project; `lmop_status` keeps EPA's word.
  - **A project fed by several landfills is on each landfill's row with the same capacity** (project 1016-0, 22.5 MW, on three New Jersey landfills), so capacity is never summed over rows; the header says so, and counted once a project id the operational projects hold 1,745.4 MW of rated capacity.
  - All 69 of EPA's columns are kept, in snake case, beside the standard's.
- **The cross-check** (`runs/c079/s2127/cross.py`):
  - LMOP's 437 operational electricity project ids are rated at 1,737.5 MW against 1,584.5 MW of nameplate at the 1,210 operating landfill gas generators (285 plants) of `eia860m_operating_generators`: LMOP 1.097 of EIA, LMOP counting projects below EIA-860's 1 MW threshold and expansions as projects of their own.
  - Of LMOP's 1,331 landfills with a GHGRP id, 1,120 (84.1%) report direct emissions to the GHGRP in 2023 (`epa_ghgrp_facility_emissions`); the rest closed, fell below the threshold or stopped reporting.

## The pulls

1. `www.epa.gov/robots.txt` (read 253, read again: read 228 is session 2072's): Drupal's paths and search pages only.
2. LMOP's database page, for the file's address.
3. The composite data file (1.5 MB), seeded into the raw store and reused by the trial and the write (`--offline`).

EPA's terms are the record's (read 55, may be public).

## Errors

- **The session's test first read a row's `name` as its index** (pandas' `.name`); corrected to the column.

## Decisions made without you

- **EPA's LMOP database as the session's own choice,** for the reasons above.
- **An entities table of landfill and project rows,** EPA's own grain, rather than a table of projects that would have to pick one landfill for a project fed by several.
- **Every column of EPA's sheet kept,** so nothing a reader of LMOP expects is missing.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/epa_lmop.py`, `tests/test_session2127.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `warehouse/metadata/license_reads.csv` (253), the coverage, sources, archive manifest and license files, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c079/s2127/`, `runs/license_reads/s2127/`, `runs/s2127_*`, `warehouse/raw/epa_lmop/`.
