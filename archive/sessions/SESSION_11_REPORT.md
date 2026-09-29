# Session 11 report

Energy Research Warehouse (ERW), session 11, run 2026-09-26 (UTC). Supabase is applied and loaded, and the public site is built under `site/`, reading Supabase with the anon key only. Nothing was pushed. No key was printed or committed: `site/.env.local` holds the two site variables and is ignored by git.

## What was built

| Task | Result | Commit |
|---|---|---|
| 0 | Migrations 001, 002 and a new 003 applied. Live set loaded: 66 tables, plus catalogue and sources. **Every count matches the filtered CSVs.** `latest_prices` upsert confirmed. 16 of 16 Supabase backend tests pass. RLS verified with the anon key. The loader now writes only changed rows (see Decisions) | `f34f2da` |
| 1 | Next.js 16 app under `site/`: App Router, TypeScript, Tailwind 4, one design token file (`site/app/tokens.css`) | `0c0a80d` |
| 2 | Pages: `/`, `/prices`, `/prices/[entity]`, `/digest`, `/digest/[date]`, `/data`, `/data/standard`, `/data/methods/[slug]`, `/explorer/ercot-peak-premium`, `/about` | `0c0a80d` |
| 3 | Run locally (production build), 20 screenshots, **188 of 188 rendered numbers equal a direct Supabase query**, `site/README.md` with the Vercel steps | `0c0a80d` |
| 4 | This report | final commit |

## Task 0: Supabase

**Applied.** `apply.py` ran over `SUPABASE_DB_URL`: `001_shapes.sql`, `002_rls.sql`, and `003_columns.sql`, which is new this session. Migration 003 adds `catalogue.columns`, each live-set table's own columns in CSV order (see Errors 1).

**Loaded and reconciled.** `runs/supabase_reconcile.csv` has one row per table.

| Part | Tables | Rows (filtered CSV = Supabase) |
|---|---|---|
| Series (ISO prices last 90 days, EIA-930 last 90 days, fuel spot prices, peak premium) | 56 | 285,315 |
| Entities (EIA-860M, six interconnection queues) | 9 | 45,737 |
| Events (`news_index`) | 1 | 714 |
| `catalogue`, `sources` | 2 | 81, 92 |

- **Result:** 68 of 68 match, 0 mismatch.
- **Empty tables:** 22 of the ERCOT yearly history tables (2015 to 2025) hold 0 rows, because none of their rows falls in the 90-day window. Only the 2026 tables contribute.

**`pg_database_size`:**

| When | Size |
|---|---|
| After the first load | 219.4 MB (230,067,347 bytes) |
| After the second full load | 339.3 MB |
| After the incremental load | 339.4 MB |

- **Why the second load:** it was needed once to fill `catalogue.columns`.
- **Why it grew:** Postgres keeps the old version of every updated row until a vacuum, and the session 10 loader rewrote every row on every run.
- **The fix:** the loader now writes only the difference (Decisions 1). The incremental run wrote 2 rows and deleted 12.
- **Still over the guard:** the space already taken is not returned without a `VACUUM FULL`. I did not run one; see Open questions 1. Until then, `load.py` loads and reconciles every table but exits 1 at the 300 MB check.

**Latest prices.** `latest_prices.py` wrote 39 of 39 hubs and zones from six ISOs, and the log says `upserted 39 rows into Supabase latest_prices`. A query of the table confirmed it: 39 rows, newest interval 2026-09-26 08:00 UTC, `ercot:HB_HUBAVG` 25.18 USD/MWh at 07:30 UTC.

**Backend tests.** `ERW_BACKEND=supabase python -m pytest package/tests/test_backends.py -k supabase`: **16 passed.** The first run failed 2 of 16, and both failures were real bugs in `SupabaseBackend`, now fixed (Errors 1 and 2). The full package suite then passed (389 tests, including the Redivis and Supabase backend tests), and so did the 11 repository tests.

**Row-level security, checked with the anon key against the service key** (counts from the REST API):

| Table | Service key sees | of which internal | Anon key sees | Anon sees internal |
|---|---|---|---|---|
| `catalogue` | 81 | 6 | 75 | 0 |
| `sources` | 92 | 51 | 41 | 0 |
| `series` | 285,315 | 0 | 285,315 | 0 |
| `entities` | 45,737 | 0 | 45,737 | 0 |
| `events` | 714 | 0 | 714 | 0 |
| `latest_prices` | 39 | 0 | 39 | 0 |
| `headers` | 743 | 0 | 743 | 0 |

- **Internal rows are invisible.** Querying the six internal tables by name (`carb_auction_allowance_prices`, `fred_imf_commodity_prices`, `news_stories`, `pjm_rpm_capacity_prices`, `portwatch_chokepoint_transits`, `rggi_auction_allowance_prices`) returns 0 catalogue rows to the anon key.
- **Public rows are visible.** For example, the anon key reads `ercot:HB_HUBAVG` 25.18.
- **What this does and does not test:** the live set holds no internal table (`live_set.yaml` selects none), so the shape tables show that public rows are visible, not that RLS hides rows there. The policy is the same on every table, and `catalogue` and `sources` show it working.
- **Writes were not probed:** a check that the anon key cannot write was refused by the session's permission classifier, so it was not run. Migration 002 grants anon `select` only and revokes `insert`, `update`, `delete` and `truncate`.

## The site

**Data.**
- **One reader:** `site/lib/supabase.ts` is the only code that reads Supabase. It uses PostgREST over `fetch` with `SUPABASE_URL` and `SUPABASE_ANON_KEY`, server-side only (no `NEXT_PUBLIC_` names).
- **Every number** comes from Supabase or from a committed metadata file: `site/data/markets.json` (which tables hold each ISO's prices, and the main hub per ISO) and `site/data/site.json` (the Redivis link and the install lines).
- **Committed markdown** (digests, the data standard, the method document) is bundled at build time by `site/scripts/build-content.mjs`, so no page reads the file system at request time.
- **Missing data:** a failed read or a missing row renders "no data" with its reason. No page has a placeholder value.

**Revalidation.** `/` and `/prices` every 15 minutes (they carry `latest_prices`). `/prices/[entity]`, `/data`, `/digest` and the explorer hourly.

**Design.**
- **Tokens:** one file, `site/app/tokens.css`: background #F7F3EA, text #2E2D29, accent #8C1515, muted #6B665E, borders #D9D2C3; Georgia for headings, Inter for body.
- **Charts:** uPlot for the time series. The sparklines and the box summaries are server-rendered SVG. Charts read the same tokens through CSS variables.
- **Citations:** every chart and table cites its ERW table and, from the catalogue, the source report.
- **Layout:** responsive, checked at 390 px.

**Pages.**
- **`/` (home):** the status strip (75 public tables, 3,602,843 rows, last refresh 2026-09-26 01:27 UTC, 75 of 75 pass). The price board: one main hub per ISO with its interval, and a 7-day sparkline. Henry Hub, WTI and Brent. The digest's top 5 from `docs/digest/latest.md`. The data links.
- **`/prices`:** all 39 hubs and zones, with the latest real-time price and the day-ahead price for the current hour.
- **`/prices/[entity]`:** 30 days of real time and day-ahead, with min, mean and max.
- **`/data`:** the coverage table (public only), the Redivis dataset link and its status, the install lines, and the methodology pages.
- **`/explorer/ercot-peak-premium`:**
  - hub and year selectors (default HB_HUBAVG and the newest complete year, 2025);
  - ten headline metrics;
  - a box summary per time-of-day block;
  - a yearly chart and a monthly chart;
  - a link to the method document.
  It reproduces the thesis values in `docs/methods/ercot_peak_premium.md` for 2025: all_median 25.68, all_p999 311.80, peak_iqr 34.12, midday_min -18.25.
- **`/about`:** the project, the Stanford independent study, the IRW lineage and the license rule.

**Where the data is thin, the page says so:**
- **SPP:** no real-time series table exists, so its sparkline is day-ahead, labeled as such.
- **MISO:** the real-time table holds 3.0 days, so its sparkline says "3.0 days in the ERW table".
- **ERCOT, CAISO, NYISO, ISO-NE:** their real-time sparklines say 5.8 to 5.9 days, because the real-time tables end at the last daily run (2026-09-25).

## Screenshots

Made with `node site/scripts/screenshots.mjs`: headless Chrome over the DevTools protocol, full page, against the production build (`next build`, `next start`). Each page was captured at 1280 px (desktop) and 390 px (mobile). Heights are in CSS px.

| Page | Route | Desktop file | Height | Mobile file | Height |
|---|---|---|---|---|---|
| Home | `/` | `home-desktop.png` | 2007 | `home-mobile.png` | 4109 |
| Prices | `/prices` | `prices-desktop.png` | 2228 | `prices-mobile.png` | 4073 |
| One hub (ERCOT HB_HUBAVG) | `/prices/ercot%3AHB_HUBAVG` | `prices-entity-desktop.png` | 900 | `prices-entity-mobile.png` | 1036 |
| Digest | `/digest` | `digest-desktop.png` | 3946 | `digest-mobile.png` | 6684 |
| Digest by date | `/digest/2026-09-25` | `digest-date-desktop.png` | 4187 | `digest-date-mobile.png` | 6901 |
| Data | `/data` | `data-desktop.png` | 3051 | `data-mobile.png` | 7656 |
| Data standard | `/data/standard` | `data-standard-desktop.png` | 9941 | `data-standard-mobile.png` | 12000, cut (page is 18,142) |
| Method | `/data/methods/ercot_peak_premium` | `data-method-desktop.png` | 3549 | `data-method-mobile.png` | 5699 |
| Explorer | `/explorer/ercot-peak-premium` | `explorer-ercot-peak-premium-desktop.png` | 1821 | `explorer-ercot-peak-premium-mobile.png` | 2594 |
| About | `/about` | `about-desktop.png` | 900 | `about-mobile.png` | 994 |

All 20 files are in `site/screenshots/`. Pages taller than 12,000 px are cut at that height.

## The ten-value check

**Method.**
- **Every number is tagged:** each number the site renders through `components/Num.tsx` carries the Supabase table and key it was read from (`data-check`) and the value as read (`data-raw`).
- **Independent queries:** `site/scripts/check-values.mjs` fetches five pages and queries Supabase's REST API for each key with its own queries, independent of `site/lib/`.
- **Two checks per value:** the value Supabase returns must equal the value the page read, and the page's text must equal that value rounded for display.
- **Result: 188 of 188 values match** (13 on `/`, 72 on `/prices`, 75 on `/data`, 28 on the explorer). The full list is in `runs/site_check_values.txt`.

Ten of them:

| # | Page | Supabase query | Page shows | Supabase returns |
|---|---|---|---|---|
| 1 | `/` | `catalogue`, count of public rows | 75 | 75 |
| 2 | `/` | `catalogue`, sum of `n_rows` over public rows | 3,602,843 | 3602843 |
| 3 | `/` | `catalogue`, newest `last_run` | 2026-09-26 01:27 UTC | 2026-09-26T01:27:24+00:00 |
| 4 | `/` | `latest_prices`, `ercot:HB_HUBAVG`, `spp_rtm` | 25.18 | 25.18 |
| 5 | `/` | `latest_prices`, `spp:SPPNORTH_HUB`, `lmp_rtm_5min` | 2.75 | 2.7501 |
| 6 | `/` | `series`, `eia_fuel_spot_prices`, `eia:henry_hub`, newest | 2.90 | 2.9 |
| 7 | `/prices` | `series`, `ercot_dam_hub_prices`, `ercot:HB_NORTH`, `spp_dam`, 2026-09-26 08:00 | 24.50 | 24.5 |
| 8 | `/data` | `catalogue`, `eia860m_operating_generators`, `n_rows` | 28,605 | 28605 |
| 9 | explorer | `series`, `ercot_peak_premium_annual`, `ercot:HB_HUBAVG`, `peak_iqr`, 2025 | 34.12 | 34.12 |
| 10 | explorer | `series`, `ercot_peak_premium_annual`, `ercot:HB_HUBAVG`, `midday_min`, 2025 | -18.25 | -18.25 |

## Decisions

1. **The Supabase loader writes only the difference.**
   - **How it works:** `load.py` reads the rows Supabase holds for each table and compares them column by column with the selected CSV rows. It upserts only new or changed rows, and deletes rows the selection no longer has: one range delete for rows older than the window, and deletes by key otherwise. `loaded_at` now means the run that last wrote a row.
   - **Why:** the session 10 design rewrote the whole live set every day. With dead row versions, that would have pushed the database toward its 500 MB cap.
   - **Checked before it wrote anything:** a read-only comparison of five tables (every shape) found 0 rows differing.
2. **Migration 003 (`catalogue.columns`).** The shape tables hold every standard column, but a table may use only some of them. `news_index` has no `parties`, `mw` or `price`. With the column list, `SupabaseBackend` returns exactly the table's columns.
3. **`erw.filter` by variable or node skips tables the backend does not hold.** The Supabase live set is a subset of the catalogue, and those tables cannot be read there.
4. **Main hub per ISO on the home page** (`site/data/markets.json`):
   - ERCOT HB_HUBAVG (the thesis hub);
   - CAISO TH_SP15;
   - NYISO N.Y.C.;
   - MISO INDIANA.HUB;
   - SPP SPPNORTH_HUB;
   - ISO-NE .H.INTERNAL_HUB.
   Every hub and zone is on `/prices`.
5. **Sparkline sources.** The real-time table where one exists. For ISO-NE, the hourly real-time table, because the 15-minute table holds only 3 days. For SPP, day-ahead, labeled, because the ERW has no SPP real-time series.
6. **The Redivis link is to the dataset page, with its state stated.** Its URL, `https://redivis.com/datasets/05yh-65frzyhaz`, was read from the Redivis API. It is an unreleased draft with public access `none`, and `/data` says so.
7. **Install lines.** They are clone plus `pip install -e package`, as `package/README.md` documents. A `git+https` line would work only if the repository is public, which is not known.
8. **The site runs with `next build` and `next start`, not `next dev`.** `next dev` rewrites `site/AGENTS.md` with a managed block that contains em dashes when it detects an AI agent. `site/AGENTS.md` explains this.
9. **Scaffold files replaced.** The Next.js default favicon (the Next.js logo) and the scaffold SVGs were removed and replaced by a plain token-colored mark (`site/app/icon.svg`). All of these were created by the scaffold this session, not existing repository files.

## Errors hit

1. **`SupabaseBackend` returned all standard event columns for `news_index`.** The local CSV lacks five of them, so `test_fetch_matches_local[supabase-news_index]` failed. Fixed with migration 003 and the column list.
2. **`filter(variable="spot_price")` failed on Supabase.** Two causes:
   - it tried to read `carb_auction_allowance_prices`, which is not in the live set;
   - after that fix, it failed on the empty ERCOT yearly tables (`KeyError` on an empty frame).
   Both are fixed.
3. **The second full load took the database from 219.4 to 339.3 MB** (Decisions 1). It is over the 300 MB guard until a `VACUUM FULL`.
4. **A `VACUUM FULL`, a read of per-table sizes, and an anon-key write probe were refused** by the session's permission classifier. None was retried by another route. The vacuum statements are in `warehouse/supabase/README.md` for a human.
5. **Site build problems, fixed:**
   - a heredoc ate a backslash in `site/lib/markdown.ts` (a build error);
   - ESLint's React purity rule rejected `Date.now()` in a server component (moved to `renderTime()` in `lib/data.ts`);
   - the day-ahead line was invisible on the 30-day chart, because the 15-minute time axis broke the hourly points apart (day-ahead now spans its gaps as a stepped line).
6. **The screenshot run hung** on the 18,142 px data standard at phone width and 2x scale. Screenshots are now at 1x scale, with a 12,000 px cap and a timeout per step.
7. **`next start` did not restart after a rebuild,** because the earlier server's node process kept the port. I stopped that process (one this session had started) and reran the value check and screenshots on the new build.

## Rerun

```bash
python warehouse/supabase/apply.py
python warehouse/supabase/load.py
python warehouse/connectors/latest_prices.py
ERW_BACKEND=supabase python -m pytest package/tests/test_backends.py -k supabase -v
cd site && npm install && npm run build && npm start
node scripts/check-values.mjs && node scripts/screenshots.mjs
```

## Open questions for the human

1. **Run the `VACUUM FULL` statements** in `warehouse/supabase/README.md` (Supabase dashboard, SQL editor). Then run `load.py` once: it should report about 220 MB and exit 0. Until then, the daily `supabase_load` step fails at the size check (the data itself loads), and after three scheduled runs it will open a streak issue.
2. **Deploy on Vercel** following `site/README.md`:
   - import the repository;
   - set the root directory to `site`;
   - add `SUPABASE_URL` and `SUPABASE_ANON_KEY`;
   - keep "include files outside the root directory" on.
3. **The CAISO latest price is labeled `lmp_rtm_5min`, but it appears to be the 15-minute interval.** Every CAISO interval seen so far starts on a quarter hour, and the newest one starts after the time it was retrieved (08:00 UTC, retrieved 07:56:58). That is how CAISO's 15-minute market publishes a price before its interval. Should `latest_prices.py` name it `lmp_rtm_15min` for CAISO?
4. **Thin real-time windows:**
   - `miso_rtm_hub_prices` and `isone_rtm_zone_prices` hold only 3 days, and SPP has no real-time table;
   - `eia930_erco_demand` and `eia930_nyis_demand` hold 3 days (the EIA forecast gap noted in `docs/platform-tools.md`).
   The site shows what exists. Should these windows be extended?
5. **The daily loader now reads back the whole live set** (about 330,000 rows over REST) to compare it. This is cheap in Supabase terms and slower than the old blind upsert. If run time matters in CI, a per-table content hash could skip unchanged tables.
6. **Is the repository public?** This decides whether a `git+https` install line can be offered on `/data` (and, from session 10, the Actions minutes for the 15-minute workflow).
