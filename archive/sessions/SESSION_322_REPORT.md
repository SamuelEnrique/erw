# Session 322 report: ERCOT's notices, the Flex Alert scorecard, CAISO's 25-hour day

19 October 2026, from 20:54 UTC (the reading) and 22:49 UTC (the writes), unattended, on lab-desktop (the data machine), the second session of the chain of 19 October, daytime. Model spend USD 0.

## Read these first

- **`ercot_grid_notices`: 178 rows, 2 February 2011 to 15 October 2026; 120 count toward stress days, on 100 days.** ERCOT keeps no single history of its notices. The table reads its news releases from 2010 (EEAs, rotating outages, conservation appeals, Power and Weather Watches, OCNs a release announces) and the control room's operations messages, which ERCOT serves for six months only (May 2026 on; December 2022 answered with an empty list). Validated, in coverage, archived, in the Redivis draft, loaded (`match ercot_grid_notices: 178`), under `review_hold`. Method: `docs/methods/ercot_grid_notices.md`.
- **24 December 2022 is now an ERCOT stress day.** ERCOT's release of 16 December 2022 announced an Operating Condition Notice for 25 degrees or lower "between Thursday, December 22 through Monday, December 26": 22 to 26 December are notice days, 23 December by price and notice. `grid_stress_days` for ERCOT: 169 stress days, 113 by price and 79 by notice (113 and 64 events before), 74 events. ERCOT issued no conservation appeal or EEA for Elliott in its releases.
- **The Flex Alert scorecard runs to 31 October 2026 and no number moved.** CAISO's Grid Emergencies History Report (revised 9 October 2026, read daily) lists no Flex Alert, EEA or emergency in the 2025 or 2026 season, only Restricted Maintenance Operations and transmission notices, which the method does not count as alert days. The three stations' weather ends 27 August 2025 for Sacramento and Fresno (`noaa_isd_hourly`), so no later day is fitted either. `flex_alert_effects` (2,973 rows) and `flex_alert_model` (881) are equal value for value before and after; only their headers changed. A season with an alert would need SAC's and FAT's 2025 to 2026 hours from NOAA, a pull this session's part did not name.
- **CAISO's fall-back days are whole.** The request now ends at the next local midnight (`pd.DateOffset(days=1)`), not 24 hours after (`iso_prices.py`, `pull_caiso`): 25 hours on a fall-back day, 23 on a spring day. Filled: 2023-11-05, 2024-11-03 and 2025-11-02, day-ahead and real-time, 25 hours each (750 rows; the three days had no CAISO rows at all in `iso_hub_prices_history`). The spring days already held their 23 hours.

## What to review

1. `warehouse/connectors/ercot_grid_notices.py`: `release_kind` and `ops_kind` (which words make which kind), `named_days`, and `x_counts`.
2. `warehouse/derived/stress_days.py`: ERCOT's notices read as CAISO's are.
3. `docs/methods/battery_stress_days.md`: session 297's rule named the kinds to count once ERCOT's notices were held; the session 322 sentence says how they were applied (an OCN for extreme weather counts, as CAISO's RMO does).

## Pulls against their ceilings

| Pull | Ceiling | Used | Result |
|---|---|---|---|
| ERCOT (robots file, notice archive pages, operations messages, news release listings and releases) | 200 | 130 | all HTTP 200; `warehouse/raw/ercot_grid_notices/s322/manifest.csv` |
| CAISO's Flex Alert history page | 20 | 0 | not needed: CAISO's own report (read daily) is the list; a web search found no single page |
| CAISO OASIS, the clock-change days | 10 | 6 | three days, two markets |

ERCOT's terms were read on 12 October (read 2 of `license_reads.csv`: may be public, not modified); not asked again.

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 322"` | 0 | |
| `ercot_grid_notices.py --from-raw ...` under the lock | 0 | 178 rows |
| `stress_days.py`, twice (the second after the history merge) | 0, 0 | ERCOT 169, CAISO 58 |
| `flex_alert_scorecard.py` | 0 | the values equal |
| `hub_history.py backfill --iso caiso` for the three days | 0, 0, 0 | 50 and 200 rows a day |
| `table_stores.py` on the five tables | 0 | validate, coverage, archive, Redivis draft |
| `load.py --no-vacuum --only` the five | 0 | match on each; sources 320 |
| snapshots `s322-before`, `s322-after` around the load | 0 | 0 differences on 25 pages |
| `tests.test_session322`, 102, 306 (its pin on 24 December follows) | 0 | |

## Decisions made without you

1. **The history was merged with the archive before its stores.** This machine's `iso_hub_prices_history` lacked the runner's newest 1,968 rows; archiving it as held would have recorded them as deleted. The table written is the archive's latest (594,522 rows) plus the 750 filled rows.
2. **What counts as an ERCOT notice** (above): the system-wide calls, and an OCN for extreme weather, as CAISO's RMO counts. The control room's Advisories (geomagnetic, a study that did not solve) are held and do not count.
3. **The writes ran before the redispatched manual daily run**, not after it (session 321's report: the first manual run was cancelled before it touched data, and the next starts after the blackout).
4. **No pull for the scorecard's weather:** it is not named in this session's part.

## For Samuel's ruling

- The scorecard's 2025 and 2026 weather: allow a NOAA pull for Sacramento and Fresno from 28 August 2025 (the model could then fit later days; no alert day would join, since there was none).

## Files

- New: `warehouse/connectors/ercot_grid_notices.py`, `docs/methods/ercot_grid_notices.md`, `tests/test_session322.py`, this report; `warehouse/raw/ercot_grid_notices/s322/` (not in git).
- Changed: `warehouse/connectors/iso_prices.py` (`pull_caiso`), `warehouse/derived/stress_days.py`, `warehouse/derived/flex_alert_scorecard.py` (`END`), `docs/methods/stress_days.md`, `docs/methods/battery_stress_days.md`, `warehouse/supabase/live_set.yaml`, `warehouse/metadata/build_coverage.py`, `scripts/licenses.py` (`grid_stress_days`'s line), `tests/test_session306.py`, `tests/test_session310.py`, `coverage.csv`, `docs/coverage.md`, `sources.csv`, `archive_manifest.csv`, `redivis_uploads.csv`.
