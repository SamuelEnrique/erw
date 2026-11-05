# The trader view's daily metrics, every grid's hubs in one table (ERW derived, from the ISO price tables)

Energy Research Warehouse (ERW), method note written in session 2228 (chain 099) for a table first written on 29 September 2026 (session 29). Its six members, `<iso>_trader_daily`, were first written on 27 September 2026 (session 19).

Tables: `iso_trader_daily`

The metrics' definitions and the page that reads them are in `docs/methods/trader_view.md` (session 19), written for the six tables this one replaced; the board's use of it is in `docs/methods/price_board.md` ("The week, by hub"). This note describes the consolidated table, the code and the rows as they stand.

## Publisher and address

No publisher is asked: the table is the ERW's arithmetic on tables the warehouse already holds. Source id `erw:trader_view`; `source_url` on every row is the method note, `https://github.com/SamuelEnrique/erw/blob/main/docs/methods/trader_view.md`. Two steps write it:

- `warehouse/derived/trader_view.py` (session 19) writes one member a grid, `ercot_trader_daily`, `caiso_trader_daily`, `nyiso_trader_daily`, `miso_trader_daily`, `spp_trader_daily` and `isone_trader_daily`, from the day-ahead and real-time tables its `ISOS` map names, and Henry Hub from `eia_fuel_spot_prices` (entity `eia:henry_hub`).
- `warehouse/consolidate.py build` (session 29) folds the six into `iso_trader_daily`, told apart by the column `market` (map: `warehouse/metadata/table_migrations.csv`, six rows dated 2026-09-29; `docs/migrations/2026-09-29-consolidation.md`), and moves the members to `warehouse/output/members/`.

| `market` | Day-ahead input | Real-time input | Operating day | Input sources, as the member's header lists them |
|---|---|---|---|---|
| caiso | `caiso_dam_hub_prices` | `caiso_rtm_hub_prices` | America/Los_Angeles | caiso:PRC_LMP; caiso:PRC_INTVL_LMP |
| ercot | `ercot_dam_hub_prices` | `ercot_rtm_hub_prices` | America/Chicago | ercot:NP4-190-CD; ercot:NP6-785-ER; ercot:NP6-905-CD |
| isone | `isone_dam_zone_prices` | `isone_rtm_zone_prices_hourly` | America/New_York | isone:da_lmp_hourly; isone:rt_lmp_hourly_final; isone:rt_lmp_hourly_prelim |
| miso | `miso_dam_hub_prices` | `miso_rtm_hub_prices` | EST (no daylight saving) | miso:da_expost_lmp; miso:rt_lmp_final; miso:rt_lmp_prelim |
| nyiso | `nyiso_dam_zone_prices` | `nyiso_rtm_zone_prices` | America/New_York | nyiso:damlbmp; nyiso:realtime |
| spp | `spp_dam_hub_prices` | none | America/Chicago | spp:DA-LMP-SL |

Every member also lists eia:natural-gas/pri/fut and eia:petroleum/pri/spt, the sources of `eia_fuel_spot_prices`. The `ercot_`, `caiso_`, `miso_` and `spp_` price tables are members of `iso_dam_hub_prices` and `iso_rtm_hub_prices`, which the consolidated header names in its "Derived from" line.

## Vintage and revision

The file on the data machine was rebuilt from the ERW archive by `warehouse/archive/restore.py` through the session 29 map, as of run `20261023T152740Z-github` (its first header line); the members' own headers name run `20261023T143736Z`. It holds 16,618 rows, 39 hubs and zones, 26 August to 24 October 2026:

| `market` | Hubs or zones | Operating days | First | Last | Rows |
|---|---|---|---|---|---|
| caiso | 3 | 59 | 2026-08-26 | 2026-10-23 | 1,428 |
| ercot | 6 | 59 | 2026-08-26 | 2026-10-23 | 2,856 |
| isone | 9 | 59 | 2026-08-26 | 2026-10-23 | 4,176 |
| miso | 8 | 39 | 2026-08-26 | 2026-10-03 | 2,408 |
| nyiso | 11 | 60 | 2026-08-26 | 2026-10-24 | 5,280 |
| spp | 2 | 58 | 2026-08-26 | 2026-10-23 | 470 |

- Each daily run (`warehouse/run_daily.sh`, step `trader_view`, then `consolidate.py build`) computes every day the price tables hold again and merges it by key: each member's header says this run wrote all its rows, "0 rows are kept from earlier runs".
- A row whose value has not moved keeps the `retrieved_at` of the run that first wrote it (`keep_retrieved`): the file holds 25 distinct times, from 2026-09-27T10:18:41Z (9,161 rows) to 2026-10-23T14:37:36Z.
- MISO ends on 3 October 2026: MISO is paused since 4 October 2026 (`warehouse/metadata/paused_sources.csv`), and `miso_dam_hub_prices` ends at 2026-10-04T04:00:00Z. Its days held are computed again from what is held.
- NYISO's last day, 24 October 2026, is the next day's day-ahead market, published before it; it has day-ahead metrics only.
- SPP has no row for 15 October 2026: `spp_dam_hub_prices` holds no whole day of it for either hub.
- `vintage` is empty on every row.

## Shape and variables

Series. `entity` is the price table's own (`<iso>:<node>`, for example `ercot:HB_HUBAVG`, `nyiso:N.Y.C.`, `isone:.H.INTERNAL_HUB`); `node` is the part after the colon on every row; `market` the member (above); `freq` P1D; `ts_utc` the local operating day at 00:00:00Z (Decision 11), on all 16,618 rows; `geo` and `vintage` empty; `source` `erw:trader_view`. No key (entity, variable, ts_utc) appears twice.

The consolidated header's shape line says "ts_utc is interval start, UTC" (written for every consolidated table by `warehouse/consolidate.py`, line 156). For this table that is not so: each member's header, and every row, give the local operating day at 00:00:00Z, a day label and not an interval start.

| Variable | Unit | Rows | Grids |
|---|---|---|---|
| `da_mean_usd` | USD/MWh | 2,150 | all six |
| `da_offpeak_mean_usd` | USD/MWh | 2,150 | all six |
| `da_onpeak_mean_usd` | USD/MWh | 1,516 | all six; weekdays that are not NERC holidays |
| `implied_heat_rate` | MMBtu/MWh | 2,150 | all six |
| `da_volatility_30d_usd` | USD/MWh | 964 | all six; from 25 September 2026 |
| `rt_mean_usd` | USD/MWh | 1,922 | all but SPP |
| `da_rt_spread_mean_usd` | USD/MWh | 1,922 | all but SPP |
| `da_rt_spread_max_usd` | USD/MWh | 1,922 | all but SPP |
| `hours_rt_over_da_50` | count | 1,922 | all but SPP |

Each variable's definition is in `trader_view.md` ("Daily metrics"). Over the days held, one hub of each grid:

| Hub or zone | Days | Mean `da_mean_usd` | Lowest | Highest | Mean `da_rt_spread_mean_usd` | Mean `implied_heat_rate` |
|---|---|---|---|---|---|---|
| ercot:HB_HUBAVG | 59 | 38.73 | 16.44 | 64.45 | 0.95 | 12.94 |
| caiso:TH_SP15_GEN-APND | 59 | 45.86 | 29.16 | 98.22 | -0.28 | 15.39 |
| nyiso:N.Y.C. | 60 | 45.21 | 34.26 | 60.61 | -1.68 | 15.10 |
| isone:.H.INTERNAL_HUB | 59 | 41.24 | 29.53 | 53.10 | -2.76 | 13.82 |
| miso:INDIANA.HUB | 39 | 57.40 | 32.70 | 125.05 | 16.69 | 19.60 |
| spp:SPPNORTH_HUB | 58 | 35.33 | 9.88 | 73.21 | none | 11.84 |
| spp:SPPSOUTH_HUB | 58 | 32.58 | -12.70 | 56.04 | none | 11.00 |

USD/MWh, and MMBtu/MWh for the heat rate. The hours in which real time ran more than 50 USD/MWh above day-ahead, summed over every hub and day: CAISO 24, ERCOT 148, ISO-NE 8, MISO 272, NYISO 231. The largest hourly real-time premium of each grid: MISO 7,209.33 (INDIANA.HUB, 17 September 2026), CAISO 1,067.87 (TH_SP15_GEN-APND, 26 August), NYISO 887.40 (N.Y.C., 16 October), ERCOT 613.26 (HB_NORTH, 16 September), ISO-NE 56.25 (.Z.CONNECTICUT, 18 September).

## Reading the source

- No request is made, so neither `iso_prices.paused()` nor `paused_host()` is asked; MISO's rows are computed from the prices held before its pause.
- A member whose day-ahead table is absent stops with `SourceGap` ("input table absent"), and so does one with no complete day; on the GitHub runner such a member is "skipped", elsewhere "failed", and the other grids are still written.
- A hub and local day is written only when the day-ahead table holds as many rows, at as many distinct times, as the local day has hours (24, or 23 or 25 on a clock change). A hub missing an hour writes nothing for that day.
- On-peak is a weekday that is not a NERC holiday and a local hour from 6 to 21 inclusive (hours starting 06:00 to 21:00); off-peak is every other hour.
- A 15-minute real-time table's hour is the mean of four distinct intervals; an hourly table's hour is read as it is. The four real-time metrics need a real-time hour for every day-ahead hour of the day. `hours_rt_over_da_50` counts a spread above 50, not equal to it.
- `implied_heat_rate` takes Henry Hub of the day or of the latest trading day up to 4 days before it, and only a price above zero. If `eia_fuel_spot_prices` cannot be read, no heat rate is written and the rest is.
- `da_volatility_30d_usd` needs `da_mean_usd` on all 31 consecutive days ending on the day: the sample standard deviation (`statistics.stdev`) of the 30 changes.
- Arithmetic is Python `Decimal` on the prices as held, rounded half up to 4 decimals.
- `keep_retrieved`: a value within 1e-9 of the previous file's keeps that row's `retrieved_at`.
- `consolidate.py build` stops the family, writing nothing, when the members' columns differ, when a member's `market` column holds a value other than the map's, or when the rows written differ from the rows read. A member not in `warehouse/output` is carried from the consolidated table as it was; with none to carry from, the build stops.
- The code counts no row ceiling.

## License

The header says "License: public. Every member declares it." Each member's flag is computed by `trader_view.py`: internal if any input source is internal in `sources.csv`, else public. `sources.csv` flags `erw:trader_view` public; its tables column names the six members and `iso_rt_top_intervals`, not `iso_trader_daily`. `license_tables.csv` lists the table under CAISO, ERCOT, ISO-NE, MISO, NYISO and SPP ("the grids its coverage row lists (a table of several operators' own prices)"). `license_verdicts.csv`:

| Publisher | Read | Verdict | If commercial |
|---|---|---|---|
| ERCOT | 2 | may be public | may be public |
| CAISO | 3 | may be public | may be public |
| ISO-NE | 4 | needs written permission | needs written permission |
| NYISO | 5 | needs written permission | needs written permission |
| SPP | 6 | may be public | needs written permission |
| MISO | 7 | needs written permission | needs written permission |

`docs/licenses.md` (line 826) therefore gives the table "needs written permission", decided by ISO-NE, MISO and NYISO, its coverage flag public, and the standing "ruled: license needed from 2026-10-21"; the ERW verdict is unsettled. The header's "public" and the verdict differ; this note changes neither.

## Cross-checks (session 2228)

- 16,618 rows, the sum the header gives of its members (1,428 + 2,856 + 4,176 + 2,408 + 5,280 + 470).
- `da_mean_usd` recomputed from `iso_dam_hub_prices` (CAISO, ERCOT, MISO, SPP), `nyiso_dam_zone_prices` and `isone_dam_zone_prices`, each hub's hours grouped by its grid's local day: all 2,150 rows agree within 0.0001 USD/MWh (the largest gap 0.00005, the rounding). Every hub and day those tables hold whole has a row (2,150), and no day they hold in part has one.
- `implied_heat_rate` recomputed as `da_mean_usd` over Henry Hub in `eia_fuel_spot_prices` (the day, or up to 4 days before): all 2,150 within 0.001 (largest gap 0.000067). `eia_fuel_spot_prices` holds Henry Hub to 20 October 2026, so the days after take that price.
- No `da_onpeak_mean_usd` row falls on a Saturday or Sunday, and none on Labor Day, 7 September 2026.
- Scripts: `trader_check.py` and `trader_check2.py` in the session's scratchpad, reading each table past its `#` lines.

## What it does not hold

- PJM: the ERW holds no PJM energy price table (`trader_view.md`).
- SPP's real-time metrics: the ERW has no SPP real-time table.
- MISO after 3 October 2026, while MISO is paused.
- Days before 26 August 2026, the first day of the price tables it reads.
