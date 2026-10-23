# Session 2087 report: the energy tax credits (the IRS's Statistics of Income)

23 October 2026, from 21:11 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/068-day-26-october-data-mexico-renewables-loans-credits-pipelines.md`, unattended. Model spend USD 0. Pulls: 15 requests of 15 (below).

## Read these first

- **One table written, validated, archived, in coverage (sector power), in the release package, both holds:** `irs_soi_energy_credits_annual`, the residential energy credits individuals claimed, by state and tax year, 2015 to 2023, from SOI's Historic Table 2 (the row of all incomes): 1,074 rows for the states, DC, SOI's national row (`irs_soi:US`) and its other areas (`OA`). To 2022 one credit, SOI's "Residential energy tax credit" (N07260, A07260); for 2023, when the credit was split, the "Residential clean energy credit" (N07262, A07262) and the "Energy efficient home improvement credit" (N07265, A07265). Returns are a count; amounts, which SOI gives in thousands of dollars, are in USD.
- **The national figures:** 2,605,570 returns and USD 2.17 billion in 2015; 726,440 returns in 2018, the fewest; 3,220,260 returns and USD 7.98 billion in 2022; in 2023, 1,518,210 returns claimed USD 7.79 billion of the clean energy credit and 2,612,610 returns USD 2.32 billion of the home improvement credit.
- **The cross-check** against the totals SOI prints: the states and other areas sum to SOI's own national row, the amounts exactly in every year and the returns within 50 (SOI rounds its counts); the national rows of 2022 and 2023 are the figures SOI's labelled workbooks print beside the same labels (`22in55cm.xlsx`, `23in55cm.xlsx`).
- **The license is not settled yet:** the IRS's own terms were not read within this session's ceiling; the licenses round (session 2089) reads them. The table is flagged public in the source registry, and the license record holds it "not settled" until then.

## The pulls

1. `www.irs.gov/robots.txt` (read 222): disallows its statistics index search and site paths, not `/pub/irs-soi` or `/statistics`. 2. Historic Table 2's page (2020 to 2023). 3. The 2023 workbook, for the columns' labels. 4. `15in55cmcsv.csv`: HTTP 404 (the 2015 to 2019 files are named otherwise). 5 to 8. The 2020 to 2023 CSV files. 9. The 2015 to 2019 page. 10 to 14. The 2015 to 2019 CSV files. 15. The 2022 workbook, for its label. All saved in `warehouse/raw/irs_soi_energy/` and reused by the write (`--offline`).

## Decisions made without you

- **All incomes only** (AGI_STUB 0); the table's income classes are not taken.
- **SOI's thousands of dollars written as USD** (times 1,000), the unit the standard holds, rather than a new unit.
- **The 2023 split kept as two credits,** not added into the earlier one.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/irs_soi_energy.py`, `tests/test_session2087.py` (4 tests), this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `docs/coverage.md`, `coverage.csv`, `archive_manifest.csv`, `sources.csv`, `license_reads.csv` (222), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c068/s2087/`, `runs/license_reads/s2087/`, `runs/s2087*`, `warehouse/raw/irs_soi_energy/`.
