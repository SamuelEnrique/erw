# Crude oil first purchase prices: Mars blend and North Dakota, a month

Energy Research Warehouse (ERW), method note written in session 696 (chain 045) for a table first written on 25 September 2026.

Tables: `eia_crude_first_purchase_prices`

## Publisher and address

U.S. Energy Information Administration (EIA), Domestic Crude Oil First Purchase Prices (by stream; by area), through
EIA's API v2, two routes:

- `petroleum/pri/dfp2` (by stream), series `F003075793`, Mars Blend. Document list: `https://api.eia.gov/v2/petroleum/pri/dfp2/`.
- `petroleum/pri/dfp1` (by area), series `F002038__3`, North Dakota, which the header calls a Bakken proxy. Document
  list: `https://api.eia.gov/v2/petroleum/pri/dfp1/`.

The data address, as the rows keep it (decoded here; the key is written `REDACTED`):
`https://api.eia.gov/v2/petroleum/pri/dfp2/data/?api_key=REDACTED&frequency=monthly&data[0]=value&sort[0][column]=period&sort[0][direction]=asc&sort[1][column]=series&sort[1][direction]=asc&offset=0&length=5000&facets[series][]=F003075793`,
and the same on `dfp1` with `facets[series][]=F002038__3`. Connector: `warehouse/connectors/eia_series.py` (the table
added in session 8). Page: `https://www.eia.gov/dnav/pet/pet_pri_dfp2_k_m.htm` (the header gives this one page for both
routes).

## Vintage and revision

Monthly. coverage.csv: 1977-07-01 to 2026-07-01, 860 rows, 2 series. Each run asks for the full history EIA offers. The
write merges into the file already there (`ip.write_csv`): a row with the same (entity, variable, ts_utc) takes EIA's
new value, and a row EIA no longer gives is kept. The header's own line says each run "replaces all of it"; that holds
only while EIA keeps every month. A table is not written if its newest month is more than 150 days old.

The connector states no request ceiling. It asks one route at a time, in pages of 5,000 records 0.5 seconds apart, and
tries a failed request up to 4 times. The file read here holds two page addresses, one a route. Each response is saved
under `warehouse/raw/eia_series/<run>/`; the connector does not reuse a saved page.

The file on this machine is the run of 10 October 2026 (`20261010T143359Z`), restored from the Redivis draft by
`scripts/sync.py` (header, last line). coverage.csv names a later run, 2026-10-22T14:35:37Z, with the same 860 rows.

## Shape and variables

Series. `entity` `eia:<EIA series id>`, EIA's id unchanged. `ts_utc` the month's first day at 00:00:00Z, `freq` `P1M`,
`geo` `US` on every row, `market`, `node` and `vintage` blank. `source` the route (`eia:petroleum/pri/dfp2` or
`eia:petroleum/pri/dfp1`).

| Variable | Unit | EIA's series | Rows | Months |
|---|---|---|---|---|
| `first_purchase_price` | `USD/bbl` | `F003075793` Mars Blend First Purchase Price (Dollars per Barrel) | 271 | 2004-01 to 2026-07 |
| `first_purchase_price` | `USD/bbl` | `F002038__3` North Dakota Crude Oil First Purchase Price (Dollars per Barrel) | 589 | 1977-07 to 2026-07 |

No `x_*` fields.

As of 23 October 2026: 860 rows, 2 series (counted from the CSV, header lines skipped). Neither series misses a month
between its first and last. Mars runs from 15.13 to 125.75 USD/bbl, North Dakota from 8.41 to 126.68. July 2026: Mars
82.76, North Dakota 76.30.

## License

Public: a work of the U.S. government. ERW verdict `public` (`docs/licenses.md`, "Every table": EIA, may be public,
flag and verdict agree). The header: "License: public domain (EIA)". Cite "U.S. Energy Information Administration,
Domestic Crude Oil First Purchase Prices".

## Cross-check

None in the connector. It checks itself: a unit outside its map, a (series, period) given twice, a non-numeric value, a
series EIA returns nothing for, or a row count other than the total EIA reports stops the table.

## What it does not hold

- Two series only: the other streams of `dfp2` and the other areas of `dfp1` are not asked for. `sources.csv` registers
  `dfp2`'s selected streams for another table, `eia_crude_stream_prices`.
- No daily or weekly price: EIA's first purchase price is monthly (session 7 asked for daily and weekly and left the
  Mars and Bakken items out for that reason).
- A month EIA lists without a value has no row. The header counts 12. The run log of 26 September 2026
  (`warehouse/output/logs/eia_series_20260926T001438Z.log`) puts all 12 in the Mars series.
