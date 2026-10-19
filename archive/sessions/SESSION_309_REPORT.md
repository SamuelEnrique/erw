# Session 309 report: the open gap days

19 October 2026, 10:26 to about 11:35 UTC, unattended, on lab-desktop (the data machine), the fifth session of the chain of 19 October. Model spend USD 0.

## Read these first

- **849 open gap days became 833: 16 filled, 0 new.** The 16 are the eight EIA-930 generation members' two days each (all from EIA's API). Of the others, 769 were re-asked and are still incomplete at the source; each has a re-check row in `run_status.csv` (run `20261019T111546Z`). 57 are of held publishers (ISO-NE, NYISO, SPP) and were not asked. Seven name no single day.
- **The table with the most open days: `eia930_all_emissions`, 652, of which 484 are SWPP's.** EIA's own per-BA workbooks, downloaded today (Last-Modified 17 October 2026), hold no CO2 value for those hours, for example SWPP on 12 to 21 March 2021. The re-ask rewrote the table from the new workbooks (4,343,184 rows, 4,296 new) and left 17 incomplete BA-day groups out, but a day with no value at all stays open.
- **`eia930_all_storage`'s 115 days cannot fill.** Six are each BA's first BAT day (ERCO and ISNE 2024-11-06, MISO 2025-01-15, SWPP 2026-02-04), which EIA reports only in part. The 109 US48 days of July 2024 to January 2026 are not complete in EIA's series: the re-ask from 2024-07-15 added 72 rows and filled none of them.
- **EIA's API answered HTTP 504 for long stretches** (10:27 to 10:43, and again from 10:56). The first storage pull failed after 4 attempts on one month, writing nothing. The per-BA retry wrote US48, and I stopped it during ERCO and ISNE, since their days are first days that cannot fill. The stopped run wrote nothing, and the lock was released by this session (`lock.py release`).
- **CAISO's two gap days (2 November 2025, day-ahead and real-time) are a fault in the request, not at the source.** On the 25-hour clock-change day the query window ends at 07:00 UTC, one hour before the local day ends, so the last hour is never asked (2 requests; the day still lacks 2025-11-03T07:00Z). For a ruling: a code fix in the window of the day.

## What to review

1. `run_status.csv`, the 769 rows of run `20261019T111546Z` ("session 309 re-check ...").
2. The CAISO clock-change window (above).
3. The open list in `STATUS.md` (rebuilt by `build_status.py`).

## Pulls against their ceilings

| Source | Requests | Result |
|---|---|---|
| EIA's per-BA workbooks (gridmonitor/knownissues/xls, eight files) | 9 (one aborted at 0 bytes and asked again) | the dry run, then the write from the same files |
| EIA API, BAT storage (`eia930_storage.py`) | 82 (30 in the first pull, which failed; 28 for US48; 24 for ERCO and ISNE before the stop) | US48 written, 72 rows new |
| EIA API, demand and generation (`eia930.py --days 50`) | 54 (twice: the first run wrote members from nothing, decision 1) | 16 days filled |
| CAISO OASIS (`hub_history.py backfill`, 2 November 2025) | 2 | the day still short by its last hour |
| **Total** | **147 of 2,000** | nothing asked of ISO-NE, NYISO, SPP, MISO or PJM |

## Open gap days by table, after the session

| Table | Open | Why |
|---|---:|---|
| `eia930_all_emissions` | 652 | EIA's workbooks hold no CO2 for the hours (SWPP 484, CISO 47, PJM 43, MISO 28, NYIS 18, ERCO 17, ISNE 9); 6 rows name no single day |
| `eia930_all_storage` | 115 | first BAT days; US48's early series |
| `iso_hub_prices_history` | 45 | ISO-NE 31, NYISO 11, SPP 1 not asked (held); CAISO 2 (the window, above) |
| `isone_rtm_zone_prices` | 7 | held, not asked |
| `eia930_erco_demand`, `_nyis_`, `_swpp_` | 4, 2, 2 | EIA's day-ahead forecast lacks hours of the day, still on today's API |
| `spp_rtm_hub_prices` | 3 | held, not asked |
| `isone_rtm_zone_prices_hourly` | 2 | held, not asked |
| `eia930_all_interchange` | 1 | names no single day |

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 309"` | 0 | |
| `eia930_emissions.py --dry-run`, then `--from-raw` under the lock | 0, 0 | 4,343,184 rows; 17 incomplete BA-day groups left out |
| `eia930_storage.py --since 2024-07-15` | 1 | HTTP 504 after 4 attempts; nothing written |
| `consolidate.py split`, `eia930.py --days 50`, `consolidate.py build` under the lock | 0 | members merged with the held rows ("kept") |
| `eia930_storage.py --since 2024-07-15 --ba us48` | 0 | 72 new |
| `hub_history.py backfill --iso caiso` (2025-11-02) | 0 | 0 days written, 1 not complete in each market |
| `table_stores.py` on the four EIA tables | 0 | Redivis count(*) 4,343,184; 20,256; 105,096; 72,408 |
| `load.py --no-vacuum --only '^eia930_all_(emissions\|demand\|generation\|storage)$'` | 0 | match on all four |
| `build_status.py` | 0 | 978 recorded, 145 filled, 833 open |

## The landing

See below (filled at the push).

## Decisions made without you

1. **The first `eia930.py` run wrote members without the held rows** (the members live in the consolidated tables until `consolidate.py split`). Its files were set aside in `runs/s309_fresh_members/`, and the run was repeated after a split, so the connector merged as the daily run does (27 more requests).
2. **The storage re-ask was stopped** once EIA slowed again: the remaining BAs' gap days are first days the source holds only in part.
3. **A re-check row is written only for a table this session asked again**; a held publisher's day gets no row.
4. **The four EIA tables were loaded into the live set now**, not left to the 14:00 run.

## For Samuel's ruling

- CAISO's clock-change day: correct the query window of a 25-hour day, so the fall-back day can be written.
- `eia930_all_storage`'s six first BAT days and US48's 109: close them as known gaps (the source will not complete them), or keep them open.

## Files

- Changed: `warehouse/metadata/run_status.csv` (769 rows), `STATUS.md`, `coverage.csv`, `docs/coverage.md`, `archive_manifest.csv`, `redivis_uploads.csv`; session 308's report (its landing).
