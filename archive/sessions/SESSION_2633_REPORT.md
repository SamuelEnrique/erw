# Session 2633 report: Grand Cayman's electricity a year since 1996 (ESO's Compendium of Statistics 2024, Table 20.01), internal

25 October 2026, about 07:50 to 07:57 UTC, on lab-desktop (the data machine), chain 131, unattended. Precheck passed (`runs/c131/pre2633.out`). Model spend USD 0. Pulls: 4 requests of 15 (3 by the probe, 1 fetch the connector reads offline).

## Read these first

- **The host:** www.eso.ky's robots file names `*` with no rule (read 1282). Its Energy and Water Supply page (read 1284) lists chapter 20 of the Compendium of Statistics for each year from 2004. The newest, dated 24 December 2025 (the Compendium 2024), was fetched once (1.0 MB, `.XLS`).
- **The terms** (read 1283, ESO's home page): its footer reads "COPYRIGHT © 2026 ESO The Economics and Statistics Office. ALL RIGHTS RESERVED.", and the site links no terms of reuse. **Verdict: needs written permission** (ZIMSTAT's precedent). The table is **internal**.
- **A new table, `eso_cayman_electricity_annual`** (series, 174 rows, 6 entities, `power`): Table 20.01, "Electricity Production in Grand Cayman", from Caribbean Utilities Company's figures, each year from 1996 to 2024.
  - The series: CUC's capacity (MW), production (MWh), and consumption by class (residential, industrial and commercial, public lighting) with its total (MWh).
  - In 2024: capacity 165.5 MW, production 760,200 MWh, consumption 749,337 (residential 406,886, industrial and commercial 338,192, public lighting 4,259).
  - Each year's classes add to the total within 1 MWh. The sheet's blank spacing rows, after the header and between groups of years, are skipped; the trial's first two runs stopped at them and the reading was set right.
  - The table excludes private generators (its note); Hurricane Ivan lowered 2004's capacity.
  - Written by run `20261025T075425Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T075429Z-local`), held from the live set and from Redivis (internal).
- **Not taken:** Table 20.02 (the Sister Islands, which ends in 2016), the percent change, the census tables of lighting and cooking fuel, and the water tables.

## Cross-checks

- EIA's world table (`eia_world_electricity_annual`, read past its header lines) gives the Cayman Islands 704.1 GWh of generation and 702.0 GWh of consumption in 2024, against Grand Cayman's 760.2 and 749.3 from CUC. ESO's figures are higher, though they leave out the Sister Islands.

## Requests (4 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | www.eso.ky's robots file, home page and Energy and Water Supply page | 200 |
| 4 | chapter 20 of the Compendium 2024 (the fetch) | 200, 1.0 MB |

Reads recorded: 1282 to 1284.

## Decisions made without you

- **Grand Cayman's table taken alone,** the Sister Islands' ending in 2016.
- **Capacity kept in the table** beside the energy, in MW as the table states it.
- **Internal** under ESO's copyright line.

## For Samuel's ruling

- **Whether to ask ESO for permission to publish the table** (its figures are CUC's).

## Files

- New: `warehouse/connectors/eso_cayman_electricity.py`, `tests/test_session2633.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 1282 to 1284, ESO's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c131/s2633/`, `runs/license_reads/s2633/`, `warehouse/raw/eso_ky/`, `warehouse/output/eso_cayman_electricity_annual.csv`.
