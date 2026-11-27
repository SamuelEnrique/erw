# Page files of energy equities (contract)

Written by session 10000 (chain 701, part B) on 26 November 2026, before any of these files holds data, so that window E (chain 720) can build `/equities` and the board's equities group against it. The shape is fixed here; which companies, indices and series fill it is part D's. A later change to the shape is one dated line in "Changes" at the foot of this file and one line in `docs/state/landing_request_portable.md` saying so.

Every file is written whole by its builder, from warehouse tables only; no builder makes a request. Builder: `warehouse/derived/equity_page_files.py` (part D4). Method: `docs/methods/equities.md`. Tables read: `equity_universe`, `equity_prices_daily`, `equity_fundamentals_quarterly`, `equity_index_daily`, and for the energy prices the warehouse's own price tables named in file 4.

## Rules every file follows

- **Dates.** A trading day is written `YYYY-MM-DD`, the exchange's own day (New York). Times of writing are UTC ISO 8601 (`built`).
- **Units.** Prices in USD per share (`USD/share`), volumes in shares, market value and statement lines in USD, shares outstanding in shares, index levels in index points (`points`). Each file's `units` object names the unit of every column.
- **Held values.** A value the ERW holds but may not show, or does not hold, is never left out and never a zero: the field is present, its value is `null`, and a `held` reason says why. For a whole column of a file: `held.<column>` is the reason, for example `"license needed: no source found whose terms allow the ERW to show daily prices (docs/reviews/equities-sources-2026-11-26.md)"`. For a whole series: `status` is one of `shown`, `license needed`, `source needed`, `not filed`, and `why` says why in plain words when it is not `shown`. The page draws a held value blank with the hover "license needed" (or the `why`).
- **Moves.** A move is `{"t": day compared against, "v": its value, "ch": last minus v, "pct": ch over v times 100, 2 decimals}`, `null` when the day compared against is not held. `d` the previous trading day held; `w` the last trading day on or before 7 calendar days back; `m` one calendar month back; `ytd` the last trading day of the previous year; `y` one calendar year back. These are the board's own moves (`site/data/board.json`, `rows[].moves`).
- **No score, no signal, no view.** The files carry levels and plain changes only.
- **Examples.** Until part D writes real data, each kind has one example file at its real path with `"example": true` and every value `null`. A page must show nothing from a file whose `example` is `true` but its blanks. Part D's builder writes `"example": false`.

## 1. `site/data/equities/index.json` (the list: companies and indices by segment)

| Key | Type | Unit | What |
|---|---|---|---|
| `built` | string | UTC | when written |
| `example` | boolean | | `true` only for the example file |
| `method`, `contract`, `license` | string | | `docs/methods/equities.md`, this file, and the license of the list itself (`public`: built from SEC EDGAR, a US government source) |
| `tables` | string[] | | the tables read |
| `last_day` | string or null | day | the newest trading day held in any shown price series |
| `segments[]` | object[] | | one a segment: `id`, `label`, `rule` (the written rule of `docs/methods/equities.md` that puts a company in it, in words), `n_companies` |
| `companies[]` | object[] | | one a company: `id` (the ticker, upper case), `cik` (the SEC's ten-digit number, a string), `name` (the SEC's name), `ticker`, `exchange`, `sic` (four digits, a string), `sic_label`, `segments` (one or more segment ids; a company that fits two rules is in both and `segments_note` says why), `segments_note` (string or null), `directory_id` (the matching row of `company_directory`, by SEC number or exact legal name, or null), `price_status`, `price_why`, `fundamentals_status`, `fundamentals_why`, `first`, `last` (first and last trading day of shown prices, or null), `file` (its path under `site/data/equities/`) |
| `indices[]` | object[] | | one an energy index or its published proxy: `id`, `name`, `publisher`, `kind` (`index` or `proxy`; a proxy says what it stands for in `proxy_for`), `proxy_for` (string or null), `status`, `why`, `first`, `last`, `file` |
| `segment_series[]` | object[] | | one a segment line (file 2 with `kind` `segment`): `id`, `segment`, `file` |

## 2. `site/data/equities/series/<id>.json` (one file a company, an index or a segment, with its daily series)

`<id>` is a company's ticker (`XOM.json`), an index's id (`index-<id>.json`) or a segment's id (`segment-<segment id>.json`).

| Key | Type | Unit | What |
|---|---|---|---|
| `built`, `example`, `method`, `contract`, `license` | | | as file 1; `license` is the series' own (`public`, or `internal` with `held`) |
| `id`, `kind`, `name` | string | | `kind` is `company`, `index` or `segment` |
| `cik`, `ticker`, `exchange`, `segments` | | | companies only (null for the others) |
| `status`, `why` | string | | the price series: `shown`, `license needed`, `source needed`; `why` null when shown |
| `source` | string | | the publisher and report in words, and the address |
| `units` | object | | the unit of every column of `daily_columns` and `quarterly_columns` |
| `held` | object | | `held.<column>`: why that column is null in every row (empty object when nothing is held) |
| `daily_columns` | string[] | | companies: `["day", "close", "adj_close", "volume", "market_value"]`; indices: `["day", "level"]`; segments: `["day", "equal_weight", "value_weight", "n", "n_value"]` |
| `daily[]` | array[] | | one row a trading day held, oldest first, in the order of `daily_columns`. `adj_close` null where the source prints none; `market_value` is close times the latest shares outstanding filed on or before the day, null where either is held. A segment's two lines are each 100 on its first day held: `equal_weight` the mean of its companies' daily returns chained, `value_weight` the same weighted by the day before's market value; `n` the companies in the equal-weight line that day, `n_value` those with a public share count in the value-weight line |
| `last` | object or null | | `{"t": day, "v": value}`, the last close (company), level (index) or `equal_weight` (segment) |
| `last_value_weight` | object or null | | segments only: the last `value_weight` |
| `moves` | object | | `d`, `w`, `m`, `ytd`, `y` as in the rules above, of `last`; a segment also has `moves_value_weight` |
| `quarterly_columns` | string[] | | companies only: `["period_start", "period_end", "months", "fy", "fp", "form", "filed", "revenue", "net_income", "capex", "debt", "shares_outstanding", "accession", "url"]` |
| `quarterly[]` | array[] | | companies only: one row a period as filed, newest first. `months` is 3, 6, 9 or 12 as the filing reports it (a 10-Q's cash flow is often year to date); a value not filed for that exact period is null. `debt` and `shares_outstanding` are the filing's figures at `period_end`. `url` is the filing's address on www.sec.gov |
| `concepts` | object | | companies only: for each statement column, the XBRL concept read (for example `"revenue": "us-gaap:Revenues"`) |

## 3. `site/data/equities/board.json` (the rows the price board shows)

The board's own row form (`site/data/board.json`, `rows[]`), so the board's components draw it as they draw the other rows.

| Key | Type | Unit | What |
|---|---|---|---|
| `built`, `example`, `method`, `contract` | | | as file 1 |
| `group` | object | | `{"id": "equities", "title": "Energy equities", "filters": [...]}` in the form of the board's `groups[]`, one filter `kind` (`segment`, `index`) |
| `sources` | string[] | | the publishers in words; a row's `source` is an index into this list |
| `rows[]` | object[] | | one a segment line (two rows a segment: `weighting` `equal` and `value`) and one an index: `id`, `group` (`equities`), `label`, `unit` (`index, first day = 100` for a segment, `points` for an index), `freq` (`D`), `tags` (`{"kind": "segment" or "index", "weighting": "equal", "value" or null}`), `source`, `status` (`ok`, `licensed`, `not_held`, the board's own words), `note` (why, when not `ok`), `basis` (the rule in words), `last` (`{"t", "v"}`), `moves` (`d`, `w`, `m`, `ytd`, `y`), `spark` (`{"t0": first day, "d": day offsets, "v": values}`, the last 90 trading days), `file` (its file 2) |

A row that is not `ok` carries `id`, `group`, `label`, `unit`, `tags`, `status`, `note` and no figures, as the board's held rows do.

## 4. `site/data/equities/energy_prices.json` (the energy prices set beside them)

| Key | Type | Unit | What |
|---|---|---|---|
| `built`, `example`, `method`, `contract` | | | as file 1 |
| `series[]` | object[] | | one an energy price: `id`, `label`, `unit` (as its table holds it: `USD/bbl`, `USD/MMBtu`, `USD/MWh`, `USD/lb`, `USD/tCO2`, ...), `freq` (`D`, `W` or `M`), `table` (the warehouse table), `entity`, `variable` (its row key there), `source` (publisher and report in words), `license`, `status`, `why`, `first`, `last`, `last_value` (`{"t", "v"}`), `moves` (as the rules above) |
| `daily.<id>[]` | array[] | | `[day, value]` oldest first, for the same span as the longest shown equity series; a monthly or weekly price is written on its own dates, never spread over days |

The prices named by the chain: WTI and Brent spot, Henry Hub spot, the power hubs a page may show, uranium, the carbon prices. A held price (a grid `docs/licenses.md` holds) is a series with `status` `license needed`, its `why`, and no `daily` rows.

## Examples

Pushed with this contract, each with `"example": true` and every value null, no price invented: `site/data/equities/index.json`, `site/data/equities/series/XOM.json`, `site/data/equities/series/segment-integrated_oil_gas.json`, `site/data/equities/series/index-example.json`, `site/data/equities/board.json`, `site/data/equities/energy_prices.json`.

## The date each file was last written

| File | Last written |
|---|---|
| all six examples | 2026-11-26 (session 10000, examples only) |

## Changes

- 2026-11-26 (session 10000): the first real files. Additions only, no field moved: `index.json` carries `held` (`companies`, `indices`, `prices`: why each list is empty) and each segment a `rule_why` beside its `rule` (null until the rule can be applied); `energy_prices.json` carries `since`. While no equity series is shown, a daily energy price is written from 2016-01-01 (the span of the longest shown equity series, once there is one). Why the equity side is empty: SEC EDGAR refuses the ERW's contact string and no free source of share prices may be kept (`docs/reviews/equities-sources-2026-11-26.md`); every board row is `not_held` with that reason and no file under `series/` is written by the builder (the four example files stay, marked `"example": true`).
- 2026-11-26 (session 10000, data requests 571 and 572 of window E): additions, no field moved. Each `companies[]` entry of `index.json` carries `last_close` (`{"t": day, "v": close}`), `moves` (`d`, `w`, `m`, `ytd`, `y`, as the rules above) and `market_value` (`{"t": day, "v": USD}`), each null where its price or share count is held. Each `ok` row of `board.json` carries the board's own `avg7` (`{"v", "n"}`), `avg30` (`{"v", "n"}`), `avg365` (`{"v", "n", "ch"}`), `lo30`, `hi30` (numbers) and `range` (`{"lo", "hi", "n", "pos"}`), in the forms of `site/data/board.json`; a row that is not `ok` has none of them. While the equity side is held (the line above) no company and no `ok` row exists, so neither file carries these fields yet; the builder writes them with the first company and the first shown row.
- 2026-11-26 (session 10000, data request 574 of window E): two values the files carry that the tables above did not name; additions, no field moved. In `energy_prices.json`, a series `status` may be `paused` (a publisher on warehouse/metadata/paused_sources.csv: MISO's prices, never requested while paused), beside `shown`, `license needed`, `source needed` and `not filed`, with its `why`; and `freq` may be `Q` (the carbon allowance, a quarterly auction) beside `D`, `W` and `M`. In `board.json`, a row's `file` is `null` when the row has no series file (every row while the equity side is held). A monthly or quarterly price's `moves.d` and `moves.w` (and a quarterly one's `moves.m`) are the change from the previous value held, as the price board's monthly rows are; the page says "monthly" or "quarterly" in those cells.
- 2026-11-27 (session 10000, chain 701, part D after the owner's ruling of 26 November): the companies are real (307, from SEC EDGAR by the written rule of `docs/methods/equities.md`), each with a series file whose prices are null with their reason and whose `quarterly` rows are the filed statements. Additions only: a company's series file carries `fundamentals_why` (null when its statements are shown); a segment no SEC code holds alone has `rule` null and its reason in `rule_why`; `held.companies` is null.
- 2026-11-27 (session 10000, chain 701, done-line requests 578 and 579): additions only. Each company of `index.json` carries `newest_filed` (null when nothing is filed): `period_end`, `form`, `filed`, `url`, `revenue`, `net_income` and `capex` each `{"months", "v"}` or null, `debt` and `shares_outstanding` each a number or null, by `newestOf`'s rule. `fundamentals_why` may hold a note while `fundamentals_status` is `shown` (a filer that stopped; a new registrant).
