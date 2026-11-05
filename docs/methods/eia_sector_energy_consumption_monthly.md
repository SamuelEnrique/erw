# Industrial and commercial energy consumption, a month (EIA's Monthly Energy Review, Tables 2.3 and 2.4)

Energy Research Warehouse (ERW), method note written in session 2004 (chain 056) for a table first written on 27 September 2026 (session 18).

Tables: `eia_sector_energy_consumption_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), Monthly Energy Review (`https://www.eia.gov/totalenergy/data/monthly/`), Tables 2.3 (commercial sector) and 2.4 (industrial sector), through the EIA API v2's `total-energy` route (`https://api.eia.gov/v2/total-energy/data/`), frequency monthly, data `value`, the 14 series ids (`msn`) of `MER_SERIES` as facets, pages of 5,000 sorted by period and msn. Connector: `warehouse/connectors/eia_series.py` (session 18), beside `eia_primary_energy_monthly` (Tables 1.1 to 1.3, session 953); both share the source row `eia:total-energy`. The key comes from `EIA_API_KEY` and is shown as `REDACTED` in the address each row keeps in `source_url`.

## Vintage and revision

January 1973 to June 2026 in the file on the data machine. Its header: rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261019T211146Z-github`, from the connector's run `20261019T201827Z`; "Dates EIA lists without a value, omitted: 0". The rows' `retrieved_at` are 27 September 2026 (8,839 rows) and 30 September 2026 (149 rows).

Each run asks for the full history and `ip.write_csv` merges it on (entity, variable, ts_utc): a month EIA revises is replaced, and a row EIA stops giving is kept from an earlier run. The file's header line "every run replaces all of it" is the older wording; the code's header has said otherwise since session 865. A table whose newest month is more than 150 days old is not written.

## Shape and variables

Series, 8,988 rows: 14 series of 642 months each. `entity` `eia:<msn>`; `variable` `energy_consumption`; `unit` TBtu (EIA's trillion Btu, as published); `ts_utc` the month's first day; `freq` P1M; `geo` US; `node`, `market` and `vintage` empty (EIA's series names are in the header).

| Sector (MER table) | Series |
|---|---|
| Industrial (2.4) | TEICBUS total, TNICBUS end use, LOICBUS electrical system energy losses proportioned to the sector, ESICBUS electricity retail sales, NNICBUS natural gas (excluding supplemental gaseous fuels), PAICBUS petroleum, CLICBUS coal, REICBUS renewable energy |
| Commercial (2.3) | TECCBUS total, TNCCBUS end use, ESCCBUS electricity retail sales, NNCCBUS natural gas (excluding supplemental gaseous fuels), PACCBUS petroleum, RECCBUS renewable energy |

A total holds its parts: a sum takes one level.

## Reading the API

- The rows read must equal the total the API reports, or the table is not written; an empty answer stops it too.
- A unit not in the connector's map, or a (series, month) given twice, stops the table. Every row here is EIA's "Trillion Btu".
- A value that is not a number stops the table, except an empty value, "none" and "Not Available", which are omitted and counted (none here).
- The series are asked by facet (`msn`), not by series id, so the connector's check that each series asked for came back does not cover them (only an empty answer stops the table); all 14 are in the file.
- A page is tried up to four times; pages are 0.5 seconds apart.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`).

## Cross-checks (session 2004)

- The counts above were computed from the rows, read past the header lines.
- The industrial total is end use plus losses: TEICBUS equals TNICBUS plus LOICBUS within 0.001 TBtu in all 642 months (2025: 31,691.322 TBtu, against 26,651.193 plus 5,040.128).
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- The residential and transportation sectors, the commercial sector's coal, and the commercial sector's electrical losses as a series (its total less end use, 7,232.488 TBtu in 2025, is implied, not held).
- The Monthly Energy Review's other tables (primary energy is `eia_primary_energy_monthly`).
- Annual series: a year is the sum of its months, which this table leaves to the reader.
