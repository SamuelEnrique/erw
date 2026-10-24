# Session 2297 report: South Korea's generation and demand (the Korea Power Exchange's EPSIS)

24 October 2026, from 05:38 UTC, on lab-desktop (the data machine), a session of `queue/done/105-day-8-november-data-mexico-india-peru-korea.md`. Model spend USD 0.

Pulls: 5 requests of 15:
- www.kpx.or.kr's robots file (it allows these paths; it closes some boards);
- epsis.kpx.or.kr's robots address (no robots file: it answers with the application's page, on the same host);
- three EPSIS pages in English: Generation Output by Source, Peak/Base Demand (daily), and Average Peak/Base Demand by Month.

The trial and the writes ran offline.

## Read these first

- **EPSIS writes each page's figures into the page's own script.** A plain GET returns:
  - the whole generation table (1961 to 2025);
  - the monthly demand table (1993 to 2026);
  - the daily peak and base demand for 2026 alone.
- **Other periods come only by POST** (`selectEkgeEpsMep.ajax`), which the ERW's reader does not send. data.go.kr's sets need a key the ERW does not hold.
- **Two series tables, both internal.** The ERW held no KPX source, on main or on any running chain's branch.
  - **`kpx_korea_generation_annual`:** 1,526 figures, 1961 to 2025, in MWh as published.
    - Every column of KPX's table is a variable (25), with `x_group` and `x_label` naming each as KPX heads it.
    - The columns include KPX's subtotals: hydro, steam, combined cycle, the utilities' total, the non-utility generators in common use, and the two national totals. A sum of rows therefore double counts, and the header says so.
  - **`kpx_korea_demand_monthly`:** 270 figures, in MW.
    - `peak_demand_daily_mean` runs from January 2005 to September 2026.
    - `base_demand_daily_mean` runs from January to September 2026.
    - Each is the mean of the month's daily peak, or base, demand. The page calls it "Average Peak/Base Demand by Month", and January to September 2026 equal the means of the daily page's figures to the megawatt (January: peak 80,230 MW, base 60,392 MW).
- **The checks:**
  - **Generation subtotals:**
    - each subtotal must equal its parts to within 1 MWh a part;
    - KPX's own table misses that in eight years, 1962 to 2016, at most 1.2 percent (1963's utilities' total);
    - those differences are named in the header and the figures kept as published;
    - a difference over 5 percent would stop the run.
  - **Demand:**
    - only months ended in Korea's time are kept;
    - a month shown as 0 is not published, so it gets no row;
    - an ended year KPX publishes only in part gets no row, and each is named in the header:
      - the peak view before 2005, which holds one to seven months a year, and one a year in 1993 to 2001;
      - the base view's 2025, whose first month, November, reads 12,277 MW against December's 57,565.
- **The cross-check against Ember** (`owid_ember_electricity_annual`, Korea's demand): KPX's national total (utilities plus non-utility generators) is:
  - **equal to Ember's to the MWh** in 2000, 2010, 2015, 2020 and 2023;
  - 0.38 percent above in 2024 (627.8 against 625.4 TWh);
  - 1.57 percent above in 2025 (634.5 against 624.7 TWh), probably Ember's preliminary years.
- **License: internal.** EPSIS's pages carry "Copyright(C) 2020 Korea Power Exchange. All Right Reserved." The licenses' round (session 2299) reads KPX's terms; the license tables mark the publisher "not settled".
- **Registered:**
  - the sector rules (`power`) and the live-set holds, for both tables;
  - the license tables (licenses check: 479 tables, 0 problems).

  The test is `tests/test_session2297.py` (5 tests).

## Errors

- **The first trial stopped on KPX's own subtotals** (2016's hydro total is 13.4 MWh off its parts). These are now named rather than stopped on.
- **The first trial also read the base view wrongly:** it writes its cells as `("60392.0" == 0) ? "-" : ...` and was at first read as empty. Corrected.
- **The second trial kept the peak view's early single months and the base view's partial first month.** These are now left out by the partial-year rule.
- **The test's first fixture had wrong totals;** corrected.
- **The demand write's metadata patch did not apply** over the generation write's rows (the same lines). Each table's own rows were put in by `runs/c102/add_own_rows.py`, one after the other, with a commit between, and checked: one row each in the four files.

## Decisions made without you

- **The daily Peak/Base Demand page (2026 only) is not a table.** It holds one year, and a rerun next year would replace it. Its figures were used here only to identify what the monthly page holds.
- **KPX's subtotals are kept as variables beside their parts,** with the double count stated in the header, rather than dropping them or recomputing them.
- **An ended year published in part is left out whole,** rather than keeping months whose figures are not a full year's monthly means.

## For Samuel's ruling

- None new. KPX's terms go to the licenses' round.

## Files

- New: `warehouse/connectors/kpx_korea.py`, `tests/test_session2297.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c105/s2297/` (the probe, the trials, `look.py`, `look2.py`), `runs/s2297a_*`, `runs/s2297b_*`.
