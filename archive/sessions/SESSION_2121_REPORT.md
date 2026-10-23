# Session 2121 report: the energy industries' toxic releases (EPA's Toxics Release Inventory), in place of the households' tax credits

23 October 2026, from 22:32 UTC, on lab-desktop (the data machine), the second session of `queue/done/079-day-28-october-data-quakes-credits-rates-world-renewables.md`, unattended. Model spend USD 0. Pulls: 12 requests of 15 (below).

## Read these first

- **The file's source was taken first by chain 068:** the IRS's Statistics of Income residential energy credits are `irs_soi_energy_credits_annual` (session 2087, on chain 068's branch). As the file says, the session took another public source the ERW does not hold, and two candidates failed before it:
  - **FEMA's National Risk Index** (hazards.fema.gov): the host reset the connection on its robots file (read 238). Not asked again without a ruling.
  - **The USGS's thermoelectric power water use** (ScienceBase): www.sciencebase.gov's robots file allows `/` for every reader, then ends with "Block everything for all bots by default" (`User-agent: *`, `Disallow: /`) and names AI agents (read 239). Taken as disallowed; not asked further.
- **One table written, validated, archived, in coverage (sectors power, oil, gas and coal), in the release package, both holds:** `epa_tri_energy_releases_annual`, the Toxics Release Inventory's forms of the energy industries, reporting years 2015 to 2023: 384,483 rows, 128,161 forms. Each form is one facility's report of one chemical, with three of EPA's totals: total releases, on-site releases and off-site releases.
  - By sector over the nine years: electric utilities 36,480 forms (637 facilities), petroleum 50,078 (1,014), petroleum bulk terminals 37,195 (837), natural gas processing 3,594 (342), coal mining 814 (54).
  - **Natural gas processing appears from 2022** (4 to 35 forms a year before, 1,714 in 2022 and 1,746 in 2023): EPA added natural gas processing plants to the inventory from reporting year 2022. The header says so.
  - **A new unit, `g` (Decision 66):** EPA reports dioxins in grams and every other chemical in pounds (`lb`); each form keeps the unit EPA printed, and the two are never converted or summed. Chain 068's Decision 62 (`degC`) landed during the session and chain 069 holds three units more (63 to 65), so this one is 66, as the agents of chains 069 and 090 agreed (first written as 65 and renumbered in session 2125); the table's header, written with 65, is written again in session 2129.
  - **A form is the entity** (`tri:<TRIFD>:<chemical id>:<document control number>`): some sites file several forms of one chemical in a year (for one establishment each, or a refinery's and its terminal's under two NAICS codes, BP Whiting and Phillips 66 Ponca City among them: 132 to 201 such pairs a year). Each is kept as EPA published it; `x_trifd` and `x_chemical_id` group them, and no sum is made here.
- **The cross-check** (`runs/c079/s2121/cross.py`):
  - EPA's arithmetic holds on every form: total releases equal on-site plus off-site on all 128,161.
  - The electric utilities' releases in pounds fall from 432.6 million lb (558 facilities) in 2015 to 281.8 million in 2019 and 194.6 million (388) in 2023; their mercury and mercury compounds from 102,399 lb to 54,512 and 38,313 lb.
  - EPA's FRS id joins the table to `epa_ghgrp_facility_emissions`: 61 to 66% of the TRI's electric utilities each year are GHGRP facilities that year (the rest are plants below the GHGRP's threshold or without an FRS id in it).

## The pulls

1. `hazards.fema.gov/robots.txt` (read 238): the connection reset.
2. `www.sciencebase.gov/robots.txt` (read 239): disallows `/` for every reader by default.
3. `data.epa.gov/robots.txt` (read 240): a welcome line, no rules.
4. The 2023 basic file (61.6 MB), for its columns; seeded into the raw store.
5 to 12. The connector's trial: the 2015 to 2022 files (62 to 65 MB each), saved and reused by the write (`--offline`).

EPA's terms are the record's (read 55, may be public).

## Errors

- **The first trial stopped on a facility and chemical given twice in 2015** (the several forms above); the entity was keyed by the form and the trial run again offline.
- **A second trial stopped** because the first trial's file, with fewer columns, was still in the trial folder; removed and run again.

## Decisions made without you

- **EPA's Toxics Release Inventory in place of the IRS's credits**, after FEMA's host and ScienceBase's robots file closed the first two candidates.
- **The five energy sectors** by EPA's TRI industry sector code (2211, 324, 211, 2121, 4247); the chemical, metal and other industries are not taken.
- **Three totals of the form** (total, on site, off site), not its 70 detailed quantities, to keep the table at 384,483 rows; a later session can add the air and water columns.
- **A form as the entity,** never a sum of a site's forms.
- **`g` as a unit of its own** (Decision 66), rather than grams converted to pounds.
- **ScienceBase's robots file read as disallowing** the ERW's reader: its last group for every reader disallows `/`.

## For Samuel's ruling

- **hazards.fema.gov** (FEMA's National Risk Index) refuses the ERW's reader; **www.sciencebase.gov** disallows every reader by default. Both join the hosts not asked again without a ruling.

## Files

- New: `warehouse/connectors/epa_tri_energy.py`, `tests/test_session2121.py`, this report.
- Changed: `docs/datastandard.md` (Decision 66), `warehouse/validate/erw_validate.py` (`g`), `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `warehouse/metadata/license_reads.csv` (238 to 240), the coverage, sources, archive manifest and license files, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c079/s2121/`, `runs/license_reads/s2121/`, `runs/s2121_*`, `warehouse/raw/epa_tri_energy/`.
