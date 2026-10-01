# Session 49 report: interchange and the 3D network, a year of hub prices, weather in the event studies, Texas leases

Energy Research Warehouse (ERW), session 49, run 2026-10-01 from 03:11 UTC to about 08:10 UTC. **Wall time about 4 hours 59 minutes.**

**API spend: USD 0.00, confirmed.** No model call (the chat spec was regenerated with `ask.py --export-spec`, which makes no API call). No force push. Nothing released on Redivis: every upload wrote a draft.

**The gate was open** (the user's instruction: "no routing"), so every part ran.

| Part | Done | Rows against the ceiling | License |
|---|---|---|---|
| 0: weekly vacuum, `upload.py --tables`, /deals at a month's start | yes | no pull | |
| A: interchange and /network (session 42) | yes | 131,008 reported, 127,560 written, of 150,000 (18 days; 30 days hold 236,808) | public |
| B: a year of hub prices | yes | 251,366 of 1,500,000 | public (each ISO's own terms, as their live tables) |
| C: NOAA ISD stations | yes | 99,479 returned of 100,000 (176,885 values kept); 12 station ranges left out | public domain |
| C: EIA-930 2018 January to June | yes | 60,084 of 100,000 | public |
| D: RRC leases, Martin County, 24 months | yes | 212,252 of 500,000 | **internal** |

## Part 0

### 1. The weekly vacuum (approved)

- **Workflow:** `.github/workflows/weekly-vacuum.yml` runs Sundays at 10:00 UTC, and on workflow_dispatch.
  - It shares the daily run's concurrency group, so a vacuum never runs during a daily load.
- **The script:** `warehouse/supabase/vacuum.py` runs `VACUUM (FULL, ANALYZE)` on the six shape tables (series, entities, events, headers, catalogue, sources). It loads nothing.
  - It records `pg_database_size` before and after, and each table's size, in `run_status.csv` (connector `supabase_vacuum`). The workflow commits that file.
- **Unchanged:** the daily load keeps its plain `VACUUM (ANALYZE)`.
- **Runbook:** a paragraph in `docs/runbook.md`.
- **Dispatched once in this session** (run 36823130132, 06:07 UTC, success in about 2 minutes), before the final cost-of-power load:
  - **Supabase 394.6 MB to 356.2 MB.**
  - The workflow committed the sizes (8052dbd), merged here.

### 2. `upload.py --tables`, and `event_study_estimates` in the public draft

- **`--tables NAME...`** uploads only the named tables, each to its dataset by license. No metadata tables are uploaded.
  - `merge_headers` replaces only those tables' lines in the draft's `erw_headers`. Every other table's lines are kept as the draft holds them.
  - Placeholder lines are left out on restore.
- **`event_study_estimates`:**
  - Uploaded at 03:35 UTC (1,485 rows, session 47's table).
  - Re-uploaded after Part C with 2,320 rows, `count(*)` equal. Nothing released.
- **Found on the way:** daily run 14's commit had dropped `event_study_estimates` from coverage, because it was built from a checkout before session 47 added the table. Coverage was rebuilt (37a0d6e).

### 3. `/deals` at the start of a month

- **The change:** when no deal is dated in the current month yet, the month block shows the previous month. It says so: "No deals dated {current} yet, so these are {previous}'s, the month before."
- **The check keys** (`deals|month_*|<month>`) carry the month shown, so check-values recomputes the right month.

## Part A: interchange and the 3D network (session 42's plan)

**Done.** The full account is in `archive/sessions/SESSION_42_REPORT.md`, which now holds both runs:
- the first, which stopped at the gate on 2026-09-30, restored in full;
- this rerun, as its own section.

**Rows:**

| | Rows |
|---|---|
| Ceiling | 150,000 |
| The approved 30 days hold | 236,808, over the ceiling: not pulled |
| Pulled: the latest 18 complete UTC days, 2026-09-13 to 2026-09-30 (the API's count) | 131,008 |
| Written | 127,560 |
| Incomplete pair-days, not written | 465 |

- **Directed pairs:** 341. License public.
- **Field names checked first:** `fromba`, `toba`. The route has no respondent column, so the connector has its own pager.
- **The sign:** positive means exports by the reporting BA, checked against net generation minus demand.
  - Mean absolute difference: ERCO 1.6 MW, NYIS 0.4, ISNE 0.7. CISO, MISO, PJM and SWPP differ by 978 to 3,199 MW.
  - The opposite sign is far worse for every BA.
- **The network:**
  - 69 nodes (EIA's regions and country totals left out), 156 pairs, 168 hours.
  - Each pair is counted once, from the BA whose code sorts first, with the other's report sign-flipped where that BA is silent.
  - Positions come from a seeded 3D layout, fixed on the page.
- **`/network`:** 3d-force-graph, first under Grid, linked from each grid page, with a WebGL fallback.
- **Supabase: nothing loaded.** The nodes table stays in the committed JSON, since the live set was near its line.
- **Pages, old and new:** `/network` is new. Each `/grid/<iso>` page gains a link to it.

## Part B: a year of hub prices

**Done.**

### Pull b

- **Connector:** `warehouse/connectors/hub_history.py`. Each ISO's own pull in `iso_prices.py` is narrowed to the approved hubs, day-ahead and real-time, from 2025-09-01.
  - Days are pulled in parallel a month at a time (CAISO one at a time: OASIS resets under parallel load).
  - Completeness is checked per day.
  - It is resumable: held months are skipped.
- **The table:** `iso_hub_prices_history`. Public, each ISO's own terms, as their live tables.
- **Rows:** 251,366 of the 1,500,000 ceiling.

| Market | Rows | Days |
|---|---|---|
| CAISO day-ahead (SP15, NP15) | 18,862 | 2025-09-01 to 2026-09-30 |
| CAISO real-time | 75,448 | 2025-09-01 to 2026-09-30 |
| ISO-NE day-ahead | 9,480 | 2025-09-01 to 2026-10-01 |
| ISO-NE real-time | 34,944 | 2025-09-01 to 2026-10-01 |
| MISO day-ahead | 9,456 | 2025-09-01 to 2026-09-30 |
| MISO real-time (hourly) | 9,456 | 2025-09-01 to 2026-09-30 |
| NYISO day-ahead | 9,480 | 2025-09-01 to 2026-10-01 |
| NYISO real-time | 36,864 | 2025-09-01 to 2026-10-01 |
| SPP day-ahead | 9,456 | 2025-09-01 to 2026-10-01 |
| SPP real-time | 37,920 | 2025-09-01 to 2026-10-01 |

- **Gap days, not written:** each is a gap row in `run_status.csv`.
  - ISO-NE real-time: 31 days. The final 5-minute files miss an interval or a day.
  - NYISO real-time: 11 days (a missing RTD stamp).
  - CAISO: 1 day in each market (2025-11-02, the 25-hour day, holds 24 rows).
  - SPP: day-ahead 2026-06-04 (the file failed to parse after 4 attempts: KeyError 'Interval End'); real-time none.
- **How it was run:** four backfills, in parallel where the ISOs allow:
  - MISO, NYISO and ISO-NE in one run (20261001T035305Z), stopped after ISO-NE so that it would not pull CAISO beside the CAISO run;
  - CAISO (20261001T050229Z) in its own directory, merged by key;
  - SPP (20261001T035306Z, resumed as 20261001T060050Z, and 20261001T072517Z for August and September in parallel) in its own directory, merged by key.
- **Status rows:** the stopped run never wrote its run_status rows. They were rebuilt from its log: 6 markets, 42 gap days.
- **Files:** raw files and logs were moved into `warehouse/raw/hub_history_<iso>/` and `warehouse/output/logs/`, and the header names them.
- **Kept out of Supabase:** the history is in no live-set rule, and a test checks it.
- **The daily run** appends the consolidated live tables' rows of these hubs to it (`hub_history.py append`, after consolidation). It is restored from the Redivis draft before each run.
- **Redivis:** uploaded to the public draft (`count(*)` equal). Nothing released.

### `cost_of_power_*`, rebuilt with twelve months for every ISO

- **The builder** reads `iso_hub_prices_history` first for the five ISOs, then their rolling tables.
  - ISO-NE's 15-minute real-time prices are averaged to hours where its live table is hourly.
  - NP15 is built beside SP15, weighted by CAISO's demand.
- **Rows:**
  - monthly: 977 to 1,593;
  - hourly profile: 1,008 to 4,032;
  - carbon: 309 to 495.
- **Validator:** PASS.

**The ranked month.** The prompt asked for the latest month complete at every ISO.
- **The problem:** no such month exists. From 2025-09 on, ISO-NE's Internal Hub is complete only in January and March 2026, NYISO's N.Y.C. in four months, and MISO's Indiana Hub misses hours in January and June. Those are the ISOs' own gap days.
- **Decision:** the page uses, in order:
  1. the latest month complete at every hub;
  2. failing that, the latest month in which every hub holds at least 90 percent of its real-time hours, labelled with the hours held;
  3. failing that, the latest month every ISO holds.
- **The rules and their reason** are in `docs/methods/cost_of_power.md`.

**`/cost-of-power`, old and new defaults:** 100 MW, load factor 0.9, 90 days.

| ISO (main hub) | Ranked, old: 2026-09 (partial) | Ranked, new: 2026-08 | Flat price, old (months) | Flat price, new (2026-08) | Flat cost old, USD | Flat cost new, USD | Cheapest 80%, old | Cheapest 80%, new | 80% cost old, USD | 80% cost new, USD |
|---|---|---|---|---|---|---|---|---|---|---|
| ERCOT | 40.16 | 36.70 | 32.10 (2025-10 to 2026-09 (12)) | 35.45 | 6.24 million | 6.89 million | 25.81 | 27.60 | 4.01 million | 4.29 million |
| CAISO | 38.73 | 56.94 | 47.32 (2026-08 to 2026-09 (2)) | 55.33 | 9.20 million | 10.76 million | 38.08 | 47.84 | 5.92 million | 7.44 million |
| ISO-NE | 41.01 | 57.00 | 39.77 (2026-08 to 2026-09 (2)) | 53.66 | 7.73 million | 10.43 million | 37.57 | 48.51 | 5.84 million | 7.54 million |
| MISO | 96.83 | 46.99 | 78.61 (2026-08 to 2026-09 (2)) | 44.58 | 15.28 million | 8.67 million | 41.05 | 36.83 | 6.38 million | 5.73 million |
| NYISO | 44.93 | 58.53 | 42.39 (2026-08 to 2026-09 (2)) | 54.88 | 8.24 million | 10.67 million | 38.89 | 47.23 | 6.05 million | 7.35 million |
| SPP | 32.02 | 42.58 | 30.58 (2026-09 (1)) | 38.90 | 5.94 million | 7.56 million | 25.03 | 29.08 | 3.89 million | 4.52 million |

- **Units:** USD/MWh unless a column says USD.
- **The two defaults:** flat energy 194,400 MWh (100 MW x 0.9 x 24 x 90); the cheapest 80 percent of hours, 155,520 MWh.
- **Old ranking:** 2026-09, partial for every hub (SPP 96 of 720 hours, the others 647 or 648). Its flat prices mixed 12 months (ERCOT) with one or two late-summer months (the others).
- **New ranking:** every ISO on 2026-08. Every hub holds all 744 hours, except ISO-NE (720).
- **What the numbers show:**
  - On the same month, ERCOT is the cheapest hub for a flat load (35.45) and CAISO the dearest (55.33).
  - MISO's old figure (96.83 load-weighted) was one partial September.

**`/learn/bill`:** PG&E's wholesale reference is now NP15, labelled "CAISO's NP15 zone, weighted by CAISO's whole demand".

| | Hub | Month | Load-weighted real-time, USD/MWh |
|---|---|---|---|
| Old (session 48) | SP15 | 2026-09, partial (648 of 720 hours) | 38.73 |
| New | NP15 | 2026-08, complete | 46.99 |

SP15 for the same month: 56.94 USD/MWh.

### The shape-premium draft (`/reports/draft/shape-premium`, internal)

- **A new section, "Twelve months, six hubs":** the twelve months ending with the latest month every hub holds. For each hub it gives the count of complete real-time months, how many had a positive premium, the mean premium, and USD per MW (grid-shaped over flat). Every number has a `shape|` check key.
- **Hubs with no complete month** are left out of its sentences.
- **The rolling-window caveats** of session 48's draft were replaced.

| Hub | Complete months | Positive | Mean premium, USD/MWh | Grid-shaped over flat, USD per MW |
|---|---|---|---|---|
| ISO-NE, the internal hub | 2 | 2 | 6.99 | 10,400.03 |
| NYISO, New York City | 4 | 4 | 4.21 | 12,501.80 |
| MISO, Indiana Hub | 9 | 9 | 1.77 | 11,581.55 |
| SPP, SPP North | 10 | 10 | 1.46 | 10,742.35 |
| ERCOT, the hub average | 10 | 9 | 1.33 | 9,767.91 |
| CAISO, SP15 | 7 | 4 | 0.35 | 1,815.57 |

- **The window:** October 2025 to September 2026, real-time, complete months only.
- **The premium:** positive in every complete month at ISO-NE, NYISO, MISO and SPP; at ERCOT in 9 of 10, at CAISO in 4 of 7.
- **The month counts differ by hub,** so the sums are not a ranking. ISO-NE's figures rest on two months.

## Part C: weather and the 2018 baseline in the event studies

**Done.**

### Pulls

**c. NOAA NCEI ISD** (`warehouse/connectors/noaa_isd.py`, table `noaa_isd_hourly`, public domain):
- **Rows:** 99,479 returned by the service of the 100,000 ceiling; 176,885 values kept (temperature and dew point, degF).
- **Stations:** ten. Primary stations were pulled first, before the second stations.
- **Left out to stay under the ceiling** (12 station ranges, listed in the header):
  - IAH: ERCOT's 2023 heat and its two baselines, and COVID-19 and its two baselines;
  - LAX and ORD: COVID-19 and its two baselines.
- **Unit:** degF, because degC is not in the validator's vocabulary.
- **Decision 33:** adds `degF-day`, `bbl` and `Mcf` to the unit vocabulary.

**d. EIA-930 six-month file, 2018 January to June** (`warehouse/connectors/eia930_history.py`, table `eia930_all_history`, public):
- **Rows:** 60,084 of the 100,000 ceiling.
- **Content:** seven ISO BAs, demand and net generation, the Adjusted columns.
- **US48:** the prompt said eight BAs, but US48 is not a balancing authority in that file, so seven.

### `event_window_daily`

- **COVID-19's 728-day baseline is restored:** the seven BAs have 275 or 276 days (they had 183 or 184). US48 keeps 184.
- **Station-days per station:** `temp_mean_f`, `temp_min_f`, `temp_max_f`, `hdd_65f` and `cdd_65f`.
  - Degree days use (max + min) / 2, the National Weather Service's daily mean.
  - A day needs readings in 20 or more clock hours.
- **Rows:** 12,585 weather rows; 25,580 rows in all.
- **Supabase:** loaded, **382.1 MB to 393.5 MB**.

### `event_study.py`

- **`dow_year_temp_v1`:** the grid's degree days and their squares are added.
- **`dow_trend_v1`:** a linear trend in place of the year effects, pooled only, as a robustness row.
- **Dependent columns** are dropped the same way in Python, TypeScript and the notebook (greedy Gram-Schmidt, tolerance 1e-9). For example, HDD is all zero in August.
- **Estimates:** 2,320.
- **Parity:** TypeScript against Python, 2,060 of 2,060 estimates equal; the notebook reproduces both specifications.

### The estimates

Pooled effect per day of the window, MWh a day (USD/MWh for the hub price). Weather share = 1 - controlled / original, given only when the two share a sign and the controlled estimate is no larger.

| Event | Grid | Original (95% interval) | Controlling for temperature (95% interval) | Weather share | Linear trend row |
|---|---|---|---|---|---|
| caiso_heat_2020 | CAISO | 83,812 (46,906 to 120,719) | 24,747 (900 to 48,593) | 70.5% | 117,003 |
| uri_2021 | ERCOT | 155,795 (53,421 to 258,169) | 30,284 (-28,963 to 89,530) | 80.6% | 140,870 |
| uri_2021 | ERCOT hub price | 2,294 (686 to 3,902) | 288 (-560 to 1,135) | 87.5% | 2,244 |
| elliott_2022 | ERCOT | 269,582 (156,949 to 382,214) | 72,488 (31,734 to 113,243) | 73.1% | 245,939 |
| elliott_2022 | ISO-NE | 10,549 (1,185 to 19,913) | 3,907 (-1,811 to 9,624) | 63.0% | -2,989 |
| elliott_2022 | MISO | 236,279 (115,486 to 357,072) | 125,413 (32,144 to 218,681) | 46.9% | 269,047 |
| elliott_2022 | NYISO | 24,803 (12,283 to 37,322) | 5,921 (-3,788 to 15,631) | 76.1% | 26,280 |
| elliott_2022 | PJM | 387,000 (256,964 to 517,036) | 134,171 (24,429 to 243,913) | 65.3% | 560,038 |
| elliott_2022 | SPP | 146,161 (80,505 to 211,817) | 46,809 (20,370 to 73,248) | 68.0% | 179,503 |
| elliott_2022 | ERCOT hub price | 56.52 (-19.85 to 133) | -28.14 (-61.31 to 5.03) | none | 41.13 |
| ercot_heat_2023 | ERCOT | 271,284 (239,603 to 302,966) | 133,743 (113,032 to 154,454) | 50.7% | 242,063 |
| ercot_heat_2023 | ERCOT hub price | 129 (65.61 to 192) | 78.18 (7.02 to 149) | 39.2% | 55.00 |
| covid_2020 | CAISO | -11,272 (-21,303 to -1,240) | -20,589 (-27,829 to -13,350) | none | 67,252 |
| covid_2020 | ERCOT | -9,454 (-34,624 to 15,715) | 11,029 (-1,102 to 23,160) | none | -3,983 |
| covid_2020 | ISO-NE | -23,722 (-29,321 to -18,123) | -22,763 (-26,402 to -19,124) | 4.0% | -4,094 |
| covid_2020 | MISO | -164,978 (-190,297 to -139,658) | -134,648 (-154,769 to -114,526) | 18.4% | -58,147 |
| covid_2020 | NYISO | -38,088 (-44,059 to -32,116) | -28,931 (-33,494 to -24,368) | 24.0% | -12,055 |
| covid_2020 | PJM | -203,166 (-240,236 to -166,097) | -136,186 (-160,229 to -112,142) | 33.0% | -70,303 |
| covid_2020 | SPP | -49,682 (-60,507 to -38,857) | -36,515 (-44,685 to -28,345) | 26.5% | -9,776 |
| covid_2020 | Lower 48 | -606,601 (-767,512 to -445,689) | no station |  | none (one baseline year) |
| covid_2020 | ERCOT hub price | -4.33 (-7.50 to -1.16) | -3.71 (-6.77 to -0.66) | 14.3% | -7.29 |

**What the numbers show:**

- **Every heat wave and cold snap:** demand estimates fall by 47 to 81 percent once temperature is controlled.
  - Uri's ERCOT demand, and Elliott's in ISO-NE and NYISO, then have intervals that include zero.
  - Uri's hub price falls from 2,293.84 to 287.79 USD/MWh, and its interval includes zero.
- **ERCOT's 2023 heat** keeps intervals that exclude zero for both demand and price.
- **COVID-19, with the 2018 baseline restored:**
  - Every grid's original estimate is negative; ERCOT's interval includes zero.
  - With temperature, MISO, NYISO, PJM, SPP and ISO-NE shrink by 4 to 33 percent.
  - CAISO's grows.
  - ERCOT's turns positive, with an interval that includes zero.
- **COVID-19's originals changed** from session 47's because of the second baseline year: CISO +14,921 became -11,272, and PJM -158,686 became -203,166.

### Pages, old and new

- **Each `/events` page:**
  - adds a sentence with the temperature-controlled estimate and its interval;
  - adds a second sentence: either "The weather terms account for X percent of the estimate without them", or, where the two disagree in sign or the controlled estimate is larger, that no share can be put down to weather;
  - adds a column to the table.
- **`/events/covid-2020`** now reads its original estimates on two baseline years.
- **Where the rest is written up:**
  - the method (`docs/methods/event_study.md`): both specifications, the sentence rule, and session 49's results beside session 47's;
  - `docs/methods/events.md`: the baseline and the weather rows;
  - llms.txt: the new tables.

## Part D: Texas leases into the lease tool

**Done, internal.**

### The RRC's terms, read first

| Page | What it says |
|---|---|
| Data sets page (https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/) | "The following data sets are available from the Railroad Commission of Texas at free of charge." |
| Site policies | "The Railroad Commission of Texas (RRC) provides information via this website as a public service." It disclaims liability. "The RRC has no restrictions on linking to our website as long as a fee is not charged to access our material." |

- **No page read grants reuse or redistribution,** so per the prompt the license is **internal**.
- **What that means in practice:**
  - The table goes to the internal Redivis dataset only.
  - It is not in git, the public database or any site JSON.
  - The archive copy is in the private bucket.

### Pull e: the dump and the pilot county

**The pull** (`warehouse/connectors/rrc_production.py`):
- **The dump:** the RRC's Production Data Query dump, PDQ_DSV.zip, 3,847,917,794 bytes, from the RRC's public file share (a GoAnywhere form post).
  - Streamed to `warehouse/raw/rrc_pdq/20261001T041028Z/` with a SHA-256 manifest. It took 28 minutes.
- **The dump's range:** production months 1993-01 to 2026-07, extracts of 2026-09-18.
- **The table read:** OG_COUNTY_LEASE_CYCLE, 76,981,666 lines, read line by line from the zip in 133 s.

**The pilot county: Martin**, chosen by the dump's own county table (OG_COUNTY_CYCLE). It is the county of the Permian districts (08, 7C, 8A) with the most oil over the latest 24 months, 2024-08 to 2026-07:

| County | Oil, bbl |
|---|---|
| **Martin** | 510,799,965 |
| Midland | 482,773,827 |
| Loving | 222,533,157 |
| Upton | 219,586,856 |
| Howard | 185,983,539 |

### The table

**`rrc_lease_production_monthly`:**
- **Rows:** 212,252 of the 500,000 ceiling; 4,828 leases of 61 operators; validator PASS.
- **Granularity:** the RRC reports production by lease, not by well. So the table is by lease, named for what it holds (the plan said "well").
- **Variables:** oil leases get `oil_bbl` and `casinghead_gas_mcf`; gas leases get `gas_mcf` and `condensate_bbl`.
- **Only filed reports** are written.
- **`x_wells`:** the wells the RRC lists on the lease (OG_WELL_COMPLETION). 2,714 of the leases have one well.
- **Where it went:**
  - archived (212,252 rows, private bucket);
  - in coverage (internal, oil;gas);
  - uploaded to the **internal** Redivis draft, `count(*)` equal.

### "Load a real lease"

- **Where:** `/severance/lease/real`, behind the internal token (404 without it), noindex.
- **How it works:**
  1. Pick an operator, then a lease.
  2. The lease tool opens on the lease's real months, priced at the warehouse's monthly WTI and Henry Hub means, with the rules' flags.
- **Where the data comes from:** the table is read on the server from the warehouse's output directory. On Vercel it is absent, and the page says so.
- **A lease of several wells is marked:** the tool reads it as one well, so per-well thresholds are tested on the lease's volume.
- **Tried locally** with a throwaway token on lease O-10-39407 (one well, 23 months): the low-producing oil lease credit was flagged at 1.74 bbl per well per day. It showed no saving, because the rules file has no certified price for those months.
- **The public lease tool is unchanged:**
  - `LeaseTool.tsx` and `lib/lease.ts` still make no request;
  - `lib/rrclease.ts` is type-imports only;
  - test-lease passes 93 checks, five of them new.
- **Live:** `INTERNAL_COSTS_TOKEN` is not set on Vercel, so the route is 404 there, like the shape-premium draft.

## Supabase, before and after

| When | pg_database_size | What |
|---|---|---|
| Start | 382.1 MB | after Samuel's VACUUM FULL of series |
| Part C | 393.5 MB | `event_window_daily` loaded (the 2018 baseline and the weather rows) |
| Part B, interim | 393.4 to 394.6 MB | `cost_of_power_*` with MISO, NYISO and ISO-NE's year |
| The weekly vacuum, dispatched | 394.6 to 356.2 MB | `VACUUM (FULL, ANALYZE)` |
| Part B, with CAISO | 356.1 to 359.3 MB | |
| Part B, final | 359.3 to **359.5 MB** | all six hubs |

- **Under the 395 MB line throughout.**
- **Not loaded:** the history tables (`iso_hub_prices_history`, `eia930_all_history`, `noaa_isd_hourly`, `eia930_all_interchange`), the network tables and the RRC table. A test checks that no live-set rule matches them.

## Verify and ship

**Local checks after each part,** against a production build:
- check-values: 2,431, 2,378, then **2,381 of 2,381** values match Supabase;
- check-routes: **59 of 59**;
- Python tests: **128, OK**, 23 of them new in `tests/test_session49.py`;
- test-lease: **93 checks**;
- test-eventstudy: parity **2,060 of 2,060**.

**Pushes:** 6f6e298..06cf31a (Parts 0, A, C, D and the interim B), then 8052dbd..49b40fe (the final B). The weekly vacuum's own commit was merged in between. No force push. Origin had no daily commit to merge before either push.

**Live, after the first deploy:**
- check-values against https://erw-flame.vercel.app: **2,231 of 2,231**;
- check-routes: **59 of 59**;
- `/network` 200, `/severance/lease/real` 404 (no token on Vercel, as intended).

**Live, after the final deploy:** `/cost-of-power` ranks 2026-08; check-values **2,234 of 2,234**; check-routes **59 of 59**.

## Decisions made without a human

1. **Interchange: 18 days, not 30.** The 30 days hold 236,808 rows, over the 150,000 ceiling. 18 complete days was the most the count allowed.
2. **The network's nodes stay in the committed JSON, not Supabase.** The live set was near its line, and the page reads only the JSON.
3. **NOAA:**
   - primary stations first, then the second stations while the ceiling allowed;
   - 12 ranges left out and listed in the header;
   - degF, not degC, which is not in the vocabulary;
   - Decision 33 adds `degF-day`, `bbl` and `Mcf`.
4. **The 2018 file has seven ISO BAs.** The prompt said eight, but US48 is not a BA in EIA's six-month files. US48 keeps one baseline year.
5. **The temperature specification** uses degree days at 65 F and their squares, the grid's mean over its stations. Dependent columns are dropped the same way in all three implementations.
   - **The trend row** is pooled only.
   - **The pages' weather share** is given only when the two estimates share a sign and the controlled one is no larger.
6. **The hub history was pulled in parallel per ISO,** in separate directories merged by key.
   - The main run was stopped after ISO-NE so that it would not pull CAISO beside the CAISO run.
   - A second SPP run took August and September.
   - Status rows of the three stopped runs were rebuilt from their logs.
7. **The ranked month falls back to 90 percent coverage:** no month is complete at all six hubs. The rule is labelled on the page and in the method.
8. **NP15 is in `cost_of_power_monthly`** for `/learn/bill`, but not in `/cost-of-power`'s ISO comparison.
9. **The cost-of-power builder stays out of the daily run,** as before: the ERCOT history and the extracts are not on the runner. The hub history's append is in it.
10. **Interim loads and one dispatched vacuum,** so the live pages never broke:
    - `/learn/bill` and its problem set read NP15, which was not in Supabase until the first rebuild;
    - the vacuum gave room for the final load.
11. **RRC:**
    - **license internal;** the table is by lease, not well, because the RRC reports leases;
    - **filed reports only;** `x_wells` from the completion table;
    - **Martin County,** chosen by the data;
    - **"Load a real lease" is its own token-gated route** (`/severance/lease/real`), so the public lease page stays static and makes no request. It reads the table from the output directory, so the data never enters git, the public database or a site bundle (the build's file trace was checked).
12. **The draft's year view counts complete months only,** with the counts shown, and leaves out a hub with none.

## Errors and fixes

- **I replaced `archive/sessions/SESSION_42_REPORT.md` by mistake** (c17dd5d). It already held the report of the first run, which stopped at the gate on 2026-09-30.
  - Restored in full in 6dedc83, with the rerun appended as its own section. No line of the original is missing.
  - The archived prompt was new and overwrote nothing.
- **A stale local build:** the first local check-values found 67 mismatches on `/events/covid-2020`. Next's fetch cache had served `event_window_daily` as it was before the 2018 baseline. Clearing `.next/cache/fetch-cache` fixed it (Vercel builds fresh).
- **Stopping a background task stops only its shell.** TaskStop killed the bash wrappers but not the Python children, so an old backfill raced a new one on the same file. Fixed with Stop-Process on the PIDs, then re-pulled.
- **Coverage:** daily run 14's commit had dropped `event_study_estimates` from coverage. Rebuilt (37a0d6e).
- **Smaller fixes along the way:**
  - EIA's interchange route rejects the shared pager's sort (HTTP 400).
  - String values broke the write summary.
  - US48 has no 2018 history.
  - NYISO's irregular real-time stamps needed the per-day path's irregular branch.
  - The NOAA rows-per-day estimate was too low.
  - A heredoc turned an escape into a newline in `event_window.py` (fixed in 8f3366f).

## Open questions

1. **`INTERNAL_COSTS_TOKEN` is not set on Vercel,** so the internal pages (`/reports/draft/shape-premium`, `/severance/lease/real`) are 404 there.
   - The real-lease page also needs the RRC table on the server, and it is deliberately not deployed.
   - Should the internal pages run only locally, or from a private deployment?
2. **The RRC's reuse terms.** Ask the RRC for written permission to republish lease production, which would let the table go public.
3. **ISO-NE's gap days** leave few complete months: 31 days missing over the year, from intervals absent in the final 5-minute files. Fill those days from ISO-NE's hourly real-time report instead?
4. **Should the cost-of-power builder join the daily run** once the hub history is restored there? It still needs the ERCOT history and the EIA extracts, which are local.
5. **The interchange window** (18 days against the 30 asked) and **demand for the 62 other BAs** (see the session 42 report).
6. **The weekly vacuum** first ran by dispatch in this session. Its Sunday schedule starts on 2026-10-04.

## Wall time and spend

- **Wall time:** 03:11 to 08:10 UTC, about 4 hours 59 minutes.
- **Waiting:** most of it was spent on the hub backfills: SPP's daily real-time files are about 50 MB each, and CAISO's OASIS takes one request at a time.
- **API spend: USD 0.00, confirmed.** No model call.
