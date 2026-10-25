# The node: ERCOT's settlement points against the hub, by day and by month

Tables: `node_basis_daily`, `node_basis_summary`, `ercot_node_prices_hourly` (session 2340, the third added by session 2389; as held on 24 October 2026, 965,943 rows over 888 points, and 1,260 rows of 168 variables, October 2025 to October 2026)

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

Session 2389: as held on 24 October 2026, 499,728 rows over 236 storage settlement points (`x_class` `storage` in every row, as in the daily table's classes), 19 July to 23 October 2026, under the ceiling of 500,000.

## The hub

The basis is taken against `HB_HUBAVG`, the hub average at which the battery and generator pages price ERCOT, for
every point. ERCOT assigns each resource node to a load zone and a hub in its settlement point list (NP4-160-SG); the
ERW does not hold that list, so a point's own zone and zonal hub are not written, and its coordinates are not held
either. Taking the list is a new source, a ruling for Samuel.

## Where the prices come from, and what cannot be had (session 358)

ERCOT's public lists keep its node prices for a short time: the real-time Settlement Point Prices (NP6-905-CD) for
seven days, the day-ahead Settlement Point Prices (NP4-190-CD) for 31 days. The prompt asked for twelve months to
30 September 2026 "through the existing connector's path"; that path cannot give them, and nothing was taken from
another place. What was had, without a new source:

- **Day-ahead at every resource node, from the 60-Day DAM Disclosure** (NP3-966-ER, `ercot_dam_esr.py`, whose list
  keeps about two and a half years): each resource's Settlement Point Name and its Energy Settlement Point Price by hour,
  in the files `60d_DAM_Gen_Resource_Data` and `60d_DAM_ESR_Data`. The disclosure comes 60 days after the operating
  day: on 20 October 2026 the newest is 20 August. This machine held 4 December 2025 to 5 August 2026; session 358
  saved 1 October to 3 December 2025 and 6 to 20 August 2026 (79 zips, 709 MB, within the connector's own 3 GB ceiling).
- **Day-ahead at every point, from the 31-day list** (NP4-190-CD, `ercot_rt_spp.py --pull-dam`, session 358): 20
  September to 20 October 2026.
- **Real time at every point, from the 15-minute files** this machine has saved daily since 28 September 2026
  (`ercot_rt_spp.py`, session 204), which hold every point.
- The hub's and the zones' day-ahead from `ercot_all_hub_prices_history` and `ercot_zone_prices_history`.

So the day-ahead covers 1 October 2025 to 20 October 2026 except **21 August to 19 September 2026** (the disclosure
has not reached those days and the 31-day list no longer holds them; they come in the disclosure from 21 October to
19 November), and the autumn clock-change day (2 November 2025: the disclosure does not mark its repeated hour). Real
time covers **28 September to 18 October 2026 only**. Twelve months of real time at the nodes cannot be had from
ERCOT's public lists at any ceiling.

Requests, session 358: 113 of the ceiling of 400 (the two lists of the 60-day and day-ahead reports, one probe of the
day-ahead list, 79 disclosure zips, 31 day-ahead files), at the connectors' own pace (2 and 1.5 seconds).

## How it is computed

- A point's day in a market: every hour of the Central operating day held (23 or 25 on the clock-change days), the
  hour's price as ERCOT printed it (day-ahead) or the mean of its four 15-minute prices (real time, an hour held only
  with all four). The mean, the four-hour spread (the mean of the four dearest hours less the mean of the four
  cheapest) and the basis (the point's mean less `HB_HUBAVG`'s, the hub's day held whole too).
- The points: every settlement point a resource of the disclosures is settled at (888 with the hubs and zones), the six
  hubs and the eight load zones. A point's class comes from ERCOT's resource types at it over the year: storage
  (`PWRSTR`, `ESR`), solar (`PVGR`), wind (`WIND`), gas (the combined-cycle, simple-cycle and steam types), other, and
  `mixed` where one point settles resources of two classes (a solar and storage pair at one node).
- The summary: per point, the month's mean daily basis and spread over the days it holds; a point counts when it holds
  at least 90 percent of the hub's days that month; then the percentiles across the points of a class, the hub's own
  mean spread, and the share of points whose spread is wider than the hub's over the point's own days.
- The internal hourly table: the storage points' hours, both markets, for the newest days under 500,000 rows (13 July
  to 19 October 2026 in the first build). It is ERCOT's prices reshaped, read from the saved files; no ERW table is
  read, so coverage does not mark it derived (its tier is derived by rule), and it is licensed internal by the owner's
  rule.

## The first build (20 October 2026)

`node_basis_daily` 949,995 rows over 888 points; `node_basis_summary` 1,260 rows; `ercot_node_prices_hourly` 498,360
rows. The figures of the twelve months (day-ahead, 1 October 2025 to 30 September 2026, 335 days with the hub whole),
per point the mean over its days, against `HB_HUBAVG`, USD per MWh:

| Points (held 90 percent of the days) | Basis, 10th / median / 90th | Four-hour spread, median | Wider than the hub |
|---|---|---|---|
| every resource node (786) | -5.63 / 0.18 / 5.38 | 50.97 | 65.4 percent |
| storage (195) | -4.07 / 1.31 / 5.78 | 49.31 | 57.4 percent |
| solar (125) | -5.22 / 0.09 / 5.40 | 52.74 | 80.0 percent |
| wind (165) | -7.88 / -3.79 / 4.06 | 53.18 | 74.5 percent |
| gas (195) | -2.70 / 1.36 / 4.77 | 47.62 | 52.3 percent |
| the eight load zones | 0.71 / 2.22 / 4.68 (`LZ_SOUTH` 0.07 to `LZ_CPS` 4.78; `LZ_NORTH` 0.98) | 51.09 | 6 of 8 |

The hub's own four-hour spread over those days: 47.26. Real time, 28 September to 18 October 2026 (20 days): the
hub's spread 50.75; storage points' median spread 62.08 (76.3 percent wider than the hub), median basis 3.14. Over
the one week the battery pack quoted (28 September to 4 October), the storage points' median real-time spread is 44.11
against the pack's 44.29 (the pack's figure took 16 dearest and cheapest 15-minute intervals, this table four hours of
hourly means).

    python warehouse/connectors/ercot_rt_spp.py --pull-dam
    python warehouse/connectors/ercot_dam_esr.py --pull --days <the operating days>     # probe mode: saves the zips, writes no table
    python warehouse/lock.py run --task node -- <python> warehouse/derived/node_basis.py --from 2025-10-01
