# Electricity used a person, and the renewable share of electricity output, each economy a year (the IEA's figures as the World Bank's World Development Indicators republish them)

Energy Research Warehouse (ERW), method note written in session 2157 (chain 092) for a table first written on 23 October 2026 (session 2150).

Tables: `wb_iea_electricity_annual`

## Publisher and address

The World Bank, World Development Indicators, through its Indicators API v2 (no key), two indicators that the World Bank's metadata sources to the International Energy Agency's (IEA) Energy Statistics: EG.USE.ELEC.KH.PC, electric power consumption (kWh per capita), and EG.ELC.RNEW.ZS, renewable electricity output (percent of total electricity output). Three requests feed this table:

`https://api.worldbank.org/v2/country/all/indicator/EG.USE.ELEC.KH.PC?format=json&date=2000:2025&per_page=20000`

`https://api.worldbank.org/v2/country/all/indicator/EG.ELC.RNEW.ZS?format=json&date=2000:2025&per_page=20000`

`https://api.worldbank.org/v2/country?format=json&per_page=400` (the economies, to leave the aggregates out)

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `worldbank:wdi_iea_electricity`. Connector: `warehouse/connectors/wb_wdi_electricity.py` (session 2150), which also writes `wb_electricity_access_annual` (its own note). api.worldbank.org has no robots file (HTTP 404).

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2157), and `run_status.csv` holds no row for it. It was written by run `20261023T234510Z` and again, the same 8,220 rows, by run `20261023T234520Z` on the data machine, both reading the trial's saved answers.

## Vintage and revision

2000 to 2025 (`ts_utc` 1 January of each year): consumption a person to 2025, the renewable share to 2021 only. The answers were retrieved at 2026-10-23T23:43:36Z and 23:43:37Z by the session's trial and reused by the write runs; the rows' `vintage` is each answer's Last-Modified (2026-10-23T21:08:51Z for consumption, 12:45:37Z for the renewable share), times of the API's answer, not editions. The header gives the World Bank's last update of both indicators: 2026-10-08. `coverage.csv` gives the same 8,220 rows, 209 entities and the same first and last `ts_utc`.

Each run writes the whole table again (`ip.write_snapshot`), and every request is asked again unless `--offline`; a later World Bank update replaces every row.

## Shape and variables

Series, 8,220 rows, 209 economies, two variables. `entity` `wb:<ISO3>`; `freq` P1Y; `ts_utc` 1 January; `geo` the World Bank's ISO2 code; `market` empty; `node` the economy's name; `x_indicator` the World Bank's id; `x_region` and `x_income` the World Bank's groups. The aggregates have no row; an empty value has no row.

| Variable (indicator) | Unit | Rows | Economies | Years | Mean | Lowest | Highest |
|---|---|---|---|---|---|---|---|
| `electricity_consumption_per_person` (EG.USE.ELEC.KH.PC) | kWh/person (Decision 68) | 3,775 | 150 | 2000 to 2025 | 4,044.36 | 0 (South Sudan, 2000 to 2011, 12 rows) | 55,085.17 (Iceland, 2015) |
| `renewable_output_share` (EG.ELC.RNEW.ZS) | pct | 4,445 | 209 | 2000 to 2021 | 29.86 | 0 (372 rows) | 100.0 (30 rows: Andorra 16, Burundi 9, Bhutan 5) |

Consumption a person: 149 or 150 economies a year from 2000 to 2024 and 40 in 2025 (27 in Europe, Turkiye counted there, and Argentina, Australia, Brazil, Canada, Chile, Colombia, Costa Rica, Israel, Japan, Korea, Mexico, New Zealand and the United States); 40 economies hold all 26 years. In 2024 (149 economies) the mean was 4,303.5; the highest Iceland 49,241.2, Bahrain 23,845.7 and Norway 23,673.1; the lowest Chad 12.7, South Sudan 53.2 and Haiti 63.5. The United States: 13,671.1 in 2000, 12,385.2 in 2020 (its least), 12,933.7 in 2024 and 13,063.6 in 2025.

Renewable share: 197 to 206 economies a year, 188 holding all 22 years. In 2021 (204 economies) the mean was 34.0, one economy at 100 and two at 0. The United States rose from 8.81 (2000) to 20.27 (2021).

Two economies are here and not in the access table (American Samoa, Kosovo); eight there are not here. Namibia's `geo` is `NA` in the file, which a reader taking "NA" as missing loses. The counts were computed in session 2157 from the rows, read past the 10 header lines; no (entity, variable, ts_utc) is given twice.

## Checks the connector makes

- Before any request, api.worldbank.org is checked against `warehouse/metadata/paused_sources.csv` by connector and by host; a paused publisher stops the run with no request. It is not paused.
- The economies list must be one whole page; the aggregates (region "NA" in that list) are left out.
- Each indicator's answer must be one whole page; a row of another indicator, an economy given twice in a year, an indicator with no economy holding a value, or an (entity, variable, ts_utc) given twice stops the run, and nothing is written.
- A value the World Bank leaves empty has no row. Nothing is filled.
- Ceiling: four requests a run for the two tables (the economies and one an indicator), by the code's shape rather than a counter, all asked again unless `--offline`. Each address is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`); an HTTP 404 is not retried. One second after each request.

## The cross-check

Session 2150 set the United States' consumption a person against EIA's SEDS electricity sold to ultimate customers (ESTCB, at 3,412 Btu a kWh) over SEDS's population in `runs/c092/s2150/cross.py` (on the data machine, not in git). The ratio is 1.09 to 1.13 in every year from 2000 to 2024 (12,934 against 11,692 kWh in 2024); the report reads the steady gap as the IEA counting electricity that is not sold, such as industry's own generation used onsite, and says the check does not prove the cause.

## License

Internal. The header: "License: internal (the World Bank republishes these from the IEA's Energy Statistics, and its licence holds unless the metadata says otherwise; held until the IEA's terms are read). Cite the IEA, via the World Bank." `sources.csv` and `coverage.csv`: internal. Why: the World Bank's licence (read 141, CC BY 4.0) holds "unless indicated otherwise in the data or indicator metadata", and both indicators' metadata name the IEA's Energy Statistics as their source. Session 2153 read the IEA's verdict (read 60): it licenses the IEA's text, reports and standalone graphs under CC BY 4.0 and excepts standalone datasets, so the two indicators stay internal. `docs/licenses.md` lists the table under "Flagged internal; the sentence read allows it" (decided by the World Bank, "DISAGREES: the flag is stricter"), because `license_tables.csv` names only the World Bank as its publisher; the IEA's exception is what holds it. The table is in the live set's catalogue hold, not in the release's storage hold or the release package.

## Found while writing this note

- Nothing in the connector: the docstring, the header lines, the code and the rows agree. In the license record, `license_tables.csv` names the World Bank alone for this table, so `docs/licenses.md` reports the internal flag as stricter than the verdict; naming the IEA there too would let the record say why.

## What it does not hold

- The renewable share after 2021: the World Bank gives none.
- The IEA's own balances, generation by fuel, or consumption by sector.
- The World Bank's aggregates, and years before 2000.
