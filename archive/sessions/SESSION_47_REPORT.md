# Session 47 report: event studies; the Supabase vacuum blocked; run 14 still running

Energy Research Warehouse (ERW), session 47, run 2026-09-30 23:43 to 2026-10-01 00:20 UTC. **Wall time about 40 minutes.**

**API spend: USD 0.00, confirmed.** No model call, no data pull, no Supabase table, no force push.

- **Part B did not run,** so no rows were pulled against either ceiling: 150,000 for the interchange, 1.5 million for the year of hub prices.
- **Deployed and checked live:** routes 58 of 58, values 2,313 of 2,313 (617 of them event-study values).

## Part 0

1. **`VACUUM (FULL, ANALYZE)` was not run.**
   - The prompt approves it, but Claude Code's auto mode denied the command (classified as "Modify Shared Resources") before it reached the database. I did not try another route to the same result, as the denial requires.
   - **Supabase before:** 447.9 MB (run 13's load, 2026-09-30 22:14 UTC). **After:** unchanged by this session. Run 14's load may have moved it.
   - **Samuel:** run it yourself, in the Supabase SQL editor (`vacuum full analyze public.series;` and the other five shape tables), or allow it in Claude Code's permissions for the next session.
2. **The weekly vacuum workflow was not added,** for the same reason.
   - When I began to read the workflows to write it, auto mode denied that too, as the same outcome: a scheduled `VACUUM FULL` of the shared database.
   - Nothing was written: no workflow file and no runbook change. Both await your permission.
3. **`warehouse/connectors/eia930_interchange.py`** is kept, untracked, for session 42's interchange pull.
4. **Run 14** (workflow_dispatch, 374f8fd), checked between Part A's steps:
   - **00:15 UTC:** "Pull, validate, rebuild coverage" still in progress (from 23:05).
   - **At the end of Part A:** it had not passed, so **Part B did not run.** `SESSION_42_PROMPT.md` stays at the root.

## Part A: the event study module

**The estimator** (`warehouse/derived/event_study.py`, specification `dow_year_mean_v1`), per event, grid and outcome:

- **Outcomes:** daily demand served (MWh), and ERCOT's daily mean real-time hub price (USD/MWh).
- **Event-day indicators,** with one pooled event-window indicator in a second regression.
- **Day-of-week effects.**
- **Year effects** summing to zero over the baseline years. The event year's counterfactual is their mean.
- **Inference:** HC1 robust standard errors and 95 percent normal intervals.
  - A single day's standard error is sqrt(s2 + x'Vx), the day's own noise plus the counterfactual's robust variance. A one-day indicator's residual is zero, so a robust covariance alone would leave the noise out.
- **Hour-of-day profile:** demand from the EIA-930 hourly extracts, 409 estimates.
- **Weather:** temperature is not held, and the pages, the method and the table header say plainly that nothing controls for it.

**The table** `event_study_estimates` (derived, public): 1,485 estimates for 21 event-grid pairs.
- Validator PASS; coverage rebuilt (83 tables).
- **Not in Supabase:** the database is over the 360 MB line.
- **Not in the Redivis draft:** the uploader has no single-table option, and `--changed` from this laptop would also send 73 tables older than the runner's. It waits for a targeted upload.

**The pages:** each `/events` page has a "What the estimates say" block. It is computed at build time from `event_window_daily` with `site/lib/eventstudy.ts`, the TypeScript twin. It holds:
- the lead grid's pooled effect with its interval, as a percent of the counterfactual;
- one sentence on whether the interval excludes zero;
- a coefficient plot of the event days;
- every grid's pooled effect;
- each day's estimate.

Every number carries a check key that check-values recomputes from Supabase.

**Documentation and replication:**
- `docs/methods/event_study.md`, a methods section: specification, inference, identification, what it cannot rule out, and each result's table.
- `notebooks/event_study.ipynb` reproduces all 21 pooled and 1,035 daily estimates from `erw.fetch` (largest difference 5e-7).

**Tests:**
- **Synthetic panel with a known effect** (Python and TypeScript):
  - day effects of 20 + k are recovered exactly with no noise;
  - a constant effect of 25 is recovered by the pooled indicator;
  - the 95 percent interval covers it in 88 to 99 percent of 200 noisy panels.
- **Python against TypeScript:** equal on all 1,077 daily and pooled estimates.
- **The notebook** reproduces the table; **the windows** match `event_window.py`.
- **`tests/`:** 101 OK. **check-routes and check-values,** local and live.

### Every pooled estimate, with its 95 percent interval (per day of the window)

| Event | Grid | Outcome | Estimate | 95 percent interval | Percent of expected |
|---|---|---|---|---|---|
| COVID-19 | CAISO | demand, MWh/day | 14,920.51 | 3,097.78 to 26,743.24 | 2.92 |
| COVID-19 | ERCOT | demand | -7,630.38 | -36,976.45 to 21,715.68 | -0.81 |
| COVID-19 | ISO-NE | demand | -17,179.50 | -23,705.52 to -10,653.48 | -5.91 |
| COVID-19 | MISO | demand | -129,298.35 | -157,955.03 to -100,641.67 | -7.90 |
| COVID-19 | NYISO | demand | -29,410.11 | -36,417.16 to -22,403.05 | -7.66 |
| COVID-19 | PJM | demand | -158,685.97 | -204,987.37 to -112,384.56 | -7.97 |
| COVID-19 | SPP | demand | -36,379.89 | -49,293.60 to -23,466.18 | -5.55 |
| COVID-19 | Lower 48 | demand | -606,600.64 | -767,512.43 to -445,688.85 | -6.06 |
| COVID-19 | ERCOT hub | real-time price, USD/MWh | -5.32 | -8.77 to -1.87 | -21.28 |
| CAISO heat 2020 | CAISO | demand | 83,812.35 | 46,905.66 to 120,719.05 | 11.47 |
| Uri | ERCOT | demand | 155,794.96 | 53,420.68 to 258,169.25 | 16.24 |
| Uri | ERCOT hub | price | 2,293.84 | 686.08 to 3,901.61 | 9,850.47 |
| Elliott | ERCOT | demand | 269,581.50 | 156,948.75 to 382,214.25 | 28.31 |
| Elliott | ISO-NE | demand | 10,549.09 | 1,185.42 to 19,912.76 | 3.14 |
| Elliott | MISO | demand | 236,278.71 | 115,485.54 to 357,071.88 | 13.74 |
| Elliott | NYISO | demand | 24,802.64 | 12,282.81 to 37,322.47 | 5.99 |
| Elliott | PJM | demand | 386,999.95 | 256,963.62 to 517,036.28 | 17.73 |
| Elliott | SPP | demand | 146,160.91 | 80,505.19 to 211,816.63 | 20.90 |
| Elliott | ERCOT hub | price | 56.52 | -19.85 to 132.89 | 264.66 |
| ERCOT heat 2023 | ERCOT | demand | 271,284.09 | 239,602.57 to 302,965.60 | 20.33 |
| ERCOT heat 2023 | ERCOT hub | price | 128.68 | 65.61 to 191.74 | 208.43 |

The 1,035 daily estimates, each with its interval, are in the table and on each page.

**How to read them:**
- **Two intervals include zero:** ERCOT's demand under COVID-19, and ERCOT's hub price during Elliott.
- **The winter and summer effects include the weather and the growth since the baseline years.**
  - ERCOT's 2023 heat is measured against 2021 and 2022, and ERCOT's load grew in between.
  - Treat them as upper bounds on what the events did beyond the weather and the growth.

## Decisions made without a human

1. **Routing:**
   - The vacuum and the weekly workflow were not attempted again, nor worked around, after auto mode denied them.
   - Part A ran in full.
   - Part B did not, since run 14 had not passed when Part A was done. The prompt says "do not wait idle", and session 48 comes next.
2. **The table stays out of Supabase:** the pages compute their estimates from `event_window_daily`, which is already live, with a second implementation of the estimator held equal to the first by a test.
3. **The day-effect standard error:** sqrt(s2 + x'Vx) rather than the regression's robust standard error, which is degenerate for a one-day indicator. Explained in the method.
4. **The hour-of-day profiles** are in the table and the method, but not on the pages. They come from raw extracts, which the notebook cannot fetch through the `erw` package, and the prompt asks it to reproduce every estimate on the pages.
5. **The table is not uploaded to the Redivis draft** (above).
6. **`/deals`** showed "no deals this month" in a local build just after midnight UTC, the first hours of October. That is the page's calendar, not a fault of this session; live it passed.

## Open questions

1. **The vacuum and the weekly job:** please run `VACUUM (FULL, ANALYZE)` yourself, or allow it, and say whether the weekly workflow should be added once allowed.
2. **The Redivis upload of `event_study_estimates`:** add a single-table option to `upload.py` (a code change), or upload it by hand?
3. **A trend term:** should the event study add one (a linear year trend over the baseline years, plus one for the event year)? It would remove load growth from the 2023 and Elliott estimates, at the cost of wider intervals with only two baseline years.
4. **`/deals` at a month's start:** should it show the previous month while the new month has no deals?
