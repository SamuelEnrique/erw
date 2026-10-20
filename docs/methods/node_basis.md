# The node: ERCOT's settlement points against the hub, by day and by month

Two derived public tables, `node_basis_daily` and `node_basis_summary`, built by `warehouse/derived/node_basis.py`
(session 358, the chain of 20 October 2026), and one internal table of hourly prices behind them,
`ercot_node_prices_hourly`. They answer the node item of three packs: the battery's item 4, the generator's item 5 and
the datacenter's item 6 (section 6 of each): every page prices at a hub or a zone, and a project is paid at its own
settlement point.

## The tables' shape (written before the tables, for the code machine)

### `node_basis_daily` (public)

Shape: `series`, one statistic a row (Decisions 39 and 44). Key `(entity, variable, ts_utc)`.

| Column | What it holds |
|---|---|
| `entity` | `ercot:<settlement point>` as ERCOT writes it: a resource node (`ABINDUST_RN`), a hub (`HB_HUBAVG`) or a load zone (`LZ_NORTH`) |
| `variable` | below |
| `ts_utc` | the ERCOT operating day (Central time) at `00:00:00Z` (Decision 11) |
| `value`, `unit` | the figure; `USD/MWh` or `count` |
| `freq` | `P1D` |
| `geo`, `market`, `node` | `US-TX`; `ercot_dam` for the day-ahead rows, `ercot_rtm` for the real-time rows; the settlement point |
| `x_hub` | the hub the basis is taken against: `HB_HUBAVG`, the hub average every economics page prices at (see "The hub" below) |
| `x_resource_type` | ERCOT's resource types at the point in the day's files, joined by `+` (`PWRSTR`, `ESR`, `PVGR`, `WIND`, `CCGT90`, `SCGT90`, ...); `HU` for a hub, `LZ` for a load zone |
| `x_class` | `storage`, `solar`, `wind`, `gas`, `other` (a resource node, by its types), `hub`, `zone` |

| Variable | What it is | Unit |
|---|---|---|
| `dam_mean`, `rtm_mean` | the mean of the day's hourly prices held (real time: an hour is the mean of its four 15-minute intervals, held only when all four are) | USD/MWh |
| `dam_spread_4h`, `rtm_spread_4h` | the mean of the day's four dearest hours less the mean of its four cheapest: what moving four hours a day could capture, before losses | USD/MWh |
| `dam_basis`, `rtm_basis` | the point's daily mean less `x_hub`'s daily mean over the same hours | USD/MWh |
| `dam_hours`, `rtm_hours` | the hours held that day (23 and 25 on the clock-change days) | count |

A day is written for a point only when every hour of the operating day is held for the point and for the hub in that
market. Nothing is filled.

### `node_basis_summary` (public)

Shape: `series`. Per hub, month and class of point: the distribution across points of each point's monthly mean basis
and monthly mean four-hour spread.

| Column | What it holds |
|---|---|
| `entity` | `ercot:HB_HUBAVG` (the hub) |
| `variable` | `<market>_<class>_<statistic>`, e.g. `dam_storage_basis_p50`, `rtm_all_spread_4h_p90` |
| `ts_utc`, `freq` | the first day of the Central month at `00:00:00Z`; `P1M` |
| `x_market` | `dam` or `rtm` |
| `x_class` | `all` (every resource node), `storage`, `solar`, `wind`, `gas`, `zone` (the load zones) |
| `x_stat` | the statistic, below |

| Statistic | What it is | Unit |
|---|---|---|
| `basis_p10`, `basis_p25`, `basis_p50`, `basis_p75`, `basis_p90` | percentiles across points of the point's mean daily basis over the month | USD/MWh |
| `spread_4h_p10` ... `spread_4h_p90` | the same of the point's mean daily four-hour spread | USD/MWh |
| `hub_spread_4h` | the hub's own mean daily four-hour spread over the same days | USD/MWh |
| `share_wider_pct` | the share of points whose mean spread is wider than the hub's | pct |
| `points` | the points counted | count |
| `days` | the days of the month the market holds for the hub | count |

A point counts in a month when it holds at least 90 percent of the days the hub holds in that market and month.
Percentiles are linear between order statistics (numpy's default), stated once here.

### `ercot_node_prices_hourly` (internal)

The hourly prices the daily table is computed from, within the owner's ceiling of 500,000 rows: hourly day-ahead and
real-time rows for the storage settlement points over the newest days that fit, `variable` `spp_dam` or `spp_rtm`,
`USD/MWh`, `PT1H`, `ts_utc` the hour's start in UTC. The rest of the hours are kept only in the saved files they were
read from, and `node_basis_daily` holds every point's day. Not loaded, not in the live set.

## The hub

The basis is taken against `HB_HUBAVG`, the hub average at which the battery and generator pages price ERCOT, for
every point. ERCOT assigns each resource node to a load zone and a hub in its settlement point list (NP4-160-SG); the
ERW does not hold that list, so a point's own zone and zonal hub are not written, and its coordinates are not held
either. Taking the list is a new source, a ruling for Samuel.
