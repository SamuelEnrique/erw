# Session 2129 report: method notes for this chain's tables

23 October 2026, from 23:16 UTC, on lab-desktop (the data machine), the tenth session of `queue/done/079-day-28-october-data-quakes-credits-rates-world-renewables.md`. Model spend USD 0. Pulls: none. (The notes were drafted by a helper agent beside sessions 2130 to 2132 and checked by this session at 23:29 UTC.)

## Read these first

- **Five notes written,** one for each of this chain's tables, each with its cross-check rerun (every saved `cross.out` reproduced exactly) and a section on the session report against the table:
  - `docs/methods/usgs_comcat_earthquakes_south_central.md` (16,000 events, 2010-01-01 to 2026-10-22)
  - `docs/methods/epa_tri_energy_releases_annual.md` (384,483 rows, 128,161 forms, 2015 to 2023)
  - `docs/methods/eurostat_renewable_capacity_annual.md` (49,313 rows, 1990 to 2024)
  - `docs/methods/owid_ember_electricity_annual.md` (12,406 rows, 1990 to 2025)
  - `docs/methods/epa_lmop_landfill_projects.md` (3,399 entities, data as of September 2024)
- None of the five is scheduled: no daily step, data machine task or workflow names their connectors.
- **The helper's new figures were checked against the data by this session** before acting: the TRI's 134 natural gas processing forms of 2015 to 2021, 65 under NAICS 211130; Kosovo keyed by name in the electricity table; 20 named rows and one capacity (`lmop:2400:180761-1`, 0.06 MW) among LMOP's 1,885 landfills without a project; the five blank USGS places (three border regions, "Texas Panhandle region", one named event) and the states past the header's tenth (Arkansas 3, Nebraska 3, Missouri 2). All hold.
- **Every point acted on:**
  - **Descriptions corrected:** `usgs_earthquakes.py` (the count is 16,000 earthquakes, 16,050 with blasts and explosions; which places are blank); `epa_tri_energy.py` (the natural gas processing plants added from 2022, the 134 earlier forms); `owid_energy.py` (three Ember-only columns, two taken; Kosovo's key); `eurostat_res_capacity.py` (Switzerland among EFTA's, the euro area aggregates the code keeps); `epa_lmop.py` (the named rows without a project).
  - **Three tables written again offline for their headers** (rows unchanged): `usgs_comcat_earthquakes_south_central` (every state the places name, not the first ten), `epa_tri_energy_releases_annual` (Decision 66, and the gas plants' wording), `owid_ember_electricity_annual` (the carbon intensity left for its unit).
  - **Reports corrected** (each line marked): session 2120 (the small states and the blank places); session 2121 (the count of extra forms, which it had called "pairs", and the files' sizes, 61 to 65 MB; its line about this session's rewrite).
- **The Method cells** of the five are filled in `docs/coverage.md`.

## Errors

- **The three rewrites' metadata patches met the branch's own older rows,** as session 2079's did: each left a conflict block in `coverage.csv`, `docs/coverage.md` and `archive_manifest.csv`, and the branch was staged between the runs, so the blocks were staged too. Each block was resolved to its newer row (the patch's side, verified by its run time) and `runs/c059/resolve.sh` finds no row twice and no marker. An earlier rewrite of the TRI table in this session (for Decision 66, at 23:16 UTC) had met the same and was resolved by hand (session 2124's commit).

## Decisions made without you

- **Corrections to the descriptions and the headers, never to the rows:** the places blank in `x_place_state` stay blank rather than the parser being widened after the table's checks were run.

## For Samuel's ruling

- None new.

## Files

- New: the five notes, this report.
- Changed: the five connectors (descriptions), `docs/coverage.md`, `coverage.csv` and `archive_manifest.csv` (the three tables written again, the Method cells), `docs/licenses.md`, the reports of sessions 2120 and 2121.
- On the data machine only: `runs/c079/s2129/` (the helper's scripts), `runs/s2129_*`, `runs/c079/s2129_w*.out`.
