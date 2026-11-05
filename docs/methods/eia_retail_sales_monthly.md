# Electricity sold to retail customers, and the customers, by state and sector, a month (EIA, Form EIA-861M)

Energy Research Warehouse (ERW), method note written in session 2004 (chain 056) for a table first written on 27 September 2026 (session 18).

Tables: `eia_retail_sales_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), Electric Power Monthly, retail sales of electricity and number of customers by state and sector (Form EIA-861M, `https://www.eia.gov/electricity/data/eia861m/`), through the EIA API v2 route `electricity/retail-sales` (`https://api.eia.gov/v2/electricity/retail-sales/data/`), frequency monthly, read twice: data `sales`, then data `customers`, each with no facet (every state and sector EIA lists), pages of 5,000 sorted by period, stateid and sectorid. Source id `eia:electricity/retail-sales`, shared with `eia_retail_electricity_prices`, which reads the same route's price. Connector: `warehouse/connectors/eia_series.py` (session 18). The key comes from `EIA_API_KEY` and is shown as `REDACTED` in the address each row keeps in `source_url`.

## Vintage and revision

January 2001 to July 2026 in the file on the data machine. Its header: rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261019T211146Z-github`, from the connector's run `20261019T201827Z`; "Dates EIA lists without a value, omitted: 205". Every row's `retrieved_at` is 29 September 2026.

Each run asks for the full history and `ip.write_csv` merges it on (entity, variable, ts_utc): a month EIA revises is replaced, and a row EIA stops giving is kept from an earlier run. The file's header line "every run replaces all of it" is the older wording; the code's header has said otherwise since session 865. A table whose newest month is more than 150 days old is not written.

## Shape and variables

Series, 228,203 rows, 744 series: 62 locations, 6 sectors and 2 variables.

| Variable | Unit | Rows | Series | Entity |
|---|---|---|---|---|
| `retail_sales` | MWh (EIA's million kWh times 1,000, exact) | 114,182 | 372 | `eia:retail_sales:<stateid>:<sectorid>` |
| `customers` | count, as EIA publishes it | 114,021 | 372 | `eia:customers:<stateid>:<sectorid>` |

- Locations: the 50 states and DC (`geo` `US-<state>`), US (`geo` US), and EIA's ten census divisions ENC, ESC, MAT, MTN, NEW, PACC, PACN, SAT, WNC and WSC (`geo` empty).
- Sectors: RES residential, COM commercial, IND industrial, TRA transportation, OTH other (EIA's older series), ALL all sectors.
- `ts_utc` the month's first day; `freq` P1M; `node`, `market` and `vintage` empty (EIA's names of the series are in the header).

The states sum to the U.S., the divisions hold their states, and ALL holds the sectors: a sum takes one level.

## Reading the API

- Each pass's rows must equal the total the API reports, or the table is not written; an empty answer stops it too.
- A unit not in the connector's map, or a (series, month) given twice, stops the table.
- A value that is not a number stops the table, except an empty value, "none" and "Not Available", which are omitted and counted (205 when written).
- A zero EIA gives is kept: 76,345 rows are 0. Every one of the 31,248 customer rows before January 2008 is 0, so the customer counts begin in January 2008. Transportation sales are 0 everywhere before January 2003, and OTH sales are not 0 only in 2001 and 2002; OTH customers are 0 in every month.
- A page is tried up to four times; pages are 0.5 seconds apart.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`).

## Cross-checks (session 2004)

- The counts above were computed from the rows, read past the header lines.
- The U.S. ALL row equals RES plus COM plus IND plus TRA plus OTH within 0.02 MWh in all 307 months.
- The 50 states and DC sum to the U.S. ALL row: December 2025, 337,715,726.94 MWh against 337,715,726.86; July 2026, 415,276,356.50 against 415,276,356.52. The U.S. sold 4,058,007,156.59 MWh in 2025, the twelve months summed.
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- The route's other data columns (its price is `eia_retail_electricity_prices`).
- Utilities: the utility-level monthly sales are `eia861m_utility_sales_monthly`.
- Months before 2001, and customer counts before 2008 (held as 0, not as counts).
