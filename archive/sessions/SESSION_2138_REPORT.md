# Session 2138 report: six held tables given their method notes (ERCOT's reserves plan, storage dispatch, wind and solar; SPP's reserves; the JEDI multipliers)

23 and 24 October 2026, from 23:45 UTC, on lab-desktop (the data machine), chain 090, unattended. The notes were drafted by a helper agent in the chain's worktree while sessions 2139 to 2141 ran, then checked by this session. Model spend USD 0. Pulls: none.

## Read these first

- **How the tables were chosen:**
  - `build_coverage.py` links a table's note only when the note is named after the table or names it on a line beginning `Tables: `; 134 tables of the branch's coverage have no such note.
  - Every one of them is named somewhere in `docs/methods/`, on this branch, on main, or on the twelve `wip/` branches pushed last. So the session took those named in only one note, in passing or in a section of a larger one.
  - Chain 069's and chain 092's branches were read for notes, so none is written twice.
- **Four new notes**, in the form of `docs/methods/ercot_4cp_intervals.md`:
  - `docs/methods/ercot_as_quantities.md`: 4,800 rows, five services of 960 hours each, delivery days 3 September to 12 October 2026, none missing. Every service-hour has a price in `ercot_as_prices`. No scheduled job runs the connector; the file was last written on 11 October.
  - `docs/methods/ercot_sced_esr_hourly.md`: 1,580,775 rows, 342 resources, 1 February to 20 August 2026 (201 days, none absent). Discharge, charge and net agree with `ercot_storage_rt_monthly` within 0.001 MWh in all seven months.
  - `docs/methods/ercot_wind_solar_forecast.md`: 2,730 rows, 635 hours of actuals and 730 of forecasts for each fuel. Within 0.03 MW of `ercot_wind_solar_hsl_hourly` in its 608 shared hours. Against EIA-930's ERCO generation the median difference is 0.3 MW (wind) and 0.4 MW (solar); the large gaps fall on 4 and 5 October, where EIA is lower.
  - `docs/methods/ercot_wind_solar_output_hourly.md`: 52,608 rows, 2023 to 2025 by Central year. Wind 107.989, 111.711 and 114.939 TWh; solar 31.868, 47.749 and 67.516 TWh. Within 0.0054 percent of `generation_mix_hourly_profile` (iso:ercot, from EIA-930) in each of 35 complete months.
- **Two `Tables:` lines added to notes that already describe their tables in full:**
  - `docs/methods/reserve_quantities_nyiso_spp.md` (`spp_as_quantities`). Its New York part writes no table, so only SPP's is named.
  - `docs/methods/economic_impact.md` (`nlr_jedi_multipliers`, `impact_tax_rules`; the second keeps its own note as its link, since a note named after its table comes first).
- **The six Method cells** in `docs/coverage.md` were set by `build_coverage.py`'s own lookup; nothing else on the lines was changed (a rebuild would have moved last-run dates to this machine's copies).
- **Checked by this session:**
  - Recomputed from the tables, read past their header lines: the row and service counts, the resources and days, the forecast hours, and the yearly TWh by Central year. Each agrees with the note.
  - The solar report's id, against ERCOT's own file names (below).
- **Tests:** 1,758 tests that read the notes or the coverage page pass but one, `test_session705`, the known artifact of running from a worktree (it passes in the main checkout).

## Contradictions found, written into the notes, no code changed

1. **The wrong solar report id.** `ercot_wind_solar_forecast.py`'s docstring, its `REPORTS` entry, the table's header and `sources.csv` call the solar report NP4-745-CD. The report type it reads, 13483, is NP4-737-CD by ERCOT's own file names (every one of the 11,840 times the report's file name appears in the raw store, it reads `PVGRHRLYAVGACTNP4737`). `curtailment.py` (line 74) and `docs/methods/generation_mix_hourly.md` carry the same label. **For a code session:** the label changes a source id, so it is not changed here.
2. **`ercot_sced_esr.py`'s docstring is out of date:**
   - it says a zip holds eleven files, but all 201 saved hold ten;
   - it lists `metered_mwh` in a row, a column the table does not have (ERCOT's metered file holds none of the storage resources; the header says so);
   - it still describes the first pull (186 days, 10.4 GB), though the table now holds 201 days and 11.26 GB;
   - it says the 12 GB and 9,000,000-row ceilings are shared with the node prices, though the code counts only its own.
3. **`retrieved_at`** in `ercot_as_quantities` and `ercot_wind_solar_forecast` is the time a saved file was read in the run, not its first download.
4. **`ercot_wind_solar_output_hourly`'s header** says "24 requests, 10,177,213 bytes"; the data machine's manifest has 35 and 11,850,911. The row counts match.
5. **Two connectors do not ask `iso_prices.paused()`** before reaching ERCOT: `ercot_as_quantities.py` and `ercot_wind_solar_forecast.py`. **For a code session.**

## Decisions made without you

- **The notes drafted by a helper agent and checked here,** as sessions 2004, 2032, 2038 and 2088 did.
- **`Tables:` lines rather than new notes** where a note already describes a table in full.
- **Code and headers left alone;** the contradictions are in the notes and here.

## For Samuel's ruling

- None new.

## Files

- New: `docs/methods/ercot_as_quantities.md`, `ercot_sced_esr_hourly.md`, `ercot_wind_solar_forecast.md`, `ercot_wind_solar_output_hourly.md`, this report.
- Changed: `docs/methods/reserve_quantities_nyiso_spp.md`, `docs/methods/economic_impact.md` (a `Tables:` line each), `docs/coverage.md` (six Method cells).
- On the data machine only: `runs/c090/s2138_*`.
