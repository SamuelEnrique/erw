# Session 2608 report: New Caledonia's electricity from Enercal's activity report 2024-2025 (net production by plant, the public grid's purchases by source, transmission sales), internal, a source of the session's own choosing

25 October 2026, about 05:13 to 05:22 UTC, on lab-desktop (the data machine), chain 129, unattended. Precheck passed (`runs/c129/pre2608.out`). Model spend USD 0. Pulls: 12 requests of 20 (10 by the probe, 2 fetches; the connector reads the second offline).

## Why this source

- **The ERW held New Caledonia in no table but EIA's international one,** and no chain or queue file had taken it (the record, the queue and the unlanded chains' branches searched). Its grid is unusual: by the press's figures nickel smelters take two thirds of the territory's power, and by Enercal's the public grid's renewable share rose from 40% to 61% in three years.

## Read these first

- **The statistics office first:** ISEE's robots file allows the reader (read 1202), and its Nickel et energies page (read 1204) links `production-electricite.xls`, fetched once. But the workbook says it was updated on 6 August 2019 and its figures end in 2018, so it was not taken.
  - ISEE's Mentions legales (read 1205) forbid electronic reproduction without the director's express permission. **Verdict: needs written permission.**
- **The energy directorate's observatory** (observatoire-energie.gouv.nc, linked from DIMENC's home page, read 1207) answered HTTP 503 at its robots file: it is under maintenance for a security patch (read 1208). It is not closed; a later chain may ask again.
- **Enercal**, the territory's public generator and transmitter:
  - Its robots file names `*` with no rule (read 1209).
  - Its Mentions legales (read 1211) carry ISEE's clause word for word. **Verdict: needs written permission.** The table is **internal**.
- **The source:** Enercal's Rapport d'activite 2024-2025 (54 pages, 5.6 MB, last modified 19 January 2026). Its key-figure pages cover Enercal's years from July to June, 2022-2023 to 2024-2025:
  - page 21, "Enercal Producteur": net thermal and renewable production by plant, and Enercal Energies Nouvelles' renewable plants;
  - page 24, "Enercal Transport": the public distribution's purchases by source, and sales to the transmission network's clients.
- **A new table, `enercal_nc_electricity_annual`** (series, 83 rows, 30 entities, `power`): five blocks, each with its TOTAL. Each year is dated 1 July, with `x_period` giving the report's year. MWh is the report's GWh times 1,000.
  - The public distribution bought 683.6 GWh in 2022-2023 and 640.6 GWh in 2024-2025: coal 72.9, fuel 173.5, hydro 243.1, solar 119.3, wind 29.7 and biogas 2.1.
  - Enercal's own thermal production fell from 910.4 to 351.5 GWh after Doniambo closed.
  - Each block's rows add to its TOTAL within 0.2 GWh a year (the largest gap 0.1).
  - Written by run `20261025T051911Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T051919Z-local`), held from the live set and from Redivis (internal).
- **Not taken:** the metallurgists' sales outside the public distribution (one line split over several, with shares), network lengths, connections, the distributor's tables and the financial pages.

## Cross-checks

- EIA's world table (`eia_world_electricity_annual`, read past its header lines) gives New Caledonia 3,087 GWh of generation in 2022 and 2023 (the same figure both years) and 3,119 GWh in 2024. That includes the smelters' own plants, which Enercal's public figures leave out. The press reported the territory's consumption as 3,200 GWh a year from 2017 to 2023, against Enercal's public purchases of 620 to 684 GWh.
- Within the report: the purchases add to their TOTAL (2024-2025: 638.5 plus biogas 2.1 is 640.6). The biogas and Gadji Energie rows print one figure, and their totals place it in 2024-2025.

## Requests (12 of 20)

| n | What | Outcome |
|---|---|---|
| 1 to 4 | isee.nc's robots file, home page, Nickel et energies page and Mentions legales | 200 |
| 5 | ISEE's production-electricite.xls (a fetch) | 200, 119.8 kB, figures to 2018 |
| 6, 7 | dimenc.gouv.nc's robots file and home page | 200 |
| 8 | observatoire-energie.gouv.nc's robots file | 503, under maintenance |
| 9 to 11 | www.enercal.nc's robots file, home page and Mentions legales | 200 |
| 12 | Enercal's Rapport d'activite 2024-2025 (the fetch) | 200, 5.6 MB |

Reads recorded: 1202 to 1211.

## Decisions made without you

- **New Caledonia as the own choice,** and Enercal's report taken when ISEE's workbook proved stale.
- **Enercal's years dated 1 July,** with the report's label kept in `x_period`.
- **A "-" not written** (the report gives no key); a row of fewer figures given the last years, as its totals show.
- **Internal** under Enercal's Mentions legales.

## For Samuel's ruling

- **Whether to ask Enercal** (its publication director) for permission to publish the table. Its clause is ISEE's, so one letter's form would serve both.

## Files

- New: `warehouse/connectors/enercal_nc_electricity.py`, `tests/test_session2608.py`, this report.
- Changed: the registration; the metadata files; the license record (reads 1202 to 1211, ISEE's and Enercal's verdicts) and `docs/licenses.md`.
- On the data machine only: `runs/c129/s2608/`, `runs/license_reads/s2608/`, `warehouse/raw/isee_nc/`, `warehouse/raw/enercal_nc/`, `warehouse/output/enercal_nc_electricity_annual.csv`.
