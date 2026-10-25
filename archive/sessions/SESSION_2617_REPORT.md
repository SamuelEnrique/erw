# Session 2617 report: the Gambia's electricity a month in 2022 by source (NAWEC's Annual Activity Report 2022, Table 3), internal

25 October 2026, about 06:30 to 06:40 UTC, on lab-desktop (the data machine), chain 130, unattended. Precheck passed (`runs/c130/pre2617.out`). Model spend USD 0. Pulls: 10 requests of 15 (8 by the probe, 2 fetches; the connector reads the second offline).

## Read these first

- **The hosts:** www.gbosdata.org and nawec.gm have no robots file (HTTP 404, reads 1230 and 1231); pura.gm's names `*` with no rule (read 1232).
- **The statistics office (GBoS):** its data portal (reads 1233 and 1235) holds electricity only as national accounts value added and a price index, with no quantities.
- **The regulator (PURA):** its media list (read 1234) gives annual reports for 2009 to 2024. The 2024 report (196 pages, fetched once) states 2024's production, 696,382.06 MWh, only in prose, beside tables its text layer garbles. Not taken.
- **The utility (NAWEC):** its Annual Reports page (read 1237) links the Annual Activity Report 2022 (100 pages, 12.7 MB, last modified 13 August 2026). Its Table 3, "Electricity Month Production", gives 2022 by month and source.
- **The terms** (read 1236, NAWEC's home page): its footer reads "(c) 2026 NAWEC", a dash, then "National Water & Electricity Company, The Gambia. All rights reserved." Its Terms of Service link is an empty anchor. **Verdict: needs written permission** (ZIMSTAT's precedent).
  - The verdict's sentence is cut after the dash, as no ERW file may hold one. The first commit named the verdict but its script had stopped at that dash; it was added in a commit of its own.
  - The table is **internal**.
- **A new table, `nawec_gambia_electricity_monthly`** (series, 60 rows, 5 entities, `power`), each month of 2022:
  - `nawec` (NAWEC's own plants) and `karpower` (Karpowership, an independent producer), variable `generation`;
  - `senelec` (over SENELEC's lines) and `omvg` (through the OMVG 225 kV interconnection), variable `imports`;
  - `total`, variable `supply`. The report calls every column "production".
  - The year: NAWEC 160,353.58 MWh, SENELEC 32,003.60, OMVG 165,553.79 (from March), Karpower 213,716.57, total 571,627.54.
  - Each month's sources add to its total within 0.1 MWh, and each column's months to the Total line within 0.5 MWh.
  - Written by run `20261025T063711Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T063720Z-local`), held from the live set and from Redivis (internal).
- **Not taken:** the table's percentages; the plants' fuel and cost tables; PURA's prose figures.

## Cross-checks

- EIA's world table (`eia_world_electricity_annual`, read past its header lines) gives the Gambia 511.5 GWh of generation and no imports in 2022. NAWEC's table gives 374.1 GWh generated in the country (NAWEC and Karpower) and 197.6 GWh imported (SENELEC and OMVG): EIA counts no imports. Table 3's total equals the 571,627.54 MWh the report's text gives for 2022 (467,103.30 MWh in 2021).

## Requests (10 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | the robots files of www.gbosdata.org, nawec.gm and pura.gm | 404, 404, 200 |
| 4 | GBoS's home page | 200 |
| 5 | PURA's media list, search "report" | 200 |
| 6 | PURA's Annual Report 2024 (a fetch) | 200, 19.5 MB, prose figures |
| 7 | GBoS's macroeconomic data page | 200 |
| 8, 9 | NAWEC's home page and Annual Reports page | 200 |
| 10 | NAWEC's Annual Activity Report 2022 (the fetch) | 200, 12.7 MB |

Reads recorded: 1230 to 1237.

## Decisions made without you

- **The columns given variables by what they are:** `generation` for NAWEC and Karpower, `imports` for SENELEC and OMVG, `supply` for the total; the report's own heading is "production".
- **2022's table taken though newer years exist only in PURA's prose.**
- **Internal** under NAWEC's copyright line.

## For Samuel's ruling

- **Whether to ask NAWEC for permission to publish the table,** and for its later activity reports.

## Files

- New: `warehouse/connectors/nawec_gambia_electricity.py`, `tests/test_session2617.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 1230 to 1237, NAWEC's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c130/s2617/`, `runs/license_reads/s2617/`, `warehouse/raw/pura_gm/`, `warehouse/raw/nawec_gm/`, `warehouse/output/nawec_gambia_electricity_monthly.csv`.
