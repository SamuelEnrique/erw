# Session 2678 report: electricity generation by fuel and the supply balance for each UK nation, 2004 to 2025 (DESNZ), public, a source of the session's own choosing

25 October 2026, about 11:45 to 11:53 UTC, on lab-desktop (the data machine), chain 134, unattended. Precheck passed (`runs/c134/pre2678.out`). Model spend USD 0. Pulls: 4 requests of 20 (3 by the probe, 1 fetch of the workbook into the raw store, which the trial and the write read offline); one web search.

## Why this source

- **The ERW held DESNZ's UK-wide Energy Trends tables** (5.1 and 6.1), and nothing for Scotland, Wales, Northern Ireland or England apart. DESNZ publishes each nation's generation by fuel and supply balance once a year, as data tables beside an Energy Trends article.
- **This chain's four sources gave no table** (Lebanon, Myanmar, Iran, Turkmenistan), so the own choice went to an open publisher with a known licence.

## Read these first

- **The hosts:** www.gov.uk's robots file closes only print and search paths and names none of Claude's agents (read 1392). assets.publishing.service.gov.uk has no robots file (HTTP 404, read 1393).
- **The page** (read 1394): "Electricity generation and supply in Scotland, Wales, Northern Ireland and England, 2004 to 2025 - data tables", published 29 September 2026 with Energy Trends. The workbook is `Regional_Electricity_Generation_and_Supply_Timeseries_2026.xlsx`.
- **The terms:** the Open Government Licence v3.0, as the page states. DESNZ's verdict is on record (read 315, may be public). The table is **public**.
- **A new table, `desnz_uk_nations_electricity_annual`** (series, 4,167 rows, 200 entities, `power`), each year from 2004 to 2025, for the UK and each nation:
  - **Table 2a, generation by fuel:** the major power producers' and the other generators' rows, with their totals (`mpp_<fuel>`, `other_<fuel>`).
  - **Table 1, the supply balance:** generation, own use, net supply, net transfers to England, Northern Ireland and Europe (as published), transfers to public supply, losses, consumption, sales and the statistical difference.
  - **Units and codes:** MWh is the tables' GWh times 1,000; `geo` is GB or GB-SCT, GB-WLS, GB-NIR, GB-ENG.
- **Figures:**
  - UK generation was 393.9 TWh in 2004, 286.0 in 2024 and 293.6 in 2025.
  - In 2025: Scotland 54.0, Wales 22.5, Northern Ireland 8.2, England 208.9.
  - Scotland's major producers made 27.3 TWh of wind in 2025, and its net transfer to England was 18.5 TWh. The UK's net transfer to Europe was -29.7 TWh, a net import. The major producers' coal went from 127.8 TWh in 2004 to 0 in 2025.
- **Not taken, and kept as published:**
  - **Table 2a's "All generating companies" rows** are DESNZ's derived block, and in this file they do not add. Fossil fuels miss coal, oil and gas by up to 1,250 GWh, and the total its parts by up to 7,875.
  - **Table 2b** gives shares, in per cent.
  - **Table 1 is kept as published,** although its total generated misses its two parts in seven nation-years: Wales +1,235 GWh and England -1,250 in 2020, Northern Ireland +15 in 2020, and England and the UK -96 in 2023 and -1,071 in 2024.
  - **DESNZ's note 9:** the nations do not sum exactly to the UK.
- **A header with a stray digit:** Table 1 heads one column "2022 England6". The digit is dropped and the column read as England's.
- **Check:** a Table 2a block's fuels add to its total within 10 GWh (the largest gap is 7).
- **Its record:** written by run `20261025T115017Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T115022Z-local`), held from the live set, and in the release package (public). The write's and the finish's results were read before the commit; the patch applied cleanly.

## Cross-checks

Against the ERW's `desnz_uk_electricity_quarterly` (Energy Trends 5.1, the four quarters summed), the UK's total generated:
- 2025: 293.6 TWh in both.
- 2024: 286.0 TWh in both.

## Requests (4 of 20)

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.gov.uk's robots file; the assets host's robots address | 200; 404 |
| 3 | the publication page | 200 |
| 4 | the workbook (the fetch) | 200 |

Reads recorded: 1392 to 1394.

## Decisions made without you

- **DESNZ's nations as the own choice; public** under the OGL.
- **The derived all-companies rows left out,** and Table 1 kept with its gaps stated rather than checked.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/desnz_uk_nations_electricity.py`, `tests/test_session2678.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (reads 1392 to 1394) and `docs/licenses.md`.
- On the data machine only: `runs/c134/s2678/`, `runs/license_reads/s2678/`, `warehouse/raw/desnz_regional/`, `warehouse/output/desnz_uk_nations_electricity_annual.csv`.
