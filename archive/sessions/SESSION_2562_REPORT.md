# Session 2562 report: the Maldives' electricity, the public sector's production by island a month (2025) and Male's use by sector (2009 to 2025), NBS's yearbook, internal

25 October 2026, about 00:18 to 00:26 UTC, on lab-desktop (the data machine), the third session of `queue/done/126-day-26-november-data-eswatini-burkina-faso-maldives-suriname.md`, unattended. Precheck passed (`runs/c126/pre2562.out`). Model spend USD 0. Pulls: 9 requests of 15 (7 by the probe, 2 by the fetch the connector reads offline).

## Read these first

- **The ERW held no source for the Maldives** but EIA's international table.
- **The hosts:** statisticsmaldives.gov.mv's robots file closes /mbs/wp-admin/ only (read 1059); www.ura.gov.mv has no robots file (read 1060); www.stelco.com.mv answers its robots file with a Cloudflare challenge (HTTP 403, read 1061) and was not asked again.
- **NBS's terms:** none found. The yearbook's page, the home page and the Statistics Act and Regulation page state nothing on reuse (reads 1062 to 1064), and the Maldives Statistics Act (Act 16/2021, its English translation, read 1065) speaks of disseminating statistics to the public with equal access but grants no reuse. **Verdict: needs written permission** (RGGI's precedent: no license stated, ask). The table is **internal**.
- **The source:** two workbooks of NBS's Statistical Yearbook of Maldives 2026 (last modified 11 June 2026), both from STELCO: table 12.2, "Monthly Electricity Production by Public Sector, 2025" (35 islands), and table 12.1, "Electricity Utilization in Male', 2010 to 2025" (its columns start at 2009).
- **Table 12.2's unit:** its heading says "In '000 kWh", but its cells are kWh (K.Male' would otherwise have made 324 TWh in 2025). The connector reads them as kWh and checks it: the Greater Male' islands' production (777.8 GWh) must fall between one and three times Male's use in table 12.1 for the same year (450.3 GWh, 1.73 times); a workbook corrected to thousands would stop the run.
- **A new table, `nbs_maldives_electricity`** (series, 505 rows, 40 entities, `power`): `production` a month for 35 islands in 2025 (907.1 GWh in all; Hulhumale 437.3, Male' 324.1, Maafushi 19.7, Vilimale' 16.4, Thilafushi 10.5), and `utilization` a year in Male' by sector, 2009 to 2025 (the total 187.1 GWh in 2009, 422.3 in 2024, 450.3 in 2025, of which residential 252.5). In MWh, `ts_utc` the month's or year's first day, `x_table` the table. Each island's months checked against its total, and 12.1's sectors against its total. Written by run `20261025T002414Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T002418Z-local`), held from the live set and from Redivis (internal).
- **Not taken:** 12.2's Total column (each island's months add to it), 12.1's shares and changes, the fuel and lubricating oil tables (12.3, 12.4), Male's consumption table (12.5), the water tables.

## Cross-checks

- Against `eia_world_electricity_annual`'s Maldives: EIA's generation 855.1 GWh in 2024 (consumption 829.0), against NBS's 907.1 GWh of public-sector production in 2025, a year later; the order of size agrees (the resorts' own generation is not in NBS's table).

## Requests (9 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | statisticsmaldives.gov.mv's, www.ura.gov.mv's and www.stelco.com.mv's robots files | 200, 404, 403 (Cloudflare) |
| 4, 5 | the yearbook 2026's page, NBS's home page | 200 |
| 6, 7 | the Statistics Act and Regulation page, the Act's English translation | 200 |
| 8, 9 | tables 12.1 and 12.2 (the fetch) | 200, 31.9 kB and 17.2 kB |

Reads recorded: 1059 to 1065.

## Errors and fixes

- The fetch script, run once a workbook under one run name, rewrote the raw manifest on its second run, so table 12.1's row was lost though its file was saved; the offline trial stopped on it ("not in warehouse/raw/nbs_mv/"). The row was put back from the response the fetch had printed (its time, status and last-modified header), with the saved file's size and hash computed from the file. No second request was made.

## Decisions made without you

- **Table 12.2 read as kWh** against its heading, with the check against table 12.1 that stops the run if the cells change unit.
- **One table, two frequencies** (the month's production, the year's use), as other ERW tables hold, the table of each row in `x_table`.
- **Internal,** no terms of reuse found.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/nbs_maldives_electricity.py`, `tests/test_session2562.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 1059 to 1065, NBS's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c126/s2562/`, `warehouse/raw/nbs_mv/`, `warehouse/output/nbs_maldives_electricity.csv`.
