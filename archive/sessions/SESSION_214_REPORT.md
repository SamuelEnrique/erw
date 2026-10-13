# Session 214 report: the launch list for Monday 20 October

13 October 2026, from 01:57 UTC, unattended, on lab-desktop (the data machine), the first session of the chain of 12 October, evening (sessions 214 to 218). Branch `task/214-launch-list`. Model spend USD 0 (no model call). Pulls: none (no publisher was asked; the one network read was `scripts/sync.py --check --no-git`, Redivis and Supabase, and the `erw_health` rows of the last 7 days from Supabase). Writes to the stores: none. Precheck: six passes, on duty until 17:57 UTC.

## Read these first

- **One document: `docs/state/launch_2026-10-20.md`.** 57 pages a visitor can reach, one row each, with the tables each reads (from the page's own code), each table's license status on 20 October, its newest date against its cadence, the page's health over the last 7 days, whether it is in review today (all are), and a verdict: **29 ready, 23 ready if licenses arrive, 3 blocked, 2 not for launch.**
- **The three blocked pages:** `/board` (its builder `board_page` failed on 6 of the last 7 daily runs; sessions 202 and 206's fixes landed on 12 October and the run of 13 October is the proof), `/cost-of-power` and `/datacenters` (both quote `ercot_large_load_status`, which stops at ERCOT's report of 26 March 2026; session 217 of this chain brings it current).
- **Green days: 0 today; seven cannot show by the morning of 20 October.** `site/data/health_days.json` counts to 11 October (0). 12 October holds 5 counted failures (computed here from `erw_health` with `health.py`'s own `day_record`), every one with a fix on main since 12 October. The record on the morning of 20 October counts to 18 October: 5 if 14 to 18 October are green, 6 if 13 October is too; 7 first after the run of 20 October, and only with 13 October green.
- **For session 218: 33 public tables are behind their cadence with no run refreshing them** (the document's last table): 17 this machine may ask (ERCOT, CAISO, EIA, NOAA, NRC, CARB), 12 derived, 4 of ISO-NE, NYISO and SPP this chain may not ask. 31 more are refreshed daily and wait on their publisher's lag; they are not in the list.
- **The landing:** no freeze (`freeze.py status` exit 0); before snapshot `s214-before` at 02:15 UTC, 25 pages, 0 failed, every page in review (57 lines of text each, 0 checked numbers). Pushed to `task/214-launch-list`; the check's result, the after snapshot and the comparison are recorded by session 215's branch (as session 207 recorded 206's). Nothing a visitor sees changes: 0 differences expected.

## What was read, and how

- **The pages:** `site/lib/pages.ts` (the menu's pages, the problem sets, the seven grid pages) with the home page, Privacy, the data standard, the known faults, the methods notes, the Digest and the Roundup: 57 routes. Every route is `review` in `site/lib/release.ts`.
- **The tables a page reads:** `runs/session214/page_tables.py` walks each page file's imports three levels deep through `site/lib`, `site/components` and `site/data`, attributes a module's table names to its top-level export blocks (a page that imports two functions of `lib/data.ts` gets those two functions' tables), strips comments, and adds the tables a shipped data file names. The declared `tables` string of `pages.ts` stands beside it in `page_tables.json`; the document uses the code's list.
- **Licenses:** `site/data/license_status.json` (40 tables "license needed" from 2026-10-20, session 207) and `coverage.csv`'s license column.
- **Freshness:** `scripts/data_state.py` for 13 October, written to `runs/session214/data_2026-10-13.md` (not to `docs/state/`: the chain asked for one document), from every table's own file after `sync.py --check` found 194 of 196 tables current with Redivis (the two rolling snapshots a day ahead on Redivis). 196 tables, 37,261,990 rows; 70 over their limit (39 stuck or unscheduled, 31 refreshed without a newer row).
- **Health:** the 2,104 rows of `erw_health` since 2026-10-06 02:00 UTC, mapped to pages by the steps that write what each shows (STEPS in `runs/session214/launch_list.py`). Distinct failures of the window: `board_page` (6 days), `carb_lcfs` (6), `package tests` (7), `supabase_load` (3, the ledger alone), `policy_monitor_refresh` (2, Oregon), `ercot_zone_load` (10 October), `3-run failure streak` rows (grid_network to 9 October, carb_lcfs), the roundup's ledger load (11 October), the old laptop's `ercot_zone_load` (9 October).
- **The green count:** `health.py`'s `green_streak` and `day_record` as written (a day with no row, a failed counted step, or a daily job with no run ends the count; the record is written by the daily run for yesterday).

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py --what "sessions 214 to 218"` | 0 | six passes |
| `python scripts/sync.py --check --no-git` | 0 | 194 current, 2 diverged (the two rolling snapshots), nothing written |
| `python scripts/data_state.py ... --out runs/session214/data_2026-10-13.md` | 0 | 196 tables |
| `python scripts/freeze.py status` | 0 | no freeze |
| `node site/scripts/snapshot-live.mjs take s214-before` | 0 | 25 pages, 0 failed |
| Em dash count over the new document and this report | 0 | counted with Python before the commit |

No test, build or loader was run: the session changed no code and no table. The check run on the push runs the suite, the site build and the route check.

## Decisions made without you

1. **The data state document went to `runs/session214/`, not `docs/state/data_2026-10-13.md`.** The chain asked for one document; the launch list cites the run folder. A later session can copy it into `docs/state/` if the daily series of those documents should continue.
2. **A page's tables are read from its code, not from the menu's declared list alone.** The declared list of `pages.ts` is hand-written and in places wider or narrower than what the page reads (the board declares "the tables of docs/methods/price_board.md"; the prices page declares `latest_prices`, which is not a coverage table). Both are kept in `page_tables.json`; the document lists the code's.
3. **A consolidated table flagged whole is counted as license needed for every page that reads it,** even one that reads only ERCOT's or CAISO's rows (`iso_rtm_hub_prices` for the battery game, `event_window_daily` for the event studies): the status file flags the table, not a partition. Ruling 2.
4. **The loader's three failed rows do not block any page.** Each named `api_cost_ledger` alone, an internal table (fixed by session 206); every other table loaded on those days. The health column still shows them.
5. **A table whose staleness is its publisher's lag is "ready", not blocked** (EIA's monthly series at July, EIA's spot prices at 6 October, ERCOT's 60-day disclosures). `data_state.py`'s rule reads them as behind; the verdict says where that is all it is.
6. **`/board` is "blocked" and `/prices` is not,** though both wait on the run of 13 October: the board's file a visitor sees was not rebuilt by the runner since 6 October, while the prices page's tables are current to 13 October and only ISO-NE's real-time hourly pull failed on 12 October (patched by session 206).
7. **The verdict column is a reading, written per page in `runs/session214/launch_table.py`** so each can be checked against the row's other cells. Every other cell is read from a file.
8. **The pages' health map (STEPS) is this session's,** written from the step names of `run_daily.sh`, `refresh_board.sh`, `refresh_supply.sh` and `run_data_machine.sh`; a step that writes a table a page reads but is not in the map is not counted against that page.
9. **The green count for 12 October was computed here, not read from the file:** the daily run writes the record for yesterday, so the file could not hold it yet.

## For Samuel's ruling

1. The licenses by 20 October: write to ISO-NE (info@iso-ne.com), Natural Gas Intelligence (info@naturalgasintel.com) and WSJ (Dow Jones Reprints), or let the 23 pages show "license needed" where those tables' numbers stood (session 215). NYISO's page names no address; MISO's terms are for a person's review.
2. Whether a consolidated table (`iso_dam_hub_prices`, `iso_rtm_hub_prices`, `iso_hub_prices_history`, `event_window_daily`) should be flagged by partition, so that the battery game (ERCOT) and the event studies (ERCOT, CAISO, PJM) are not held for MISO's, ISO-NE's and NYISO's rows (decision 3).
3. Which of the 29 "ready" pages open on 20 October: each is one line of `site/lib/release.ts` on your instruction.
4. Seven green days cannot show on the morning of 20 October (the record counts to 18 October; at most 6). Whether the gate is read at the afternoon's run (7 with 13 October green), or the public day moves.
5. The 17 stale public tables this machine may ask (the document's last table): session 218 refreshes them within each connector's ceiling under this chain's rules; the four of ISO-NE, NYISO and SPP wait for the ruling on opening those grids (session 178's question).
6. The generator page's exports are switched off since session 204 (`GENERATOR=1`); `/cost-of-power/seller` shows its export of 7 October. Whether to turn them on (the six tests that hold the CSV) before 20 October.
7. The Digest and the Roundup read no table (their pages render `docs/digest/` and `docs/roundup/`), so the list marks them "ready"; their issues are written from `news_index`, `energy_deals` and `datacenter_projects`, all "license needed" from 20 October for the news publishers' headlines and links. Whether the hold reaches the two briefs.

## Files

- `docs/state/launch_2026-10-20.md` (new, in git).
- `runs/session214/` (this machine, not in git): `page_tables.py`, `page_tables.json`, `launch_list.py`, `launch_list.out`, `launch_rows.json`, `launch_table.py`, `launch_table.md`, `stale_public.md`, `doc_head.md`, `doc_foot.md`, `data_2026-10-13.md`, `data_state.out`, `data_state_cache.json`, `sync_check.out`, `health7.json`, `snapshot_before.out`.
- `runs/snapshots/s214-before/`.
