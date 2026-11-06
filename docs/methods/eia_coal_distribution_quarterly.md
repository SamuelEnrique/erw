# Where the coal goes (EIA's Annual Coal Distribution Report)

Energy Research Warehouse (ERW), method note written in session 960 (chain 054) for a table first written on 23 October 2026.

Tables: `eia_coal_distribution_quarterly`

## Publisher and address

U.S. Energy Information Administration (EIA), Annual Coal Distribution Report (`https://www.eia.gov/coal/distribution/annual/`), its domestic distribution workbooks by origin state (`xls/o_<yy>state.xlsx`) and by destination state (`xls/d_<yy>state.xlsx`), the latest year the page links. Connector: `warehouse/connectors/eia_coal_distribution.py` (session 957). EIA's robots file allows `/coal/distribution/`.

## Vintage and revision

2024, final (released 19 November 2025, the workbooks last modified 30 October 2025); the 2025 report is due in October 2026. A snapshot (ceiling three requests, the page and the two workbooks; `--offline` reads the saved ones). The connector takes the latest year the page links, so a new report is taken without a change.

## Shape and variables

Series, 1,207 rows, 2024 by quarter. `entity` `eia_coal_flow:<origin>:<destination>:<consumer type>:<mode>`, slugs of EIA's words; `variable` shipments; `unit` short_ton; `ts_utc` the quarter's first day; `freq` P3M; `geo` US-<destination state>, US for EIA's U.S. rows; `x_*` the origin, destination, consumer type and mode as EIA writes them.

- Origins: EIA's 23 coal-origin states and regions (Kentucky (East) and (West), West Virginia (Northern) and (Southern), Pennsylvania (Anthracite) and (Bituminous) and the rest), and "U.S. (All States)".
- Consumer types: Electric Power Sector, Industrial Plants Excluding Coke, Coke Plant, Commercial/Institutional. Modes: Railroad, Truck, River, Tramway and Conveyor, Tidewater Piers.
- "U.S. (All States)" rows are EIA's total level: a sum takes one level.

## Reading the workbooks

- Headings must be as read; a destination not in the map, a quarter not 1 to 4, or a flow given twice stops the run.
- The destination workbook holds the same rows in another order and must agree row for row, or the run stops.
- Nothing is filled.

## License

Public: a work of the U.S. government (record 1 of `license_reads.csv`).

## Cross-checks (sessions 957 and 960)

- The U.S. rows sum to 393.9 million short tons, EIA's "total domestic coal distribution" for 2024; Wyoming's shipments 190.7 and Texas's receipts 45.7, as the report's highlights say.
- The electric power sector's shipments by destination state against `eia_coal_receipts_annual`'s 2024 plant receipts: within 5 percent in 29 of the 34 states above a million tons (Texas 45.5 in both; 354.6 and 351.5 million tons in all).
- Session 960, against the code and the table: the rows computed again; the header's one false line of the first write (about truncations) was removed by session 957 before its commit, and the table written again.

## What it does not hold

- Years before 2024 (the report's earlier editions), and foreign distribution (exports by producing state).
- Shipments by mine or by plant (the plant receipts are `eia_coal_receipts_annual`).
