# Session 36C report: Supabase headroom, the event key, and COVID-19 in the seven ISO grids

Energy Research Warehouse (ERW), session 36C, run 2026-09-30 from about 07:15 to 08:40 UTC. **Wall time about 85 minutes.**

**API spend: USD 0.00.** No model call. The cost ledger's last row is 05:12 UTC, before this session.

- **No data pull.** The only fetch was one page read as text for the COVID-19 framing: the Governor of California's release of 2020-03-19.
- **Nothing released or deleted.** Nothing was released on Redivis or deleted from it. No force push.
- **Deployed and checked live:** routes 42 of 42, values 1,508 of 1,508.
- **Commits:** a922980 (step 1), 20a021b (step 2), ed46fc3 and 16014d5 (step 3), 41bba26 (prompt archived). The daily job did not land during the session, so there was nothing to merge.

## 1. Supabase headroom

**The change.** The live set's recent window is now **35 days, not 90** (`warehouse/supabase/live_set.yaml`). The site reads at most 34 days of those tables:

| Page | Days read |
|---|---|
| `/prices/<hub>` | 30 |
| `/storage` | 31 |
| Grid pages (EIA-930 generation) | 34 |
| `/emissions` and grid pages (hourly intensity) | 3 to 4 |
| `/markets` | 20 |
| Home | 7 |

- `/ask`, `/data`, the chat tools and `llms.txt` now say 35 days.
- Redivis and the CSVs keep every row.
- `load.py` prints a warning above `warn_mb: 350`. The limit stays at 400.

**Measured per table (after the load and VACUUM FULL):**

| Table | Rows before | MB before | Rows after | MB after |
|---|---|---|---|---|
| eia930_all_emissions | 126,546 | 35.1 | 46,984 | 13.0 |
| carbon_intensity_hourly | 33,646 | 9.3 | 12,542 | 3.5 |
| eia930_all_storage | 10,650 | 6.1 | 4,040 | 2.3 |
| eia930_all_generation | 65,112 | 48.4 | 64,456 | 47.9 |
| iso_rtm_hub_prices, eia930_all_demand, nyiso_rtm_zone_prices, isone_rtm_zone_prices | already about 35 days | 11.4, 10.0, 9.2, 6.7 | unchanged | unchanged |

**Database totals:**

- **After step 1:** 376.6 MB before, **326.3 MB** after the load and VACUUM FULL, meeting the target of 330 MB or less. The `series` table went from 321.9 to 271.5 MB.
- **At the end of the session: 337.4 MB** after this session's last load and VACUUM FULL. That is under the 350 MB warning line, but above the 330 MB target. Of the 11.1 MB rise since step 1:
  - about 4 MB is the 7,794 COVID rows (2.2 MB of heap, plus index);
  - about 7 MB is the wider key of step 2. All 530,592 `series` rows carry an `event` column, and the primary key index is now 50 MB.
  - I did not cut the site's windows further to get back under 330 MB (open question 1).

## 2. The event key

- **The key.** `event_window_daily` is now keyed (entity, variable, ts_utc, event), recorded as decision 32 in `docs/datastandard.md`. Every other series table keeps (entity, variable, ts_utc).
- **What changed to match:**
  - the validator;
  - the archive's key hashes;
  - the table script;
  - the package's uniqueness test and its Supabase reader's order;
  - the Supabase live set: migration 011 gives `series` an `event` column, `''` for every other table, and its primary key includes it. The migration is applied, and the loader writes, compares and deletes by it.
- **Uri is unchanged under the new key.** The rebuilt table's `uri_2021` rows equal the 36B file's 556 rows column for column, apart from `retrieved_at`. This was checked twice: after step 2, and again after the COVID rows were added.
- **The archive** recorded Uri's 556 old-key hashes as deleted and the rows as new under the new hashes. That is the true record of a key change; `restore.py` rebuilds the table from the newer state.

## 3. COVID-19: `covid_2020`

### What was built

**Window and grids:**

- 2020-03-01 to 2020-05-31 (92 days).
- CISO, ERCO, ISNE, MISO, NYIS, PJM, SWPP and US48, each on its local day:
  - ERCO: ERCOT operating days (Central time);
  - SWPP: Central time;
  - MISO: EST all year;
  - ISNE, NYIS, PJM and US48: Eastern time;
  - CISO: Pacific time.

**Baseline:** weekday-aligned, the same weekday 364 and 728 days earlier, as the prompt asked. **The 728-day baseline is not held.** Its days, 2018-03-04 to 2018-06-03, come before EIA's per-BA workbooks start (2018-07-01), and those are the only EIA-930 history the warehouse holds. So the baseline is **2019 alone**. The table's header, the run log and the method page all say so.

**Variables, 7,794 rows:**

| Variable | Rows |
|---|---|
| `demand_mwh`, `demand_min_mw`, `demand_max_mw` (window and baseline days) | 1,469 each |
| `intensity_generation` | 1,351 |
| `demand_mwh_vs_baseline`, `demand_pct_vs_baseline` (unit `pct`, event days) | 733 each |
| `demand_mwh_vs_baseline_week`, `demand_pct_vs_baseline_week` (`freq` `P1W`, dated at the week's Sunday; 13 whole weeks, 2020-03-01 to 05-30) | 101 each |
| `rt_mean`, `da_mean` of `ercot:HB_HUBAVG` (price context) | 184 each |

**The table in all:** 8,350 rows, 556 of them Uri's.

**138 days or variables were left out, each named in the header and log:**

- 107 are SWPP days with missing CO2: `eia930_all_emissions` holds no SWPP rows on those UTC days, so intensity is left out.
- 8 are the 2018 baseline, one line per grid.
- The rest are real gaps:
  - one missing CISO hour (2020-03-12);
  - PJM's 2020-03-08, 1 hour of 23;
  - a MISO hour on 2019-05-31;
  - scattered CO2 hours.
- A week or a day comparison with a missing day, in either year, is left out.

**A fix found in the build.** At first, "complete day = 24 hours" dropped 2019-03-10 and 2020-03-08, the spring change to daylight time, in every grid except MISO. A local day of 23 hours (92 real-time intervals) now counts as complete. Uri's days never cross a change, so its code and rows are untouched.

**Cross-check.** US48's week of 2020-03-01, recomputed from the raw extract's 168 plus 168 hours: -11.8241 pct. This equals the row.

### Each grid's deepest weekly drop against 2019

Each figure is a row of `demand_pct_vs_baseline_week`. The page shows both columns where they differ.

| Grid | Deepest week (row) | Deepest from the week of 2020-03-22 on (row) |
|---|---|---|
| CAISO (`eia930:CISO`) | **-10.7316 pct, week of 2020-04-12** | the same |
| ERCOT (`eia930:ERCO`) | -15.3258 pct, week of 2020-03-01 | **-12.2639 pct, week of 2020-05-24** |
| ISO-NE (`eia930:ISNE`) | -12.4982 pct, week of 2020-03-01 | **-9.4202 pct, week of 2020-04-05** |
| MISO (`eia930:MISO`) | -13.8954 pct, week of 2020-03-01 | **-12.0775 pct, week of 2020-05-17** |
| NYISO (`eia930:NYIS`) | **-11.7677 pct, week of 2020-05-17** | the same |
| PJM (`eia930:PJM`) | **-14.8333 pct, week of 2020-05-17** | the same |
| SPP (`eia930:SWPP`) | -16.9658 pct, week of 2020-03-01 | **-11.5692 pct, week of 2020-05-10** |
| Lower 48 (`eia930:US48`) | -11.8241 pct, week of 2020-03-01 | **-10.6248 pct, week of 2020-05-17** |

Each value is the row's own, to four decimals; the page shows two, with the row's check key.

**Why two columns.** In ERCOT, ISO-NE, MISO, SPP and the lower 48, the literal deepest week is the week of 2020-03-01. That is before California's order of 2020-03-19, and before any other. With one baseline year, 2019's weather is in every comparison, and the warehouse holds no weather for 2019 or 2020. So the page gives the literal deepest week, as the prompt asks. Where that week comes first, it also gives the deepest week from 2020-03-22 on, the first whole week after the order. The page says why, and does not claim to know what caused the early drop.

### The page: `/events/covid-2020`

- **Framing:** California's Governor "issued a stay at home order to protect the health and well-being of all Californians" on 2020-03-19. This quotes the Governor's release (https://www.gov.ca.gov/2020/03/19/governor-gavin-newsom-issues-stay-at-home-order/), read as text. The order's PDF, Executive Order N-33-20, is a scan with no text layer. A sentence about other states' orders was removed because no source I read supports it.
- **One chart:** weekly demand against 2019, in percent, for all eight grids on one axis. The seven ISOs use the site's categorical palette slots; the lower 48 uses the Stanford cardinal accent.
- **A small multiple per grid:** daily demand served in 2020, and 2019 on the same weekday, drawn 364 days later. Each has its deepest-drop line, and links to its `/grid/<iso>` page.
- **ERCOT price context:** real-time and day-ahead daily means.
- **Also on the page:** tier chips, citations and a method link.
- **Listed** on `/events` and in the nav's Events line.

**Site changes that go with it:**

- `series()` takes `event` and orders by it.
- The Uri page now reads `event: "uri_2021"` only. Without this, COVID's 2019 and 2020 rows would have leaked into its year lines.
- check-values series keys take an optional sixth part, the event, and both event pages use it.

### Verify and ship

- **Validator:** `event_window_daily` passes (8,350 rows, 16 variables, 9 entities).
- **Coverage:** 79 tables, 78 validator reports reused. `event_window_daily` is public, derived, sector power;carbon, ISOs CAISO;ERCOT;ISO-NE;MISO;NYISO;PJM;SPP;US48, interval P1D;P1W.
- **Archive:** 8,350 rows.
- **Supabase,** this table only: 8,350 rows match. 331.3 MB before (after step 2, not yet vacuumed), 337.4 MB after the load and VACUUM FULL.
- **Redivis draft (public dataset):** `count(*)` 8,350, equal to the CSV. Nothing released. License check ok.
- **llms.txt:** a question row and the event text. The chat spec is regenerated and `check_spec` passes. The chat's `query` tool filters by `event` through `where`.
- **`docs/methods/events.md`:** the COVID section with the weekday-aligned baseline, the missing 2018 year, the weather caveat, the variables and the page.
- **`tests/`:** 67 of 67.
- **Local checks:** routes 42 of 42, values 1,508 of 1,508 (13 on the COVID page, 7 on Uri's).
- **Live checks:**
  - **First pass:** routes 42 of 42 and values 1,334 of 1,334. The grid pages' queue figures were missing. During Vercel's build, right after the VACUUM FULL, their `energy_projects` read hit a statement timeout (HTTP 500, 57014), and the pages showed that read as failed.
  - **Check of the query:** the same query now takes 0.2 to 0.9 s.
  - **Final pass:** the next deploy (the prompt-archive commit) rebuilt the pages. **Routes 42 of 42, values 1,508 of 1,508.**

## Decisions made without a human

1. **Baseline 2019 alone** for `covid_2020`. The prompt's 2018 offset is kept in the code, and is left out only because the data are not held. Nothing was pulled to restore it.
2. **Weeks are Sunday to Saturday** from the window's first day, 2020-03-01, a Sunday. A week's figure is its seven days' demand over the seven baseline days' demand.
3. **The deepest-drop line gives a second figure** from the week of 2020-03-22 on, where the literal deepest week comes before California's order.
4. **The main chart plots weekly points, not daily ones.** With eight lines, daily noise would hide the comparison. The daily rows are in the table and drawn in the small multiples.
5. **Daylight time:** a 23-hour local day is complete, in `build_covid` only.
6. **Supabase at 337.4 MB** is left as is (open question 1).

## Open questions

1. **Supabase headroom.** 337.4 MB against the 330 MB target, with the warning at 350. The wider key added about 7 MB for every table. Options:
   - trim the recent window to 32 days (the grid pages read 34 days of generation, so they would need to change too);
   - load only the COVID variables the site reads;
   - accept the current size.
2. **The 2018 baseline.** EIA's six-month EIA-930 files for January to June 2018 would restore the 728-day offset. Pull them in a later session?
3. **Weather.** Both events now need historical weather to separate the event from the season: Uri's demand, and COVID's early-March drop against a single baseline year.
4. **Other states' orders.** The page cites only California. A dated list from a primary source, such as each state's order, would let the page mark each grid's own first order.

## Skipped

- Nothing asked for.
