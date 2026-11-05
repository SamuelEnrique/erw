# Session 2818 report: European industry's electricity by NACE activity (Eurostat, nrg_d_indq_n), the third own choice (run before 2815)

26 October 2026, from about 05:27 to 05:35 UTC, on lab-desktop (the data machine), chain 143, unattended. Precheck passed (`runs/c143/pre2818.out`). Model spend USD 0. Pulls: 6 of 20 (4 by the probe, 2 by the fetch). Run before session 2815, as file 143 asks, so that 2815's notes and draft take this table.

## Read these first

- **`eurostat_industry_electricity_annual` is new:** Eurostat's energy consumption in industry by NACE Rev. 2 activity (nrg_d_indq_n), electricity only, 2017 to 2024. Each European country's industrial electricity use by activity: mining, the manufacturing divisions and some of their groups (aluminium, cement, glass, pulp, the chemical groups), and construction.
  - 8,307 rows, 34 areas, 55 activities, in MWh. The activities overlap (divisions, groups and aggregates), and the header says not to sum them.
  - The table has been written, validated, archived and put in coverage. It is held from the live set and from Redivis storage until session 2815's draft.
- **Why this source:** the ERW held industry's electricity as one total (`eurostat_electricity_consumption_annual`), not which industries use it. No connector, note or chain names nrg_d_indq_n.
- **Figures:**
  - **Germany 2024: industry 190.6 TWh**, of it chemicals (C20) 43.3, basic metals (C24) 31.7, food, drink and tobacco 18.0, paper (C17) 15.2, non-metallic minerals 10.3, aluminium 5.1.
  - The EU in 2023: chemicals 135.0 TWh, basic metals 134.4, food, drink and tobacco 110.1.
- **Zeros for splits not reported,** as session 2798 found in the household table:
  - 42 country years give 0 for every activity (several countries in 2017 to 2019);
  - 529 groups give 0 for every child under a positive parent (Austria's chemicals, 3,408 GWh in 2020, and its six groups 0).

  Their 4,199 observations are not written, counted in the header and listed in the run log. 1,104 other zeros are kept, and 488 confidential observations have no row.
- **Checks:**
  - **The hierarchy:** each group's children against their parent within 0.5 GWh holds in 1,835 of 1,851 cases. The 16 others are kept as published.
  - **Against the held table:** this table's total against `eurostat_electricity_consumption_annual`'s industry, in the 191 country years both give. 123 agree within 0.1 per cent (Germany 2024: 190,603 GWh in both) and 140 within 1 per cent. 11 differ by more than 5 per cent: Estonia 2017 to 2020, Italy 2021, Greece 2020, Georgia 2024, the Netherlands 2017 to 2019 and Serbia 2020 (corrected by session 2815, which first listed only the Netherlands' 2017). These are the two datasets' vintages, kept as published.
- **A conflict at the write:** the metadata patch met the nuclear table's rows (session 2812) in `coverage.csv`, `docs/coverage.md` and `archive_manifest.csv`. Each block was resolved as the union of its two new rows (`runs/c124/resolve_union.py`), before any commit. No marker and no row twice remained.

## The requests

| n | What | Outcome |
|---|---|---|
| 1 | ec.europa.eu's robots file | 200, byte for byte session 2813's |
| 2 | the dataflow with `references=datastructure` | HTTP 400, not supported (no retry: the probe) |
| 3 | the data structure | 200, the key freq.unit.siec.nace_r2.geo |
| 4 | the electricity data, `A.GWH.E7000..` (probe) | 200 |
| 5 | the same, into the connector's raw folder | 200, byte for byte |
| 6 | the NACE_R2 codelist | 200 |

Reads recorded: 1625 to 1628.

## Decisions made without you

- **Zeros under a positive parent read as splits not reported** and not written, as in session 2798. Reversible: drop the rule in `build`.
- **Electricity only** from a dataset of every fuel.

## For Samuel's ruling

- None new.

## Files

- New:
  - `warehouse/connectors/eurostat_industry_electricity.py`
  - `tests/test_session2818.py` (5 tests, passing)
  - this report
- Changed:
  - the table's registration and holds;
  - the license record (reads 1625 to 1628) and `docs/licenses.md`;
  - coverage, sources, the archive manifest and the release v1 records.
- On the data machine only:
  - `runs/c143/s2818/`, `runs/license_reads/s2818/`;
  - `warehouse/raw/eurostat_industry_electricity/`.
