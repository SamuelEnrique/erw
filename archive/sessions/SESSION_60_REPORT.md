# Session 60 report: the Flex Alert scorecard (California grid-stress tool v1)

Energy Research Warehouse (ERW), session 60, run on the portable laptop, 2026-10-02 04:41 UTC to about 08:55 UTC. **Wall time about 4 hours 15 minutes.**

**Spend: USD 0.00, confirmed.** No model calls: the scorecard is least squares, the notebook and tests are numpy, and no workflow was dispatched. No force push. Nothing released on Redivis.

**The machine and the lock.**
- At the start, this laptop's role was set to `data` (`python warehouse/lock.py role data --name portable-laptop`), per Samuel's decision of Oct 2.
- The data lock was taken for the whole session, renewed as it ran, and released at the end.

**Read this first: an incident, caused and repaired in this session.** A Supabase load from this laptop's older working copies rolled back part of the live site for up to three hours. It is repaired. A gate in the loader now refuses a repeat. Section 5 has the details.

## 1. The pulls, against their ceilings

| Pull | Ceiling | Pulled | Notes |
|---|---|---|---|
| a. NOAA ISD, SAC, FAT and LAX, May to October, 2018 to 2025 | 150,000 rows | **127,394 rows returned** (24 station-years, 25 responses) | 232,175 new values in `noaa_isd_hourly` (temperature and dew point are two per observation; 13,675 replaced earlier SAC and LAX values), now 412,435 rows. NCEI's 2025 data ends 2025-08-27. Fresno (FAT, 72389093193) is new; `noaa_isd.py --seasons` resumes from saved responses |
| b. CAISO OASIS day-ahead LMP, SP15 and NP15, alert and emergency days and the comparison days | 60,000 rows | **3,024 rows** (63 days, 127 responses; no gaps, no retries) | 223 days were wanted. **160 were not requested:** OASIS serves about 39 months of history. A request for 2022-09-06 answered "No data returned for the specified selection" under report versions 1 and 12, while 2023-07-25 answered with prices. A first run's 6 requests for July 2018 (all "no data") and 6 probe requests to find that boundary are the only other calls |

**Licenses.**
- NOAA NCEI: public domain.
- CAISO: its Privacy and Terms of Use, credit the California ISO. This was already recorded for the warehouse's CAISO tables.

Raw responses are saved under `warehouse/raw/noaa_isd/20261002T044621Z/` and `warehouse/raw/caiso_alert_prices/`.

## 2. The model and its out-of-sample error

**The model.** `warehouse/derived/flex_alert_scorecard.py` fits one least-squares model per local hour, on the 1,276 complete non-alert days of May to October, 2018-07 to 2025. Its terms:
- **Weather:**
  - population-weighted cooling degree hours (CDH) at 65 F (Los Angeles 0.50, Sacramento 0.30, Fresno 0.20) and its square;
  - the mean CDH of the 24 hours before, and its square;
  - the weighted dew point, and CDH times dew point.
- **Calendar:** Saturday, Sunday, US federal holidays, month and year.

**The out-of-sample check.** The hottest tenth of non-alert days is 128 days, each with a weighted high of at least 87.0 F. They are split into five folds, and each fold is predicted by the model fitted on every other non-alert day. In the hours 16:00 to 21:00:
- **bias: -239.3 MW.** Actual less predicted, so the model over-predicts hot evenings.
- **RMSE: 1,598.6 MW.**
- **MAE: 1,257.4 MW.**
- **MAPE: 3.18 percent.**

In sample, the RMSE over the same hours is 1,353.1 MW.

**Five specifications, all reported.** They were named before the alert-day estimates were computed; the page and the method show all five:

| Specification | Hot-day bias, MW | Hot-day RMSE, MW | Pooled estimate, MW (90 percent) |
|---|---|---|---|
| minimal (CDH, CDH squared, calendar: the prompt's) | -272.3 | 1,917.9 | -59.0 (-756.8 to 545.7) |
| base (plus the 24 hours before and the dew point) | -497.1 | 1,744.5 | 861.2 (197.2 to 1,478.8) |
| base plus its square | -273.0 | 1,635.2 | -460.3 (-1,189.5 to 227.7) |
| base plus CDH x dew point | -486.6 | 1,728.5 | 896.9 (234.0 to 1,510.5) |
| **chosen (both)** | **-239.3** | **1,598.6** | **-503.2 (-1,274.9 to 247.4)** |

## 3. The pooled effect, the extremes, the value

**Pooled.** Across 38 alert days and 204 alert hours, the estimated cut is **-503.2 MW**, with a 90 percent interval of **-1,274.9 to 247.4 MW**. A positive number is a cut; this one means demand served ran *above* the model. It is -1.20 percent of predicted demand, -102,650 MWh. The interval includes zero.

The alert days cover:
- every ISO-wide Flex Alert, EEA and pre-2022 emergency notice day from 2018-07-24 to 2024-07-24;
- 2021-07-12 left out for incomplete data;
- no 2025 days: CAISO's report ends 2025-04-30.

**The five largest estimated cuts (MW, 90 percent):**

| Day | Cut, MW | Interval | Weighted high, F | Training days as hot |
|---|---|---|---|---|
| 2022-09-09 | 4,379.7 | 1,122.4 to 7,742.5 | 100.5 | 0 |
| 2020-09-07 | 2,391.4 | -449.0 to 5,091.0 | 93.5 | 3 |
| 2021-07-09 | 2,159.4 | -97.8 to 4,425.1 | 90.8 | 17 |
| 2022-09-08 | 1,835.7 | -1,004.0 to 4,399.3 | 101.4 | 0 |
| 2020-08-16 | 1,671.6 | -898.8 to 4,250.5 | 98.6 | 1 |

**The five smallest (most negative: demand above the model):**

| Day | Cut, MW | Interval | Weighted high, F | Training days as hot |
|---|---|---|---|---|
| 2022-09-07 | -4,170.9 | -6,934.2 to -1,417.6 | 94.5 | 2 |
| 2023-07-25 | -2,788.9 | -4,561.5 to -978.3 | 87.2 | 118 |
| 2022-08-17 | -2,597.3 | -5,126.2 to -359.3 | 83.8 | 363 |
| 2020-09-05 | -2,556.1 | -5,331.9 to -296.1 | 91.2 | 13 |
| 2024-07-24 | -2,413.3 | -4,526.2 to -638.3 | 88.1 | 69 |

**Total wholesale value: USD -5.47 million (90 percent, -8.04 to -2.60 million).** This covers only the 19 alert hours of the 4 alert days with a day-ahead price:

| Day | Value, USD |
|---|---|
| 2023-07-20 | -479,791 |
| 2023-07-25 | -1,976,096 |
| 2023-07-26 | -1,329,252 |
| 2024-07-24 | -1,684,221 |

On those four days demand ran above the model, so the "value" is negative. The 2020 and 2022 heat waves have no price, because OASIS no longer serves them. On the hottest non-alert days with a price, the evening's day-ahead price averaged USD 137.07/MWh.

## 4. What the estimate can and cannot say

**It can say:**
- A weather-and-calendar counterfactual, fitted the way a utility baseline would be, finds **no demand reduction on alert days that it can tell apart from its own error**. The pooled interval spans zero, about -1.3 to +0.2 GW.
- The sign of the pooled estimate depends on the specification. The two specifications that report a cut of about 0.9 GW are the ones that over-predict hot days most. The three that are best on hot days put the pooled effect at or below zero.
- Any statewide conservation effect of a few hundred megawatts is smaller than the model's hot-evening error (RMSE 1.6 GW, bias -0.24 GW). This data and this model cannot measure it.

**It cannot say:**
- **What the Flex Alert message alone did.** On alert days the state also dispatches paid programs (DSGS, ELRP), utilities call demand response, and on 2020-08-14 and 2020-08-15 CAISO ordered rotating outages. The estimate is their combined demand-side effect.
- **What happened on the three days hotter than any training day** (2020-09-06, 2022-09-08 and 2022-09-09). There the model extrapolates.
  - 2022-09-09's large "cut" is more likely the remnants of Tropical Storm Kay, whose clouds and rain over Southern California three airports need not register.
  - 2022-09-07's large negative is the mirror image.
- **What a 20-minute response to an emergency text did.** Hourly data dilutes it.
- **What the 2018 to 2022 alerts were worth**, at any price.

**On the page.** All of this is on `/grid/caiso/alerts` in plain words, with:
- the ranked list, each day showing how many training days were as hot;
- the year-by-year chart;
- 38 evening charts;
- the hot-day check chart;
- the specification table.

## 5. The incident: live tables rolled back, and repaired

**What happened.** At about 05:25 UTC this session ran `python warehouse/supabase/load.py` to put the two new tables into Supabase. The loader makes Supabase hold exactly what this machine's `warehouse/output` holds, for every live-set table. This laptop's working copies were days older than the daily run's of 00:24 UTC; it had last refreshed them on 2026-09-29. The load therefore replaced the live site's newer rows with older ones in **44 tables**, among them:
- the 35-day windows of ISO prices and EIA-930 demand, generation, storage and emissions;
- weather, battery storage, curtailment, the price board, fuel prices;
- the queues and the project map.

Session 59's `sync.py --check` had not flagged them: it compares row counts, and most counts matched.

**The repair.**
1. For each live-set table whose local data differed from the last Redivis upload, the Redivis draft copy was downloaded and compared by newest `retrieved_at` (by row count for the two tables without one).
2. Where the draft was newer (44 tables), the local copy was backed up to the scratch folder, replaced with the draft's, and reloaded.
3. `event_window_daily` was kept: the local copy, with session 58's September 2022 rows, is newer than its draft.
4. A first pass covered 32 tables by about 06:15 UTC. It missed the loader's `recent:` section (12 more tables). A second pass and a retry after a network drop covered those by about 08:05 UTC.

Every table now matches Supabase, and check-values passed 4,269 of 4,269 values before the deploy. The live site therefore showed older data for some tables from about 05:25 to between 06:15 and 08:05 UTC. Nothing was lost: the newer rows were in the Redivis draft, and the backups stay in the session's scratch folder.

**The gate (commit 0f52b5a).** `load.py` now refuses a table that is older than Supabase's copy: its newest `retrieved_at` is older, or, without one, it has fewer rows. The refusal says to sync from the cloud first, or to pass `--allow-older <table>` for a deliberate rollback. It is tested with a mocked client. The daily job is unaffected: it merges new rows into restored tables, so its rows are never older.

**Two defects the repair exposed, both fixed:**
- **Line counting in sync.** `scripts/sync.py` counted lines, not CSV records. Quoted line breaks in the queue tables made three tables look different from coverage when they matched, which is why session 59 reported "3 differ". All 96 tables now match.
- **Restored dates.** `upload.as_erw_text`, which every restore from Redivis goes through, wrote date columns as `2015-09-09T00:00:00Z`. The erw client parses `YYYY-MM-DD`, so `test_session35` and `test_session51` failed on restored tables. Date columns at midnight are now written `YYYY-MM-DD`; tested.

**Lesson, in docs and code.** A data machine must sync from the cloud (`scripts/sync.py --refresh`) before it writes Supabase. The loader now enforces this rather than trusting it.

## 6. What was built

- **Weather pull:** `warehouse/connectors/noaa_isd.py --seasons`, with Fresno added.
- **Price pull:** `warehouse/connectors/caiso_alert_prices.py` writes the new table `caiso_dam_alert_day_hub_prices` (history, not in Supabase).
- **The scorecard:** `warehouse/derived/flex_alert_scorecard.py` writes `flex_alert_effects` (2,973 rows) and `flex_alert_model` (881 rows). Both are tier derived and public, pass the validator, and are in the Supabase live set and the Redivis draft.
- **The page:** `/grid/caiso/alerts`, linked from the Reliability section and `/events`. Every number on it is a warehouse value with its check key (395 on the page). Charts are plain SVG in the house palette: actual demand in cardinal, the prediction dashed, the band shaded, cuts in Palo Alto green.
- **The method:** `docs/methods/flex_alert_scorecard.md`, written as a methods section.
- **The notebook:** `notebooks/flex_alert_scorecard.ipynb` is a second implementation of the panel, the 24 regressions, every day's, year's and pooled estimate, the five-fold check for all five variants and the value. It asserts each equal to the tables, and its full run re-runs the bootstrap with the published seed and reproduces every interval.
- **Questions for Clara:** `docs/reviews/clara-questions.md` has five new ones (11 to 15): which alerts matter most, what a credible counterfactual needs, how the state measures program impact today, what data would make it better, and who would use it.
- **Tests:** `tests/test_session60.py`, 9 tests:
  - the estimator recovers a known 1,000 MW cut on a synthetic panel, and finds none where none was put;
  - every time-frame form CAISO's report uses is read;
  - the published tables agree with each other;
  - the notebook runs;
  - the loader's gate;
  - restored dates.
- **Checks:**
  - full test suite: 228 tests, with the 2 errors from the restored dates fixed and re-run (50 of 50 in the affected modules);
  - check-values before the deploy: 4,269 of 4,269;
  - check-routes before the deploy: 65 of 65 (one transient Supabase statement timeout on `/cost-of-power` during a parallel build; gone on rebuild).

**Deploy.** Pushed at 08:21 UTC (`066ce61`); `/grid/caiso/alerts` answers 200 with every value. Live, after the deploy:
- check-routes: **65 of 65**;
- check-values: **4,249 of 4,249** values match Supabase, 395 of them on `/grid/caiso/alerts`.

## 7. For Samuel: one list

1. **Older CAISO prices, for the 2018 to 2022 alert days.** Without them the scorecard can't value 34 of its 38 days, among them both great heat waves. A script can't get them: OASIS's API serves only 39 months, and older data comes from CAISO staff on request.
   1. Write to CAISO's OASIS support, through the contact on the OASIS site's help page or CAISO's general market inquiries. Ask for the PRC_LMP day-ahead (DAM) hourly LMPs at TH_SP15_GEN-APND and TH_NP15_GEN-APND for the days listed in the header of `warehouse/output/caiso_dam_alert_day_hub_prices.csv` (2018-07 to 2023-06).
   2. When the files arrive, put them in `warehouse/raw/caiso_alert_prices/manual/`. A session can load them under the same checks and re-run the scorecard.
2. **Send Clara the five new questions** (`docs/reviews/clara-questions.md`, 11 to 15). Only you can write to her.
3. **The home laptop as a code machine** (your decision of Oct 2; it reverses session 59's plan). It needs that machine.
   1. On the home laptop, in PowerShell: `cd <the erw folder>`, then `git pull`.
   2. Run `powershell -ExecutionPolicy Bypass -File scripts\setup.ps1 -Role code -Name home-laptop`.
   3. If its worker was registered as a data machine, the same command with `-Worker` registers it again as code.
4. **Review the Redivis draft when convenient.** Four tables are new or changed:
   - `flex_alert_effects`
   - `flex_alert_model`
   - `caiso_dam_alert_day_hub_prices`
   - `noaa_isd_hourly`

   Releasing a version is always your click on redivis.com.

## 8. Notes

- **The daily job.** It will next run on 2026-10-03 at 14:00 UTC (today's run had already succeeded, so the `once=1` gate skips today). Its new lock step and the loader's gate first run then.
- **The scorecard is not in the daily run.** It depends on the CISO workbook extract and the season weather, which live on the data machine. It changes only when CAISO revises its report or a season ends. Re-run it on the data machine, under the lock, after `noaa_isd.py --seasons` and `caiso_alert_prices.py`.
- **A local Next.js server.** One from an earlier session is still running on port 3052 of this laptop (node, PID 26476). It is harmless, and this session left it alone.
