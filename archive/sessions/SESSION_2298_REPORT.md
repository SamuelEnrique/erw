# Session 2298 report: six held tables described

24 October 2026, from 05:51 UTC, on lab-desktop (the data machine), a session of `queue/done/105-day-8-november-data-mexico-india-peru-korea.md`. Model spend USD 0. Pulls: none.

## Read these first

- **How the tables were chosen.**
  - The held tables with no method note were found by `runs/c105/s2298/find_unnoted.py`, chain 104's script pointed at this worktree. A table counts as described if a `Tables:` line or a note's file name names it, on main, chain 103's branch or chain 104's branch. 65 have none.
  - Six source tables that chains 103 and 104 did not take were chosen.
  - This chain's own tables wait for session 2303.
- **Six notes** in `docs/methods/`. Three helpers drafted them, two tables each, from the connectors, the tables and the records, with no request. I read each and checked its `Tables:` line and its dash count (0).
  - `eia930_all_interchange.md`: 295,104 rows, 345 directed pairs, 2026-09-13 to 2026-10-21.
  - `eia930_all_storage.md`: 73,224 rows, five respondents, from 2024-11-01.
  - `eia930_all_emissions.md`: 4,350,240 rows, 8 areas, 8 variables, from 2018-07-02.
  - `eia930_demand_growth.md`: 24,108 rows. All 24,108 values were recomputed exactly from the eight EIA workbooks its header names.
  - `eia_all_futures_prices.md`: 21,240 rows, 16 series, 2019-01-01 to 2024-04-05. Every row matches session 127's 16 raw answers.
  - `miso_as_prices.md`: 54,936 rows, 763 days, 2024-09-01 to 2026-10-03. Every row matches the 763 raw files. Last written at 04:19 UTC on 4 October, about an hour before MISO's pause. No job runs it, and the connector refuses even `--offline`.
- **The cross-checks:**
  - **The hourly pairs against the daily interchange table:** 11,439 pair-days, of which 11,310 are equal (the counts session 2284 found from the other side).
  - **Battery storage against `eia930_all_generation`:** 6,888 hours, of which 6,866 are equal.
  - **CO2** against EIA's workbook extracts on this machine and `carbon_intensity_hourly`.
  - **The futures** against EIA's spot prices.
  - **MISO's reserve prices** against its hub prices and the other ISOs' reserve prices.
  - The scripts and their outputs are in `runs/c105/s2298/`.
- **The Method cells:** `docs/coverage.md` names the six notes.
  - `eia930_demand_growth`'s coverage row now says its eight grids, not "DEMAND", and its tier is derived, not source. This comes from two new rules in `build_coverage.py`; the table is ERW code over EIA's workbooks.

## Where the descriptions and the data disagree

**Acted on** (wording only; no row changes, and a header follows at its table's next write):

1. **`eia930_interchange.py`:**
   - The table holds every directed pair EIA reports: 14 reporting codes are EIA's regions and US48, and twelve neighbours never report. It is not "between balancing authorities", and pairs are not "reported by both BAs".
   - The connector was written in session 46 and first run in session 49, which asked for 18 days and wrote 16.
   - Docstring and header changed.
2. **`eia930_event_hourly.py`:** the hourly interchange table is not a rolling window. It grows daily from 2026-09-13.
3. **`eia930_storage.py`:**
   - ISNE and SWPP never report charging, and ERCO does only from 2025-12-15 (docstring and header).
   - `eia930_all_generation` is not a rolling 30 days.
   - The first days held are given beside EIA's first hours.
4. **`run_daily.sh`:** "EIA-930 carries no battery series" now ends "for CAISO".
5. **`live_set.yaml`:** the `/storage` comment now says the recent window is 35 days since session 36C, not 90.
6. **`eia930_emissions.py`:**
   - The daily run passes `--days 10` (since session 321), not 3.
   - The header names the seven ISO BAs and the Lower 48, not "by balancing authority".
7. **`demand_growth.py`:**
   - The rule's description now includes session 118's range test, which removes no hour in this build.
   - "The two before and the two after that are held" is reworded to what the code does.
8. **`impossible_hours.py`:** the two hours given as UTC were local times: PJM 18:00 Eastern (22:00 UTC), SPP 04:00 Central (09:00 UTC).
9. **`eia_futures.py`:** "No. 2 heating oil" is EIA's name; the prices follow EIA's New York Harbor ultra-low sulfur diesel spot price (within 1 percent on 999 of 1,318 days).
10. **`miso_as_prices.py`:** the left-out demand-side and stored-energy prices equal the kept ones in all 18,312 hours.

**Recorded in the notes, not acted on** (each needs a pull, a rebuild or a rule beyond this session):

- **Days missing with no gap row:**
  - `eia930_all_interchange` has no row for 2026-10-14 and 2026-10-15; the runs between 15 and 19 October did not reach them.
  - `eia930_all_storage` has no row for 2026-10-15 for ISNE, MISO and SWPP, though `eia930_all_generation` holds those hours.
  - `eia930_all_emissions` lacks 73 days with no gap row (PJM 2018-07-11 to 2018-09-18, among others).
  - Recovering these needs a re-ask, left for the daily jobs' owner.
- **Missing run records and misleading header lines:**
  - Several runs left no `run_status.csv` row: session 49's pull, the futures and the MISO reserve prices.
  - The "Retrieved:" line of the futures and MISO tables names the writing run, not the requests.
- **Values held as EIA reports them:**
  - interchange near -2.15 million MW on four hours;
  - SPP's zero CO2 generated from July to August 2018, and its 101 days without CO2 from 2025-11-29;
  - nine 2019 holidays carrying the previous day's futures.
- **The demand growth table's site copy:**
  - It differs from the table in four US48 values of 2026, after session 438's rebuild without `--snapshot`.
  - The "blank" counts in its note and in `faults.yaml` include each workbook's empty tail.
  - `faults.yaml` and session 97's report name `eia930_all_emissions` as carrying faulty demand, but it holds CO2 only.
- **Other descriptions:**
  - `sync.py` restores the futures table's rows in another order, so its hash differs from the archive's until sorted.
  - `vintage` is blank in the MISO table though `Last-Modified` is in the raw manifest.
  - Session 85's report gives the MISO files as 493 MB; they are 514.5 MB.
  - Earlier session reports' spans for US48's missing storage days are wrong (2024-07-15 to 2024-10-31 is right).

## Errors

- None.

## Decisions made without you

- **The six tables,** chosen among the source tables chains 103 and 104 did not take.
- **The helpers wrote the notes;** I acted on the wording contradictions and left the data ones recorded.
- **`eia930_demand_growth`'s tier and grids corrected in `build_coverage.py`** (it is computed by ERW code from EIA's workbooks).

## For Samuel's ruling

- **The futures table's license.** CME Group's terms have never been read (two attempts failed) and the table stays internal. `docs/licenses.md` still shows "may be public" in its "if the ERW sells anything" column. The note records this.

## Files

- New:
  - the six notes in `docs/methods/`;
  - this report.
- Changed:
  - the connectors `eia930_interchange.py`, `eia930_event_hourly.py`, `eia930_storage.py`, `eia930_emissions.py`, `eia_futures.py` and `miso_as_prices.py`;
  - `warehouse/derived/demand_growth.py` and `impossible_hours.py`;
  - `warehouse/run_daily.sh`, `warehouse/supabase/live_set.yaml` and `warehouse/metadata/build_coverage.py`;
  - `docs/coverage.md` and `coverage.csv`.
- Tests: the 27 test files naming these tables, connectors or the coverage rules, 510 tests, OK (35 skipped).
- On the data machine only: `runs/c105/s2298/`.
