# Session 2798 report: European households' electricity by end use (Eurostat, nrg_d_hhq), the session's own choice

26 October 2026, from about 03:12 to 03:23 UTC, on lab-desktop (the data machine), chain 142, unattended. Precheck passed (`runs/c142/pre2798.out`). Model spend USD 0. Pulls: 4 of 20.

## Read these first

- **`eurostat_household_electricity_annual` is new:** Eurostat's disaggregated final energy consumption in households (nrg_d_hhq), electricity only. It gives each European country's households' electricity a year, 2010 to 2024, by end use: space heating, space cooling, water heating, cooking, lighting and electrical appliances, and other end uses, with their total. 3150 rows, 38 areas, 7 items, in MWh (Eurostat's GWh times 1,000).
  - The table has been written, validated, archived and put in coverage.
  - It is held from the live set and from Redivis storage until session 2801's draft.
- **Why this source:** the ERW held the households' total (`eurostat_electricity_consumption_annual`, session 2757, from nrg_cb_e) but not what households use it for. No connector, method note, source row or unlanded chain names nrg_d_hhq.
- **The EU in 2024:** 712.4 TWh, of which:
  - lighting and appliances 54.9 per cent;
  - space heating 16.0;
  - cooking 12.4;
  - water heating 11.4;
  - space cooling 3.1;
  - other uses 2.2.
- **The six end uses make the total** within 0.001 GWh in all 444 country years that give all seven items. This is a check that stops the run.
- **97 country years are not written:** all seven items are zero there. These are the years a country did not report the split:
  - 18 countries a year in 2010 to 2012, 17 in 2013 and 2014;
  - 5 in 2015, 3 in 2016, 1 in 2017;
  - none from 2018.

  The header counts them and the run log lists them. 370 other zeros are kept (mostly space cooling).
- **Cross-check against the held table:** the households' total compared with `eurostat_electricity_consumption_annual`'s `households` in the 451 country years both give:
  - **Agreement:** 392 within 1 GWh and 416 within 1 per cent.
  - **The rest differ** by up to 31 per cent (North Macedonia 2024; Georgia 2021 23 per cent; Turkey 2024 6.5 per cent; Croatia 1.2 to 6 per cent in most years). nrg_d_hhq was last updated on 9 June 2026, nrg_cb_e later; this is read as the two datasets' different vintages and kept as published.
  - **The EU27_2020 aggregate before 2015 sums only the members that reported the split.** It is 34 to 37 per cent under nrg_cb_e's households in 2010 to 2014, and 3 per cent under in 2015. **Only the EU's figures from 2016 compare with the held table.** Session 2801's note says so.

## The requests

1. **ec.europa.eu's robots file (read 1597):** byte for byte the file session 2790 read. `/eurostat/api/dissemination/` is open and no Claude agent is named.
2. **nrg_cb_e, every balance item of electricity, and the NRG_BAL codelist** (2 requests): asked for nrg_cb_e's branches. The data file was byte for byte the one session 2757 holds (`eurostat_electricity_consumption_annual`), so nothing new was taken from it. The codelist gave the end uses' names, which the connector writes in its code. Both files are kept under `warehouse/raw/eurostat_electricity_branches/` (not in git).
3. **nrg_d_hhq, `A..E7000.GWH.`:** the table's one request (357 KB).

## Decisions made without you

- **No row for a country year whose seven items are all zero.** No country's households use no electricity. The years match the reporting obligation's start: Eurostat's data from 2015, with a few late reporters. The count is in the header. Reversible: drop the filter in `build`.
- **The EU27_2020 aggregate kept for every year**, its incompleteness before 2016 left to the note rather than cut.
- **The end uses' names written in the connector** from the codelist read here. The table needs one request, not two.

## For Samuel's ruling

- None.

## Files

- New:
  - `warehouse/connectors/eurostat_household_electricity.py`
  - `tests/test_session2798.py` (3 tests, passing)
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py` and `warehouse/supabase/live_set.yaml` (the table registered and held)
  - the license record and `docs/licenses.md`
  - coverage, sources and the archive manifest
  - the release v1 records
- On the data machine only: `runs/c142/s2798/` (the probe, the fetch script, the trial, the checks).
