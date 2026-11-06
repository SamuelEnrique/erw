# Sessions 2951 and 2952 report: the EIA-860M pipeline

6 November 2026, about 08:16 to 08:22 UTC, on lab-desktop (the data machine), chain 157 (the owner's), unattended. Model spend USD 0. Pulls: none.

## Read these first

- **`generator_pipeline_by_grid` is written:** 5,147 rows, public, commit `c05da6760` on `wip/c157-data`.
  - **Two months:** September 2026, the current snapshot (`eia860m_planned_generators` and `_operating_`), and August 2026, the workbook `eia860m_retired_all`'s pull kept in the raw files on 6 October. No earlier month is on this machine.
  - **The cells:** planned nameplate MW and count by balancing authority, state, energy source, EIA status and planned year, for each month.
  - **The moves, August to September** (by balancing authority and for the US):
    - **entered** 121 generators, 7,299.4 MW;
    - **came online** 70, 5,383.4 MW;
    - **left** 6, 572.9 MW (cancelled, postponed or withdrawn, not told apart: September's "Canceled or Postponed" sheet is not held);
    - **status moved** 81, 6,454.1 MW;
    - **slipped a year** 76, 4,637.5 MW.
  - **The months reconcile exactly:** August's 288,721.1 MW + 7,299.4 entered - 5,383.4 online - 572.9 left + 200.0 MW revised in generators held in both = September's 290,264.2 MW.
  - **Came online, against EIA's own dates:** of the 70, the operating table dates 62 to September 2026 and 8 to August. EIA-923 is held only to December 2025, so it cannot check these months.
  - **The datacenter tag** (a plant or owner name naming a data center or a lab, the owner's rule) **matches no planned generator in either month.** The column is kept at zero; the method note says why.
- **The write** (`runs/c147/write_table.sh`, under the data lock): validator PASS; coverage, sector power, with a rule added to `build_coverage.py`; archive run `20261106T082024Z-local`. The first run stopped at coverage: the "Derived from" line named the raw workbook, which is not a table, so it is now named on the Snapshots line only.
- **`docs/methods/generator_pipeline_by_grid.md`** written; **test** `tests/test_session2951.py` (4 passed).
- **Session 2952** had no second half to do: the table, its checks and its note were finished in this one.

## Decisions made without you

- **"Left" not split into cancelled, postponed and withdrawn:** this month's sheet that tells them apart is not held.
- **The fuel is EIA's energy source code**, which both months carry, not the ERW's technology group, which only the table has.

## For Samuel's ruling

- **Keeping each month's EIA-860M workbook on this machine:** the table can only give the moves between months whose workbooks are held, and the daily pull keeps only the current snapshot. Whether to keep each month's file is a question for the owner.
