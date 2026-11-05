# Session 2670 report: Aland's electricity sales by distributor and sector, with its exports, 1980 to 2025 (ASUB's PxWeb table MI010), public, a third source of the session's own choosing

25 October 2026, about 10:43 to 10:50 UTC, on lab-desktop (the data machine), chain 133, unattended. Run before sessions 2667 to 2669, so that their notes, draft and records hold its table. Precheck passed (`runs/c133/pre2670.out`). Model spend USD 0. Pulls: 5 requests of 20 (4 by the probe, 1 POST by the connector's online trial; the write reads it offline).

## Why this source

- **Argentina's Energy Secretariat first:** its open data portal, datos.energia.gob.ar, did not answer over http or https (reads 1369 and 1370), so nothing on it was asked. CAMMESA has been closed since session 2283.
- **Aland's sales then:** ASUB's MI010 is a table the ERW did not hold, beside MI009 (supply by origin, held since session 2651). It adds what MI009 lacks, the islands' exports, which began in 2022 as their wind output grew, and their sales by distributor and sector. It takes a source id of its own (`asub_ax:MI010`).

## Read these first

- **The host:** pxweb.asub.ax still has no robots file (HTTP 404, read 1371). MI010's metadata (read 1372) gives the years 1980, 1985, 1990 and 1994 to 2025; four regions (all of Aland, Mariehamns Energi, Alands elandelslag, export); GWh or per cent; and six sectors.
- **The terms:** ASUB's CC BY 4.0, read in session 2651 (read 1326, its verdict on record). The table is **public**.
- **A new table, `asub_aland_electricity_sales_annual`** (series, 603 rows, 18 entities, `power`), from one JSON-stat POST (the GWh figures):
  - `asub:ax:<region>:<sector>`, variable `sales` (`exports` for the region export); MWh is the table's GWh times 1,000.
  - Aland's sales were 87 GWh in 1980, 297 in 2021 and 276 in 2025. In 2025 they were households 121, services 56, the public sector 45, industry 38 and agriculture 16.
  - In 2025 Mariehamns Energi sold 98 GWh and Alands elandelslag 178. Exports were 0 until 2021, then 22 GWh in 2022 and 47 in 2025.
- **Checks for whole-GWh rounding:** a distributor's sectors must meet its total within 3 GWh (the table's largest gap is 2), and the two distributors Aland's total within 1.5 GWh.
- **Kept as given:** exports have a total only, and Mariehamn has no agriculture row.
- **Its record:** written by run `20261025T104743Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T104748Z-local`), held from the live set, and in the release package (public). The write's and the finish's results were read before the commit; the patch applied cleanly.

## Cross-checks

Against MI009's supply (`asub_aland_electricity_annual`), in GWh:

| Year | Supply | Sales | Exports | Rest | Share of supply |
|---|---|---|---|---|---|
| 2000 | 242.1 | 209 | 0 | 33.1 | 13.7 % |
| 2015 | 287.5 | 264 | 0 | 23.5 | 8.2 % |
| 2025 | 350.6 | 276 | 47 | 27.6 | 7.9 % |

The rest is grid losses and use the two tables leave apart; neither table names it.

## Requests (5 of 20)

| n | What | Outcome |
|---|---|---|
| 1, 2 | datos.energia.gob.ar's robots file, http and https | no answer |
| 3 | pxweb.asub.ax's robots address | 404 |
| 4 | MI010's metadata | 200 |
| 5 | MI010 (the POST, by the online trial) | 200 |

Reads recorded: 1369 to 1372.

## Decisions made without you

- **Run before sessions 2667 to 2669,** so that this chain's notes, Stanford draft and records include its table.
- **A second ASUB table as the third own choice,** after Argentina's portal did not answer; public under the verdict on record.
- **Rounding checks of 3 and 1.5 GWh,** the figures being whole GWh.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/asub_aland_sales.py`, `tests/test_session2670.py`, this report.
- Changed: the registration; the metadata files; the release package; the license record (reads 1369 to 1372) and `docs/licenses.md`.
- On the data machine only: `runs/c133/s2670/`, `runs/license_reads/s2670/`, `warehouse/raw/asub_ax/query_MI010.json`, `warehouse/output/asub_aland_electricity_sales_annual.csv`.
