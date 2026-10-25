# Session 2622 report: Liechtenstein's electricity a year since 1985 (the Amt fuer Statistik's Energie 2025, Tabelle 5), public, a source of the session's own choosing

25 October 2026, about 06:47 to 06:55 UTC, on lab-desktop (the data machine), chain 130, unattended. Precheck passed (`runs/c130/pre2622.out`). Model spend USD 0. Pulls: 5 requests of 20 (4 by the probe, 1 fetch the connector reads offline).

## Why this source

- **The ERW held Liechtenstein in no table,** EIA's world table included, and no chain or queue file had taken it (the record, the queue and the unlanded chains' branches searched). It is a near-total importer of electricity, two thirds of its consumption in 2025.
- **Guam was tried first** (read 1254). The US territories are in no ERW table but EIA's world one, but the Guam Power Authority's site is a Wix site with no table in reach. Nothing more was asked of it.

## Read these first

- **The host:** www.statistikportal.li's robots file names `*` with no rule (read 1255). Its Energie topic page (read 1257) links the Energie 2025 tables workbook (published 1 July 2026) and the eTab tables.
- **The terms:** the workbook's Metadaten sheet (read 1258, recorded from the fetch as session 991 recorded a data file's sheet) states "Nutzungsbedingungen: CC BY 4.0". **Verdict: may be public.** The table is **public**, cited as the Office's.
- **A new table, `asli_liechtenstein_electricity_annual`** (series, 164 rows, 4 entities, `power`): domestic production (`generation`), imports, exports and domestic consumption, MWh, each year from 1985 to 2025.
  - In 2025: production 136,358.7 MWh, imports 271,226, exports 0, consumption 407,584.7 (66.5% imported).
  - Each year's production plus imports less exports equals consumption within 1 MWh.
  - Written by run `20261025T065201Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T065206Z-local`), held from the live set; in the release package (public). The Stanford draft is session 2625's.
- **2022 is printed twice.** The Office changed how it counts photovoltaic production in 2023 and gives 2022 by both methods, but the two rows are not labelled.
  - The first row is taken as the old method and the second as the new, the order of the table's own note ("nach der alten und neuen Methode").
  - 2022 is written with the new figures, as 2023 on are counted by them. The old ones are kept in `x_old_method_value` (production 100,496.2 against 103,291.9 MWh), and `x_pv_method` marks every year old or new.
- **Not taken:** Tables 6 to 19 (production by source, heat, photovoltaics and the other plants), the eTab tables (on another host, etab.llv.li).

## Cross-checks

- EIA's world table holds no Liechtenstein. Within the workbook, Table 5's note gives domestic production as the sum of photovoltaics, combined heat and power and hydro (Tables 6, 8 and 9); the check above is the table's own balance.

## Requests (5 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | guampowerauthority.com's robots file | 200 |
| 2 to 4 | www.statistikportal.li's robots file, home page and Energie page | 200 |
| 5 | the Energie 2025 tables workbook (the fetch) | 200, 113.7 kB |

Reads recorded: 1254 to 1258.

## Decisions made without you

- **Liechtenstein as the own choice,** after Guam's site proved out of reach.
- **2022's two rows read as old, then new,** by the note's order, and the new written.
- **Public** under the workbook's CC BY 4.0.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/asli_liechtenstein_electricity.py`, `tests/test_session2622.py`, this report.
- Changed: the registration; the metadata files; the release package (`docs/redivis/release-v1/`); the license record (reads 1254 to 1258, the Office's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c130/s2622/`, `runs/license_reads/s2622/`, `warehouse/raw/asli_li/`, `warehouse/output/asli_liechtenstein_electricity_annual.csv`.
