# Stress days of the grids (session 306)

The table `grid_stress_days`, built by `warehouse/derived/stress_days.py` from tables the ERW already holds. No request is made to any publisher. The chain prompt names it `stress_days`; a series table's name has three parts (`docs/datastandard.md`, Decisions 19 and 47). The rule is the code machine's session 297, `docs/methods/battery_stress_days.md`; this note says how the data machine applies it.

Tables: `grid_stress_days`

## Why a rule

Before session 306 the repository recorded two ways of naming a stress day, one per grid: ERCOT's are three named events (Winter Storm Uri, Winter Storm Elliott, the August 2023 heat; `warehouse/derived/event_window.py`), and CAISO's are the days of its own system-wide notices (`docs/methods/battery_stack.md`, session 246). Neither reaches the other five grids. The chain prompt of 19 October 2026 gives the rule for all of them, the one the code machine's session 297 writes:

> A local day is a stress day on a grid when the day's mean real-time price at the grid's main hub is above the 98th percentile of the daily means of the 365 days before it, or when the operator issued an emergency notice that day.

## How it is applied

| Part | What is done |
|---|---|
| The main hub | The price board's (`price_board.py` `MAIN`): ERCOT HB_HUBAVG, CAISO SP15, NYISO N.Y.C., MISO Indiana Hub, SPP North Hub, ISO-NE Internal Hub |
| The day | The grid's own local day (ERCOT and SPP Central time, CAISO Pacific, NYISO and ISO-NE Eastern, MISO Eastern Standard) |
| The day's mean | ERCOT: `ercot_hub_prices_daily`'s `rt_mean` at HB_HUBAVG (from 2015; that table leaves a short day out). The others: the mean of the hub's real-time intervals in `iso_hub_prices_history`, only for a day with every local hour held (session 297: "a day with any hour missing is not tested"; a day at a clock change has 23 or 25 hours) |
| The threshold | The 98th percentile of the daily means held among the 365 days before the day, the day itself left out, and only when at least 329 of those days (nine tenths) are held. Before that a day is judged by the notice test alone |
| The notices | CAISO's (`caiso_grid_emergencies`): the system-wide kinds of session 246 (a Flex Alert, Restricted Maintenance Operations, an Energy Emergency Alert watch or level 1 to 3, a Stage 1 to 3 emergency, a Warning, an Alert, a load interruption). A Transmission Emergency and a voluntary load reduction do not count. No other operator's notices are held |
| The events | Stress days at most three days apart are one event (`x_event`), named for its first day (`<grid>_stress_<YYYYMMDD>`), except that an event holding a day of a named event's window keeps that name: `uri_2021` (7 to 24 February 2021), `elliott_2022` (19 to 29 December 2022), `ercot_heat_2023` (1 August to 10 September 2023), as `event_window.py` sets them |
| What is written | One row per grid and stress day, on days the grid's prices are held: the day's mean, the reason (price, notice, or both), the threshold and the days it was taken over, and CAISO's notice kinds |

PJM has no row: the ERW holds neither a PJM hub price (PJM's data is licensed) nor a PJM notice.

## What the rule gives (built 19 October 2026, session 322)

| Grid | Days held | Judged by price from | Stress days | By price | By notice | Events |
|---|---|---|---|---|---|---|
| ERCOT | 2015-01-01 to 2026-10-14 | 2015-11-26 | 169 | 113 | 79 (`ercot_grid_notices`, session 322; 113 and 64 events before) | 74 |
| CAISO | 2023-07-06 to 2026-10-18 (from 2023-07-14 until session 307; the fall-back days of 2023 to 2025 filled in session 322) | 2024-05-30 | 58 | 24 | 36 | 25 |
| NYISO | 2024-09-01 to 2026-10-18 | 2025-08-15 | 10 | 10 | (none held) | 2 |
| MISO | 2024-09-01 to 2026-10-02 | 2025-07-27 | 16 | 16 | (none held) | 7 |
| SPP | 2024-09-01 to 2026-10-18 | 2025-07-27 | 17 | 17 | (none held) | 9 |
| ISO-NE | 2024-09-01 to 2026-10-18 | 2025-08-23 | 12 | 12 | (none held) | 3 |

The header of `grid_stress_days.csv` carries each run's own counts.

## The cross-check against ERCOT's named events

- **Winter Storm Uri: 11 to 19 February 2021 are all stress days by price** (event `uri_2021`), 15 to 19 February among them (daily means USD 6,764.8, 8,970.1, 9,002.0, 8,989.1 and 3,410.8 per MWh against thresholds of 99.1 to 314.8).
- **Winter Storm Elliott: 22 to 26 December 2022 are stress days, 23 December by price and notice (USD 557.5 against 217.5), the others by notice.** 24 December's mean was USD 63.2 against a threshold of 225.6 (the summer of 2022 had raised the year's 98th percentile), so the price test alone missed it (session 306). Since session 322 the ERW holds ERCOT's notices (`ercot_grid_notices`, `docs/methods/ercot_grid_notices.md`): ERCOT's release of 16 December 2022 announced an Operating Condition Notice for temperatures of 25 degrees or lower between 22 and 26 December, an OCN for extreme weather, which the rule counts as it counts CAISO's notices. ERCOT issued no conservation appeal or EEA for Elliott in its releases.
- **The summer 2023 heat: 11 stress days from 4 August to 6 September 2023** (event `ercot_heat_2023`).

Columns: value the day's mean real-time price at the main hub (USD/MWh), variable `stress_day`, ts_utc the local day at
00:00Z; `x_reason` price, notice, or price and notice; `x_event` the event; `x_trailing_p98` and `x_trailing_days` the
threshold and the days it was taken over; `x_notices` the notice kinds that day.

Session 2270: since session 322 ERCOT's notices are held too (`ercot_grid_notices`, those marked `x_counts` yes), so
`x_notices` carries ERCOT's kinds as well as CAISO's (among ERCOT's stress days, `weather_watch` 36 times,
`conservation_appeal` 18), and the first Limit below and "CAISO's notice kinds" above are true of CAISO and ERCOT
together: the price test alone holds on four grids, not five. The table held on 24 October 2026 has 282 rows, as the
counts above.

## Limits

- Only CAISO's notices are held, so on five grids the rule is the price test alone.
- The four grids whose prices start on 1 September 2024 are judged by price only from the summer of 2025.
- A threshold taken over a year with a winter storm in it is high for the year after: ERCOT's threshold was USD 423.9 per MWh on 20 February 2021, the day after Uri's last stress day.
