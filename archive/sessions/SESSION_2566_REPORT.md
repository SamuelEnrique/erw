# Session 2566 report: Peru's electricity production a month by department, 2005 to June 2026 (BCRPData, MINEM's figures), public, a source of the session's own choosing

25 October 2026, about 00:50 to 00:59 UTC, on lab-desktop (the data machine), chain 126, unattended. Precheck passed (`runs/c126/pre2566.out`). Model spend USD 0. Pulls: 11 requests of 20 (8 by the probe, 3 by the fetch the connector reads offline).

## Why this source

- **Peru, a market of 65 TWh a year, was held only in EIA's international table.** Chain 105's session 2296 could not read COES, whose files are listed only by its pages' POST scripts. No chain had taken BCRP, MINEM or INEI, and none of their hosts is on the closed list of file 126 (`license_verdicts.csv`, `warehouse/output/retired/` and the queue files read first).
- **INEI** was looked at first: www.inei.gob.pe serves its home page at the robots address (no robots file, read 1076), m.inei.gob.pe's certificate fails verification (read 1077), and a search found no table file of INEI's for electricity. MINEM's monthly "Estadistica Subsector Electricidad" is a PDF a month on gob.pe (its robots file allows the reader, read 1078).
- **BCRPData,** the central bank's statistics database, republishes MINEM's monthly production by department as 25 series in GWh from January 2005, through an API that answers ten series a request: three requests for the whole record.

## Read these first

- **The hosts:** estadisticas.bcrp.gob.pe has no robots file (HTTP 404, read 1079); www.bcrp.gob.pe's is Joomla's default (read 1080).
- **BCRP's terms** (read 1082, BCRPData's Condiciones de Uso): "Puede reproducirse total o parcialmente, sin autorizacion expresa, siempre y cuando se cite la fuente." (as printed, with its accent). The same page says that the responsibility for statistics from outside sources rests with the entity that provides them. **Verdict: may be public.** The table is **public**, citing BCRP and MINEM; its release rows are added to `docs/redivis/release-v1/`.
- **A new table, `bcrp_peru_electricity_monthly`** (series, 6,450 rows, 25 entities, `power`): `production` a month, January 2005 to June 2026, for the 24 departments and the total (series RD13043DM to RD13067DM, each row's code in `x_series_code`). In MWh (BCRP's GWh times 1,000), `ts_utc` the month's first day. The total for 2025 is 65.109 TWh; Lima produced 2,888 GWh of June 2026's 5,634. Written by run `20261025T005601Z` under the data lock, validated (exit 0), in coverage, archived (`20261025T005606Z-local`).
- **The departments and the total:** BCRP's departments add to its total within 10 GWh a month (0.22% at most, April 2021). The connector stops beyond 0.5% and keeps both as given.
- **Not taken:** the series' annual changes (RD13068DM to RD13092DM), which are computed from these.

## Cross-checks

- Against `eia_world_electricity_annual`'s Peru: 2019, EIA 56.864 TWh against BCRP's 56.967; 2023, 60.863 against 61.962; 2024, 59.303 (EIA's estimate) against 63.565.

## Requests (11 of 20)

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.inei.gob.pe's and m.inei.gob.pe's robots files | the home page served; a certificate failure |
| 3 | www.gob.pe's robots file | 200 |
| 4, 5 | estadisticas.bcrp.gob.pe's and www.bcrp.gob.pe's robots files | 404, 200 |
| 6 to 8 | BCRPData's list of the series, its Condiciones de Uso, its API page | 200 |
| 9 to 11 | the three API requests (the fetch) | 200, 50.1 kB, 53.1 kB and 28.3 kB |

Reads recorded: 1076 to 1083.

## Decisions made without you

- **BCRP's republication of MINEM's figures taken as public** under BCRP's own terms, which allow reproduction with the source cited; MINEM is cited as the original source.
- **The fetch saved each request under its own run name** (`s2566-fetch-1` to `-3`), after session 2562's manifest was overwritten by a second request under one name.

## For Samuel's ruling

- None new.

## Files

- New: `warehouse/connectors/bcrp_peru_electricity.py`, `tests/test_session2566.py`, this report.
- Changed: the registration; the metadata files; the release package (the table's rows); the license record (reads 1076 to 1083, BCRP's verdict) and `docs/licenses.md`.
- On the data machine only: `runs/c126/s2566/`, `warehouse/raw/bcrp_pe/`, `warehouse/output/bcrp_peru_electricity_monthly.csv`.
