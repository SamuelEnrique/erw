# Session 11402 report (chain 770, part B item 1, the old laptop, 28 November 2026)

The ERW forecast (`https://erw-flame.vercel.app/forecast`, in review) audited as a power trader's quant who wants it wrong: `docs/reviews/forecast-model-audit-2026-11-28.md`, with its scripts and outputs in `docs/reviews/forecast-model-audit-2026-11-28/`.

## What was done

- Read the brief, chain 770's file, chain 710's file, the battery and grid audits, the ground, the method notes, the data requests, and main's log on the forecast.
- This machine holds none of the demand tables the forecast reads, so every figure was restated from the page's own files and from two earlier builds of them (`git show`), with none of the builder's code. What needs the tables is five data requests.
- Five findings, each on its own branch cut from origin/main, each pushed; none requested.

## In short (as in the audit)

- The arithmetic is right: the default view to the digit; the last 30 days restated in 61 of 64 places (the other three by a rule the hour rows cannot carry); the score file adds up; every method scored on one count of hours (9,015 of 9,015 groups).
- Nothing is known early in the backtest's code; revisions let the backtest read day A as revised, a live forecast as first published: 184 of 696 hours moved, 0.08 percent on mean (finding 5).
- The live price forecast is made at 19:00 UTC, after ERCOT's day-ahead prices are usually public, and refit on demand one day newer than the forecast scored (finding 3).
- Main's place files are a day behind the ledger: "Tomorrow" is 27 November on 28 November, and for 35 places a forecast no ledger holds (finding 2); a tomorrow drawn from the ledger says it read demand it did not (finding 1).
- The tomorrow file and the ledger agree on every figure (request 577).
- The hourly demand forecast beats both naive lines before its choice window too, in all 64 places.
- The choice is made on the window it is scored on: SPP's price regression and PSCO's peak lose to the naive line over the rest of the backtest (finding 4, for Samuel).
- The band holds 78.5 percent over two years, as the page says, and far less in a cold month, which the page's own month table shows.

## Branches

| Branch | Head | Kind |
|---|---|---|
| `wip/audit-forecast-doc` | this commit | the audit and this report |
| `wip/audit-forecast-1` | `18d30a35e` | words (run.py from_ledger) |
| `wip/audit-forecast-2` | `ae81856ab` | words (view.tsx, the page: chain 720's file) |
| `wip/audit-forecast-3` | `a8d99768f` | words (run.py made_rule, predict_price.md) |
| `wip/audit-forecast-4` | `21e5f2677` | test only, for Samuel's ruling |
| `wip/audit-forecast-5` | `74d58b919` | words (predict.md) |

## Landing rows for the main session to write

1. `wip/audit-forecast-1`: a tomorrow drawn from the ledger carries the ledger's horizon and last hour read, and the making's day as fit day (`warehouse/predict/run.py`); no forecast figure moves; shows at the data machine's next run. Test `tests/test_audit_forecast_1.py`; `tests/test_predict.py` 36 of 36 here.
2. `wip/audit-forecast-2`: the Tomorrow block says when the ledger holds a later day than the place file (`site/app/forecast/view.tsx`). Drawn to HTML from main's files; the page's three drawing tests and tests 10410, 10411, 10413 pass. No site build was run on this machine: the desk's fresh build is needed before landing.
3. `wip/audit-forecast-3`: the price made rule and `predict_price.md` section 2 say what the live forecast is (19:00 UTC, after ERCOT's prices, two days of demand). Test `tests/test_audit_forecast_3.py`.
4. `wip/audit-forecast-5`: `predict.md` section 2 says the backtest reads demand as revised, with the measure. Test `tests/test_audit_forecast_5.py`.
5. Branches 1 and 3 both edit `warehouse/predict/run.py` (different functions and the `made_rule` line); a trial merge is advised before landing both.

## For Samuel's ruling (one line each, default "left as it is")

- Finding 4: choose each method on the whole backtest, not the last two years: SPP's price forecast becomes yesterday's price (last two years 14.52 to 16.53 USD/MWh, backtest 34.63 to 18.73), PSCO's peak becomes yesterday's peak (7.35 to 8.76 percent; 10.39 to 8.35), Tennessee's peak the regression (8.32 to 8.49; 8.62 to 7.95), 13 smaller moves under 2 percent.
- Finding 3: hold the live price forecast to the scored horizon (three days of demand) and run it before ERCOT publishes; its effect on SPP's and CAISO's live forecasts needs data request 4.

## Data requests for the main session to write

1. The desk: main's place files, `index.json`, `scores.json`, `price_hubs.json` level with the ledger (the run's files or a newer run), and `ledger_price_hubs.csv` committed when written.
2. Data machine: per place, the hours screened out of the operator's forecast over the last two years and both MAEs with them put back.
3. Data machine: the ledger's band coverage (inside, below, above) against the actuals, by place, once 30 days are held from 27 November.
4. Data machine: `run.py --now 2026-11-27T14:00:00Z --no-ledger --places region-cent ba-swpp region-cal ba-ciso`, the price forecasts set beside the ledger's 19:00 UTC making for 28 November.
5. The 24 empty SPA rows of `ledger_demand.csv` (data request 20) are still on main and in the page's ledger download.

## Rules and slips

- No model call, no table written, no lock, no build, no browser, no em dash. Tables read: none (the demand tables are not on this machine).
- Slip: one bash heredoc was attempted for a draft file and failed on a quote before it wrote anything; the draft was then written with the Write tool. One `sed` replacement for a draw script lost its backslashes (as the machine's memory warns); the script was rewritten with the Write tool.
- The site's `node_modules` junction made in the worktree was removed at the end.
