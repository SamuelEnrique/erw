# Henry Hub natural gas, WTI Cushing and Brent crude oil spot prices, a trading day (EIA)

Energy Research Warehouse (ERW), method note written in session 2018 (chain 057) for a table first written on 25 September 2026 (session 5).

Tables: `eia_fuel_spot_prices`

## Publisher and address

U.S. Energy Information Administration (EIA), through two routes of the EIA API v2, one series id each, frequency daily, sorted by period, pages of 5,000:

| Entity | Route | EIA series | EIA's report and page |
|---|---|---|---|
| `eia:henry_hub` | `natural-gas/pri/fut` | RNGWHHD | Natural Gas Spot and Futures Prices (NYMEX), daily, `https://www.eia.gov/dnav/ng/ng_pri_fut_s1_d.htm` |
| `eia:wti_cushing` | `petroleum/pri/spt` | RWTC | Spot Prices for Crude Oil and Petroleum Products, daily, `https://www.eia.gov/dnav/pet/pet_pri_spt_s1_d.htm` |
| `eia:brent` | `petroleum/pri/spt` | RBRTE | the same |

The address, as the rows keep it (decoded here): `https://api.eia.gov/v2/petroleum/pri/spt/data/?api_key=REDACTED&frequency=daily&data[0]=value&facets[series][]=RBRTE&sort[0][column]=period&sort[0][direction]=asc&offset=0&length=5000`, and the same with the other route and series. Source ids `eia:natural-gas/pri/fut` and `eia:petroleum/pri/spt`. Connector: `warehouse/connectors/eia_fuels.py` (session 5), its only table. The key comes from `EIA_API_KEY` and is written `REDACTED` in the address each row keeps.

## Vintage and revision

2 January 1986 to 20 October 2026 in the file on the data machine. Its header: rebuilt from the ERW archive by `warehouse/restore_tables.py` as of run `20261022T152428Z-github`, from the connector's run `20261022T143423Z`; "Dates EIA lists with no value, omitted: {'eia:henry_hub': 1, 'eia:wti_cushing': 0, 'eia:brent': 0}". The rows' `retrieved_at` are 29 September 2026 (27,702 rows), 30 September (15), 8 October (15), 19 October (19) and 22 October 2026 (15). `coverage.csv` gives the same 27,766 rows and dates.

Each run asks for each series' full daily history and `ip.write_csv` merges it into the file on (entity, variable, ts_utc): a day EIA revises is replaced, and a row EIA stops giving is kept from an earlier run. The connector's docstring and the header's line "every run replaces all of it" said otherwise; the code does not delete the file before it writes. Session 2018 corrected both in the connector; the file's header takes the new line at the next run. Each series' newest date must be within 10 calendar days of the run, or the table is not written.

## Shape and variables

Series, 27,766 rows: 3 series. `variable` `spot_price`; `ts_utc` EIA's trading date at 00:00:00Z, a date, not an instant (no Saturday or Sunday in the table); `freq` P1D; `market`, `node` and `vintage` empty.

| Entity | Unit | `geo` | Rows | Dates |
|---|---|---|---|---|
| `eia:wti_cushing` | USD/bbl | US-OK | 10,276 | 1986-01-02 to 2026-10-20 |
| `eia:brent` | USD/bbl | empty | 10,003 | 1987-05-20 to 2026-10-20 |
| `eia:henry_hub` | USD/MMBtu | US-LA | 7,487 | 1997-01-07 to 2026-10-20 |

Trading days only: a day without a price has no row. One value is negative, WTI on 20 April 2020 (-36.98 USD/bbl); the connector keeps it as EIA gives it. The highest: WTI 145.31 and Brent 143.95 on 3 July 2008, Henry Hub 30.72 on 23 January 2026. On 20 October 2026: Brent 115.22, WTI 107.89, Henry Hub 3.10.

## Reading the API

- Each series is read on its own; its rows must equal the total the API reports, or the table is not written.
- EIA's unit must map to the series' unit ("$/BBL" to USD/bbl, "$/MMBTU" to USD/MMBtu), or the table stops; a date given twice stops it.
- A value that is not a number stops the table, except an empty one, which is omitted, logged with its date and counted in the header (Henry Hub, 1: the first run's log names 5 January 2018, a date with no Henry Hub row and a WTI row).
- No ceiling is stated. A page is tried up to four times; pages are 0.5 seconds apart.

## License

The header has no license line; `coverage.csv` says public, and `docs/licenses.md` gives the ERW verdict public (EIA, "may be public"). EIA's own notices on these series, quoted in `docs/methods/price_board_v4.md`, name another party as the source: for the crude oil spot prices "Sources: Refinitiv, an LSEG business", and for Henry Hub "Spot Price: Refinitiv, an LSEG business." The prices are therefore Refinitiv's (LSEG's), republished by EIA. Session 127 (`archive/sessions/SESSION_127_REPORT.md`) held EIA's NYMEX futures back as internal on that kind of reading, left these tables public, and asked a person to rule on them too. EIA's general terms are record 1 of `license_reads.csv`.

## Cross-checks (session 2018)

- The counts above were computed from the rows, read past the 13 header lines; no (entity, variable, ts_utc) is given twice, and no date is a weekend.
- Days a year: 247 to 253 for each series in 2023 to 2025 (2025: Brent 253, WTI 248, Henry Hub 247), as for trading days; 2025's means are Brent 69.143, WTI 65.388 USD/bbl and Henry Hub 3.519 USD/MMBtu.
- WTI and Brent share 9,834 dates; 442 dates have WTI only and 169 Brent only. Brent less WTI on the shared dates: median -0.615 USD/bbl over the whole history, 4.33 since January 2025.
- The connector has no cross-check of its own beyond its reading rules.

## What it does not hold

- Futures: EIA's NYMEX futures are `eia_all_futures_prices` (internal). Refined products are `eia_product_spot_prices`.
- Other crude grades by the day: EIA publishes none (`eia_board.py`'s docstring, and session 127's report); monthly prices by stream are `eia_crude_stream_prices`.
- Days without a trade, and the Henry Hub day EIA lists with no value.
