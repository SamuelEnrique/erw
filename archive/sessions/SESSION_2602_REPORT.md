# Session 2602 report: the Solomon Islands' electricity production by station, 2017 to 2025 (Solomon Power's Annual Report 2025), internal; queue file 130 written first

25 October 2026, about 04:42 to 04:55 UTC, on lab-desktop (the data machine), chain 129, unattended. Precheck passed (`runs/c129/pre2602.out`). Model spend USD 0. Pulls: 6 requests of 15 (5 by the probe, 1 by the fetch the connector reads offline).

## First: the next file

- **`queue/next/130-day-30-november-data-liberia-gambia-palau-chad.md`** (sessions 2616 to 2629) written by `runs/c129/write_130.py` from this chain's file (its rules word for word, the four source sessions' countries changed, every session number moved by 14) and pushed to main as `6ad032f2` before any other work. Its before and after snapshots: 0 differences. Session 2615 updates it.

## Read these first

- **The statistics office is closed to the reader:** www.statistics.gov.sb's certificate fails verification (read 1169); nothing was asked of it again.
- **The utility's hosts:** www.solomonpower.com.sb and solomonpower.com.sb serve one robots file naming `*` with a crawl delay of 10 seconds, closing only the site's system paths (reads 1170 and 1172); the delay was kept. The Annual Reports page lists the reports for 2010 to 2025 (read 1173).
- **The terms** (read 1171, the home page): its footer reads "© 2026 | Solomon Islands Electricity Authority"; the site links no terms, privacy or copyright page, and the Annual Report 2025 states no terms of reuse (searched). A copyright line with no reuse statement, read as ZIMSTAT's (session 2495). **Verdict: needs written permission.** The table is **internal**.
- **The source:** Solomon Power's Annual Report 2025 (68 pages, 6.27 MB, last modified 23 September 2026), page 15's table "Energy Produced", in GWh, by station for 2017 to 2025.
- **A new table, `siea_solomon_electricity_annual`** (series, 49 rows, 6 entities, `power`): Lungga, Honiara, the outstations, Henderson solar (1 MW) and the total for each of nine years, and Ranadi solar (50 kW) for 2022 to 2025 (its years printed "Not Available" are not written). The total grew from 93.34 GWh in 2017 to 118.00 GWh in 2025; Lungga made 101.10 GWh of 2025's. MWh as the report's GWh times 1,000. Each year's stations add to its total within 0.1 GWh (the largest gap 0.042 in 2022, exactly Ranadi's figure, and 0.015 in 2023, also Ranadi's: the total seems to leave Ranadi out in those two years; 0.04 in 2017). Written by run `20261025T045248Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T045306Z-local`), held from the live set and from Redivis (internal).
- **Not taken:** the page's peak demand (19,296 kW in 2025, one figure for Honiara, not a series), the report's sales and financial tables.

## Cross-checks

- EIA's world table (`eia_world_electricity_annual`, read past its header lines) gives the Solomon Islands' total generation as 106.0 GWh in 2017 and 111.8 GWh in 2024, against Solomon Power's 93.34 and 110.92. EIA's figure is the country's, Solomon Power's its own grids only; the gap narrows from 12.7 GWh to 0.9 over the years.
- Within the report: the text's 102.51 GWh for Lungga and Honiara in 2025 is the table's 101.10 plus 1.41; its 2.82 GWh for Henderson and Ranadi is 2.68 plus 0.14.

## Requests (6 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.statistics.gov.sb's robots file | SSLError, the certificate fails |
| 2 | www.solomonpower.com.sb's robots file | 200 |
| 3 | its home page (redirected to solomonpower.com.sb) | 200 |
| 4 | solomonpower.com.sb's robots file | 200 |
| 5 | the Annual Reports page (after the crawl delay) | 200 |
| 6 | the Annual Report 2025 (the fetch, after the crawl delay) | 200, 6.27 MB |

Reads recorded: 1169 to 1173. Test 205's bound raised by 40 for chain 129's reads (from 1169).

## Decisions made without you

- **Internal** under a copyright line with no reuse statement.
- **Ranadi's "Not Available" years left out**, not written as zero.

## For Samuel's ruling

- **Whether to write to Solomon Power for permission to publish the table** (the page read names no person or address). Held internal until then.

## Files

- New: `warehouse/connectors/siea_solomon_electricity.py`, `tests/test_session2602.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 1169 to 1173, Solomon Power's verdict), `docs/licenses.md`, test 205's bound.
- On the data machine only: `runs/c129/s2602/`, `runs/license_reads/s2602/`, `warehouse/raw/siea_sb/`, `warehouse/output/siea_solomon_electricity_annual.csv`.
