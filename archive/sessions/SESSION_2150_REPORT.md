# Session 2150 report: the world's electricity access (the World Bank's indicators)

23 October 2026, from 23:41 UTC, on lab-desktop (the data machine), a session of `queue/done/092-day-30-october-data-bpa-snowpack-access-outlook-permits.md`. Model spend USD 0. Pulls: api.worldbank.org, 10 requests of 15. They were its robots address (404, there is none); the three indicators' metadata; a probe of one indicator and of the economies list; and the trial's four, asked again since they change. Also Supabase for the locks.

## Read these first

- **Two series tables, from the World Bank's Indicators API v2 (no key):**
  - **`wb_electricity_access_annual`** (5,350 rows, 215 economies, 2000 to 2024): access to electricity, percent of population (EG.ELC.ACCS.ZS), the World Bank's own SDG 7.1.1 electrification dataset. **Public** under the World Bank's CC BY 4.0 (read 141).
  - **`wb_iea_electricity_annual`** (8,220 rows, 209 economies, 2000 to 2025): electric power consumption per person (EG.USE.ELEC.KH.PC, kWh) and renewable electricity output as a share of the total (EG.ELC.RNEW.ZS). **Internal:** the World Bank's licence holds "unless indicated otherwise in the data or indicator metadata", and both indicators' metadata name the IEA's Energy Statistics as their source. The IEA's terms are for session 2153's round.
- **The World Bank's aggregates** (regions, income groups, the world) are left out by its own economies list (region "NA"), and an empty value has no row.
- **A new unit, `kWh/person` (Decision 68),** in the standard and the validator together. 66 and 67 are chains 079's and 090's, by agreement among the three agents.
- **The cross-check** (`runs/c092/s2150/cross.py`): the United States' consumption per person (the IEA's) against EIA's SEDS electricity sold to ultimate customers (ESTCB, at 3,412 Btu a kWh) over SEDS's population. The ratio is 1.09 to 1.13 in every year from 2000 to 2024 (12,934 against 11,692 kWh in 2024). That steady gap fits the IEA counting electricity that is not sold, such as industry's own generation used onsite and direct use; this check does not prove the cause. Access in 2024: 15 economies of 215 below half (South Sudan 5.4 percent, Chad 13.4, Malawi 15.6), 122 at 100 percent, the United States at 100 in every year.
- **Registered:** the sector rules (`power`), both live set holds, the release's storage hold and release rows for the public table only; license tables (licenses check 0 problems, release check 0 differences); no row twice. The test: `tests/test_session2150.py` (4 tests).

## Errors

- **`register.py` stopped on the release list** for the first table, because the anchor I gave it (the SNOTEL table) is internal and not in that list. The access table's release entry was added after `bpa_ba_hourly` by hand, and the IEA table registered after it.
- **The second table's metadata patch met the first's** (their rows are adjacent); each side only added its own row, resolved by union (`runs/union_resolve.py`). The first table's second finish then exited 1 only because its release rows were already there.

## Decisions made without you

- **The IEA's two indicators held internal** until the IEA's terms are read, as Our World in Data's columns from other publishers were to be held.
- **From 2000,** as the file asked.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/wb_wdi_electricity.py`, `tests/test_session2150.py`, this report.
- Changed: `docs/datastandard.md`, `warehouse/validate/erw_validate.py`, `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`, `warehouse/redivis/release_v1.py`, `docs/coverage.md`, `coverage.csv`, `sources.csv`, `archive_manifest.csv`, `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c092/s2150/`.
