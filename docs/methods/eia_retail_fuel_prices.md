# US retail gasoline and diesel prices, weekly

Energy Research Warehouse (ERW), method note written in session 696 (chain 045) for a table first written on 25 September 2026.

Tables: `eia_retail_fuel_prices`

## Publisher and address

U.S. Energy Information Administration (EIA), Gasoline and Diesel Fuel Update (retail prices), through EIA's API v2,
route `petroleum/pri/gnd` (document list `https://api.eia.gov/v2/petroleum/pri/gnd/`). The rows cite the request:
`https://api.eia.gov/v2/petroleum/pri/gnd/data/?api_key=REDACTED&frequency=weekly&data[0]=value&...&offset=0&length=5000&facets[series][]=EMM_EPMR_PTE_NUS_DPG&facets[series][]=EMM_EPM0_PTE_NUS_DPG&facets[series][]=EMD_EPD2D_PTE_NUS_DPG`
(URL-encoded in the file; the key is never written). Connector: `warehouse/connectors/eia_series.py` (session 7), which
writes eleven other EIA tables as well. Page: `https://www.eia.gov/dnav/pet/pet_pri_gnd_dcus_nus_w.htm`.

## Vintage and revision

Weekly. Held from coverage.csv: 1990-08-20 to 2026-10-19, last run 2026-10-22T14:35:37Z. The daily run
(`warehouse/run_daily.sh`) runs the connector every day. Each run asks for the full history the API offers and replaces
all of it, so EIA's revisions arrive with the next run. The connector pages at 5,000 rows a request (2 requests for this
table today: offsets 0 and 5000) and fails if the rows it got differ from the total EIA reports. No request ceiling is
stated. A table whose newest date is more than 21 days old is not written. The `vintage` column is empty on every row.

The file on the data machine was rebuilt from the ERW archive by `warehouse/restore_tables.py` (its first header line).
The archive stores a row when a run finds it new or changed (ARCHITECTURE.md, section 1a), so `retrieved_at` holds six
times: 2026-09-29T01:02:32Z (4,994 rows, 1990-08-20 to 2024-08-19), 2026-09-29T01:02:34Z (328 rows, 2024-08-19 to
2026-09-21), and one week each on 2026-09-30, 2026-10-06, 2026-10-15 and 2026-10-22 (3 rows each).

## Shape and variables

Series. `entity` `eia:<EIA series id>`, the id unchanged. `ts_utc` the week-ending date EIA reports, at 00:00:00Z;
`freq` `P1W`; `geo` `US`; `market` and `node` empty; `source` `eia:petroleum/pri/gnd`. No x_* fields.

| Entity | EIA's name | Variable | Unit |
|---|---|---|---|
| `eia:EMM_EPMR_PTE_NUS_DPG` | U.S. Regular All Formulations Retail Gasoline Prices | `retail_price` | `USD/gal` |
| `eia:EMM_EPM0_PTE_NUS_DPG` | U.S. All Grades All Formulations Retail Gasoline Prices | `retail_price` | `USD/gal` |
| `eia:EMD_EPD2D_PTE_NUS_DPG` | U.S. No 2 Diesel Retail Prices | `retail_price` | `USD/gal` |

The unit is EIA's `$/GAL`, kept as published (no conversion).

As of 23 October 2026: 5,334 rows, 3 series, 1,882 weeks.

| Series | Rows | First week | Lowest | Highest | 2026-10-19 |
|---|---|---|---|---|---|
| Regular gasoline | 1,882 | 1990-08-20 | 0.907 (1999-02-22) | 5.006 (2022-06-13) | 4.284 |
| All grades gasoline | 1,751 | 1993-04-05 | 0.949 (1999-02-22) | 5.107 (2022-06-13) | 4.424 |
| No 2 diesel | 1,701 | 1994-03-21 | 0.953 (1999-02-22) | 6.529 (2026-09-21) | 6.276 |

Each series steps by 7 days, except regular gasoline from 1990-12-03 to 1991-01-21 (49 days). The header counts 6
dates EIA lists without a value, omitted; session 7's report names them as 6 weeks of retail regular gasoline.

## License

ERW verdict (docs/licenses.md, "Every table"): verdict today "may be public"; flag in coverage.csv "public"; flag and
verdict "agrees"; if the ERW sells anything "may be public"; ERW verdict "public". EIA's page (read 1): "U.S. government
publications are in the public domain and are not subject to copyright protection." EIA asks for "Source: U.S.
Energy Information Administration" with the date. Cite "U.S. Energy Information Administration, Gasoline and Diesel
Fuel Update", with the week used.

## Cross-check

None in the connector. It checks that every series it asks for comes back, that EIA's unit is the expected one, that no
(series, week) is listed twice and that no value is text; these are gates, not a comparison with another source.

## What it does not hold

- Only the three U.S. series the connector names. The route's other series (regions, states, cities, other grades and
  formulations) are not requested.
- No taxes, margins or price components.
- A week EIA lists without a value has no row; nothing is filled.
- No earlier vintages in the table: a revision replaces the value. Earlier values are in the archive.
