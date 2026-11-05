# Session 2230 report: a source of the session's own choosing (Germany's grid, SMARD)

24 October 2026, from 02:42 UTC, on lab-desktop (the data machine), chain 099, unattended. Run before session 2229 so that its publisher is in the licenses round. Model spend USD 0. Pulls: 6 requests of 20 (4 by the probe, the download centre's answer read for its form, and the trial's one POST; the write ran offline).

## Read these first

- **Why this source:**
  - Germany is Europe's largest grid, and the ERW held its monthly totals only through Eurostat (session 2225), not its operator data.
  - No source of the registry names SMARD, the Bundesnetzagentur, AEMO, RTE, REE, ONS or the other operators searched.
  - Chains 097 and 098 and this chain's next file (101: France, Spain, Brazil, Australia) do not take it.
- **Two sources considered first and dropped,** both held: EIA's Annual Energy Outlook (`eia_aeo_electricity`) and its International Energy Outlook (`eia_ieo_projections`).
- **A new table, `smard_germany_monthly`** (series, 1,800 rows, `power`): Germany's actual generation by twelve sources (biomass, hydropower, offshore and onshore wind, photovoltaics, other renewable, nuclear, lignite, hard coal, fossil gas, pumped storage, other conventional) and its grid load, a month from January 2015 to September 2026, in MWh. Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set, its release rows added.
- **The source:**
  - One POST to SMARD's download centre, the form behind its Data download page, answering a zip of two CSV files.
  - The module numbers of its form were taken from memory of that form and confirmed by the answer: its columns are the twelve sources and the grid load.
  - SMARD's monthly chart files would have cost one request a series and year (156 in all).
- **The license:** SMARD's Data use page licenses its market data CC BY 4.0, attributed "Bundesnetzagentur | SMARD.de". It says the data come from the transmission system operators through ENTSO-E, verified by the Bundesnetzagentur. The verdict is for the licenses round, read 390.
- **Cross-checks, full years 2016 to 2025:**
  - SMARD's generation is 0.894 (2017) to 0.995 (2020, 2023) of Eurostat's net production for Germany (`eurostat_electricity_monthly`, session 2225).
  - Its grid load is 0.853 (2016) to 0.901 (2021) of Ember's German demand.
  - Both are steady but below. The gaps are not explained here beyond SMARD's own note that its figures are the operators' through ENTSO-E. The table is SMARD's measure, not a national total.
  - Generation falls from 545.2 TWh (2018) to 437.7 (2024) and 437.9 (2025).

## Requests (6 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.smard.de/robots.txt | 404 |
| 2 | www.smard.de/en | 200: the Data use link |
| 3 | www.smard.de/en/datennutzung | 200: CC BY 4.0 |
| 4 | the chart data's monthly index for the grid load | 200: one file a year |
| 5 | the download centre (a test of the form) | 200, a zip of two CSVs |
| 6 | the download centre from 1 January 2015, German time (the trial) | 200 |

Reads recorded: 389 and 390.

## Decisions made without you

- **The download centre in place of the chart files,** for the ceiling.
- **SMARD's figures kept as its own,** beside Eurostat's, not reconciled to them.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/smard_germany.py`, `tests/test_session2230.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, `docs/redivis/release-v1/`, the license record.
- On the data machine only: `runs/c099/s2230/`, `warehouse/raw/smard_germany/`, `warehouse/output/smard_germany_monthly.csv`.
