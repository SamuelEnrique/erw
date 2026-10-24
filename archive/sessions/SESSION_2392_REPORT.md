# Session 2392 report: a third source of the session's own choosing (Luxembourg's electricity sector statistics, ILR), public

24 October 2026, from 09:32 UTC to 09:58 UTC, on lab-desktop (the data machine), chain 113, unattended. Model spend USD 0. Pulls: 10 requests of 20 (7 by the probe, 1 by the fetch, 2 by the trial; the write read the saved files offline).

## Read these first

- **Why this source:** the ERW held Luxembourg only inside `eurostat_electricity_monthly` and `owid_ember_electricity_annual`. The regulator's own figures add what neither gives: the electricity withdrawn each month by class of customer, the customers, and by source the capacity, the production, the connections and the self-consumers. No ERW table and no running chain held ILR or data.public.lu (main and the wip branches of chains 110 and 112 and the code machine's searched). Both agents beside this chain were told.
- **The portal:** data.public.lu has no robots file (HTTP 404, read 609); download.data.public.lu's allows every path (read 614). No rule names an AI agent. Its API 1 search found nothing; API 2's search found 18 data sets, ILR's among them (reads 610 to 612).
- **A new table, `ilr_luxembourg_electricity`** (series, 668 rows, 15 entities, `power`):
  - `withdrawal`: the electricity withdrawn each month by industrial (more than 2 GWh a year), professional and residential customers, January 2017 to June 2026, MWh. The 2026 months are marked `provisional` in `x_status`, as ILR's note says.
  - `customers`: customers at 31 December by class and in all, 2017 to 2025.
  - By source of energy, 2022 to 2025: `capacity` (MW), `injection` and `generation` (national production, MWh), `connections` (count).
  - Self-consumers and sharing groups by source, 2022 to 2025: `self_consumers`, `self_consumption_capacity`, `self_consumption`, `self_consumer_injection`.
  - `import` and `export` by neighbour (Germany, Belgium, France), 2017 to 2025, MWh.
  - ILR's totals are kept as entity `ilr:lu:total`: a sum takes one level.
  - Written, validated (0 errors, 0 warnings), archived, and held from the Redivis storage and the live set like the chain's other tables.
- **Public, under CC BY 4.0.** The data set's record gives licence `cc-by` (read 613), and the portal's licence list names it "Creative Commons Attribution 4.0" (read 615). `license_verdicts.csv` gains ILR, "may be public". The connector stops if the record's licence ever changes.
- **Not taken: sheet 7's monthly import and export.** From October to December 2025 they run the other way from the annual totals. The annual import from Germany, 2,627.26 GWh, equals the monthly imports to September plus the monthly "exports" from October, 2,626.49 GWh. Also not taken: the battery sheet (its power is in kVA), and the shares, switching rates, prices and planning sheets.

## Cross-checks

Against `eurostat_electricity_monthly` (Luxembourg, twelve months a year, 2022 to 2025):
- wind 0.905 to 0.996; hydro 0.924 to 0.976.
- Solar 0.923 to 0.939 in 2022 and 2023, but 0.693 in 2024 and 1.445 in 2025. ILR's own figure for 2024 grows from 0.36 TWh to 0.63 TWh in 2025; the two publishers perhaps count self-consumed solar differently (not checked).
- Withdrawals plus self-consumption over Eurostat's available for the market: 0.992 to 1.027 (1.092 in 2025).
- ILR's imports are 0.735 to 0.835 of Eurostat's. With Eurostat's energy used for pumped storage added, they are 0.933 to 1.004. Luxembourg's pumped-storage plant (Vianden) draws from and feeds the German grid; ILR's figures leave it out, and its exports are a small share (0.033 to 0.093) of Eurostat's for the same reason.

Against `owid_ember_electricity_annual`: withdrawals are 0.887 to 0.928 of Ember's demand, 2017 to 2025.

## Requests (10 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | data.public.lu/robots.txt | 404: no robots file |
| 2, 3 | the portal's API 1 search (electricite, accented) | 200: no data set |
| 4 | the portal's API 2 search (electricity) | 200: 18 data sets |
| 5 | ILR's data set record | 200: licence cc-by, one xlsx |
| 6 | download.data.public.lu/robots.txt | 200: allows every path |
| 7 | the workbook (the fetch) | 200, 104,406 bytes, last modified 1 September 2026 |
| 8 | the portal's licence list | 200: cc-by is Creative Commons Attribution 4.0 |
| 9, 10 | the record and the workbook again (the trial) | 200 |

Reads recorded: 609 to 615.

## Decisions made without you

- **Public under the portal's CC BY 4.0,** ILR named in the header.
- **The monthly trade left out,** its last quarter reversed against the annual totals; the annual trade taken.
- **One table with monthly and annual rows** (`freq` P1M and P1Y), not five tables.
- **The write waited about twelve minutes** on the data lock (chain 112's and chain 110's Stanford uploads held it). Session 2393 ran meanwhile.

## For Samuel's ruling

- None.

## Files

- New: `warehouse/connectors/ilr_luxembourg_electricity.py`, `tests/test_session2392.py`, this report.
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`;
  - `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`;
  - the license record (reads 609 to 615, ILR's verdict, `license_tables.csv`, `docs/licenses.md`) and `docs/redivis/release-v1/` (the table's rows).
- On the data machine only: `runs/c113/s2392/`, `warehouse/raw/ilr_electricity/`, `warehouse/output/ilr_luxembourg_electricity.csv`.
