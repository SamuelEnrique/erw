# Session 2552 report: Saudi Arabia's electricity a year (GASTAT's Electrical Energy Statistics 2024, the Ministry of Energy's figures), the session's own choice, internal

24 October 2026, about 23:11 to 23:18 UTC, on lab-desktop (the data machine), chain 125, unattended. Precheck passed (`runs/c125/pre2552.out`). Model spend USD 0. Pulls: 5 requests of 20 (4 by the probe, 1 by the fetch the connector reads offline).

## Read these first

- **Why Saudi Arabia:** the largest grid of the Gulf, which the ERW held only in EIA's and OWID's international tables. Other own choices were looked at first and dropped without a request: the Scottish Government's energy statistics are DESNZ's Energy Trends by country (held as DESNZ's), Luxembourg is held (ILR), and Hawaii's DBEDT gives its monthly electricity figures in PDFs only.
- **The host:** www.stats.gov.sa's robots file closes `/api/`, `/c/portal/` and `/o/` (read 1034); its documents are under `/documents/`. The methodology report (read 1035) links the "Electrical energy statistics" tab (read 1036), which lists the 2024 workbook and PDF (Arabic editions).
- **GASTAT's use policy** (read 1037), 1.2.2: "Except for trademarks, logos, and any clearly identified third-party material, GASTAT permits users to copy, reproduce, publish, distribute, transmit, adapt, modify, translate, build upon, and otherwise reuse the materials and data made available on this website for any purpose, including commercial use ..., provided that GASTAT is acknowledged as the official source and any modifications are clearly indicated". **Verdict: may be public** for GASTAT's own material. But every table of this workbook names the Ministry of Energy as its source, which the policy excepts as third-party material: the table is registered under "Ministry of Energy, Saudi Arabia, as published by GASTAT" and stays **internal**, not settled. For you.
- **The source:** "Electrical Energy Statistics 2024" (Arabic edition, 0.21 MB), fetched once; its sheets 1 to 8 are read, each found by its name and words of its title (in Arabic), each column by words of its header.
- **A new table, `gastat_saudi_electricity_annual`** (series, 177 rows, 28 entities, `power`): licensed capacity in total and by type of unit (2019 to 2024; 92.5 GW in 2024), peak load in total and by the Saudi Electricity Company's four business areas (74.8 GW in 2024), the energy sent to the network and the energy consumed (2010 to 2024; 402.628 and 340.430 TWh in 2024), consumption by category (2021 to 2024), and the energy sold in 2024 by administrative region (13) and category. Capacity and peak load in MW, energy in MWh. GASTAT's approximation sign is kept as `x_approx` (11 rows). Consumption by category sums to the energy consumed each year (340,430 GWh in 2024). Written by run `20261024T231634Z` under the data lock, validated (exit 0), in coverage, archived (`20261024T231638Z-local`), held from the live set and from Redivis (internal).

## Cross-checks

- The regions' sales in 2024 sum to 340.376 TWh, against the energy consumed, 340.430 TWh.
- Against `eia_world_electricity_annual`'s Saudi Arabia for 2024: EIA's generation 445.757 TWh against GASTAT's energy sent out 402.628 TWh (90%; EIA counts self-generation and other producers off the grid's metering); EIA's consumption 405.978 TWh against GASTAT's 340.430 (GASTAT's consumption is sales only, its footnote says).

## Requests (5 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.stats.gov.sa's robots file | 200 |
| 2, 3 | the methodology report and the statistics tab | 200 |
| 4 | the workbook (the fetch) | 200, 0.21 MB |
| 5 | GASTAT's use policy | 200 |

Reads recorded: 1034 to 1037. Five web searches found the sources looked at; they reached no publisher's host.

## Decisions made without you

- **Saudi Arabia as the own choice; internal** while the policy's third-party exception may cover the Ministry of Energy's figures.
- **The approximation signs kept** in a column, the figures taken as published.

## For Samuel's ruling

- **Whether GASTAT's grant covers tables it attributes to the Ministry of Energy.** If it does, the table could be public with GASTAT acknowledged.

## Files

- New: `warehouse/connectors/gastat_saudi_electricity.py`, `tests/test_session2552.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 1034 to 1037, GASTAT's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c125/s2552/`, `warehouse/raw/gastat_sa/`, `warehouse/output/gastat_saudi_electricity_annual.csv`.
