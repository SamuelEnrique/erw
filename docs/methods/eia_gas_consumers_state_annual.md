# Natural gas consumers by state and sector

Energy Research Warehouse (ERW), method note written in session 862 (chain 046) for a table first written on 23 October 2026.

Tables: `eia_gas_consumers_state_annual`

## Publisher and address

U.S. Energy Information Administration (EIA), Natural Gas Annual, number of natural gas consumers, through EIA's API v2,
route `natural-gas/cons/num`:
`https://api.eia.gov/v2/natural-gas/cons/num/data/?frequency=annual&data[]=value` (the key is never written). Page:
`https://www.eia.gov/dnav/ng/ng_cons_num_dcu_nus_a.htm`. Connector: `warehouse/connectors/eia_gas_consumers.py`
(session 861).

## Vintage and revision

Annual, 1986 to 2024 when written. Retrieved 2026-10-23T02:20:47Z. A snapshot: each run replaces the table whole, so
EIA's revisions arrive at the next run with `--fresh` (pages saved in `warehouse/raw/eia_gas_consumers/` are reused
otherwise; `--offline` asks nothing). Ceiling 6 requests a run (pages of 5,000, 3 seconds apart). Session 861 made 6 of
its 20 requests; the write reused the trial's pages.

## Shape and variables

Series. `entity` `eia_gas_consumers:<EIA area>`: `NUS` the U.S., `S<state>` a state or DC. `ts_utc` the year's 1 January,
00:00:00Z; `freq` `P1Y`; `geo` `US-<state>` for a state, `US` for the U.S.; `node` EIA's series description. Variables
are EIA's process names ("Number of Residential Consumers" is `residential_consumers`). Every variable is a `count`.

| Variable | What it counts | Years when written | Rows |
|---|---|---|---|
| `residential_consumers` | residential consumers | 1986 to 2024 | 1,987 |
| `commercial_consumers` | commercial consumers | 1986 to 2024 | 1,987 |
| `industrial_consumers` | industrial consumers | 1986 to 2024 | 1,934 |
| `residential_consumers_sales` | residential, bought from a utility | 1997 to 2024 | 1,299 |
| `residential_consumers_transported` | residential, gas transported for them | 1997 to 2024 | 788 |
| `commercial_consumers_sales` | commercial, bought from a utility | 1998 to 2024 | 1,248 |
| `commercial_consumers_transported` | commercial, gas transported for them | 1998 to 2024 | 1,198 |
| `industrial_consumers_sales` | industrial, bought from a utility | 1998 to 2024 | 1,224 |
| `industrial_consumers_transported` | industrial, gas transported for them | 1998 to 2024 | 1,199 |

The U.S. row starts in 1987; the states start in 1986. A value EIA leaves empty has no row; nothing is filled. A unit
other than COUNT or MCF, or a key given twice, stops the run.

When written: 12,864 rows, 52 areas (the states, DC and the U.S.), 1986 to 2024. EIA's route gave 18,571 records; the
5,707 in MCF are left out (see below).

## License

Public: a work of the U.S. government (EIA's copyright page, record 1 of the license reads, `docs/licenses.md`). Verdict
in `docs/licenses.md`: public. Cite "U.S. Energy Information Administration, Natural Gas Annual".

## Cross-check (session 861)

- The states sum to EIA's U.S. row at a median of 1.0000 for all nine variables.
- The residential and commercial totals match exactly every year.
- Transported industrial consumers fall to 0.82 in one year (states that withhold the split).

## What it does not hold

- EIA's average consumption per consumer (unit MCF, 5,707 records): a ratio of two series the warehouse holds, left
  out and counted in the header. Consumption by state is in `eia_gas_consumption_state_monthly`.
- The sales and transported split before 1997 (residential) or 1998 (commercial and industrial).
- Any value EIA withholds; nothing is filled.
