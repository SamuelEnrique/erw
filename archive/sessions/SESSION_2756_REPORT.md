# Session 2756 report: Denmark's electricity supply a year from 1966 (Statistics Denmark's energy account), an own choice

25 October 2026, about 22:13 to 22:20 UTC, on lab-desktop (the data machine), chain 139, unattended. Precheck passed (`runs/c139/pre2756.out`). Model spend USD 0. Pulls: 7 requests of 20 (6 by the probe, 1 fetch of the extract, read offline by the trial and the write); one web search.

## Read these first

- **Why this source:** Statistics Denmark was in neither `sources.csv`, the license record nor any queue file, and the unlanded chains' records do not name it. Its StatBank has an open API, and its terms allow commercial re-use with credit. Its energy account reaches back to 1966, before Eurostat's 1990 and Energinet's hourly data.
- **`dst_dk_electricity_supply_annual`, public, held from the live set and in the Stanford holds** (`warehouse/connectors/dst_energy_account.py`, 360 rows):
  - From StatBank table ENE1HT, "Energy Account in specific units (detailed table)", supply, updated 18 June 2026, in one API request.
  - Six variables, each year from 1966 to 2025, in MWh (Statistics Denmark's GWh times 1,000): `electricity_total_supply`, `electricity_imports`, `electricity_production`, `wind_power_supply`, `hydro_power_supply`, `solar_power_supply`.
  - Denmark's production: 8,956 GWh in 1966, 24,012 in 1990, 33,038 in 2025. Wind: 610 GWh in 1990, 19,078 in 2025. Imports: 1,654 GWh in 1966, 26,249 in 2025.
  - **Checked exactly every year:** total supply = production + imports; each renewable's total supply = its renewable supply; the cells StatBank gives as 0 every year (imports and "total production" of wind, hydro and solar, and the renewable supply of electricity) are 0. Those are not written.
- **Cross-check** against `eurostat_electricity_production_annual` (Denmark, 1990 to 2024):
  - Wind (RA300), hydro (RA100) and solar photovoltaic (RA420): 102 of 105 year pairs agree within 0.5 GWh. The three that do not: wind in 2018 (Eurostat 13,902 GWh, Statistics Denmark 13,899) and 2022 (19,048 and 19,022), and solar in 2022 (2,385 and 2,203). Each publisher's revisions, stated here, not corrected.
  - Production against Eurostat's gross production: below it in 31 of 35 years, by 0.4 to 7.6 per cent (1990: 24,012 against 25,982 GWh; 2024: 34,474 against 35,318), and above it in 2011 to 2013 and 2017, by 1.0 to 6.6 per cent. **Corrected in session 2759:** this report first read the account's production as net of the plants' own use, which the four years above Eurostat's contradict; the reading is withdrawn.
- **Terms and verdict:** www.dst.dk's and dst.dk's robots files are the same file. It closes Sitecore, upload and Extranet paths, gives GPTBot a crawl delay, and names no Claude agent (reads 1498 and 1499). api.statbank.dk has no robots file (read 1500). The source references page (read 1501, outcome exactly `read`): "You are free to re-use and reproduce contents from dst.dk and statbank.dk. This includes even commercial use." It adds that this "corresponds to the license known as Creative Commons, CC 4.0 BY". **Verdict added: may be public** (`runs/c139/s2756_verdict.py`), crediting "Source: Statistics Denmark - StatBank.dk/ENE1HT".
- **Written under the data lock:** validated, archived (360 rows), in coverage. The patch applied cleanly, with no conflict marker. Coverage has 601 tables and `sources.csv` 691 sources, none twice. `finish_table.sh`: the release and license checks pass (601 tables, 251 verdicts, 0 problems).

## Requests (7 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | www.dst.dk's robots file (its own request) | 200 |
| 2 | dst.dk's robots file (its own request) | 200, the same file |
| 3 | api.statbank.dk's robots file (its own request) | 404 |
| 4 | the source references and terms page | 200 |
| 5 | StatBank's table list (API) | 200, 2,310 tables |
| 6 | ENE1HT's table information (API) | 200 |
| 7 | ENE1HT's extract, CSV (the fetch) | 200, 58,985 bytes |

Reads recorded: 1498 to 1503.

## Decisions made without you

- **The zero cells left out:** they stand for supplies that do not exist (wind is not imported). Each is checked to be 0.
- **Production not called net or gross:** neither file says (session 2759 withdrew this report's first reading, net).
- **Prices not taken:** ENERGI1 and ENERGI2 give household and non-household electricity prices in DKK, half-yearly. The ERW states prices in USD.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/dst_energy_account.py`, `tests/test_session2756.py`, this report.
- Changed: `build_coverage.py`, `release_v1.py`, `live_set.yaml`, `coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, the license record (reads 1498 to 1503, one verdict), `license_tables.csv`, `docs/licenses.md`, `docs/redivis/release-v1/`.
- On the data machine only: `runs/c139/s2756/`, `runs/c139/s2756_verdict.py`, `runs/license_reads/s2756/`, `warehouse/raw/dst_statbank/s2756ene1ht/`.
