# Stress days of the grids (session 306)

The table `grid_stress_days`, built by `warehouse/derived/stress_days.py` from tables the ERW already holds. No request is made to any publisher. The chain prompt names it `stress_days`; a series table's name has three parts (`docs/datastandard.md`, Decisions 19 and 47). The rule is the code machine's session 297, `docs/methods/battery_stress_days.md`; this note says how the data machine applies it.

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

## What the rule gives (built 19 October 2026)

| Grid | Days held | Judged by price from | Stress days | By price | By notice | Events |
|---|---|---|---|---|---|---|
| ERCOT | 2015-01-01 to 2026-10-14 | 2015-11-26 | 113 | 113 | (none held) | 64 |
| CAISO | 2023-07-14 to 2026-10-14 | 2024-06-08 | 58 | 24 | 36 | 25 |
| NYISO | 2024-09-01 to 2026-10-14 | 2025-08-15 | 10 | 10 | (none held) | 2 |
| MISO | 2024-09-01 to 2026-10-02 | 2025-07-27 | 16 | 16 | (none held) | 7 |
| SPP | 2024-09-01 to 2026-10-13 | 2025-07-27 | 17 | 17 | (none held) | 9 |
| ISO-NE | 2024-09-01 to 2026-10-13 | 2025-08-23 | 12 | 12 | (none held) | 3 |

The header of `grid_stress_days.csv` carries each run's own counts.

## The cross-check against ERCOT's named events

- **Winter Storm Uri: 11 to 19 February 2021 are all stress days by price** (event `uri_2021`), 15 to 19 February among them (daily means USD 6,764.8, 8,970.1, 9,002.0, 8,989.1 and 3,410.8 per MWh against thresholds of 99.1 to 314.8).
- **Winter Storm Elliott: 23 December 2022 is a stress day (USD 557.5 against 217.5); 24 December 2022 is not.** Its mean was USD 63.2 against a threshold of 225.6: the summer of 2022 had raised the year's 98th percentile. The ERW holds none of ERCOT's notices, so the notice test cannot make it one. The rule does not reproduce the named event's second day; `elliott_2022` holds one day here, and the named events stay where they are used (`event_window.py`).
- **The summer 2023 heat: 11 stress days from 4 August to 6 September 2023** (event `ercot_heat_2023`).

## Limits

- Only CAISO's notices are held, so on five grids the rule is the price test alone.
- The four grids whose prices start on 1 September 2024 are judged by price only from the summer of 2025.
- A threshold taken over a year with a winter storm in it is high for the year after: ERCOT's threshold was USD 423.9 per MWh on 20 February 2021, the day after Uri's last stress day.
