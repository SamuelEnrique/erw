# Session 273 report: CAISO's price history before September 2024

14 October 2026, 09:55 to 12:50 UTC, unattended, on lab-desktop (the data machine), the third session of the overnight chain of 14 October. Branch `task/273-caiso-history`. Model spend USD 0: no model call. Pulls, all CAISO's OASIS, one request at a time, within each connector's ceiling: the two hubs' day-ahead and real-time prices, 14 July 2023 to 31 August 2024 (`hub_history.py backfill`, 830 days requested, one request a day and market); the reserve prices for the same days (`caiso_as_prices.py`, 415); CAISO's list of aggregated nodes (one) and ten load aggregation points' day-ahead prices for 2025 (365, an analysis). Sessions 274 to 277 were built and landed while this pull ran.

## Read these first

- **CAISO's prices now begin on 14 July 2023, the oldest day OASIS still served** (it keeps about 39 months). SP15 and NP15, day-ahead and real-time: 414 days each, one day incomplete in each market and not written; `iso_hub_prices_history` 490,300 to 589,650 rows (of its 1,500,000 ceiling). The reserves: `caiso_as_prices` 147,840 to 227,520 rows (of 500,000). ZP26's day-ahead already reached June 2023; its real time stays from September 2024 (ruling 3).
- **The battery for CAISO runs from August 2023, the first whole month** (`battery_stack.py`), so 2024 is a whole year beside 2025. Every month before October 2026 is unchanged to the cent; the month in progress gained its new days (ERCOT's too).
- **California has ten stress events now, not four,** by the same rule from CAISO's own notices. **15 to 17 August 2023 is the dearest stretch held:** USD 7,696 per MW for a 4-hour battery day-ahead, 4,153 of it on 16 August. July 2024 holds a nine-day event and the first that is not Restricted Maintenance Operations alone (an Energy Emergency Alert watch, 24 and 25 July).
- **The cross-checks: 2025 is unchanged (84.72 the market monitor's way, 85.34 the page's); 2024 is new.** The page's model in 2024: USD 109.43 per kW (energy 60.75, regulation 47.79); the real fleet: 53, about 43 of it energy. The same shape as 2025, larger: energy about two fifths above the fleet's, regulation about five times.
- **The southern gap is not the hub.** At the LA Basin's own load aggregation points the model gives USD 81.1 per kW for 2025, 3.6 below the hub's 84.72, against the market monitor's 62.6. The hub stands where SCE's and SDG&E's own aggregates stand (84.14, 85.03). The direction agrees (the south low, Fresno high: ours 94.77, theirs 111.7) and the spread does not (14 against 49). The rest lies in the two models' regulation, which this cannot separate.
- **The generator's capture file reaches July 2023 at SP15 and NP15,** and solar in 2024 now has its comparison: SP15 real time USD 9.37 per MWh captured, Berkeley Lab's solar nodes 8.62.

## The new depth

| Table | Before | After |
|---|---|---|
| `iso_hub_prices_history`, CAISO (SP15, NP15; DAM and RTM) | from 2024-09-01, 184,828 rows | from 2023-07-14, 284,178 rows |
| `caiso_as_prices` | from 2024-09-01, 147,840 rows | from 2023-07-14, 227,520 rows |
| `battery_stack_monthly`, CAISO | 2024-09 to 2026-10, 2,028 rows | 2023-08 to 2026-10, 3,042 rows |
| `battery_stack_stress_daily`, CAISO | 4 events, 252 rows | 10 events, 630 rows |
| `site/data/seller/capture.json`, SP15 and NP15 | from 2024-09-01 | from 2023-07-14 (ZP26 as it was) |

- Stores of the four tables (validator, coverage, archive, Redivis draft): each exit 0. The live set: `battery_stack_monthly` 1,112 rows written, `battery_stack_stress_daily` 378; snapshots `s273-before-load` and `s273-after-load`, 0 differences.

## What changed in the cross-checks

| Cross-check | Before | Now |
|---|---|---|
| 2025, the market monitor's way (4 hours, day-ahead) | 84.72 against 77.3 | the same |
| 2025, the page's model; the real fleet | 85.34; energy 35, regulation 9 | the same |
| 2024 | no whole year held | the page's 109.43 (energy 60.75, regulation 47.79, reserves 0.89); as theirs 108.87; the fleet 53, "nearly 82 percent" from energy |
| The southern areas | "not explained" | the node explains about a sixth; the rest is the regulation models (`docs/methods/battery_stack.md`, "The southern areas, with CAISO's node list") |
| Solar, 2024, the generator | not computed | SP15 9.37 captured, flat 29.39, 31.9 percent; Berkeley Lab 8.62 at solar nodes, 29.67 flat there, 29.1 percent |
| Wind, the peaker, 2025 | as session 253 left them | unchanged (2025's prices did not move) |

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py --what "session 273"` | 0 | six of six |
| `lock.py run -- hub_history.py backfill --iso caiso --start 2023-07-14 --until 2024-09-01`, then `caiso_as_prices.py` the same days | 0, 0 | 09:55 to 12:07 UTC |
| `lock.py run -- battery_stack.py` | 0 | 11,556 and 1,890 rows |
| `capture_price.py`, then `site/scripts/test-capture.mjs` | 0, 0 | all passed |
| `lock.py run -- table_stores.py` for the four tables | 0 | 16 steps, each 0 |
| `lock.py run -- load.py --no-vacuum --only '^battery_stack_(monthly|stress_daily)$'` | 0 | match |
| `battery_caiso_years.py`, `caiso_southern_nodes.py --pull`, the generator check for 2024 | 0, 0, 0 | above |
| `python -m unittest` 246, 253, 263, 264, 265, 247, 257; then 273, 246, 253 | 0, 0 | 105 and 30 tests |
| `python -m unittest discover -s tests` | see the landing | |

## Decisions made without you

1. **"As far back as CAISO publishes" is OASIS's own edge on the day, 14 July 2023.** CAISO's older prices are not on OASIS; nothing else was asked.
2. **The battery starts at August 2023,** the first whole month, as every other grid starts on a month.
3. **ZP26's real time was not pulled back:** the zone history's ceiling (3,000,000 rows read) has 114,597 left, and ZP26's 14 months of five-minute prices would take about 120,000. Its day-ahead already reaches June 2023.
4. **The southern examination is an analysis, not a table:** ten load aggregation points for one year, under its own ceiling of 120,000 rows, in `warehouse/output/analysis_internal/`. Which sub-LAP lies in which local capacity area is the ERW's reading of the names, and the note says so.
5. **The six new events are the rule's,** unpicked; the note lists them in the same form as the four before.
6. **Session 277's refresh of the zone history's CAISO part rode on this branch** (its stores' metadata), because both write the same metadata files on this checkout.

## For Samuel's ruling

1. The page's California history now begins in August 2023: the battery page says "From August 2023" (`site/lib/batterystack.ts`). The generator page reads its own files.
2. Regulation in both years is about five times what the real fleet was paid. Session 246's ruling 4 (the market monitor's caveat beside the ancillary income) now has two years behind it.
3. ZP26's real time before September 2024: raise the zone history's ceiling, or leave it.
4. A node list for the battery page ("where your battery sits"): the southern table shows the place moves energy income by about USD 30 per kW a year.

## Files

- New: `warehouse/analysis/caiso_southern_nodes.py`, `warehouse/analysis/battery_caiso_years.py`, `tests/test_session273.py`, this report.
- Changed: `warehouse/derived/battery_stack.py` (CAISO's start), `site/lib/batterystack.ts` (its words), `site/data/seller/capture.json`, `docs/methods/battery_stack.md`, `docs/methods/generator_earns_algorithm.md`, `tests/test_session257.py`, and the metadata the stores wrote.
- On this machine, not in git: the tables, `warehouse/output/analysis_internal/` (the years, the southern nodes and their prices), `runs/session273/`.

## The landings recorded here

- **Session 272:** before `s272-before` 09:54:07 UTC; pushed 09:54:13 (`task/272-large-load-public`, `12debbf8`); check run 38545750349 success 10:04:00; merged `d77571ce`; deployed 10:06:11; after `s272-after` 10:06:13; `compare`: 0 differences. Expected: a table loaded that no page reads yet, a helper no page calls.
- **Session 274:** before `s274-before` 10:22:43; pushed 10:23:44 (`task/274-motion`, `e85fb811`); run 38549265856 success 10:34:09; merged `16bb71c4`; deployed 10:35:34; after `s274-after` 10:35:36; 0 differences. Expected: no page changed.
- **Session 275:** before `s275-before` 10:35:49; pushed 10:35:54 (`task/275-redivis-v1`, `d815547b`); run 38550692557 success 10:44:06; merged `886a3320`; deployed 10:45:32; after `s275-after` 10:45:37; 0 differences. Expected: documents and a script.
- **Session 276:** before `s276-before` 10:45:42; pushed 10:45:48 (`task/276-subscribe-analytics`, `b1881e27`); run 38551834769 success 10:54:46; merged `5da59d21`; deployed 10:56:10; after `s276-after` 10:56:17; 0 differences. Expected: scripts and a runbook section.

## The landing

- In session 278's report.
