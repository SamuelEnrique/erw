# Session 2795 report: CPS Energy not taken (its robots file names Anthropic's agents); Austria's monthly electricity statistics in its place

26 October 2026, about 03:04 to 03:10 UTC, on lab-desktop (the data machine), chain 142, unattended. Precheck passed (`runs/c142/pre2795.out`). Model spend USD 0. Pulls: 7 requests of 15 (3 by the probe, 4 by the fetch).

## Read these first

- **CPS Energy not taken: its robots file bars the reader.** www.cpsenergy.com's and cpsenergy.com's robots files allow `/` to `*` with a Content-Signal of `ai-train=no`. They disallow `/` to ClaudeBot, anthropic-ai and Claude-Web by name, among other AI agents (reads 1594 and 1595). That is honoured, as the memory's rule for named AI agents asks; nothing else of CPS Energy was asked.
- **Another public grid source, as file 142 asks:** Statistics Austria's monthly electricity statistics, under that office's verdict (session 2764).
- **`statat_austria_electricity_monthly`, public, held from the live set and in the Stanford holds** (`warehouse/connectors/statat_electricity_monthly.py`, 793 rows, 12 entities, January 2023 to July 2026):
  - From the four yearly files MEle2023.ods to MEle2026.ods (the last compiled on 23 September 2026), each with two sheets in GWh. They are read by streaming with the standard library (session 2764's reader, copied into the connector).
  - `net_production` for the total and by source (conventional thermal and its five fuels, hydro with pure and mixed, wind, and solar from 2025), and the balance: imports and imports from the EU, exports and exports to the EU, pumped storage use, losses, and consumption. In MWh.
  - **Compared every month within 0.15 GWh:** the total against its sources, only in years whose file lists solar (2023's and 2024's do not, and their totals include it); conventional thermal against its fuels; hydro against pure and mixed; and the two sheets' totals. Two differences are kept as published: conventional thermal in May 2024 (0.2 GWh) and the summary sheet's total in May 2026 (45.9 GWh above the production sheet's).
- **Cross-check** against `econtrol_austria_electricity_monthly`: imports and exports **equal** E-Control's in every month compared (January 2023 imports 2,837.1 GWh; July 2026 2,584.2; exports 1,659.6 and 1,857.1). Statistics Austria compiles these files from E-Control's and Eurostat's statistics, so the table adds little beyond its own balance lines and the solar row.
- **Terms:** www.statistik.at's robots file asked again in its own request (read 1596), byte for byte as before. Statistics Austria's verdict (read 1518) covers the files; the license record shows the table as agreed, public.
- **Written under the data lock:** validated, archived (793 rows), in coverage. The patch applied cleanly with no marker. Coverage has 612 tables and `sources.csv` 702 sources, none twice. `finish_table.sh`: the release and license checks pass (612 tables, 0 problems).
- **This chain's four utilities gave no table,** as file 142 foresaw. SRP, Santee Cooper and NYPA publish no file the reader may take (NYPA's is on Open NY), and CPS Energy bars Anthropic's agents.

## Requests (7 of 15)

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.cpsenergy.com's and cpsenergy.com's robots files (each its own request) | 200, ClaudeBot, anthropic-ai and Claude-Web disallowed |
| 3 | www.statistik.at's robots file (its own request) | 200, as before |
| 4 to 7 | MEle2023.ods to MEle2026.ods (the fetch) | 200 each |

Reads recorded: 1594 to 1596.

## Decisions made without you

- **The replacement's overlap with E-Control stated,** rather than a less related source sought.
- **The total compared only where solar is listed.**

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/statat_electricity_monthly.py`, `tests/test_session2795.py`, this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, the license record (reads 1594 to 1596), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c142/s2795/`, `runs/license_reads/s2795/`, `warehouse/raw/statistik_austria/s2795mele*/`.
