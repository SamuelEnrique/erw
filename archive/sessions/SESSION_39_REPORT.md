# Session 39 report: three more events on the template

Energy Research Warehouse (ERW), session 39, run 2026-09-30 from 10:39 UTC. The events, pages and stores were done by 11:05 UTC. The session then waited for the 14:00 UTC daily run until 13:10, when the watcher was stopped (section 4). **Wall time about 31 minutes of work,** about 2.5 hours in all.

**API spend: USD 0.00, confirmed.** No model call. The cost ledger's last row is 05:12 UTC.

- **No pull, no new table:** every row is in `event_window_daily`.
- **Nothing released or deleted** on Redivis. No force push.
- **Deployed and checked live:** routes 48 of 48, values 1,631 of 1,631.

**What the framing rests on.** Every framing claim quotes a primary source, read as text this session, and each quote was matched against the text before it went on a page. A claim with no text behind it was dropped: two were, below.

## 1. The events

All three are in `event_window_daily` under the same key (entity, variable, ts_utc, event). The baseline is the same weekday 364 and 728 days earlier. Both baseline years are held for all three, because EIA's workbooks start 2018-07-01.

The COVID-19 builder now takes each event's options:

- weekly rows (COVID-19 only);
- the peak hour against the baseline (`demand_max_mw_vs_baseline`, `demand_max_pct_vs_baseline`, new for these three);
- the hub's daily max beside its mean.

Uri's and COVID-19's 8,350 rows are unchanged, apart from `retrieved_at`. The archive took 2,529 new rows and no changed ones. **The table now holds 10,879 rows.**

### `caiso_heat_2020`: CAISO, 2020-08-10 to 2020-08-24 (216 rows, one commit)

- **Headline, per row** (`eia930:CISO`):
  - The peak hour most above the baseline was **+23.50 percent on 2020-08-18** (`demand_max_pct_vs_baseline`), 46,643 MW (`demand_max_mw`).
  - On the outage days it was +10.74 percent (2020-08-14) and +21.58 percent (2020-08-15).
  - The highest intensity was 305.93 kg CO2/MWh on 2020-08-18.
- **Source for the framing:** CAISO, CPUC and CEC, *Final Root Cause Analysis, Mid-August 2020 Extreme Heat Wave*, January 13, 2021 (https://www.caiso.com/Documents/Final-Root-Cause-Analysis-Mid-August-2020-Extreme-Heat-Wave.pdf). Quoted: "the two rotating outages in the CAISO footprint on August 14 and 15, 2020"; "August 17 through 19 were projected to have much higher supply shortfalls".
- **What contradicted the story:**
  - The highest demand against the baseline came on 18 August, not on the outage days.
  - The same report explains why: the shortfalls projected for 17 to 19 August were averted by a statewide mitigation effort and conservation. The page says so.
- **No price chart:** CAISO's 2020 prices are not held, and the page says so.
- **Left out:** three CISO days, each missing one hour in EIA's data: 2020-08-10, 2019-08-13 and 2019-08-25. The comparisons for 2020-08-10, 11 and 23 are missing.

### `elliott_2022`: PJM, MISO, SPP, NYISO, ISO-NE, ERCOT, 2022-12-19 to 2022-12-29 (1,167 rows, one commit)

- **Headlines, per row:**

  | Grid | Peak hour, highest against the baseline | Highest hour of the window |
  |---|---|---|
  | PJM | +41.76% on 2022-12-23 | 135,328 MW on 2022-12-23 |
  | MISO | +39.61% on 2022-12-23 | 101,533 MW on 2022-12-23 |
  | SPP | +50.45% on 2022-12-23 | 47,026 MW on 2022-12-22 |
  | NYISO | +17.18% on 2022-12-24 | 22,004 MW on 2022-12-24 |
  | ISO-NE | +10.80% on 2022-12-24 | 17,382 MW on 2022-12-24 |
  | ERCOT | +65.01% on 2022-12-23 | 73,976 MW on 2022-12-23 |

  ERCOT hub average prices:
  - highest 15-minute real-time price **3,701.72 USD/MWh on 2022-12-23**;
  - highest daily real-time mean 557.53 (12-23);
  - highest day-ahead hour 2,539.16 (12-24).
- **Sources for the framing:**
  - FERC, NERC and the Regional Entities, *Inquiry into Bulk-Power System Operations During December 2022 Winter Storm Elliott* (https://www.ferc.gov/sites/default/files/2024-02/24_Winter-Storm_Elliot_0207_UPDATE.pdf). Quoted: the storm blanketed "most of the eastern United States on December 23 and 24, and did not subside until December 26"; "there were 90,500 MW of coincident unplanned generating unit outages, derates and failures to start".
  - PJM, *Winter Storm Elliott Event Analysis and Recommendation Report*, 2023-07-17 (https://www.pjm.com/-/media/DotCom/library/reports-notices/special-reports/2023/20230717-winter-storm-elliott-event-analysis-and-recommendation-report.pdf). Quoted: "almost a quarter of the generation capacity", 47,000 MW, on forced outages; load on Dec. 23 "came in at about 136,000 MW" against a forecast of about 127,000; PJM "remained reliable, was able to serve its customers"; TVA and Duke "were both in an EEA-3 and shedding load".
- **What agreed.** PJM's highest EIA hour, 135,328 MW on 12-23, matches the report's "about 136,000 MW".
- **What contradicted the story:**
  - PJM's report says SPP "set a new winter peak" on Dec. 23.
  - In EIA-930, SPP's highest hour of the window is 18:00 Central on 2022-12-22 (47,026 MW), which is 00:00 UTC on the 23rd. On the 23rd itself (Central) SPP's highest hour was 45,146 MW.
  - The page states both and does not claim which count the report used.
  - The forced outages of Dec. 24 do not show in PJM's demand served, since PJM served its load. ISO-NE barely moved.
- **Dropped:** "outside these six grids" for the utilities that shed load, which is my inference, replaced by PJM's own sentence naming TVA and Duke.
- **Left out:** MISO 2021-12-27 misses an hour, so MISO's comparison for 2022-12-26 is missing. SWPP's CO2 is missing on several December days of 2020 and 2021.

### `ercot_heat_2023`: ERCOT, 2023-08-01 to 2023-09-10 (1,146 rows, one commit)

- **Headlines, per row:**
  - The highest hour of the window was **85,432 MW on 2023-08-10**.
  - On the emergency day, 2023-09-06, the highest hour was **82,692 MW**.
  - The peak hour most above the baseline was +30.31 percent on 2023-08-13; the day most above it, +32.81 percent on 2023-09-08.
  - The highest 15-minute real-time price was **5,075.46 USD/MWh on 2023-09-06**; the highest daily mean 902.56 (08-17); the highest day-ahead hour 4,191.66 (08-25).
- **Sources for the framing:** ERCOT's two releases of 2023-09-06:
  - https://www.ercot.com/news/release/2023-09-06-ercot-has-initiated: the EEA 2;
  - https://www.ercot.com/news/release/2023-09-06-ercot-has-exited: quoted "No power outages associated with the ERCOT power grid were necessary"; "Texas set a new September peak demand record today of 82,705 MW driven by extreme heat across the state"; and the chief executive's "High demand, lower wind generation, and the declining solar generation during sunset led to lower operating reserves on the grid".
- **What contradicted the story:**
  - The emergency did not come on the day of the highest demand. EIA's highest hour that day, 82,692 MW, sits 13 MW under ERCOT's September record. The window's highest hour came on 2023-08-10.
  - The price marks the emergency.
  - ERCOT's own release puts the cause in supply as well as demand.
- **Dropped:**
  - "with no emergency" for 2023-08-10: no text read states it.
  - "an hour's average, so a little below ERCOT's figures": not sourced; now "need not equal".

## 2. The /events index

Five cards, each with its dates, its grids and one headline number read from the table with its check key:

| Event | Headline |
|---|---|
| Uri | 9,051.55 USD/MWh (2021-02-17) |
| COVID-19 | lower 48, -11.82 percent (week of 2020-03-01) |
| CAISO | +23.50 percent (2020-08-18) |
| Elliott | PJM 135,328 MW (2022-12-23) |
| ERCOT 2023 | 5,075.46 USD/MWh (2023-09-06) |

## 3. Verify and ship

- **Validator:** `event_window_daily` passes.
- **Coverage:** 82 tables; `event_window_daily` 10,879 rows, 2018-08-13 to 2023-09-10.
- **Archive:** 2,529 rows.
- **Supabase,** this table only: 10,879 rows match. **341.7 MB before, 342.8 MB after** the load and VACUUM FULL.
- **Redivis draft (public):** `count(*)` 10,879. Nothing released. License check ok.
- **llms.txt:** a question row and the three events. The chat spec is regenerated and `check_spec` passes.
- **check-routes and check-values:** they cover the index and the three pages (55 values on the event pages).
- **`tests/`:** 75 of 75.
- **Local and live checks:** routes 48 of 48, values 1,631 of 1,631.

**A site fix.** The first local build after the VACUUM FULL lost the grid pages' queue reads again, to the anon role's 3 s statement timeout. Migration 012's index had fixed the query itself (23 ms), but a build right after a VACUUM FULL meets cold tables with seven grid pages at once. The site's one Supabase reader (`site/lib/supabase.ts`) now retries a statement timeout (Postgres 57014) once, after a second. Afterwards the local and live counts were whole.

## 4. Run health and the 14:00 UTC daily run

**Whether the 14:00 UTC run of 2026-09-30 landed and passed is not known to this report.**

- **When I last checked:** at 13:10 UTC, no run of `daily-prices.yml` had been created since 2026-09-29, and origin/main had no new commit (GitHub Actions API).
- **Why I could not keep watching:** the watcher polling for it was stopped by Claude Code because the machine ran low on memory. I did not restart it, as the notice asked.
- **Timing:** the report is pushed without the result. Recent scheduled runs started late, at 17:58, 20:18 and 18:58 UTC, and took about an hour.
- **Nothing to merge:** no daily job landed during the session.

**The last scheduled run failed the gate.** Run 36615905147 (2026-09-29, 18:58 to 19:53 UTC, code daca511) failed in "Pull, validate, rebuild coverage" and committed nothing. Issue #6 holds the log tail:

- **The error:** `ValueError: price_board_carbon: input tables ['carb_auction_allowance_prices'] are not in warehouse/output`.
- **Why the input was missing:** the CARB connector has failed on the runner for days (issue #3: HTTP 202), so its CSV was never there.
- **The fix is already on main.** `apply_derived` in `warehouse/metadata/build_coverage.py` takes an absent input's license from the previous coverage (session 36A), and that run used code from before it. So today's run should pass this step. That is expected, not observed.

**Run health otherwise:**

- **The last passing run:** 2026-09-28 23:16 UTC (workflow_dispatch, commit 6affd1f).
- **Open issues, each a market failing three daily runs:**
  - #3, `carb_auction_allowance_prices`: CARB's PDF answers HTTP 202;
  - #4, `nyiso_interconnection_queue`: HTTP 202;
  - #5, `ercot_large_load_queue`: ERCOT publishes no request-level list.
- **The 29 September run's annotations:**
  - `energy_projects` and `ercot_peak_premium` skipped, their inputs absent in CI (ruling 3 of session 10);
  - Node.js 20 is deprecated for the workflow's actions;
  - the ubuntu-latest label moves to Ubuntu 26 from 2026-10-19.

**Wall time:** 10:39 to about 11:10 UTC for the session's work (about 31 minutes). Waiting for the daily run until 13:10 UTC brings the total to about 2.5 hours.

## Decisions made without a human

1. **One builder.** The three events reuse the COVID-19 code path with per-event options, so Uri's and COVID-19's rows stay as they were.
2. **The headline is the peak hour against the baseline.** Heat waves and cold snaps are stories of the peak hour, and the "deepest or highest day against baseline" is a row of `demand_max_pct_vs_baseline`. Daily demand against the baseline is in the table too.
3. **Contradictions are stated beside the story they contradict,** with the source's own words where it explains them (CAISO), and without choosing where the warehouse cannot tell (SPP's peak date).
4. **The FERC-NERC report is cited from its February 2024 update on ferc.gov.** The FERC page itself answered HTTP 403 to a script; the PDF did not.
5. **A one-retry rule in the site's Supabase reader,** for statement timeouts only.

## Open questions

1. **The 14:00 UTC run of 2026-09-30:** did it land and pass the gate? It had not started when this report was written.
2. **SPP's winter peak date:** EIA-930's hourly data against SPP's own record. An SPP source would settle it.
3. **Weather** would explain CAISO's 18 August and ERCOT's 13 August; `weather_obs_hourly` starts in 2026.
4. **Load shed amounts** (CAISO 14 and 15 August 2020, and the Southeast in Elliott) are not in the warehouse, so demand served understates demand on those days.
5. **Supabase:** 342.8 MB of the 350 MB warning line. The next table needs a window trimmed first.

## Skipped

- New tables and pulls, as instructed.
