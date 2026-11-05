# Session 2765 report: Spain's dwellings by their electricity consumption, every municipality, 2021 census (INE)

25 October 2026, about 23:44 to 23:53 UTC, on lab-desktop (the data machine), chain 140, unattended. Precheck passed (`runs/c140/pre2765.out`). Model spend USD 0. Pulls: 13 requests of 15 (11 by the probe, 1 HEAD request to confirm the CSV export's address, 1 fetch of the file); two web searches.

## Read these first

- **INE's energy statistics are not in its Tempus API:** the energy consumption survey (ECE) and the physical energy flow accounts (CFFE) returned empty table lists by code, by IOE code and in Spanish (reads 1523 to 1526). That cost four requests; a fifth asked Tempus for table 59531, which is a JAXI table (read 1527, 404).
- **The one HEAD request** confirming the JAXI CSV export address was made with `requests` outside the probe, so it is not in the license record. It is counted here against the ceiling.
- **`ine_es_dwellings_electricity_2021`, public, held from the live set and in the Stanford holds** (`warehouse/connectors/ine_es_dwellings_electricity.py`, 58,626 rows, 3,257 areas, 18 variables):
  - From the 2021 Population and Housing Census, "Viviendas según su intensidad de uso" (JAXI tpx 59531, "dwellings by intensity of use from electricity consumption"), its CSV export (6.4 MB). INE updated the data on 22 November 2024.
  - For Spain, its 19 autonomous communities and cities, 52 provinces and 3,185 municipalities: total, empty, low-consumption and occasional-use dwellings, eleven consumption bands from 751 kWh to over 10,000 kWh (counts), and the median annual consumption (MWh per dwelling, INE's kWh divided by 1,000).
  - Spain: 26,623,708 dwellings, 3,828,307 empty, 941,637 of low consumption, 2,517,628 of occasional use; median annual consumption 2,196 kWh.
  - **Checked exactly, for every area, all passing:** the total equals the empty, low-consumption and occasional-use dwellings plus the eleven bands; occasional use equals its two bands; and every count of the nation, a community and a province equals the sum of its communities, provinces or municipalities.
  - Stamped 2021-01-01 (the 2021 census); the file states no year of consumption.
- **Cross-check** against `eurostat_electricity_consumption_annual` (Spain's households, 2021: 73,149 GWh). The bands give at least 49,731 GWh (each band at its lower edge, over 10,000 kWh at 10,001). The bands up to 10,000 kWh give at most 64,368 GWh, to which the 391,748 dwellings above 10,000 kWh add what they use. To reach Eurostat's figure, those dwellings would have to average about 22.4 MWh. (Corrected in session 2773: this report first gave 32 MWh, adding the 10,000 kWh twice.) The two measure different things: the census's metered dwellings, and the balance's household sector. Stated, not reconciled.
- **Terms and verdict:**
  - www.ine.es's robots file closes cgi-bin, search, test and admin paths and names no Claude agent (read 1519); ine.es serves the same file (read 1520). servicios.ine.es has none (read 1521).
  - INE's legal notice (read 1529, outcome exactly `read`): the statistical information is under CC BY 4.0, commercial use included, citing the authorship. **Verdict added: may be public** (`runs/c140/s2765_verdict.py`).
  - The header credits "Elaboración propia con datos extraídos del sitio web del INE: www.ine.es" with the update date, as the notice asks.
- **Written under the data lock:** validated, archived (58,626 rows), in coverage. The patch applied cleanly with no marker. Coverage has 605 tables and `sources.csv` 695 sources, none twice. `finish_table.sh`: the release and license checks pass (605 tables, 253 verdicts, 0 problems).

## Requests (13 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | www.ine.es's, ine.es's and servicios.ine.es's robots files (each its own request) | 200, 200, 404 |
| 4 | Tempus: the operations | 200, 166 |
| 5 to 8 | Tempus: ECE's and CFFE's tables (by code, IOE code, in Spanish) | 200, empty |
| 9 | Tempus: table 59531's groups | 404 |
| 10 | the JAXI table page for 59531 | 200 |
| 11 | INE's legal notice | 200 |
| 12 | a HEAD request for the CSV export (outside the probe) | 200 |
| 13 | 59531.csv (the fetch) | 200, 6,351,072 bytes |

Reads recorded: 1519 to 1529.

## Decisions made without you

- **A census table taken in place of an energy-balance one:** INE's energy tables are not in its API, and Red Eléctrica's national balance is held. This table is new to the ERW: residential electricity use, every municipality.
- **The median stated in MWh** (kWh / 1,000) rather than a new unit.
- **Stamped 2021-01-01, freq P1Y,** as the census's year.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/ine_es_dwellings_electricity.py`, `tests/test_session2765.py`, this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, the license record (reads 1519 to 1529, one verdict), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c140/s2765/`, `runs/c140/s2765_verdict.py`, `runs/license_reads/s2765/`, `warehouse/raw/ine_es/s2765hog/`.
