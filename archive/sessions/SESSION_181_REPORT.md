# Session 181 report: Automated Analysis, discovery (10 October 2026)

Branch `wip/181-discovery` in the worktree `C:/Users/lossa/Documents/erw-142`. Nothing pushed, nothing applied, nothing
registered. Model spend USD 0 (no model call). No pull from an outside host. Outputs: `runs/session181/`.

## Read these first

- **The scanner is built and its first run is in hand: 17 flags, 8 drafts.** Of the 17 I judge 13 real, 1 an artifact
  and 3 uncertain, each after reading its raw rows (table below; `runs/session181/raw_checks.md`). The drafts are NOT in
  the database yet: migration 029 is written, tried in a rolled-back transaction, and waits for the coordinator.
- **The worker is NOT registered** (an unattended session may not install persistence). The scripts, the status command
  and the exact proof are written and tested without registering: "For the coordinator", steps 9 to 13.
- **The impact study works and refuses honestly.** Winter Storm Uri (14 days from 7 February 2021): ERCOT North Hub
  real-time rose USD 3,025.91 per MWh, the control USD 9.51; difference USD 3,016.40, standard error USD 1,598.93: within
  1.96 standard errors of zero (five days at the cap beside nine ordinary ones). A quiet date (15 May 2024): difference
  minus USD 37.49, standard error USD 19.95: no difference beyond the error. A third case shows a difference beyond it.
- **One addition you did not ask for:** a card asked for on `/analysis` could not be read on the deployed site (its link
  was a 404 until someone committed the file). Migration 029 adds one read function and the list now has "show the
  card". Without it the impact study could be asked for and never seen.
- **Two things that are not this session's, found by its checks, both on main and on production today:**
  (a) `tests/test_session156.py`'s node test fails at main's head, the base of this branch (`2cb3fe5c`, today's daily
  run): the Ask briefing's sentence gives Texas's curtailment share as 4.45 and `site/data/curtailment/ercot.json` now
  gives 4.46. (b) `check-values.mjs` fails on 2 values of `/learn/problems/networks-and-money` (ERCOT's ties at
  2026-10-09T03:00Z: the page shows 1 tie and 526 MW, Supabase holds 2 and 812), the same 2 on production
  (`runs/session181/check_values_prod.out`). This branch touches neither page nor file. Today's daily run also
  recorded "supabase_load: connector exit 1".

## What to review (internal view: open `https://erw-flame.vercel.app/internal/open` first; after the landing)

### `https://erw-flame.vercel.app/internal/findings`

1. Open it. You should see "Scanner drafts (internal)", four counts (draft 8, full card asked 0, approved 0, dismissed
   0) and "Waiting for a ruling", 8 drafts, strongest first.
2. The first draft: "SPIKE BEYOND ITS OWN HISTORY", in red "Draft: raised by the scanner, not reviewed", the line
   "caiso:AS_CAISO_EXP as_price_dam_nr (caiso_dam): USD 20.65 per MW-hour on 2026-10-06, 2.6 times the 99th percentile
   of its prior 3 years". Hover the chart: each day's value; the flagged day carries a dot; two dashed lines, the 99th
   percentile (8.00) and the threshold (16.00). Three callouts: 8.00 against 20.65; threshold 16.00, multiple 2.58;
   median 0.6075, 754 points. A footnote that begins "A draft raised by the scanner, version 1.0.0". No paragraph, no
   download.
3. Click **Approve** under it. The label becomes "Approved" and a line "approved 2026-10-.. UTC" appears. Open
   `https://erw-flame.vercel.app/analysis`: the section "Found by the scanner" holds that card, marked in red "Found by
   the scanner, flagged 2026-10-06, approved <the day>".
4. Back on the list, the third draft (RECORD HIGH, `eia:retail_price:DC:IND`, USD 321.5 per MWh): click **Dismiss**
   (I judge it an artifact). It moves under "Ruled" and never appears on `/analysis`.
5. Click **Ask for a full card** on any of the eight. The note reads "marked: no analysis of the engine fits this
   series, so a session writes the card": none of the eight is one of the impact study's 23 series. The line under the
   buttons says in advance which of the two a draft would get. (A draft on ERCOT North Hub would queue the impact study
   around its date; the page check proves that path with the scanner's own draft from a backtest of 22 February 2021.)
6. A private window: `https://erw-flame.vercel.app/internal/findings` is a 404. So is the same address with
   `?token=` and the token: this page takes no token in an address.

### `https://erw-flame.vercel.app/analysis`

1. The findings: an eighth card, "IMPACT OF AN EVENT ON A SERIES". Subtitle "ERCOT North Hub real-time price: a rise of
   USD 3,025.91 per MWh around 7 February 2021; the control: a rise of USD 9.51 per MWh". Hover the chart: both series
   by day, the 14 days after shaded. Callouts: 21.46 and 3,047.37; 56.85 and 66.35; "3,016.40 higher", standard error
   1,598.93. One sentence written by code. A table of three rows (the difference in differences, the constant, the
   slope before the date). A second chart, "Before the date: did the two move in parallel?". Downloads: data (CSV),
   Python, Stata do-file, and the two renders.
2. "Found by the scanner": the drafts you approved, or "No draft of the scanner has been approved yet".
3. "Ask for a finding": the list of requests now has **show the card** on a done request (it was a link that answered
   404 for a card not yet committed). Click it: the card is drawn under the list.
4. "Impact of an event on a series": pick a Series, a Control series, an Event. Choose "A date I pick (year, month,
   day)": a date field appears. Pick 15 May 2024, window 14 days, click **Ask the warehouse**. The note reads "queued
   at ... (request ...)", and under it "Request ...: queued: it waits for the data machine". When the worker has run
   (1 to 5 minutes once it is registered) the card appears there: "...The difference between the two changes is minus
   USD 37.49 per MWh, standard error USD 19.95 per MWh (Newey-West, 3 lags, 28 days). That difference is within 1.96
   standard errors of zero: no difference beyond the error." with three downloads.
5. Set the Control to the same series as the Series: a line says the card would be refused. Ask anyway: the card reads
   "The control is the series itself ... Pick another control." and draws nothing. **Reset** puts the defaults back.
6. `https://erw-flame.vercel.app/data/methods/automated_analysis_scanner` (new) and
   `https://erw-flame.vercel.app/data/methods/automated_analysis_findings` ("Analysis 8").
7. A private window: `/analysis` is the in-review page, as before.

## The scanner's first run (10 October 2026, the main copy's tables, read only)

- Command: `findings_scanner.py --in-dir C:/Users/lossa/Documents/erw/warehouse/output --meta-dir .../warehouse/metadata
  --out-dir runs/session181/first_run`. Files: `flags.json`, `suppressed.json`, `drafts.json`, `scan_summary.json`.
- **Scanned:** 117 tables, 36,852 series seen, 6,797 scanned, 105 pairs tested. 198 to 251 seconds a run.
- **Not scanned, and why:** 28 public tables are entities or events (no series of values: the queues, the generator
  lists, the news index, the policy tables); 19 tables by the stated exclusions (3 forecasts, 4 price board tables, 5
  tables about past events, 3 average shapes by hour, the 2 network replay tables, the table of records, and
  `carb_lcfs_credit_prices`, a known gap); the series of 4 tables fit no grain (`ai_power_regions` 187,
  `census_metro_population` 1,650, `noaa_grid_weather_stations` 245, `noaa_isd_hourly` 16).
- **Of the series seen and not scanned:** 20,516 too short or nearly constant; 7,300 with no fresh point; 139 of a
  paused publisher (MISO); 2 whose key does not name one series; 173 scanned on their history since a change of source.
- **Raised:** 17 flags: 12 records, 3 spikes, 2 weekly changes, 0 negative prices, 0 pairs. **Suppressed by a known
  fault:** 20 (all `shoulder_hours_monthly` and `ba_supply_monthly`, under `eia930_ciso_generation_break`, open since
  16 December 2025). **Drafts:** 8.
- **Three guards came from the first run itself**, each fixed by a rule and not by hand: a month still open was
  flagged as a record low; a derived table repeated its source table's record; three reserve products raised one event
  three times.
- **The counts at each setting** (the same tables, the same day):

| Setting | What changed | Raised | Suppressed | Drafts |
|---|---|---|---|---|
| A | the first thresholds (margin 0.25 sigma; yearly points fresh for 500 days) | 52 | 34 | 10 |
| B | a period still open is never evaluated; a derived table's repeat of its source is one flag | 35 | 46 | 9 |
| C | a record's standing counted to the flagged point; margin 0.5 sigma; a year fresh for 120 days; grain read from spacing where freq is empty | 16 | 20 | 9 |
| D (final) | a weekly point is a survey day; one draft a rule and entity; spikes only on positive series | 17 | 20 | 8 |

- Why each change: A flagged October's first 48 hours as record lows in three monthly tables (20 flags) and the year
  2026 in a yearly one: an artifact, removed by a rule. B then showed the year 2025's statistics as "new" in October
  2026 (9 flags, real and stale: the batteries finding already says it), hence 120 days. The margin went from 0.25 to
  0.5 sigma because 22 of B's 31 records passed their old record by less than half a robust standard deviation.
- **A backtest, the week of Winter Storm Uri** (`--date 2021-02-22`, two tables): 194 flags from one event in one table
  (57 records, 54 spikes, 55 weekly changes, 28 pairs), cut to 5 drafts by the caps. The caps hold the volume; the
  drafts of such a week are three views of one event. `runs/session181/backtest_2021-02-22/`.

### Every flag of the first run, with my judgment

| # | Rule | Table | Series | Date | Value | Threshold crossed | Draft | Judgment |
|---|---|---|---|---|---|---|---|---|
| 1 | spike | `caiso_as_prices` | `caiso:AS_CAISO_EXP` as_price_dam_nr | 2026-10-06 | 20.65 USD/MW-hour | 2 x the 99th percentile of the prior 3 years: 16.00 (percentile 8.00) | yes | **real**: non-spinning reserve cleared up to USD 150 per MW-hour in the evening hours of 3 to 9 October (24 hours held each day, CAISO PRC_AS); reserve scarcity in the evening ramp. One event with rows 2 and 4 |
| 2 | spike | `caiso_as_prices` | `caiso:AS_CAISO_EXP` as_price_dam_sr | 2026-10-07 | 20.86 USD/MW-hour | 2 x the 99th percentile of the prior 3 years: 16.00 (percentile 8.00) | no | **real**: the same event, spinning reserve (same hours, same prices as non-spinning); not drafted twice |
| 3 | record | `eia_state_generation_monthly` | `eia:generation:WY:NG` net_generation | 2026-07-01 | 1,028,747 MWh | record high: 765,381 (2024-07), stood 24 points, passed by 9.86 sigma (0.5 needed) | yes | **real**: 1.03 TWh against 0.60 a year before; EIA-860M lists 1,490 MW of gas steam units at Jim Bridger and Naughton (first operated 1971 to 1975, so former coal units), so the level is possible; the size is EIA's first release for July and can be revised |
| 4 | spike | `caiso_as_prices` | `caiso:AS_CAISO_EXP` as_price_dam_ru | 2026-10-07 | 22.77 USD/MW-hour | 2 x the 99th percentile of the prior 3 years: 18.09 (percentile 9.04) | no | **real**: the same event, regulation up; not drafted twice |
| 5 | record | `eia_retail_electricity_prices` | `eia:retail_price:DC:IND` retail_price | 2026-07-01 | 321.5 USD/MWh | record high: 272.6 (2006-06), stood 241 points, passed by 1.84 sigma (0.5 needed) | yes | **artifact**: a definition artifact: revenue over sales for a handful of industrial customers in DC; the series ran 78.6 (Aug 2025), 261.6 (Jan 2026), 143.8 (Mar 2026), and 9.6 in 2004. Dismiss |
| 6 | weekly | `eia_regional_retail_fuel_prices` | `eia:EMM_EPMR_PTE_YCLE_DPG` retail_price | 2026-10-05 | -0.4670 USD/gal | weekly change outside its 5-year range -0.2480 to 0.9150 | yes | **real**: Cleveland regular gasoline fell from USD 4.326 to 3.859 in a week, the largest weekly fall in five years; the rows are as EIA published them. Local and small: that city's price cycles are sharp (a rise of 0.915 is in its range) |
| 7 | record | `eia_retail_sales_monthly` | `eia:retail_sales:UT:RES` retail_sales | 2026-07-01 | 1,658,263 MWh | record high: 1,484,757 (2024-07), stood 24 points, passed by 1.01 sigma (0.5 needed) | yes | **uncertain**: 1.66 TWh against a record of 1.48 (July 2024), 12 percent more; weather or growth is not separated: July 2026 cooling degree days for Utah would settle it (no Utah station is held) |
| 8 | weekly | `cftc_cot_positions` | `cftc:023651` managed_money_long | 2026-09-29 | -46,041 count | weekly change outside its 5-year range -37,814 to 32,886 | yes | **real**: managed money cut Henry Hub longs from 266,563 to 220,522 contracts in the week to 29 September, the largest weekly cut held since 2015 (next: 41,243 in November 2018); rows as the CFTC published them |
| 9 | record | `eia_retail_electricity_prices` | `eia:retail_price:IA:IND` retail_price | 2026-07-01 | 99.90 USD/MWh | record high: 91.70 (2022-07), stood 48 points, passed by 0.80 sigma (0.5 needed) | yes | **real**: Iowa industrial price USD 99.9 per MWh against 91.7 (July 2022) and 90.7 (July 2025): a seasonal July peak, higher each year; modest |
| 10 | record | `eia_retail_sales_monthly` | `eia:retail_sales:IN:COM` retail_sales | 2026-07-01 | 2,801,230 MWh | record high: 2,649,955 (2001-09), stood 298 points, passed by 0.79 sigma (0.5 needed) | yes | **real**: Indiana commercial sales 2.80 TWh, 9.8 percent above July 2025; the record it breaks stood since September 2001. Large data centers are usually booked as commercial: worth a look at the load-growth lens |
| 11 | record | `eia_state_generation_monthly` | `eia:generation:NV:ALL` net_generation | 2026-07-01 | 5,510,076 MWh | record high: 5,148,942 (2024-07), stood 24 points, passed by 0.73 sigma (0.5 needed) | no | **real**: Nevada generation 5.51 TWh against 5.15 (July 2024); part of the Mountain West's July (rows 12 and 13) |
| 12 | record | `eia_state_generation_monthly` | `eia:generation:MTN:ALL` net_generation | 2026-07-01 | 41,572,951 MWh | record high: 39,214,870 (2024-07), stood 24 points, passed by 0.72 sigma (0.5 needed) | no | **real**: Mountain division generation 41.6 TWh against 39.2 (July 2024); one regional story with Nevada, Utah and Wyoming above |
| 13 | record | `eia_retail_sales_monthly` | `eia:retail_sales:MTN:ALL` retail_sales | 2026-07-01 | 35,631,295 MWh | record high: 33,740,506 (2024-07), stood 24 points, passed by 0.65 sigma (0.5 needed) | no | **real**: Mountain division sales 35.6 TWh against 33.7 (July 2024): the same July |
| 14 | record | `eia_state_generation_monthly` | `eia:generation:IN:OOG` net_generation | 2026-06-01 | 65,787 MWh | record low: 88,633 (2009-05), stood 205 points, passed by 0.61 sigma (0.5 needed) | no | **uncertain**: Indiana's other-gases generation (blast furnace and similar gases) 65,787 MWh in June against 125,902 in May and 133,037 in July: a one-month dip, an outage or a late report; EIA's next revision settles it |
| 15 | record | `state_generation_mix_monthly` | `eia:IN` net_generation_oil_and_other_mwh | 2026-06-01 | 108,766 MWh | record low: 146,257 (2019-02), stood 88 points, passed by 0.61 sigma (0.5 needed) | no | **uncertain**: the derived sum that holds row 14 (oil and other gases): the same June dip, the same doubt |
| 16 | record | `eia_retail_electricity_prices` | `eia:retail_price:ID:ALL` retail_price | 2026-06-01 | 113.3 USD/MWh | record high: 103.6 (2024-06), stood 24 points, passed by 0.59 sigma (0.5 needed) | no | **real**: Idaho all-sector price USD 113.3 per MWh in June against 103.6 (June 2024); July (108.7) is above the old record too; modest |
| 17 | record | `eia_retail_electricity_prices` | `eia:retail_price:US:IND` retail_price | 2026-07-01 | 97.70 USD/MWh | record high: 93.80 (2022-08), stood 47 points, passed by 0.52 sigma (0.5 needed) | no | **real**: the national industrial price, USD 97.7 per MWh, above its record of August 2022 (93.8): the highest in the 25 years held |

- **Counts:** 13 real, 1 artifact, 3 uncertain. The 13 real are five stories: California's reserve prices (rows 1, 2,
  4); the Mountain West's July (3, 11, 12, 13); industrial and all-sector retail prices at records (9, 16, 17);
  Indiana's commercial sales (10); two market moves (6, 8).
- **What "real" means here:** the rows say what the flag says, the days are complete, and no known fault, revision
  window, partial period or unit change explains it. EIA's newest months are first releases.
- **Not raised by the first run:** no first negative price, no pair break. Both rules are exercised by the tests and by
  the Uri backtest (28 pair flags there).
- **Seen in the rows, not flagged by the final setting:** Lower Atlantic diesel at USD 6.096 per gallon on 14
  September and 6.139 on 21 September, above its June 2022 record (5.762). Real. The record was first broken 26 days
  before the scan, outside the 21 days a weekly point stays fresh, and the week after it broke a record that had stood
  one week. A scan in the week of 14 September would have raised it. Setting B raised it because B counted a weekly
  point by its week's last day, which kept 14 September inside the fresh window.

## The impact study: the cases, with their numbers

| Case | Series, control | Before | After | Control before, after | Difference in differences | SE (Newey-West) | Lags, days | Reading |
|---|---|---|---|---|---|---|---|---|
| Uri, 14 days from 7 February 2021 (the default card) | ERCOT North Hub real-time, NYISO New York City real-time | 21.46 | 3,047.37 | 56.85, 66.35 | 3,016.40 | 1,598.93 | 3, 28 | within 1.96 standard errors of zero (p 0.070) |
| A quiet date, 14 days from 15 May 2024 | the same | 49.17 | 21.61 | 24.42, 34.34 | minus 37.49 | 19.95 | 3, 28 | no difference beyond the error (p 0.071) |
| 7 days from 13 February 2021 | the same | 158.88 | 5,943.36 | 53.36, 75.00 | 5,762.84 | 1,480.80 | 2, 14 | more than 1.96 standard errors from zero |
| The same week, a control the storm also hit | ERCOT North Hub day-ahead, SPP South Hub day-ahead | 46.88 | 5,845.02 | 58.30, 1,981.70 | 3,874.73 | 638.32 | 2, 14 | beyond the error; the control's own rise takes a third off |

- All in USD per MWh. Cards: `site/data/findings/impact_study.json` (Uri, committed with its CSV, Python, do-file and
  two renders); `runs/session181/impact_quiet/`, `runs/session181/impact_uri7/`.
- The Uri card's honest answer over 14 days is "within the error": the regression has 28 days, five of them at the
  price cap. The sentence states the numbers and never a cause.
- Refusals, each run on the real tables (`runs/session181/impact_refused/`): the control is the series itself; the
  control is in another unit (Henry Hub against a power price); 1 March 2015 is outside what NYISO holds (from 2
  January 2019); 6 October 2026 with 7 days has 2 days after it (5 needed); 31 February does not exist. Each card says
  what is missing and draws nothing.
- Specification: (series minus control) = a + b * after + e, least squares on the days both hold; Newey-West, Bartlett
  kernel, L = floor(4 * (n / 100)^(2/9)), factor n / (n - 2), as Stata's `newey`. `statsmodels` is not in the venv:
  `newey_west` is computed with numpy and tested against a case worked by hand (y = 1, 3, 2, 6: standard errors the
  square roots of 0.5 and 3.5) and against the sums written out.
- The do-file reads its CSV past the four comment lines: `import delimited "...", varnames(5) rowrange(6)
  stringcols(_all) clear` (the comment lines hold no comma). The seven old do-files are untouched.

## Where the scanner runs daily, and what it costs

- **On the data machine**, the only machine with the histories the rules compare with: `warehouse/run_data_machine.sh`
  gains the soft step `dm_scanner` after its sync (the scan, the run kept under `runs/scanner/<date>/`, the drafts
  added to the review list). **About 4 minutes** (198 to 251 seconds here, with a site build running beside the
  slowest). It reads tables and writes none; it needs no data lock of its own.
- **On GitHub's runner**: no scan. A record over the whole history, the prior year of prices, the prior three and five
  years and the 365-day fit all lose their history on rolling windows. `warehouse/run_daily.sh` gains the soft step
  `scanner_request`: it queues the day's scan (a row of `analysis_requests`, finding `scanner_daily`) for the worker
  here. Seconds. Without a service key it exits `ERW_SKIP_EXIT` with its reason.
- Both are soft steps under `warehouse/health.py`; neither is a `model_step`; a failure never stops a run. A draft is
  never raised twice, so the two paths can both run.
- If the data machine's daily run is not started on a day, the worker still scans what the machine holds when it takes
  the runner's request: tables a day behind raise nothing new (the fresh-point rule), they do not raise false flags.

## What was built

- **Scanner:** `warehouse/analysis/findings/findings_scanner.py`; `warehouse/config/scanner.yaml` (every threshold,
  every key commented); `docs/methods/automated_analysis_scanner.md`; the two soft steps.
- **Impact study:** `warehouse/analysis/findings/impact_study.py`; one added line in `run_finding.py`
  (`FINDINGS.append`) and one in `site/lib/findings.ts` (`ORDER.push`); `site/data/findings/impact_study.json` and
  `catalogue.json`; `site/public/findings/erw_2026_impact_event_control.csv`, `impact_study.py`, `impact_study.do`, two
  PNGs; "Analysis 8" in `docs/methods/automated_analysis_findings.md`.
- **Database:** `warehouse/supabase/migrations/029_scanner_drafts.sql` (the table `scanner_drafts`; functions
  `scanner_drafts_list`, `scanner_draft_set_state`, `analysis_request_card`), its rollback, `verify_rls.py` (the table
  and two functions added), the record in `warehouse/supabase/README.md`.
- **Site:** `site/app/internal/findings/` (the page; `state/route.ts`, the POST; `approved/route.ts`);
  `site/lib/scanner.ts`; `site/lib/discoverychart.ts` (chart kind `flag_line`: hover, the flagged point, reference
  lines, a shaded band); `site/components/analysis/DraftReview.tsx`, `ScannerFound.tsx`, `ImpactForm.tsx` (the impact
  study's inputs, self-contained for session 182's flow), `RequestCard.tsx`; small additions to `FindingCard.tsx`,
  `RequestForm.tsx`, `findingchart.ts`, `app/analysis/page.tsx`, `app/api/analysis/route.ts`.
- **Worker as a service:** `warehouse/analysis/findings/worker.py` (one instance by a lock file with stale-lock
  recovery, a bounded backoff on a network or Supabase failure, a clean stop, a state file, `--status`, the scanner's
  request); `scripts/register_findings_worker.ps1`, `scripts/unregister_findings_worker.ps1`,
  `scripts/queue_analysis_request.py`. The worker takes no data lock at all and calls no model.
- **Checks and tests:** `site/scripts/check-internal-findings.mjs`, `site/scripts/findings-stub.mjs` (the stand-in for
  029's functions), `tests/test_session181.py` (48 tests), `tests/test_session181_worker.py` (29 tests),
  `tests/fixtures/session181/` (the first run's 8 drafts; one draft of the Uri backtest).

## Pulls and model spend against their ceilings

- Pulls: none. No request to an outside host. Model spend: USD 0. No model call anywhere, in code or in a check.
- Production Supabase: one rolled-back transaction (migration 029 and its rollback, `runs/session181/sql_trial.out`,
  "nothing was changed", checked on a new connection), and reads with the anon key by the local build and its checks.
  The local server's usage route may have counted the checks' page views (`site_usage_record`), as for any local
  check run since session 177; this session did not look.

## Checks run (each its own command; outputs under `C:/Users/lossa/Documents/erw/runs/session181/`)

| Check | Exit | Output |
|---|---|---|
| `npm ci` (Next 16.3.8), under the build mutex | 0 | `npm_ci.out` |
| `npm run build`, the final build, under the mutex | 0 | `build3.out` |
| `tests.test_session181` (48 tests, 1 skipped in the worktree: the events' header; 0 skipped with `ERW_DATA_DIR`) | 0 | `t_181.out`, `t_181_events.out` |
| `tests.test_session181_worker` (29 tests) | 0 | `t_181_worker_final.out` |
| `tests.test_session170`, `173`, `174`, `177`, `149`, `157` | 0 each | `t_170.out`, `t_173.out`, `t_174.out`, `t_177.out`, `t_149.out`, `t_157.out` |
| the whole suite, `python -m unittest discover -s tests`: 2,947 tests, 220 skipped, 1 failure, `test_session156`'s node test (4.46 against 4.45: main's head, not this branch; "Read these first") | 1 | `suite.out` |
| migration 029 and its rollback in one rolled-back transaction (28 checks) | 0 | `sql_trial.out` |
| the loader's dry run (8 drafts, nothing sent) | 0 | `load_dry_run.out` |
| `check-internal-findings.mjs` against the stand-in (114 of 114; a real browser; 390 px for `/internal/findings` and the impact form) | 0 | `check_internal_findings.out` |
| `check-analysis.mjs` (186 of 186) | 0 | `check_analysis.out` |
| `check-security.mjs` (48 of 48, `/internal/findings` added to its list) | 0 | `check_security.out` |
| `check-csp.mjs` (84 pages, 0 enforced violations) and `--phone` (5 pages, 0 wider than the screen) | 0, 0 | `check_csp.out`, `check_csp_phone.out` |
| `check-routes.mjs`, first run: one FAIL, `/prices/miso%3AINDIANA.HUB` answered 404 once (200 when asked again by hand) | 1 | `check_routes.out` |
| `check-routes.mjs`, second run on the same build | 0 | `check_routes_2.out` |
| `check-values.mjs`, whole, first run: 6,909 of 6,957; 17 failed (15 of them the battery page's October figures from the local build's fetch cache, gone on the second run) | 1 | `check_values_1.out` |
| `check-values.mjs`, second and third runs: 6,924 of 6,957; 2 failed, both `/learn/problems/networks-and-money` | 1, 1 | `check_values_2.out`, `check_values_3.out` |
| `check-values.mjs` on production (reads): 6,924 of 6,957; the same 2 failed | 1 | `check_values_prod.out` |
| `render-cards.mjs --only impact_study` (both sizes, bundled fonts) | 0 | `render_impact.out` |
| `worker.py --once --local-dir` on a real request; the `.ps1` files through PowerShell's parser; `-DryRun` | 0 | `worker_once_local.out`, `ps1_checks.out` |
| `worker.py --once --local-dir` on two impact study requests as the page sends them (one computed in 6 seconds, one refused: the control is the series) | 0 | `worker_once_impact.out` |

## Decisions made without you

1. **Sub-daily series are scanned by UTC day** (mean, minimum, maximum). A record of a 15-minute price is a record of
   its day's mean; a first negative price uses the day's lowest interval.
2. **A record needs more than being a record:** three years of days (or 60 months), an old record that stood a year
   (24 months), and a margin of 0.5 robust standard deviations. Without them every climbing series flags every month.
3. **A fault recorded without dates suppresses its tables whole.** Conservative: `shoulder_hours_monthly` and
   `ba_supply_monthly` cannot flag while `eia930_ciso_generation_break` is open. The 20 suppressed flags are kept and
   named in `suppressed.json`.
4. **Volume caps:** 12 drafts a day, 3 a table, 5 a rule, 1 a rule and entity. Every flag stays in `flags.json`.
5. **Where it runs:** the data machine scans; the runner asks. Both soft steps.
6. **Approved drafts reach `/analysis` through the browser** (`/internal/findings/approved`, internal view only), so
   `/analysis` stays the static page it was and reads no database when it is built.
7. **"Ask for a full card"** queues the impact study on the flagged series around its date (14 days, a default control
   on another grid in the same unit) where the series is one of the study's 23; otherwise it only marks the draft for a
   session. Code writes no paragraph.
8. **The impact study's date is three chosen inputs** (year, month, day): the queue takes chosen inputs only, and the
   catalogue's rule is that a default is one of its choices. The form shows one date field.
9. **The control must be in the series' unit.** "Price against gas" is a scanner pair (a regression), not an impact
   pair (a difference in levels).
10. **An event's date is its window's first day** as `event_window_daily` holds it (Uri: 7 February 2021).
11. **`analysis_request_card` in migration 029** and "show the card": see "Read these first". The card carries its rows
    and its do-file so its downloads are made in the page; a requested card has no render.
12. **The render frames leave out the second chart** (the pre-period): with it neither frame fitted. The footnote on
    the render gives the pre-period slope and says the chart is on the site.
13. **`TABLES` of the impact study names only `event_window_daily`**, so the Roundup's runner is not made to restore
    366 MB of zone prices. The study runs on the data machine.
14. **Neighbours' files touched, each by one line:** session 177's test whitelist of read functions (two names added);
    `check-security.mjs` and `check-csp.mjs` (the new page added to their lists); `RequestForm.tsx` (its selects
    bounded: with a longer option the page scrolled sideways at 390 px).
15. **One backtest draft is a fixture** (`draft_backtest_uri.json`): the scanner's own draft as of 22 February 2021 with
    the caps lifted, used only to prove the queued full card in the page check. It is real data and is in no list a
    person sees.
16. **A draft names its series by the table's own key** (`eia:generation:WY:NG net_generation`), not by a plain name.
17. **The scanner's `version` stayed 1.0.0** through the tuning: nothing was loaded anywhere before the final setting.

## For the coordinator (in order; from `C:/Users/lossa/Documents/erw` once the branch is merged there)

1. Snapshot before, its own command: `node site/scripts/snapshot-live.mjs take before181`.
2. Apply the migration (it adds one table and three functions; nothing a page reads changes; safe before the deploy):
   `'C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe' warehouse/supabase/apply.py --only 029 > runs/session181/apply_029.out 2>&1; echo "exit=$?"`
3. Verify: `'C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe' warehouse/supabase/verify_rls.py --catalog > runs/session181/verify_rls_after.out 2>&1; echo "exit=$?"`.
   Must be exit 0, "PASS: 0 mismatch(es)", `scanner_drafts` expected blocked and seen blocked, `scanner_drafts_list`
   and `analysis_request_card` refused, 24 tables with row-level security on.
4. Load the first run's drafts. No data lock: no warehouse table and no table a page of a visitor reads.
   Dry run: `'C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe' warehouse/analysis/findings/findings_scanner.py --load runs/session181/first_run/drafts.json --dry-run`
   Then: `'C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe' warehouse/analysis/findings/findings_scanner.py --load runs/session181/first_run/drafts.json > runs/session181/load_drafts.out 2>&1; echo "exit=$?"`
   Must read "8 draft(s) added to scanner_drafts; 0 already there or with an open draft". Run again: "0 draft(s) added".
5. In the main copy after the merge: `npm ci`, `npm run build` (the mutex),
   `python -m unittest tests.test_session181 tests.test_session181_worker`.
6. Deploy the usual way; `take after181`; `compare before181 after181`. Expected: no difference on any of the 25 pages
   (the three live pages read nothing this session changed; `/analysis` and `/internal/findings` are not among them).
   Before the push, know the two failures of "Read these first": the suite's one failure and `check-values`' two are on
   main and on production already.
7. After the deploy: `node site/scripts/check-security.mjs https://erw-flame.vercel.app > runs/session181/check_security_prod.out 2>&1; echo "exit=$?"` (48 of 48, with "/internal/findings: 404 without the cookie, 200 with it");
   `node site/scripts/check-csp.mjs https://erw-flame.vercel.app > runs/session181/check_csp_prod.out 2>&1; echo "exit=$?"`;
   `node site/scripts/check-analysis.mjs https://erw-flame.vercel.app`; `node site/scripts/check-values.mjs https://erw-flame.vercel.app` (twice if the first differs).
8. By eye, internal view: `https://erw-flame.vercel.app/internal/findings` lists 8 drafts. Do not rule on them: that is
   Samuel's. (`check-internal-findings.mjs` runs only against the stand-in: it approves and dismisses.)
9. Register the worker (an elevated PowerShell adds the startup trigger; a plain one registers log-on only and says so):
   `powershell -ExecutionPolicy Bypass -File scripts\register_findings_worker.ps1 -DryRun`, then the same without `-DryRun`.
   Last line: `REGISTERED: 1 task named 'ERW findings worker', state Running. Log: ...\runs\findings_worker.log`.
10. Show the task: `schtasks /Query /TN "ERW findings worker" /V /FO LIST`.
11. Status: `.venv\Scripts\python.exe warehouse\analysis\findings\worker.py --status` (registered, alive, heartbeat).
12. Queue one real request through the page's database function and watch it:
    `.venv\Scripts\python.exe scripts\queue_analysis_request.py --watch 300` (asks `queue_divorce` from 2010: one small
    table, a card of its own). Expect `queued`, `running`, `done`, the times, the machine and the card id.
13. See it complete: the watch's `done` line; step 11 again (`last request: ... done`); the file
    `site\data\findings\queue_divorce__first_year-2010.json`; the row on `/analysis` under "Ask for a finding", done,
    with "show the card". Then ask the impact study from the page (review step 4) and see its card arrive.
14. Write the time of step 2 in `warehouse/supabase/README.md` (the 029 row).
- More detail on steps 9 to 13, and the restart and one-instance proofs: `runs/session181/worker_notes.md`.
- To undo: `apply.py --rollback 029` (the drafts and their rulings go with the table; the site falls back to "could
  not be read"); `powershell -ExecutionPolicy Bypass -File scripts\unregister_findings_worker.ps1`.
- For session 182: the impact study's inputs are `ImpactForm` (one prop, the catalogue entry) and the module
  `impact_study.py`; a requested card is drawn by `RequestCard` (one prop, the request id). `FINDINGS` and `ORDER` were
  extended by added lines only. `findingchart.ts` gained three added lines and one widened type.

## To finish

- **The registration and the one real request** are steps 9 to 13 above; nothing else is held.
- **The first real load into `scanner_drafts`** (step 4) is the first time the insert meets the real table: the SQL
  was tried with the same 8 drafts inside the rolled-back transaction, the REST call was not.
- **Plain names for a draft's series** ("Wyoming, natural gas generation") need a table of names by table: a session.
- **One draft an event.** The Uri backtest gives three drafts of one storm. Grouping flags of one table and week into
  one draft is the next rule to add; the caps bound the volume until then.
- **A full card for a series outside the impact study's 23** is a marked draft that a session writes.
- **Rules to make, Samuel:** whether an undated known fault should silence its tables whole (decision 3); whether 12
  drafts a day is the right ceiling; whether the DC industrial price, and series like it (a ratio over few customers),
  should be excluded by a rule on the count of customers, which the table does not hold.
- `warehouse/run_data_machine.sh` is started by a person or the machine's scheduler: the scan is daily only if that run
  is. The runner's request to the worker covers the days it is not.

## The landing


## The landing (written by the chain's coordinator, 10 October 2026)

- Landed from `wip/181b-land` (the three cards of session 182, landed an hour earlier, `origin/main` and
  `wip/181-discovery` merged). Two conflicts, both resolved by keeping both sessions' entries:
  `warehouse/analysis/findings/run_finding.py` (session 182's three findings, then `impact_study`) and
  `site/data/findings/catalogue.json` (11 entries; equal to `run_finding.py --list`).
- Before it, on the landing branch, two things this report names as not this session's:
  - `tests/test_session156.py` failed on main since the daily run of 16:18 UTC (Texas's curtailment share: the question
    file said 4.46, the file 4.45). One assertion of `site/scripts/test-ask-ready.mjs` no longer pins a figure the
    daily run moves, as session 159 ruled for its neighbour (`a19f1b45`). It would have stopped every landing.
  - `check-values` on `/learn/problems/networks-and-money`: by 17:30 UTC the two values matched again on the local
    build (6,957 of 6,957) and on production (below): the page's cached hour had been behind the live rows.
- In the main copy at the merged tree (`00782e99`): tests 181, 181 worker, 182, 170, 173, 174, 177, 176: 218 tests OK;
  `npm run build` exit 0; `check-internal-findings` against the stand-in 114 of 114; `check-analysis` 255 of 255;
  `check-findings-grids` 163 of 163; `check-security` 48 of 48; `check-routes`: first run exit 1
  (`/prices/miso%3AINDIANA.HUB` answered 404 once on the cold build, as in the agent's run), second run exit 0, 156
  pages in review and 0 failed; `check-values` 6,957 of 6,957, then 6,926 with 31 latest prices superseded; `check-csp`
  in a real browser: 84 pages, 0 violations; the whole suite in the clean worktree: 2,989 tests OK, 233 skipped.
- No freeze. `181_before` at 18:01:00 UTC (25 pages, exit 0), its own command, before the migration.
- **Migration 029 applied at 18:01:09 UTC** (`apply_029.out`, exit 0). `verify_rls.py --catalog`: exit 0, "PASS: 0
  mismatch(es)", `scanner_drafts` expected blocked and seen blocked (HTTP 401, 42501), `scanner_drafts_list` and
  `analysis_request_card` refused to the anon key, 24 tables with row-level security on (`verify_rls_after.out`).
- **The first run's drafts are in the review list:** the dry run named 8; the load answered "8 draft(s) added to
  scanner_drafts; 0 already there or with an open draft"; run again: "0 draft(s) added ... 8 already there". All 8 are
  in state `draft`; nothing was approved or dismissed (that is yours). Strongest first: the spike in `caiso_as_prices`
  of 6 October 2026, then the record in `eia_state_generation_monthly` of July 2026.
- Pushed as `task/181-discovery`; run 38074130505 success; merge `1885332c`; Vercel production "Deployment has
  completed" at 18:09:44 UTC; `181_after` at 18:09:53 UTC; comparison: **0 differences on the 25 pages**
  (`compare_181.out`, exit 0). Expected.
- On production: `check-security` 48 of 48 ("/internal/findings: 404 without the cookie, 200 with it, no token in the
  page"); `check-analysis` 255 of 255; `check-csp`: 84 pages, 0 enforced and 0 report-only violations;
  `check-values`: exit 0, 6,926 of 6,957 with 31 latest prices superseded by a newer interval.
- **The worker is registered and running, and one request completed.**
  - `scripts\register_findings_worker.ps1 -DryRun`, then for real: "REGISTERED: 1 task named 'ERW findings worker',
    state Running." The permission layer that refused session 173 let it through this time because the owner had
    confirmed the service in this conversation.
  - **It starts at log-on only.** This session's shell is not elevated, so the script left the startup trigger out and
    said so. `schtasks /Query`: "Schedule Type: At logon time", "Logon Mode: Interactive only", "Status: Running"
    (`task_query.out`). It restarts on failure and runs one instance. To have it start before anybody logs on, run the
    same script once from an elevated PowerShell (right-click, "Run as administrator"):
    `powershell -ExecutionPolicy Bypass -File C:\Users\lossa\Documents\erw\scripts\register_findings_worker.ps1`.
    A restart of the machine was not made, so "survives a restart" is proven by the task's trigger and settings, not
    by a restart.
  - `worker.py --status` before: "process: alive, pid 3324 ... 0 done"; the request
    `20261010T181100Z-44b6f4` (`queue_divorce`, 2010 to 2020) was queued at 18:11:01 UTC through the page's own
    database function and was **done at 18:11:47 UTC** (46 seconds; `queue_watch.out`); `--status` after: "1 done, 0
    failed", "last request: ... queue_divorce done" (`worker_status2.out`); the log `runs\findings_worker.log` holds it.
  - The worker writes a requested card's file and downloads into the main copy's working tree
    (`site/data/findings/queue_divorce__first_year-2010.json` and three files under `site/public/findings/`). They are
    left untracked: the page reads a requested card from its queue row since migration 029, and committing each
    requested card is a ruling for you.
  - To remove it: `powershell -ExecutionPolicy Bypass -File scripts\unregister_findings_worker.ps1`.
- The scanner's daily request: the daily run queues it (`scanner_request`), and the worker, now running, takes it on
  this machine. The first scheduled one is the run of 11 October, 14:00 UTC.
