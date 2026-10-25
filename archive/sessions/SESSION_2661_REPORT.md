# Session 2661 report: Iraq's electricity production by plant type, purchases, sales and losses a year, 2021 to 2024 (COSIT), internal

25 October 2026, about 10:16 to 10:24 UTC, on lab-desktop (the data machine), chain 133, unattended. Precheck passed (`runs/c133/pre2661.out`). Model spend USD 0. Pulls: 5 requests of 15 (4 by the probe, 1 fetch of the workbook into the raw store, which the trial and the write read offline).

## Read these first

- **The ERW held Iraq only in EIA's world tables;** no source or read named COSIT or the Ministry of Electricity.
- **The host:** cosit.gov.iq's robots file is Joomla's. It closes the system paths to `*`, `/images/` and `/media/` among them, and names no AI agent (read 1358). The electricity files sit under `/documents/`, which it leaves open; the PDFs under `/images/` were not asked.
- **The way in:**
  - The English home page guessed at `/en/` does not exist (read 1359).
  - The Arabic home page (read 1360) links the industry section's "water and electricity projects" page (read 1361).
  - That page gives a report and a workbook of the electricity projects statistics for each year from 2015 to 2024. The 2024 workbook, `6.xlsx`, was last modified on 23 February 2026.
- **The terms:** the footer reserves "the rights of the site's design and making" ("حقوق تصميم وتنفيذ الموقع محفوظة"), and no page read states terms of reuse for the statistics.
  - **Verdict: needs written permission,** read as ZIMSTAT's copyright line (session 2495).
  - The table is **internal**.
- **A new table, `cosit_iraq_electricity_annual`** (series, 56 rows, 14 entities, `power`), from the 2024 workbook's Tables 1 to 3. Each table is found by its English title and read by its English labels:
  - **Generation:** the Ministry's plants by type (steam, gas, diesel, hydro) and in all.
  - **Purchases:** the energy imported or bought from private (investment) plants, and that from the Kurdistan Region.
  - **Supply, sales and losses:** the system's total (`supply`), the energy sold to consumers (`sales`), and internal consumption and losses at plants and on the transmission and distribution networks (`losses`).
  - The values in dinars, the counts of plants and workers, and the rates of change are not taken.
- **Figures:**
  - In 2024 the system's total was 165.6 TWh: the Ministry's plants 96.6 (gas 58.3, steam 32.0), imports and investment 59.7, and the Kurdistan Region 9.3 (3.7 in 2023).
  - 67.5 TWh were sold, and internal consumption and losses came to 98.2, of them 82.0 on the distribution networks.
- **Checks:**
  - The plant types add to the energy generated, and the two purchases to their total.
  - Generated plus purchased equals the total, and the three losses add to theirs, each within 1 MWh, in every year.
  - Table 1 equals Table 2 where both give a row.
- **Its record:** written by run `20261025T102043Z` under the data lock and validated (exit 0). It is in coverage, archived (`20261025T102047Z-local`), held from the live set, and not in the release package (internal). Its method note is session 2667's.
- **Not taken:** the workbooks of 2015 to 2023, whose tables differ in form, and the tables by governorate and company (Tables 4 to 15).

## Cross-checks

Against `eia_world_electricity_annual`'s Iraq:
- **Hydro agrees:** 3.35, 2.65 and 1.38 TWh in 2021 to 2023 in both. For 2024 COSIT gives 3.49 and EIA 2.0.
- **Totals not comparable:** EIA's generation (149.7 TWh in 2024) counts private and Kurdistan plants as generation, while COSIT counts them as purchases with imports, so the totals cannot be compared directly.

## Requests (5 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | cosit.gov.iq's robots file | 200 |
| 2 | a guessed English home page | 404 |
| 3, 4 | the Arabic home page and the water and electricity projects page | 200 |
| 5 | `6.xlsx` (the fetch) | 200 |

Reads recorded: 1358 to 1361.

## Decisions made without you

- **Internal,** COSIT stating no terms of reuse.
- **The 2024 workbook alone** (2021 to 2024); the earlier workbooks are left for a later chain.
- **Investment plants' energy kept with imports** as COSIT gives it ("Imported energy + investment"), under the variable `purchases`.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/cosit_iraq_electricity.py`, `tests/test_session2661.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 1358 to 1361, COSIT's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c133/s2661/`, `runs/license_reads/s2661/`, `warehouse/raw/cosit_iq/`, `warehouse/output/cosit_iraq_electricity_annual.csv`.
