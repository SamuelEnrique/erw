# Coal production by state, coal rank and mine type

Energy Research Warehouse (ERW), method note written in session 685 (chain 044) for a table first written on 22 October 2026.

Tables: `eia_coal_production_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), Annual Coal Report, state aggregates (Form EIA-7A and MSHA Form 7000-2),
through EIA's API v2, route `coal/aggregate-production`:
`https://api.eia.gov/v2/coal/aggregate-production/data/?frequency=annual&data[]=production&data[]=number-of-mines&data[]=average-employees&start=2001`
(the key is never written). Connector: `warehouse/connectors/eia_coal_production.py`. Page: `https://www.eia.gov/coal/annual/`.

## Vintage and revision

Annual, 2001 to 2024 when written (EIA's route ends at 2024). A snapshot: each run replaces the table whole, so EIA's
revisions arrive at the next run with `--fresh` (a page saved in `warehouse/raw/eia_coal_production/` is reused
otherwise; `--offline` asks nothing). Ceiling 8 requests; session 685 used 2 (the trial) and the write reused them.

## Shape and variables

Series. `entity` `eia_coal_production:<stateRegionId>:<coalRankId>:<mineTypeId>`, EIA's codes: states (`WY`), EIA's
regions (`PRB` the Powder River Basin, `APP` Appalachia, `INT` the Interior, and others) and `US`; ranks `BIT`, `SUB`,
`LIG`, `ANT` and `TOT` (all ranks); mine types `SUR`, `UND`, `REF` (refuse recovery) and `ALL`. `ts_utc` the year's
1 January, `freq` `P1Y`; `geo` `US-<state>` for a state, `US` otherwise; `node` EIA's names.

| Variable | Unit | EIA's column |
|---|---|---|
| `production` | `short_ton` (2,000 lb; Decision 50) | `production` |
| `mines` | `count` | `number-of-mines` |
| `employees` | `count` | `average-employees` |

When written: 22,630 rows, 422 series.

## License

Public: a work of the U.S. government (EIA's copyright page, record 1 of `license_reads.csv`). Cite "U.S. Energy
Information Administration, Annual Coal Report".

## Cross-check (session 685)

The states' all-rank, all-mine production against EIA's U.S. row, every year: 99.75 to 99.95 percent (the rest is
production EIA does not place in a state); the ranks' sum against the U.S. total: exactly equal each year. The U.S. in
2023: 578.0 million short tons; in 2024: 512.5 million.

## What it does not hold

- No mine-level rows (route `coal/mine-production`), no shipments, no reserves.
- EIA's labor hours and productivity (short tons per labor hour): the vocabulary's `hour` is an hour of the day, not a
  quantity of work.
- A figure EIA withholds has no row; nothing is filled.
