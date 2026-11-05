# Session 2771 report: Luxembourg's electricity generation a year from 1928 (STATEC's LUSTAT), a second own choice

26 October 2026, about 00:08 to 00:16 UTC, on lab-desktop (the data machine), chain 140, unattended. Precheck passed (`runs/c140/pre2771.out`). Model spend USD 0. Pulls: 6 requests of 20 (5 by the probe, redirects capped at 5; 1 fetch).

## Read these first

- **Why this source:** STATEC, Luxembourg's national statistics institute, was in neither the record nor the queue; the ERW held only the regulator ILR's electricity figures. Its LUSTAT service is a .Stat Suite SDMX API, and its data are public domain (CC0 1.0).
- **`statec_lu_electricity_generation_annual`, public, held from the live set and in the Stanford holds** (`warehouse/connectors/statec_electricity_generation.py`, 942 rows, 19 entities, 1928 to 2024):
  - From LUSTAT dataflow DF_A4203, "Electricity generation", every key in one request (CSV with labels). The GWh rows are taken; the TJ and ktep rows, the same figures in other units, are not.
  - STATEC's 19 codes kept as entities:
    - total gross and net generation;
    - gross primary and secondary generation;
    - net generation by plant type (hydro, wind, solar, thermal, CHP);
    - the five under primary and secondary;
    - pumping, siderurgy, biogas, wood wastes and pellets.
  - Net generation: 428,000 MWh in 1928, 1,322,035 in 1990, 2,708,833 in 2024. 901 observations STATEC marks not available have no row.
  - **How the codes relate,** found in the data and checked:
    - gross primary is its three parts and gross secondary its two, exactly every year (a miss stops the run);
    - the total gross is primary plus secondary;
    - net is the five plant types, except 1933 (4.5 GWh), which is counted and kept as published.
- **Cross-check** against `eurostat_electricity_production_annual` (Luxembourg):
  - The total gross agrees within 4.2 GWh (1990: 1,378.2 against 1,377.0; 2010: 4,591.5 against 4,591.3; 2020 equal; 2024: 2,738.1 against 2,742.3).
  - Wind and solar are equal in every year shown.
  - Pumping (sssl01) against Eurostat's pumped hydro is within 7.7 GWh (2010: 1,368.0 against 1,360.3).
- **Terms and verdict:**
  - lustat.statec.lu has no robots file; its address answers the data explorer's page (read 1560). statistiques.public.lu's robots file closes `/` to a few SEO crawlers and query strings and search to `*`, and names no Claude agent (read 1561). www.statistiques.public.lu does not resolve (read 1562).
  - STATEC's legal notice, linked from LUSTAT's footer (read 1564, outcome exactly `read`): the portal's information is published "without restriction, under the terms of the Universal Transfer in the Public Domain Creative Commons CC0 1.0", with goodwill guidelines asking for the source and the links. **Verdict added: may be public** (`runs/c140/s2771_verdict.py`).
- **Two faults of mine, caught before the write:**
  - The test's "given twice" case did not stop: a duplicated missing observation was never stored, so it was not caught. The connector now tracks every key it sees.
  - The connector's publisher name did not match the verdict's key. Both now read "STATEC (Luxembourg)", and the license record shows the table as agreed, public.
- **Written under the data lock:** validated, archived (942 rows), in coverage. The patch applied cleanly with no marker. Coverage has 607 tables and `sources.csv` 697 sources, none twice. `finish_table.sh`: the release and license checks pass (607 tables, 257 verdicts, 0 problems).

## Requests (6 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | lustat.statec.lu's robots file (its own request) | the explorer's page, no file |
| 2 | statistiques.public.lu's robots file (its own request) | 200 |
| 3 | www.statistiques.public.lu's robots file (its own request) | does not resolve |
| 4 | LUSTAT's dataflow list | 200, 901 dataflows |
| 5 | STATEC's legal notice | 200, CC0 1.0 |
| 6 | DF_A4203, every key, CSV (the fetch) | 200, 830,029 bytes |

Reads recorded: 1560 to 1564.

## Decisions made without you

- **STATEC's codes kept as entities** with its labels in `node`, rather than renamed: the hierarchy is stated as the data show it.
- **DF_A4208 (imports and exports by country) not taken:** one source a session.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/statec_electricity_generation.py`, `tests/test_session2771.py`, this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, the license record (reads 1560 to 1564, one verdict), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c140/s2771/`, `runs/c140/s2771_verdict.py`, `runs/license_reads/s2771/`, `warehouse/raw/statec/`.
