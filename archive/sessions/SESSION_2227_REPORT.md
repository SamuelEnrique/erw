# Session 2227 report: Norway's electricity (Statistics Norway)

24 October 2026, from 02:22 UTC, on lab-desktop (the data machine), chain 099, unattended. Model spend USD 0. Pulls: 8 requests of 15 (6 by the probe, the metadata and the query by the trial; the write ran offline). The write waited for the data lock from 02:27 to 02:39 UTC while chain 097's Stanford draft and writes held it.

## Read these first

- **Table 08307, which the chain file names, was not asked:** the monthly tables found first, 08583 and 12824, are closed series (2010 to 2019 and 2010 to 2023), and SSB's table search found the current one: **14091, Electricity balance (MWh), January 1993 to September 2026**, updated 19 October 2026.
- **A new table, `ssb_norway_electricity_monthly`** (series, 5,550 rows, `power`): Norway's electricity balance a month from January 1993, across 26 lines:
  - total generation and its hydro, wind, solar and thermal parts;
  - imports and exports;
  - gross consumption, pumped storage, grid loss and statistical difference;
  - net consumption by industry (the power intensive manufacturers by kind) and households.

  The values are in MWh, as SSB gives them. The 4,980 cells SSB leaves empty have no row. Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set, its release rows added.
- **The license:** data.ssb.no's robots.txt redirects to SSB's API page (www.ssb.no/api). That page states: "I likhet med resten av ssb.no benytter API-ene lisensen CC BY 4.0" (like the rest of ssb.no, the APIs use the CC BY 4.0 license). The table is registered `public`, and its verdict is for the licenses round (session 2229), read 365.
- **Cross-checks, full years 2016 to 2025:**
  - Against Eurostat (`eurostat_electricity_monthly`, session 2225, Norway): SSB's total generation equals Eurostat's net production within 0.05 percent every year from 2017. In 2016 it is 2.9 percent above (149.53 against 145.32 TWh). Imports and exports agree within 0.2 percent from 2017; in 2016 exports differ by 2.5 percent.
  - Against Ember's demand (`owid_ember_electricity_annual`): SSB's gross consumption is within 1.2 percent every year (133.12 against 131.62 TWh in 2016; 138.99 against 137.71 in 2025).
  - Total generation: 124.4 TWh (2010) to 161.8 TWh (2025); net exports 34.31 less 11.51 TWh in 2025.

## Requests (8 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | data.ssb.no/robots.txt | 200 after a redirect to www.ssb.no/api: the APIs' license |
| 2 | www.ssb.no/robots.txt | 200: disallows /a/kostra/stt only |
| 3, 4 | tables 12824 and 08583's metadata | 200: closed series |
| 5 | the table search ("electricity balance") | 200: 14091 |
| 6 | table 14091's metadata | 200: 26 lines, 405 months |
| 7, 8 | the metadata and the JSON query (the trial) | 200 |

Reads recorded: 365 and 366.

## Decisions made without you

- **From 1993, not 2010:** the table holds both, and the earlier years cost no request.
- **Table 14091 in 08307's place,** said above.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/ssb_electricity.py`, `tests/test_session2227.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, `docs/redivis/release-v1/`, the license record.
- On the data machine only: `runs/c099/s2227/`, `warehouse/raw/ssb_electricity/`, `warehouse/output/ssb_norway_electricity_monthly.csv`.
