# Session 2214 report: six held-but-undescribed tables get their notes

24 October 2026, from 01:45 UTC (the notes drafted by a helper beside sessions 2215 to 2217, checked and finished from 01:57 UTC), on lab-desktop (the data machine), the fifth session of `queue/done/098-day-2-november-data-price-indexes-reservoirs-rooftops.md`, unattended. Model spend USD 0. Pulls: none.

## Read these first

- **Six tables without a method note, none named in a note on main or on the running chains' branches,** now have one each, written from the connector and the table and checked as session 960 checked its notes:
  - `desnz_uk_renewables_quarterly`
  - `caiso_dam_alert_day_hub_prices`
  - `nyiso_dam_cleared_energy`
  - `nyiso_rtm_zone_prices`
  - `nyiso_load_queue`
  - `spp_dam_cleared_energy`

  Their Method cells in coverage link them.
- **What the checks found and what was done** (each note's "Where the description and the data disagree"):
  - **DESNZ renewables:** a sum over the technologies must leave out co-firing (capacity) and non-biodegradable wastes (generation) as well as TOTAL. With TOTAL alone left out, the sum runs up to 3.695% (capacity) and 4.792% (generation) above it. Capacity and generation also name five technologies differently (16 and 15 entities, 20 together).
    - **Fixed:** the connector's docstring and header now say so and give each block's count. The table was written again offline from the saved workbook: the same 1,982 rows, the archive unchanged.
  - **CAISO alert days:** the header called 160 days "left incomplete" by CAISO. They were never requested: they lie outside OASIS's 39-month history. Its cutoff also moves with the run date.
    - **Fixed in the connector's header text.** The table is not written again, since the connector runs against OASIS by hand and this session made no request. The next run carries the fix.
  - **NYISO load queue:** the docstring mapped statuses by code, but the code maps by the key's words (the same result on this sheet).
    - **The docstring now states the code's rule.**
  - **NYISO's three tables:** their headers' license lines predate the license record's ruling of 21 October 2026 (license needed).
    - **Recorded, not changed,** as earlier notes did for NYISO's other tables: the license record governs, and the release package holds them whole.
  - **NYISO real time, a missing day:** 15 October 2026 is absent at every zone, and the 3-day window will not ask for it again.
    - **Recorded, not filled:** a backfill is a request to NYISO, whose data is unsettled, and this session had no pulls.
  - **SPP day-ahead cleared:** no disagreement.
- **A correction to session 2174's report** (chain 094): "within 2.5%" for the 2024 UK solar capacity against IRENA's holds only measured against DESNZ's figure (2.455%). Against IRENA's figure the gap is 2.517%. Every other figure of that report holds.
- **`nyiso_load_queue`'s coverage row would turn `internal` if rebuilt.**
  - Its header line, "License: public, with a caution", is not a declared license under `build_coverage.py`'s rule: the word must be followed by a stop or a space. The source's license (internal) then decides.
  - `tests/test_session410` requires the row public (`DECLARED_PUBLIC`), and the Method cells' build turned it internal.
  - The row is put back as on main, with only its Method cell new.
  - The next full coverage build, or the connector's next run (which writes "License: internal" since session 149), will turn it internal and fail that test. The test's list then needs the table taken out, which is a question about the table's standing (below).

## Checks that passed (the helper's, `runs/c098/s2214/`)

- CAISO alert days: all 3,024 hub-hours equal `iso_hub_prices_history`.
- NYISO real time: hourly means match the zone price history within 0.01 in 11,646 of 11,660 hours.
- NYISO day-ahead cleared: scheduled load runs a median 1.0291 of actual zone load.
- SPP day-ahead cleared: the daily sum runs a median 1.0795 of EIA-930's SWPP demand.
- NYISO load queue: the header's counts hold (53 in line, 14,232.9 MW; 17 withdrawn; 4 in service).
- DESNZ renewables: session 2174's cross-check reruns identical.

## Errors

- None.

## Decisions made without you

- **The six tables picked** from the tables without a note, none named on main or on chains 097's and 099's branches.
- **Only the DESNZ table written again,** since its fix needed no request; CAISO's and NYISO's headers change at their next runs.
- **NYISO's missing day not filled,** for the reason above.

## For Samuel's ruling

- **`nyiso_load_queue`: public or internal in coverage?** The file's header (7 October) says public with a caution; the connector since your ruling of 7 October writes internal; the license record rules NYISO's data license needed from 21 October; `tests/test_session410` holds it public. Undone: the row stays public as on main until you rule, and then the test's `DECLARED_PUBLIC` loses or keeps it.
- NYISO's license, as before.

## Files

- New: `docs/methods/desnz_uk_renewables_quarterly.md`, `caiso_dam_alert_day_hub_prices.md`, `nyiso_dam_cleared_energy.md`, `nyiso_rtm_zone_prices.md`, `nyiso_load_queue.md`, `spp_dam_cleared_energy.md`, this report.
- Changed: `warehouse/connectors/desnz_renewables.py`, `warehouse/connectors/caiso_alert_prices.py`, `warehouse/connectors/nyiso_load_queue.py` (docstring and header text only), `docs/coverage.md`, `warehouse/metadata/coverage.csv`.
- On the data machine only: `runs/c098/s2214/`, `runs/s2214_*`.
