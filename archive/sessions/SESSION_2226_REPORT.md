# Session 2226 report: the UK's gas balance (DESNZ, Energy Trends section 4)

24 October 2026, from 02:16 UTC, on lab-desktop (the data machine), chain 099, unattended. Model spend USD 0. Pulls: 5 requests of 15 (the two robots files, the page twice, once by the probe and once by the trial, and the workbook; the write ran offline).

## Read these first

- **A new table, `desnz_uk_gas_quarterly`** (series, 2,394 rows, `gas`): the UK's natural gas supply and consumption, a quarter from the first of 1998 to the second of 2026 (provisional). It comes from DESNZ's Energy Trends table ET 4.1, sheet "Quarter (GWh)". Its 21 lines run from indigenous production and imports (of which LNG), exports, stock change and transfers to total supply and demand, transformation (electricity and heat generation), energy industry use, losses, and final consumption by sector. The values are in MWh (DESNZ's GWh times 1,000). Written, validated (0 errors, 0 warnings), archived, held from the Redivis storage and the live set, its release rows added. Public under the Open Government Licence (DESNZ's verdict), the attribution in the header.
- **DESNZ's notes are carried in the header:** imports and exports on a physical flow basis from 2000; LNG imports include cargoes from 2016; stock change positive is a draw; the series breaks they name.
- **The chain file's "imports by route"** is the monthly ET 4.3, not taken. The quarterly table's imports and LNG imports are the routes it gives.
- **Cross-checks:**
  - The balance holds: total supply less total demand equals DESNZ's statistical difference within 10 MWh in every quarter.
  - Against `desnz_uk_electricity_quarterly` (chain 094, ET 5.1b), the electricity generated from gas by all generating companies over the gas used for electricity generation, in all 114 shared quarters: a median 0.468, 0.429 to 0.496. Yearly it rises from 0.440 (1998) to 0.478 to 0.488 from 2016, a plausible fleet efficiency.
  - LNG is 13.7 to 44.9 percent of the UK's imports a year from 2016 (44.9 in 2022).
  - The chain file's LNG check against EIA's U.S. LNG exports to the UK could not be made: `eia_lng_exports_monthly` is by U.S. terminal, not by destination.

## Requests (5 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.gov.uk/robots.txt | 200: print and search pages only |
| 2 | the Energy Trends section 4 page | 200: ET 4.1 to 4.5 |
| 3 | assets.publishing.service.gov.uk/robots.txt | 404 |
| 4 | ET_4.1_SEP_26.xlsx | 200, 149,197 bytes |
| 5 | the page again (the trial, for the file's address) | 200 |

Reads recorded: 384 to 386.

## Decisions made without you

- **The GWh sheet, not the million cubic metres one;** the two are the same balance in two units.
- **The quarterly table only;** ET 4.2 (monthly, Official Statistics in Development), 4.3 and 4.4 (monthly imports and exports by route) are left for a later session.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/desnz_gas.py`, `tests/test_session2226.py`, this report.
- Changed: `warehouse/metadata/build_coverage.py`, `warehouse/redivis/release_v1.py`, `warehouse/supabase/live_set.yaml`, `docs/coverage.md`, `warehouse/metadata/coverage.csv`, `warehouse/metadata/sources.csv`, `warehouse/metadata/archive_manifest.csv`, `docs/redivis/release-v1/`, the license record.
- On the data machine only: `runs/c099/s2226/`, `warehouse/raw/desnz_gas/`, `warehouse/output/desnz_uk_gas_quarterly.csv`.
