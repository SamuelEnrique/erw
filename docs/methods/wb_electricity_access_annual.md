# Access to electricity, the share of each economy's people, a year (the World Bank, World Development Indicators, EG.ELC.ACCS.ZS)

Energy Research Warehouse (ERW), method note written in session 2157 (chain 092) for a table first written on 23 October 2026 (session 2150).

Tables: `wb_electricity_access_annual`

## Publisher and address

The World Bank, World Development Indicators, through its Indicators API v2 (no key). The indicator is EG.ELC.ACCS.ZS, access to electricity, percent of population, the World Bank's own SDG 7.1.1 electrification dataset. Two requests feed this table:

`https://api.worldbank.org/v2/country/all/indicator/EG.ELC.ACCS.ZS?format=json&date=2000:2025&per_page=20000`

`https://api.worldbank.org/v2/country?format=json&per_page=400` (the economies, to leave the aggregates out)

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `worldbank:wdi_electricity_access`. Connector: `warehouse/connectors/wb_wdi_electricity.py` (session 2150), which also writes `wb_iea_electricity_annual` from two more indicators (its own note). api.worldbank.org has no robots file (HTTP 404).

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2157), and `run_status.csv` holds no row for it. It was written by run `20261023T234510Z` and again, the same 5,350 rows, by run `20261023T234520Z` on the data machine (the header's "the previous file held 5350 rows"), both reading the trial's saved answers.

## Vintage and revision

2000 to 2024 (`ts_utc` 1 January of each year). The run asked 2000 to 2025; the World Bank gives no value for 2025. The answer was retrieved at 2026-10-23T23:43:34Z by the session's trial and reused by the write runs; the rows' `vintage` (the answer's Last-Modified, 2026-10-23T23:42:33Z) is the time the API answered, not an edition. The header gives the World Bank's own last update of the indicator: 2026-10-08. `coverage.csv` gives the same 5,350 rows, 215 entities and the same first and last `ts_utc`.

Each run writes the whole table again (`ip.write_snapshot`), and every request is asked again unless `--offline`. The World Bank revises the series when it updates the indicator; a later run replaces every row.

## Shape and variables

Series, 5,350 rows, 215 economies, one variable. `entity` `wb:<ISO3>`; `variable` `access_to_electricity`; `unit` pct; `freq` P1Y; `ts_utc` 1 January of the year; `geo` the World Bank's ISO2 code; `market` empty; `node` the economy's name; `x_indicator` EG.ELC.ACCS.ZS; `x_region` and `x_income` the World Bank's groups. The World Bank's aggregates (regions, income groups, the world) have no row; an empty value has no row.

| Variable | Unit | Rows | Economies | Mean | Lowest | Highest |
|---|---|---|---|---|---|---|
| `access_to_electricity` | pct | 5,350 | 215 | 81.81 | 0.8 (South Sudan, 2007) | 100.0 (2,127 rows) |

211 economies hold every year from 2000 to 2024; Guinea-Bissau has 23 years, South Sudan 18, Liberia 18 and North Korea 16. A year holds 211 economies in 2000 and 2001, 212 from 2002 to 2006, 214 in 2007 and 2008 and 215 from 2009.

| `x_region` | Economies | Mean 2000 | Mean 2024 | Lowest 2024 |
|---|---|---|---|---|
| East Asia & Pacific | 36 | 76.1 | 94.3 | 43.3 |
| Europe & Central Asia | 57 | 99.2 | 100.0 | 99.9 |
| Latin America & Caribbean | 42 | 88.9 | 97.5 | 53.9 |
| Middle East, North Africa, Afghanistan & Pakistan | 23 | 88.2 | 95.9 | 69.2 |
| North America | 3 | 100.0 | 100.0 | 100.0 |
| South Asia | 6 | 51.2 | 99.6 | 97.9 |
| Sub-Saharan Africa | 48 | 27.7 | 58.2 | 5.4 |

By income group in 2024: high income (85 economies) 99.9, upper middle (58) 97.5, lower middle (47) 80.8, low income (25) 46.0. In 2000, 52 of 211 economies were below half and 65 at 100; in 2024, 15 of 215 below half (South Sudan 5.4, Chad 13.4, Malawi 15.6 the lowest) and 122 at 100. The United States is 100 in every year. The counts were computed in session 2157 from the rows, read past the 10 header lines; no (entity, variable, ts_utc) is given twice.

A note for readers: Namibia's `geo` is the ISO2 code `NA`, written as such in the file. A CSV reader that takes "NA" as missing (pandas by default) loses it; read with `keep_default_na=False` or name the missing values.

## Checks the connector makes

- Before any request, api.worldbank.org is checked against `warehouse/metadata/paused_sources.csv` by connector and by host; a paused publisher stops the run with no request. It is not paused.
- The economies list must be one whole page (one page, and its total equal to its rows); the aggregates, whose region is "NA" in that list, are left out.
- Each indicator's answer must be one whole page; a row of another indicator, an economy given twice in a year, an indicator with no economy holding a value, or an (entity, variable, ts_utc) given twice stops the run, and nothing is written.
- A value the World Bank leaves empty has no row. Nothing is filled.
- Ceiling: four requests a run (the economies and one an indicator, three indicators for the two tables), by the code's shape rather than a counter, all asked again unless `--offline`. Each address is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`); an HTTP 404 is not retried. One second after each request.

## The cross-check

Session 2150's cross-check, `runs/c092/s2150/cross.py` (on the data machine, not in git), set the United States' consumption per person from the sister table against EIA's SEDS retail sales; for this table it counted 2024's economies (15 of 215 below half, 122 at 100) and found the United States at 100 in every year. No outside source was set against the access figures themselves.

## License

The header: "License: public (the World Bank: CC BY 4.0; see license_verdicts.csv). Cite the World Bank, World Development Indicators, and its SDG 7.1.1 electrification dataset." `license_verdicts.csv` gives the World Bank "may be public" (read 141, CC BY 4.0 "unless indicated otherwise in the data or indicator metadata"; the same if the ERW sells anything), and `docs/licenses.md` gives the ERW verdict public. `sources.csv` and `coverage.csv`: public. This indicator is the World Bank's own, so its licence holds (session 2153). Session 2150's report holds the table in the live set's catalogue hold and the release's storage hold, with the release package's rows.

## Found while writing this note

- Nothing: the docstring, the header lines, the code and the rows agree.

## What it does not hold

- The World Bank's regional, income group and world aggregates.
- The urban and rural splits of access (other indicators), and clean cooking access.
- Years before 2000.
