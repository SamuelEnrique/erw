# LNG exports by terminal: volume and price, a month

Energy Research Warehouse (ERW), method note written in session 696 (chain 045) for a table first written on 25 September 2026.

Tables: `eia_lng_exports_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), U.S. Natural Gas Exports and Re-Exports by Point of Exit (LNG), through
EIA's API v2, route `natural-gas/move/poe2`. Document list: `https://api.eia.gov/v2/natural-gas/move/poe2/`. The data
address, as the rows keep it (decoded here; the key is written `REDACTED`):
`https://api.eia.gov/v2/natural-gas/move/poe2/data/?api_key=REDACTED&frequency=monthly&data[0]=value&sort[0][column]=period&sort[0][direction]=asc&sort[1][column]=series&sort[1][direction]=asc&offset=0&length=5000`
followed by one `facets[series][]=` for each of the 18 series the header names. Connector:
`warehouse/connectors/eia_series.py` (session 7). Page: `https://www.eia.gov/dnav/ng/ng_move_poe2_a_EPG0_ENG_Mmcf_m.htm`.

## Vintage and revision

Monthly. coverage.csv: 2013-11-01 to 2026-07-01, 1,083 rows, 17 series. Each run asks for the full history EIA offers.
The write merges into the file already there (`ip.write_csv`): a row with the same (entity, variable, ts_utc) takes
EIA's new value, and a row EIA no longer gives is kept. The header's own line says each run "replaces all of it"; that
holds only while EIA keeps every month. A table is not written if its newest month is more than 150 days old.

The connector states no request ceiling. It asks in pages of 5,000 records 0.5 seconds apart and tries a failed request
up to 4 times; the file read here holds one page address. Each response is saved under
`warehouse/raw/eia_series/<run>/`; the connector does not reuse a saved page.

The file on this machine is the run of 10 October 2026 (`20261010T143359Z`), restored from the Redivis draft by
`scripts/sync.py` (header, last line). coverage.csv names a later run, 2026-10-22T14:35:37Z, with the same 1,083 rows.

## Shape and variables

Series. `entity` `eia:<EIA series id>`, EIA's id unchanged: `NGM_EPG0_ENG_Y<terminal>-Z00_MMCF` for a volume,
`NGM_EPG0_PNG_Y<terminal>-Z00_DMCF` for a price. `ts_utc` the month's first day at 00:00:00Z, `freq` `P1M`, `geo` `US`
on every row, `market`, `node` and `vintage` blank. The variable follows the unit: `MMcf` is a volume, anything else a
price.

| Variable | Unit | EIA's series |
|---|---|---|
| `export_volume` | `MMcf` (million cubic feet) | `NGM_EPG0_ENG_Y<terminal>-Z00_MMCF`, for example "Sabine Pass, LA Liquefied Natural Gas Exports (Million Cubic Feet)" |
| `export_price` | `USD/Mcf` (dollars per thousand cubic feet) | `NGM_EPG0_PNG_Y<terminal>-Z00_DMCF`, for example "Price of Sabine Pass, LA Liquefied Natural Gas Exports (Dollars per Thousand Cubic Feet)" |

EIA's names for each series are in the header's "Series:" line.

The terminals, by the connector's codes, with what the CSV holds (counted from the CSV, header lines skipped):

| Code | Terminal | Volume rows | Volume months | Price rows | Price months |
|---|---|---|---|---|---|
| `SPL` | Sabine Pass, LA | 126 | 2016-02 to 2026-07 | 90 | 2016-02 to 2026-07 |
| `CRP` | Corpus Christi, TX | 92 | 2018-12 to 2026-07 | 56 | 2018-12 to 2026-07 |
| `CAM` | Cameron, LA | 86 | 2019-05 to 2026-07 | 55 | 2022-01 to 2026-07 |
| `FPT` | Freeport, TX | 82 | 2013-11 to 2026-07 | 54 | 2013-11 to 2026-07 |
| `CCPL` | Cameron (Calcasieu Pass), LA | 53 | 2022-03 to 2026-07 | 53 | 2022-03 to 2026-07 |
| `PLAQ` | Plaquemines, LA | 20 | 2024-12 to 2026-07 | 20 | 2024-12 to 2026-07 |
| `CPT` | Cove Point, MD | 100 | 2018-03 to 2026-07 | 64 | 2018-03 to 2026-07 |
| `ELBA` | Elba Island, GA | 73 | 2019-12 to 2026-07 | 55 | 2022-01 to 2026-07 |
| `GPT` | Golden Pass, TX | 4 | 2026-04 to 2026-07 | 0 | none |

No `x_*` fields.

As of 23 October 2026: 1,083 rows (636 `export_volume`, 447 `export_price`), 17 series, 9 terminals. July 2026 volumes:
Sabine Pass 120,445 MMcf, Plaquemines 100,810, Corpus Christi 97,129.

## License

Public: a work of the U.S. government. ERW verdict `public` (`docs/licenses.md`, "Every table": EIA, may be public,
flag and verdict agree). The header: "License: public domain (EIA)". Cite "U.S. Energy Information Administration,
U.S. Natural Gas Exports and Re-Exports by Point of Exit".

## Cross-check

None in the connector. It checks itself: a unit outside its map, a (series, period) given twice, a non-numeric value, a
series EIA returns nothing for, or a row count other than the total EIA reports stops the table.

Session 625 (`archive/sessions/SESSION_625_REPORT.md`) compared `eia_gas_trade_country_monthly`'s U.S. LNG exports with
this table's terminals summed by month, 132 months from November 2013: median ratio 0.999, from 0.980 to 1.382, never
equal. The two come from different EIA routes (by country, and by point of exit); the session did not look into the
difference.

## What it does not hold

- No Golden Pass price: the header names `NGM_EPG0_PNG_YGPT-Z00_DMCF`, but the CSV has no row of it. The run log of
  25 September 2026 (`warehouse/output/logs/eia_series_20260925T220528Z.log`) counted 3 of its months listed without a
  value.
- A month EIA lists without a value has no row. The header counts 189. The log of 25 September counted 188 then, all in
  price series: Sabine Pass 36, Corpus Christi 36, Cove Point 36, Cameron 31, Freeport 28, Elba Island 18, Golden Pass 3.
- Months inside a series' span with no row (counted from the CSV): Freeport volume 71 of 153 months, between 2013-12 and
  2023-01; Elba Island volume 7 (2020-02 to 2020-07, and 2021-01); Cameron volume 2020-09; Cove Point volume 2022-10. The
  prices of Sabine Pass, Corpus Christi and Cove Point have no month from 2019-01 to 2021-12; Freeport's price has 54 of
  153 months.
- No destination country (route `natural-gas/move/poe2` by point of exit only; countries are in
  `eia_gas_trade_country_monthly`), no pipeline or truck exports, no imports.
