# Session 2684 report: renewable electricity generation a year by UK region and technology, 2003 to 2025 (DESNZ's Regional Renewable Statistics), public, a third source of the session's own choosing

25 October 2026, about 12:00 to 12:05 UTC, on lab-desktop (the data machine), chain 134, unattended. Run before sessions 2681 to 2683, so that their notes, draft and records hold its table. Precheck passed (`runs/c134/pre2684.out`). Model spend USD 0. Pulls: 3 requests of 20 (2 by the probe, 1 fetch of the workbook into the raw store under a run name of its own, read offline by the trial and the write).

## Why this source

- **Session 2678 took the UK nations' generation by fuel,** and the ERW held no region of England. DESNZ's Regional Renewable Statistics give renewable generation for England's nine regions and the nations each year from 2003.
- **The publisher and the host are the same as session 2678's,** and DESNZ's verdict is on record, so the session's ceiling went to the data.

## Read these first

- **The host:** www.gov.uk's robots file closes only print and search paths (read 1399). The assets host has no robots file (session 2678, read 1393).
- **The page** (read 1400) lists the regional workbooks of generation, capacity, sites, load factors and generation per GVA, 2003 to 2025. This session takes generation, `Regional_generation_GWh_2003-2025.xlsx`, a sheet a year.
- **The terms:** the Open Government Licence v3.0 (DESNZ's verdict, read 315). The table is **public**.
- **A new table, `desnz_regional_renewables_annual`** (series, 3,002 rows, 194 entities, `power`), 2003 to 2025:
  - `desnz_re:<region>:<technology>` for England's nine regions, Wales, Scotland, Northern Ireland, England, the sites not attributed to a region, and the UK.
  - MWh is the workbook's GWh times 1,000; `geo` gives England's regions England's code, as ISO 3166-2 has none for them.
- **The columns change over the years:** one "Wind" column early, then onshore and offshore; "Other bioenergy" early, then sewage gas, anaerobic digestion and biomass and waste apart. Each column is kept as its own technology, and none is merged.
- **Figures:**
  - UK renewable generation was 10.6 TWh in 2003, 26.2 in 2010, 133.5 in 2020 and 152.9 in 2025.
  - In 2025 Scotland made 39.0 TWh, 22.0 of it onshore wind. Yorkshire and the Humber made 34.8, 18.2 of it biomass and waste. The East of England made 11.4 of offshore wind, and London 1.5 in all.
- **"[x]"** (too few sites to show) has no row.
- **Checks, all passing:**
  - a region's technologies add to its total within 1 GWh (no more than it where a cell is "[x]");
  - England's nine regions add to England within 1 GWh;
  - the nations and the other sites add to the UK within 1 GWh.
- **Its record:** written by run `20261025T120249Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T120253Z-local`), held from the live set, and in the release package (public). The write's and the finish's results were read before the commit; the patch applied cleanly.

## Cross-checks

Against the ERW's `desnz_uk_renewables_quarterly` (Energy Trends 6.1, four quarters summed), the UK in 2025, in TWh:
- in all, 152.9 against 153.0;
- onshore wind 34.4 and 34.4; offshore wind 52.0 and 52.0; solar 20.1 and 20.1.

## Requests (3 of 20)

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.gov.uk's robots file; the Regional Renewable Statistics page | 200 |
| 3 | the generation workbook (the fetch) | 200 |

Reads recorded: 1399 and 1400.

## Decisions made without you

- **Run before sessions 2681 to 2683,** so that this chain's notes, Stanford draft and records include its table.
- **DESNZ's regional renewables as the third own choice; public** under the verdict on record.
- **Each year's columns kept as given,** not merged into a common set.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/desnz_regional_renewables.py`, `tests/test_session2684.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (reads 1399 and 1400) and `docs/licenses.md`.
- On the data machine only: `runs/c134/s2684/`, `runs/license_reads/s2684/`, `warehouse/raw/desnz_regional/s2684probe1/`, `warehouse/output/desnz_regional_renewables_annual.csv`.
