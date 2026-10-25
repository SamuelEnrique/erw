# Session 2743 report: the major power producers' capacity by UK country, 1999 to 2025 (DESNZ's DUKES 5.8), public, a second source of the session's own choosing

25 October 2026, about 20:58 to 21:02 UTC, on lab-desktop (the data machine), chain 138, unattended. Precheck passed (`runs/c138/pre2743.out`). Model spend USD 0. Pulls: 2 requests of 20 (1 by the probe, 1 fetch of the workbook, read offline by the trial and the write).

## Why this source

- **The country split of chain 137's DUKES 5.7:** DUKES 5.8 gives the major power producers' capacity for England and Wales, Scotland and Northern Ireland, from the same chapter, host and licence. The ERW held these countries only in DESNZ's renewables and consumption tables.

## Read these first

- **The host:** www.gov.uk's robots file closes only print and search paths and names no Claude agent (read 1479). The terms are the Open Government Licence v3.0 (read 315), so the table is **public**.
- **A new table, `desnz_uk_mpp_capacity_countries_annual`** (series, 1,539 rows, 51 entities, `power`), 1999 to 2025 (1996 to 1998 are "[x]", DESNZ's note 1):
  - Entity `desnz_mppr:<country>:<item>`, for England and Wales, Scotland and Northern Ireland.
  - `derated_capacity` (5.8.A, by fuel, MW) and `thermal_capacity` (5.8.B's thermal plant types, 5.8.C, MW).
  - `capacity_share` (5.8.B), as a ratio. The sheet's heading says "per cent", but its cells hold fractions such as 0.7977.
  - These are de-rated figures, as in DUKES 5.7 (notes 3 and 5).
- **Figures:**
  - In 2025: England and Wales 49,400 MW (79.8 per cent), Scotland 10,256 (16.6), Northern Ireland 2,276 (3.7).
  - In 1999 Scotland held 13.9 per cent.
- **Checks, all passing:**
  - each country's fuels add to its total, and its plant types to its thermal total, within 0.5 MW;
  - the three shares add to 1, each equal to the country's total over the three, within 0.001.
- **Its record:** written by run `20261025T210025Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T210029Z-local`), held from the live set, and in the release package (public). The patch applied cleanly.

## Cross-check

Against `desnz_uk_derated_capacity_annual` (DUKES 5.7, chain 137): the three countries' totals add to its major power producers' total exactly.

| Year | The three countries (MW) | DUKES 5.7 (MW) |
|---|---|---|
| 2015 | 70,321.67 | 70,321.67 |
| 2016 | 67,964.93 | 67,964.93 |
| 2025 | 61,931.21 | 61,931.21 |

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.gov.uk's robots file (its own request) | 200 |
| 2 | DUKES_5.8.xlsx (the fetch) | 200 |

Read recorded: 1479.

## Decisions made without you

- **DUKES 5.8 as the second own choice; public.**
- **The shares stated as a ratio,** the cells' own form, not the heading's per cent.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/desnz_dukes_mpp_countries.py`, `tests/test_session2743.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (read 1479) and `docs/licenses.md`.
- On the data machine only: `runs/c138/s2743/`, `runs/license_reads/s2743/`, `warehouse/raw/desnz_dukes/s2743probe1/`, `warehouse/output/desnz_uk_mpp_capacity_countries_annual.csv`.
