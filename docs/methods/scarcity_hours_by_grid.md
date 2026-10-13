# Each grid's own scarcity signal, hour by hour

Energy Research Warehouse (ERW), session 254 (13 October 2026). Table: `scarcity_hours_by_grid` (derived, series, hourly, public). Code: `warehouse/derived/scarcity_hours_by_grid.py`. No page reads it yet; the datacenter page's second question, "Will the power be there?" ([`datacenter_pays_algorithm.md`](datacenter_pays_algorithm.md), 4.15), is the reader it was built for.

## Why

- The page counts an hour as short when the price is at or above USD 1,000 per MWh: one level for every grid (the owner's ruling of 12 October 2026). That count says what the market did. It does not say what the grid's operator said.
- Each operator has its own signal. ERCOT priced scarcity through an adder on real-time energy; CAISO declares an emergency. This table sets the two side by side, hour by hour, so that a page can say "the price was above USD 1,000 in 12 hours; the operator's own signal was on in 759".
- Where a grid's own signal is not held as a table, it is not in this table: nothing is inferred from prices.

## The table

One row per grid, hour and variable. `entity` is `iso:<grid>`; `ts_utc` is the hour's start; `unit` is `count`; `freq` is `PT1H`.

| Variable | What it is | `x_detail` |
|---|---|---|
| `rt_intervals_ge_1000` | The hour's 15-minute real-time intervals priced at or above USD 1,000 per MWh at the grid's hub, 0 to 4 | `held=<n>`: the intervals of the hour the warehouse holds |
| `rt_hour_ge_1000` | 1 when the mean of the hour's held real-time intervals is at or above USD 1,000, else 0. This is the page's count for the real-time market | |
| `da_hour_ge_1000` | 1 when the hour's day-ahead price is at or above USD 1,000, else 0 | |
| `own_signal` | The grid's own scarcity signal: 1 in force, 0 not. Written only for an hour the signal is held for | ERCOT: `rtorpa_mean=<USD per MWh>`. CAISO: every notice in force in the hour, `<type>@<region>`, joined by `;` |

- **An hour without a row is not held. It is not a zero.** A reader counts zeros from rows.
- **The level** is USD 1,000 per MWh, `LEVEL` in the code, the page's `SCARCITY_USD`.

## The window

- The 36 whole months before the month of the run, in each grid's standard time: for the run of October 2026, October 2023 to September 2026, 26,304 hours a grid.
- Standard time, not the clock on the wall, as the page counts its months: ERCOT's hours run from `2023-10-01T06:00:00Z` (Central standard, UTC-6), CAISO's from `2023-10-01T08:00:00Z` (Pacific standard, UTC-8).
- The table is rebuilt whole each run; the window moves when the month changes.

## The price count

| Grid | Hub | Real time | Day ahead | Held from |
|---|---|---|---|---|
| ERCOT | `HB_HUBAVG` | `ercot_all_hub_prices_history` (to 26 August 2026), then `iso_rtm_hub_prices`; market `ercot_rtm`, 15-minute | the same history, then `iso_dam_hub_prices`; market `ercot_dam` | the whole window |
| CAISO | `TH_SP15_GEN-APND` | `iso_hub_prices_history`, then `iso_rtm_hub_prices`; market `caiso_rtm`, 15-minute | `iso_hub_prices_history`, then `iso_dam_hub_prices`; market `caiso_dam` | 1 September 2024 |

- An interval held by both tables is read once, from the history.
- Only ERCOT's and CAISO's rows of the three `iso_` tables are read.
- The hubs are those of findings 8 and 9 (`batteries_lunch_grids`, `peak_hour_grids`). The datacenter page counts its own region's price from its own files; this table's price rows are the hub's, for setting beside the signal, and do not replace the page's count.

## Each grid's own signal

### ERCOT: its reserve adder above zero

- `ercot_rtm_price_adders`, entity `ercot:system`, variable `rtorpa_mean`: the hour's time-weighted mean of the Real-Time On-Line Reserve Price Adder, the adder of the operating reserve demand curve ([`ercot_rt_price_adders.md`](ercot_rt_price_adders.md)).
- `own_signal` is 1 when that mean is above zero, else 0. The mean itself is in `x_detail`, so a reader can set a higher level without another table: the datacenter page counts the adder at or above USD 100, because most hours above zero are fractions of a cent.
- **Held to 4 December 2025 and no longer.** ERCOT published the adder from 1 June 2014 to 4 December 2025. No `own_signal` row is written for a later hour. The reliability deployment adder its file carries since then is another thing and is not joined.

### CAISO: an EEA or an alert in force

- `caiso_grid_emergencies` (CAISO's Grid Emergencies History Report, refreshed in this session; the report's revision of 9 October 2026).
- `own_signal` is 1 when one of these notices was in force in any part of the hour, for any region: an Energy Emergency Alert (`eea_watch`, `eea1`, `eea2`, `eea3`) or an alert (`flex_alert`; and `alert`, `warning`, `stage1` to `stage3`, CAISO's notices before May 2022, none of which falls in the window).
- **Not the signal:** restricted maintenance operations (`rmo`) and transmission emergencies. A restricted maintenance notice asks plants to put off maintenance; a transmission emergency is local. They are named in `x_detail` for the hours they were in force, and the row's value stays 0.
- A notice's hours are its own "from" and "through" times (Pacific clock time, as CAISO prints them), turned into UTC. A notice printed on each day it covers is read once.
- **Held for every hour of the window:** the report is CAISO's whole history to the day it was revised, so an hour before that day with no notice is a 0, not a gap.

### Not in the table

- **NYISO, ISO-NE, SPP, MISO.** Their own signal is reserve shortage pricing; no table of those hours is held. Their price tables need a license from 21 October 2026 or are held (`warehouse/metadata/license_status.csv`), so their price count is not here either. Adding a grid is one entry in `GRIDS`.
- **PJM.** No PJM price is held.

## What the first run holds (13 October 2026, window October 2023 to September 2026)

| | ERCOT (`HB_HUBAVG`) | CAISO (`TH_SP15_GEN-APND`) |
|---|---|---|
| Hours in the window | 26,304 | 26,304 |
| Real-time hours held | 26,304 | 18,191 (from 1 September 2024) |
| Real-time hours at or above USD 1,000 | 12 (49 intervals) | 1 (11 intervals in 6 hours) |
| Day-ahead hours at or above USD 1,000 | 22 (January 2024: 4; May 2024: 4; January 2026: 14) | 0 |
| Own signal: hours held | 19,097 (to 4 December 2025) | 26,304 |
| Own signal: hours in force | 759 (2023, from October: 136; 2024: 430; 2025: 193) | 7 (an EEA Watch, 24 July 2024, 17:25 to 23:59 Pacific) |
| Hours with any notice in force | | 578 |

- **ERCOT, the two counts together.** In the 19,097 hours with both held, the price was at or above USD 1,000 in 11 and the adder was above zero in 10 of those 11. The adder was above zero in 759 hours in all: the signal is on far more often than the price count, which is why the page uses USD 100 for it.
- **ERCOT's twelve months of the page** (October 2025 to September 2026): 1,558 hours of the adder held, 1 October to 4 December 2025, the figure the datacenter page prints; 44 of them above zero.
- **CAISO.** One hour at or above USD 1,000 in 25 months of prices (27 August 2026), and one EEA in 36 months. The two do not overlap: the EEA Watch of 24 July 2024 is before CAISO's prices are held.

## Checks

- The validator: `python warehouse/validate/erw_validate.py warehouse/output/scarcity_hours_by_grid.csv`, pass.
- `tests/test_session254.py`: the window in standard time; a notice's hours across midnight UTC and across a clock change; a notice repeated by day read once; restricted maintenance named and not counted; the adder's hours after its last one not written; an interval in both price tables read once; the counts above against the table on the data machine (skipped where the table is not).
- By hand: the EEA Watch of 24 July 2024, 17:25 to 23:59 Pacific daylight time, is 00:25 to 06:59 UTC on 25 July, seven hours starting 00:00 to 06:00 UTC: the seven rows with `own_signal` 1.

## License

Public. A derived table inherits the most restrictive license of its inputs: ERCOT (raw data in public parts of its site may be redistributed in compilations and analyses) and CAISO (its materials may be used with credit to the California ISO). Credit: California ISO, Grid Emergencies History Report; ERCOT.
