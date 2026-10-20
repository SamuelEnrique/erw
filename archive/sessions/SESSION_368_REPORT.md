# Session 368 report: /api/download pages by key, not by offset

20 October 2026, from about 18:10 UTC, unattended, on samueloldlaptop (the code machine), a session of the chain of 20 October, day (`queue/done/012-day-20-october-code.md`, its "Session 368" paragraph; the night note `docs/state/review_2026-10-20_code.md`, item 3 of "First"). Branch `wip/368-download-keyset` in the worktree `erw-368`, from origin/main at `5b4f13b9`. Model spend USD 0. No pull, no warehouse data written, nothing written to Supabase or Redivis (the route and the check read with the anon key; the route's own limit counter is unchanged).

## Read these first

- **The ten tables download whole now.** On the local build (which reads production Supabase), `check-download.mjs` read every row of the six largest tables and the four that sometimes failed, each count equal to the live set's count taken by the database itself: **10 of 10 files whole, exit 0**. The old route, built from origin/main and run the same way an hour before: **3 of 10** (502 on seven tables, each after 3.2 s, the statement timeout).
- **The bytes did not change.** Five small tables (one of each shape, plus one with a `ba` column and one with an `event` column) and the four mid-size ones that the old route could still serve: the new route's CSV is identical to production's and to the old local build's, byte for byte once the "Downloaded ... at <time>" line's time is masked (the only bytes that differ between any two downloads). The rows come in the same order. Table below.
- **The limit rose from 200,000 to 500,000 rows**, and `/data`'s sentence says so ("up to 500,000 rows"): `ercot_as_prices` is whole in the live set with 338,132 rows, so the old route would have answered it 413 even with a working count. This is the one page change (shots in `docs/brand/review-368/`). With no count, the limit is kept as the rows stream: past it the stream ends in an error, never in a file that looks whole. Lower it if 500,000 is too generous (one line, and the sentence).
- **A table of more than 50,000 rows no longer states its count** on the "Downloaded" line: "N rows or more, read page by page (the count is not taken on a table this large)". A table that ends within its first 50,000 rows (read before the answer starts) keeps the line exactly as before. Of the ten, four state no count now: `carbon_intensity_hourly`, `ercot_as_prices`, `state_generation_mix_monthly`, `eia930_all_generation`.
- **Found, not changed (for your ruling):** the download leaves the `ba` and `event` columns empty although the live set holds them (the route never selected them). `event_window_daily`'s CSV therefore repeats an (entity, variable, ts_utc) once per event with nothing to tell the events apart. Kept as it was, because the prompt asks for the same bytes; the one-line patch is in `runs/chain_oct20d/s368/route_ba_event.patch`.

## What to review

1. https://erw-flame.vercel.app/data : any "Download CSV" of the ten tables, for example https://erw-flame.vercel.app/api/download?table=ercot_as_prices (about 75 MB, a minute) and https://erw-flame.vercel.app/api/download?table=iso_rtm_hub_prices ; the sentence under the catalogue ("up to 500,000 rows").
2. https://erw-flame.vercel.app/board : the board's foot, `ercot_as_prices`' CSV (it failed every time before).
3. `docs/brand/review-368/` (the sentence only).
4. `site/app/api/download/route.ts`, `pages()`.

## What was done

- **The route** (`site/app/api/download/route.ts`). No count query, no offset. Each page starts after the last row of the page before, on the primary key of the shape in the live set (`warehouse/supabase/migrations/001_shapes.sql`, `011_series_event_key.sql`): series `(table_name, entity, variable, ts_utc, event)`, entities `(table_name, entity_id)`, events `(table_name, event_id)`. Source of the key: the migrations (the site's catalogue carries the columns, not the key, so the key is the shape's; no table needed coverage's key columns). PostgREST has no row comparison, so a series page after a row is read in up to three ranges, each a range of the primary key's index: the rest of the row's (entity, variable) (`ts_utc=gte.t` with `or=(ts_utc.gt.t,event.gt.ev)`), then the rest of its entity (`variable=gt.v`), then the entities after it (`entity=gt.e`); a full page goes back to the narrowest range, a short page of the last range ends the table. The key is selected under its own names (`k0:entity`, ...) so that the CSV's cells are built exactly as before (`event` is not one of the selected columns, as before). A page that fails is read again twice (0.5 s, 1 s) before the download fails.
- **The order** is the old one: the old route ordered series by `entity, variable, ts_utc` (unique but for `event`), entities by `entity_id`, events by `event_id`; the key adds `event` last, which the primary key's index already gave. Proven by the identical bytes, `event_window_daily` and `battery_stack_stress_daily` included.
- **Memory.** The stream is pulled (`pull`), a page at a time as the reader takes it, so a slow reader never makes the server hold the table; the cancel ends the reading. The first 50,000 rows (50 pages, at most about 12 MB of text) are read before the answer, so a failure there is still a plain 502 and a small table keeps its count line. Seen locally: the first byte of a large table comes after about 8 to 13 s (those 50 pages).
- **`export const maxDuration = 300`**: `ercot_as_prices` is about 350 reads (59 s locally, 65 s straight from this machine to Supabase); the ask route already sets 120, so the plan allows more than 60.
- **The check** (`site/scripts/check-download.mjs <base> [table ...]`): reads each of the ten tables' whole CSV from the route, parses it by CSV rules as it streams (quoted fields), and checks the answer, a clean end, the provenance and the catalogue's columns, every row's field count, no key twice where the CSV carries the whole key, and the row count against the live set's count taken by the database (`count=exact` in 30-day ranges of `ts_utc` or `event_date`, a range that times out halved; an entities table whole, or in ranges of `entity_id`), and against the count the "Downloaded" line states. It prints coverage.csv's `n_rows` beside it (the whole table: a windowed table holds fewer in the live set). Exit 0 only if every file is whole.
- **The test** (`tests/test_session368.py`): static tests of the route (no `count=`, no `Prefer`, no `content-range`, no offset in its code; the key equals the migrations' primary keys; the three ranges; anon key only; the stream pulled; the count line kept for a small table; the license, limit and catalogue checks before the rows; `maxDuration`), `/data`'s sentence names the route's `MAX_ROWS`, and the check run against `ERW_CHECK_DOWNLOAD_BASE` (skipped when unset; it downloads about 240 MB).

## Byte comparison (`runs/chain_oct20d/s368/compare.txt`)

The "Downloaded" line's time masked (`norm/`), then `cmp`. Production fetched at 18:12 UTC, the old local build at 18:50, the new local build at 19:23.

| Table | Rows | Bytes (each source) | sha256 (masked, first 16) | cmp new vs production / old local |
|---|---|---|---|---|
| ercot_peak_premium_annual (series) | 2,016 | 443,308 | 31b13fa819223925 | identical / identical |
| storage_capacity (entities) | 1,627 | 646,119 | 1543f72f24e6fc4f | identical / identical |
| caiso_grid_emergencies (events) | 1,906 | 626,852 | e7316c326c0e4e37 | identical / identical |
| cost_of_power_monthly (series, `ba`) | 2,304 | 548,702 | 8499b483c6da6300 | identical / identical |
| battery_stack_stress_daily (series, `event`) | 1,890 | 469,233 | 17657a123af6d0a3 | identical / identical |
| eia_fuel_spot_prices | 27,754 | 9,114,217 | 96e5dbf54c963a81 | not fetched / identical |
| event_window_daily | 29,953 | 6,025,659 | a5628d86793d34e0 | not fetched / identical |
| energy_projects | 34,634 | 11,786,340 | 25db4738060b5668 | not fetched / identical |
| iso_dam_hub_prices | 13,072 | 3,818,747 | e946406ce99c4333 | not fetched / identical |

## The ten tables, new route on the local build (`check_download_new_local.out`)

| Table | Rows read | Live set (database count) | coverage.csv | Seconds | MB | Whole | Old route (local) |
|---|---|---|---|---|---|---|---|
| eia930_all_emissions | 46,812 | 46,812 | 4,345,896 | 13.4 | 11.7 | yes | 502 |
| carbon_intensity_hourly | 156,235 | 156,235 | 1,126,793 | 39.3 | 36.6 | yes | 502 |
| ercot_as_prices | 338,132 | 338,132 | 338,132 | 58.9 | 74.7 | yes | 502 |
| state_generation_mix_monthly | 107,560 | 107,560 | 107,560 | 24.0 | 21.6 | yes | 502 |
| eia930_all_generation | 67,274 | 67,274 | 107,208 | 20.3 | 50.3 | yes | 502 |
| iso_rtm_hub_prices | 36,329 | 36,329 | 57,312 | 16.3 | 10.3 | yes | 502 |
| eia_fuel_spot_prices | 27,754 | 27,754 | 27,754 | 8.7 | 9.1 | yes | 200, whole |
| iso_dam_hub_prices | 13,072 | 13,072 | 22,224 | 7.9 | 3.8 | yes | 502 |
| event_window_daily | 29,953 | 29,953 | 29,953 | 8.1 | 6.0 | yes | 200, whole |
| energy_projects | 34,634 | 34,634 | 39,784 (withdrawn rows are not loaded) | 10.5 | 11.8 | yes | 200, whole |

## Checks

| Check | Exit | Result |
|---|---|---|
| `tsc --noEmit` (erw-368) | 0 | |
| `eslint` on the route, the check and `data/page.tsx` | 0 | |
| `tests.test_session368`, `tests.test_session328`, `tests.test_session282` | 0 | 26 tests OK (1 skipped: the live check, no base set) |
| `npm run build` of origin/main (the baseline) | 0 | no statement timeout |
| `check-download.mjs http://localhost:3368` on the old route | 1 | 3 of 10 whole (the baseline) |
| `npm run build` at `b16f8fb4` | 0 | no statement timeout |
| `check-download.mjs http://localhost:3368` | 0 | 10 of 10 whole (times above) |
| `ERW_CHECK_DOWNLOAD_BASE=http://localhost:3368 tests.test_session368` | 0 | 10 tests OK, 343 s |
| Byte comparison, nine tables | 0 | identical (table above) |
| `CHECK_VALUES_PAGES=/data check-values` | 0 | 241 of 241 |
| `check-table-downloads` on `/board`, `/prices`, `/prices?tab=ercot`, `/demand` | 0 | 16 of 16; `/board` now proven on `ercot_as_prices`, its first table (it was "unproven" before) |
| The route's refusals: `table=../x`, an unknown table | 0 | 400, 404 as before |
| Impeccable `detect --json site/app/data/page.tsx` | 0 | no finding |
| Shots of `/data`, 1280 and 390, before (production) and after (the build) | 0 | four, `docs/brand/review-368/` |

`check-download` against production is the orchestrator's, after the landing: `node scripts/check-download.mjs https://erw-flame.vercel.app` (in `site/`), or `ERW_CHECK_DOWNLOAD_BASE=https://erw-flame.vercel.app` with the test. It makes ten downloads of the sixty an hour a visitor may.

## Landing

(the orchestrator's)

## Decisions made without you

- The key is each shape's primary key from the migrations, not a coverage row's columns: every table of a shape shares one key in the live set, and the catalogue has no key column.
- The limit rose to 500,000 rows (from 200,000), checked as rows stream; `/data`'s sentence follows. Needed for `ercot_as_prices` (338,132 rows, whole in the live set).
- The first 50,000 rows are read before the answer starts, so a table within them keeps its exact count line (and its bytes); a larger table's line says the count was not taken. Bounded memory, no second pass over the table.
- `maxDuration = 300` on the route.
- A failed page is read twice more before the download fails.
- `ba` and `event` stay empty in the CSV, as before (the prompt's "same bytes"); the fix is a ruling below.

## For Samuel's ruling

- **Fill `ba` and `event` in the downloads** (the live set holds them; the CSV has had them empty since session 21): `runs/chain_oct20d/s368/route_ba_event.patch`, one line. It changes the bytes of every table that carries either column (`eia930_all_*`, `carbon_intensity_*`, `cost_of_power_*`, `event_window_daily`, `battery_stack_stress_daily` and others), and makes `event_window_daily`'s rows tell their events apart.
- **The limit of 500,000 rows** a download: keep, or choose another (the route's `MAX_ROWS` and `/data`'s sentence; the test pins that they agree).

## Files

- Changed: `site/app/api/download/route.ts`, `site/app/data/page.tsx` (one word of a sentence).
- New: `site/scripts/check-download.mjs`, `tests/test_session368.py`, `docs/brand/review-368/` (four shots and a README), this report.
- Not in git: `runs/chain_oct20d/s368/` (the saved CSVs `prod_before/`, `local_before/`, `local_after/`, `norm/`, `compare.txt`, the check outputs, the build logs, the probes `keyset_probe.mjs` and `catalogue_probe.mjs`, `route_ba_event.patch`).
