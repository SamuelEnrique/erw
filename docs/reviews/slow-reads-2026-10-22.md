# The database's heavier reads, measured (session 580, 22 October 2026)

Roadmap draft item 6: "the database answers its heavier reads again". Session 580 timed every read the site's pages
make, on a build and on a route check against that build, and read the slowest against the live set's indexes.

## Summary

- Tonight the database answers every read the site makes in 80 to 200 ms when asked alone. No read was cancelled by
  the statement timeout (no `57014` in either log), and no request of the route check took over 1 second.
- The only slow requests were among the first 35 of the build's 210: nine took 0.9 to 6.9 s, all in the opening burst,
  when eleven build workers each send two reads at once (session 90's turns) to a database the build finds cold. Asked
  again alone a few minutes later, the same nine took 80 to 200 ms each.
- Two of the five slowest are served by an index that fits neither their filter nor their order: the queue read of
  `energy_projects` (map, resources overlay) and the event pages' reads of `event_window_daily`. Migration 036 holds a
  small partial index for each. **It is written and not applied** (For Samuel's ruling). The other three fit the
  primary key and need nothing.
- PostgREST refuses a query plan to the anon key (`PGRST107`, "None of these media types are available", for
  `application/vnd.pgrst.plan+text`): the plans below are read from the tables' indexes in
  `warehouse/supabase/migrations/`, not from `EXPLAIN`.

## How it was measured

- `site/lib/supabase.ts` prints one line a request, `[erw-read] {kind, table, query, status, range, ms}`, when the
  server or the build is started with `ERW_READ_TIMING=1`. Off (the default everywhere), no clock is read and no line
  is printed: the request is the one it was, with the same address, headers and cache settings. The time runs from the request to its answer's headers, inside the build's turn
  (a wait for a slot is not counted). A retry and each page of a large read are lines of their own.
- `ERW_READ_TIMING=1 npm run build` in the worktree of `wip/580-s` (exit 0, 210 requests, no statement timeout), then
  `ERW_READ_TIMING=1 next start -p 3580` and `node scripts/check-routes.mjs http://localhost:3580 http://localhost:3580`
  (exit 0: 226 pages with the internal cookie and as a visitor, 10,367 requests, most answered from Next's data cache;
  the baseline was the local server itself, so no request went to production).
- `node scripts/slow-reads.mjs <log> 20` groups the lines by kind, table and query (a request asked more than once
  keeps its slowest time and how often it was asked) and prints the slowest.
- The 25 slowest requests were then asked again, one at a time, three times each, straight to PostgREST with the anon
  key (read-only GETs, the same query strings), and nine row counts were read the same way.

## The twenty slowest requests

One row a request (one page of up to 1,000 rows), slowest first, across the build and the route check. "ms" is the
slowest time seen there; "alone" is the three times when asked again one at a time; "asked" is how often the site
asked it (most of them answered from Next's data cache).

| # | table | filter (table_name first) | offset | rows | ms | alone (ms) | asked |
|---|---|---|---|---|---|---|---|
| 1 | entities | energy_projects, extra->>kind=eq.queue | 0 | 1000 | 6910 | 196/196/174 | 1 |
| 2 | catalogue | (none) | 0 | 131 | 6091 | 154/112/136 | 922 |
| 3 | series | cost_of_power_hourly_profile, entity=eq.ercot:HB_HUBAVG | 0 | 624 | 5358 | 107/101/151 | 2 |
| 4 | series | event_window_daily, event=eq.cold_2026 | 0 | 1000 | 5318 | 103/128/128 | 2 |
| 5 | series | event_window_daily, entity=eq.eia930:CISO, variable=eq.demand_max_pct_vs_baseline, event=eq.caiso_heat_2020 | 0 | 12 | 5316 | 80/93/99 | 2 |
| 6 | series | event_window_daily, entity=eq.ercot:HB_HUBAVG, event=eq.covid_2020 | 0 | 552 | 4266 | 124/108/101 | 1 |
| 7 | series | eia930_all_demand, entity=in.("eia930:ERCO","eia930:CISO"), variable=eq.demand_mw, ts_utc=gte.2026-10-16T00:15:46Z | 0 | 238 | 1200 | 102/100/89 | 1 |
| 8 | series | cost_of_power_monthly | 0 | 1000 | 1187 | 108/139/115 | 1 |
| 9 | series | event_window_daily, variable=eq.demand_mwh, event=eq.covid_2020 | 0 | 1000 | 968 | 111/124/111 | 1 |
| 10 | series | event_window_daily, event=eq.caiso_heat_2020 | 0 | 666 | 518 | 124/109/98 | 2 |
| 11 | series | iso_curtailment_monthly, entity=eq.caiso:ISO | 3000 | 0 | 421 | 94/88/110 | 8 |
| 12 | series | eia_fuel_spot_prices, entity=eq.eia:henry_hub, variable=eq.spot_price, ts_utc=gte.2026-08-01T00:00:00Z | 0 | 53 | 357 | 86/103/122 | 1 |
| 13 | entities | energy_projects, extra->>kind=eq.queue | 3000 | 713 | 331 | 189/186/189 | 1 |
| 14 | series | eia930_all_generation, entity=eq.eia930:US48, ts_utc=gte.2026-10-13T00:00:00Z | 2000 | 1000 | 324 | 116/118/159 | 14 |
| 15 | series | eia930_all_generation, entity=eq.eia930:US48, ts_utc=gte.2026-09-18T00:00:00Z | 2000 | 1000 | 322 | 114/116/136 | 18 |
| 16 | series | eia930_all_generation, entity=eq.eia930:SWPP, ts_utc=gte.2026-10-12T00:00:00Z | 2000 | 160 | 320 | 86/124/107 | 78 |
| 17 | series | eia930_all_generation, entity=eq.eia930:SWPP, ts_utc=gte.2026-10-12T00:00:00Z | 4000 | 0 | 319 | 95/115/101 | 78 |
| 18 | series | eia930_all_generation, entity=eq.eia930:US48, ts_utc=gte.2026-09-18T00:00:00Z | 3000 | 1000 | 311 | 116/109/131 | 18 |
| 19 | series | eia930_all_storage, variable=eq.net_generation_battery_mw, ts_utc=gte.2026-09-21T00:00:00Z | 2000 | 1000 | 299 | 149/127/153 | 2 |
| 20 | series | state_generation_mix_monthly, entity=eq.eia:US | 1000 | 1000 | 299 | 114/168/125 | 52 |

Every `series` read selects `entity,variable,ts_utc,value,unit,freq` and orders by `entity,variable,ts_utc,event`.
Rows 11 and 17 answered no row: the pages beyond a read's end that session 148's reader asks for together (expected).
Rows 1 to 9 all fell in the build's first 35 requests; the build's other 175 averaged 66 ms, the slowest 357 ms.

## The five slowest, read against the indexes

Row counts read with `Prefer: count=exact` on 22 October.

1. **entities, energy_projects, kind queue, by entity_id** (`app/map/page.tsx`, `lib/resourcesdata.ts`). 3,713 of
   34,634 rows. The primary key `(table_name, entity_id)` gives the order; `extra->>'kind'` is checked row by row, so
   each page walks about nine rows for one it keeps, and the fourth page walks most of the table: 190 ms alone, the
   slowest request asked alone tonight. **Lacks an index**: migration 036's `entities_projects_kind`,
   `((extra->>'kind'), entity_id) where table_name = 'energy_projects'`.
2. **catalogue, every row, by table_name.** 131 rows; the primary key is `table_name`. Nothing to add: its 6 s was the
   build's opening burst. It is the most asked read of the site (922 times in the route check, from Next's data cache).
3. **series, cost_of_power_hourly_profile, one entity** (`app/cost-of-power/GridsView.tsx`). 624 of 4,368 rows. The
   primary key `(table_name, entity, variable, ts_utc, event)` holds the filter and the order. Nothing to add.
4. **series, event_window_daily, one event** (the nine `app/events/*` pages). 1,515 of 29,953 rows for cold_2026;
   20,060 for covid_2020. The event is the last column of the primary key, so the read walks the whole table in key
   order and keeps one row in twenty. **Lacks an index**: migration 036's `series_event_window_by_event`,
   `(event, entity, variable, ts_utc) where table_name = 'event_window_daily'`, which gives the filter and, with the
   event fixed, the read's order.
5. **series, event_window_daily, one entity, variable and event.** 12 rows. The primary key's first three columns
   narrow it to one variable of one entity; the event is then checked row by row, a few hundred rows at most. The new
   index serves it too; on its own it needs nothing.

Row 7 (`entity=in.(...)`) and rows 14 to 18 (`eia930_all_generation`, one entity since a date, every variable) are
served by the primary key's prefix and filtered on `ts_utc` within each variable; at 90 to 160 ms alone they need
nothing tonight.

## What this does not settle

- The burst at the start of a build is the one place a read still nears the 3 s limit. Session 90's two reads at a time
  per worker, with eleven workers, is 22 at once; the measurements here do not say whether the wait is the database's
  or the build machine's (the clock runs in a worker that is also compiling pages). A build that sets fewer workers, or
  one read a worker, would tell; no setting was changed here.
- The indexes are proposed from the tables' indexes and row counts, not from a plan. Once 036 is applied, `explain
  (analyze, buffers)` of the two reads in the SQL editor confirms the planner uses them (a partial index is used only
  when the query names the table as a literal, as a PostgREST filter does).
- One night's measurement, on a database that the probe found open (`scripts/db_probe.py`, 0.65 s for 1,000 rows).
  The reads that failed in October's landings (sessions 235 to 249, 461) were on a busy or cold database; a second
  measurement during the daily run's load (14:04 to 15:30 UTC) would show the reads under load.

## Files

- `site/lib/supabase.ts`: `readTiming`, `readClock`, `readLine`; both readers timed inside the turn. The measurement above was made with a first form of the same switch (a wrapper around the request, the same clock points); it was rewritten after the build so that session 148's test, which holds that one line sends a page's request, stands as it was.
- `site/scripts/test-read-timing.mjs`, `site/scripts/slow-reads.mjs`, `tests/test_session580.py`.
- `warehouse/supabase/migrations/036_slow_read_indexes.sql` and `warehouse/supabase/rollbacks/036_slow_read_indexes.sql`
  (not applied).
