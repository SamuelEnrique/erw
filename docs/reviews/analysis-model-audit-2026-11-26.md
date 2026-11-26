# Automated Analysis: the engine audited as a hostile econometrician would

Session 10204, 26 November 2026, chain 710 part C, on the old laptop. Read as an econometrician who wants to find the engine wrong. The audit of the findings' sentences (`docs/reviews/findings-audit-2026-11-19.md`) is not repeated: this is the engine under them.

- Nothing changed on main but this file and its evidence folder. No table written, no lock taken, no default moved, no draft's state changed, no model called (spend USD 0).
- Each finding's test is on its own branch, `wip/audit-analysis-<n>`. Branches 5, 9, 12 and 13 change words only and are returned for landing; every other branch holds a test that shows the finding, not for landing, and the fix is Samuel's ruling.
- Evidence: every script and its output in `docs/reviews/analysis-model-audit-2026-11-26/` (`a1` to `a11`), run on this machine from files on disk, the main checkout's tables read and never written.

## In short

- **The arithmetic is right.** Every figure re-done by hand came out to the digit: all 37 yearly claims of the forty (first, last, the five tests, the strength), four of them again from ERCOT's prices (drafts 4, 5, 6 and 20), the impact study's difference and Newey-West error, the hourly curtailment fit and its clustered error, and five figures of the week of 2026-W44 (WTI's 107.17 and its score 87.5, the ERCOT peak premium 16.91, CAISO curtailment 33,335.55 MWh, HB_WEST's 19 negative hours, CAISO's evening batteries 6,763.2 MW).
- **Held and paused grids' figures are in public files (finding 2, the most urgent).** The impact study's default card and its download hold 56 days of NYISO New York City prices; the template gallery holds 88 NYISO, 54 ISO-NE and 48 MISO charts; the weekly results hold NYISO's and SPP's regulation prices; all are copied to the site's public folders. No step of the weekly run or the gallery reads the license file.
- **The five tests are not a test against chance (finding 1).** A yearly series with no trend at all passes all five 12 to 16 percent of the time if its years are independent, 38 to 43 percent if they persist, 50 to 83 percent if it wanders like a price. The deep hunt tried 234 candidates over their regions and kept what passed; no draft says how many were tried.
- **Draft 3 falls by construction (finding 3).** The "tightest hours" are the hours of highest demand less wind less solar: the more solar a grid has, the less sun is in them. Solar's 71.1 to 5.0 percent says that, not that solar fails in tight hours.
- **Draft 6's first figure is an artifact (finding 4).** A plain mean of clock hours: 40 percent of 2015's cheapest hours fall from 21:00 to 02:59, where 23:00 counts as 23 and 01:00 as 1. The circular mean is 2.5, not 6.0; the move is 8.0 hours, not 4.6.
- **The engine of all forty has no method note (finding 5, fixed in words).** None of the three notes describes the deep hunt (`warehouse/analysis/findings/deep/builder.py`). Its drafts also lack the step-or-trend flag the weekly hunt's carry: 12 of 37 are a step by the engine's own rule (finding 6).
- **What the cards' errors assume.** The impact study's verdict flips with the lag count (p from 0.006 to 0.076 on 28 days); clustering the hourly curtailment fit by week instead of day makes its error 1.64 times larger, by month 2.64 times (the sign holds); the scanner, on series with nothing in them, raises 30 to 36 flags a day across the 6,797 series it scans (findings 10, 11).
- **Draft findings shown wrong: 3 and 6.** Their states are untouched. Drafts 33 and 39 rest on six years, one of them weather (finding 7).

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/research/page.tsx` (`/analysis` redirects to `/research`, `site/next.config.ts`) | The page: the request form, today's chart, this week's chart, the findings library, the archive |
| `site/app/api/analysis/route.ts` | `POST /api/analysis`: a reader's request or a finding with its inputs becomes a row of `analysis_requests` (migration 027) |
| `site/app/internal/findings/page.tsx`, `state/route.ts` | The review list; approve, dismiss, ask for a full card. Nothing reaches `/research` without approval |
| `site/scripts/build-content.mjs` (lines 145 to 165) | Copies the whole of `docs/analysis/` (the weeks, `results.json`, the gallery) to `site/public/analysis-files/` |
| `site/proxy.ts` (line 71) | The review curtain's matcher leaves every address with an extension alone: a `.csv` or `.json` under `public/` is served to anyone |
| `warehouse/analysis/run.py` | The weekly job: every template and watch line, the rule since session 119 (`change`: a change ranked among the last 104 weekly or 36 monthly changes, at least 8; `finding`: the two sentences), the chart of the week, `results.json`, the gallery over every parameter choice |
| `warehouse/analysis/watch.py` | The watch list: one line a measure (table, entity, variable, how a period is made, what it is compared with) |
| `warehouse/analysis/templates/*.py` (10) | The chart templates: `peak_premium_block`, `da_rt_spread_by_hour`, `forecast_error`, `curtailment_midday`, `implied_heat_rate`, `storage_evening_peak`, `negative_price_hours`, `deals_by_month`, `datacenters_by_state`, `chokepoint_transits` (internal) |
| `warehouse/analysis/findings/findings_scanner.py`, `warehouse/config/scanner.yaml` | The daily scanner: five rules (record, first negative price, spike, weekly change outside its five-year range, a pair's break) over every table `coverage.csv` calls public |
| `warehouse/analysis/findings/daily_chart.py` | The Digest's chart of the day from the scanner's flags; `HELD = ("nyiso", "spp")` |
| `warehouse/analysis/findings/hunt.py`, `hunt_measures.py` | The weekly hunt: 20 patterns, `test_claim` (the five tests), `blocked_grids`, the session-361 statistics on its drafts |
| `warehouse/analysis/findings/deep/builder.py` and 44 family modules | The deep hunt (chains 164 and 502): 234 candidates, each run over its regions and tested by `hunt.test_claim`; the source of all forty shortlisted drafts and of the 549 in `docs/findings/` |
| `warehouse/analysis/findings/deep/rank.py` | The reading order: consequence plus novelty plus strength |
| `warehouse/analysis/findings/findings_common.py` | `ols_hc1` (HC1 with Newey-West beside it), `trend_p`, `step_or_trend` |
| `warehouse/analysis/findings/*.py` (11 cards) | The findings library: `batteries_lunch`, `batteries_lunch_grids`, `batteries_curtailment`, `batteries_curtailment_hourly`, `impact_study`, `gas_sets_price`, `negative_prices_west`, `peak_hour_grids`, `peak_hour_moved`, `queue_divorce`, `who_rescues_whom` |
| `docs/methods/automated_analysis.md`, `automated_analysis_scanner.md`, `automated_analysis_findings.md` | The three notes. None describes the deep hunt (finding 5) |
| `docs/findings/<family>/<slug>.*`, `docs/findings/_top40/`, `docs/reviews/findings-shortlist-2026-11-19.md` | The forty: each draft's sentence, yearly CSV, chart, Python and Stata reproductions; the sheet and its Stata runner |

## Each statistic re-done by hand

| Template or engine | Finding re-done | Data | Result |
|---|---|---|---|
| The deep hunt's claim and five tests (`hunt.test_claim`) | all 37 yearly claims of the forty | each draft's own CSV, an independent restatement (no import of `hunt.py`) | 37 of 37: first and last, test 1's count, the strength to its printed two decimals (`a2`) |
| `midday_discount` (deep, prices) | draft 4, LZ_WEST | `ercot_zone_prices_history` | 2015 128.9493, 2025 48.9315 (the draft: 128.949269, 48.931538) (`a3`) |
| `evening_premium` | draft 5, HB_SOUTH | `ercot_all_hub_prices_history` | 109.5488, 160.9938 (109.549, 160.994) |
| `cheapest_hour` | draft 6, HB_NORTH | the same | 6.0356, 10.6740 (6.03562, 10.674) |
| `wide_spread_days` | draft 20, LZ_WEST | `ercot_zone_prices_history` | 28.7671, 84.1096 (the same) |
| `impact_study` | the default card (Uri, 14 days) | its download `erw_2026_impact_event_control.csv` | b 3,016.4007, Newey-West error 1,598.9276 at 3 lags, p 0.0704: the card's, to the digit (`a5`) |
| `batteries_curtailment_hourly` | the third fit | its download `erw_2026_caiso_curtailment_hourly.csv` | -0.0956246 per MW, error 0.0101466 clustered by day (2,807 days): the card's |
| `run.change` and `run.finding` (the rule) | 2026-W44, WTI | `eia_fuel_spot_prices` | 107.17 against 99.93, +7.24, score 87.5, 13 of 104 as large: the caption's (`a11`) |
| `peak_premium_block` | W44, ERCOT HB_NORTH | `iso_rtm_hub_prices` | 32.96 minus 16.05 = 16.91 |
| `curtailment_midday` | W44 | `caiso_curtailment_daily` | 33,335.55 MWh |
| `negative_price_hours` | W44, HB_WEST, September 2026 | `iso_rtm_hub_prices` | 19 of 720 hours |
| `storage_evening_peak` | W44 | `caiso_battery_storage` | 6,763.2 MW (17:00 to 20:59 Pacific, 336 intervals) |
| The scanner's rules | not re-done on a flag (no run's `flags.json` on this machine); their behaviour measured on simulated series (finding 10) | | |
| Not re-done | `da_rt_spread_by_hour`, `forecast_error`, `implied_heat_rate`, `deals_by_month`, `datacenters_by_state` (a count that moves as the ERW reads), the 28 tables of the forty this machine does not hold (their claims re-done from their CSVs only) | | |

## Findings, most urgent first

| # | Finding | Severity | Measured | Branch | Fix |
|---|---|---|---|---|---|
| 2 | Held and paused grids' figures in public files | high | 56 NYISO days in a download; 190 gallery charts (NYISO 88, ISO-NE 54, MISO 48); NYISO and SPP in every week's results since the holds | `wip/audit-analysis-2` | figures: ruling |
| 1 | The five tests are not a test against chance; how many were tried is not said | high | no-trend series pass 12 to 83 percent; 234 candidates | `wip/audit-analysis-1` | ruling |
| 3 | The tightest hours are chosen by net load: draft 3 falls by construction | high (for draft 3) | a grid whose demand and sun never change: 43.5 to 3.2 percent as solar grows from 5 to 60 percent of the peak | `wip/audit-analysis-3` | ruling; data request |
| 4 | A plain mean of clock hours across midnight (draft 6) | medium | 2015: 6.04 plain, 2.54 circular, 3 median | `wip/audit-analysis-4` | ruling |
| 5 | The deep hunt has no method note | medium | the engine of 549 drafts and all forty | `wip/audit-analysis-5` | words: landing |
| 6 | The forty carry no step-or-trend flag and no round | medium | 12 of 37 a step by the engine's own rule | `wip/audit-analysis-6` | ruling |
| 7 | A trend from four to seven years passes | medium | four points can pass; 9 of the forty rest on six or seven | `wip/audit-analysis-7` | ruling |
| 8 | The chart of the week is the largest of 21 to 31 scores, and the caption reads as if it were one | medium | under no change, the largest of 21 is at or above 87.5 with probability 0.94 | `wip/audit-analysis-8` | ruling |
| 10 | The scanner's flags by chance | medium | 30 to 36 a day across 6,797 series with nothing in them | `wip/audit-analysis-10` | ruling |
| 11 | What the regressions' errors assume about neighbouring days and hours | medium | impact p 0.006 to 0.076 by lag; hourly error x1.64 by week, x2.64 by month | `wip/audit-analysis-11` | ruling |
| 9 | "The week before" when the week before is not held | low | the engine compares with two weeks back and says "the week before"; no published week has hit it | `wip/audit-analysis-9` | words: landing |
| 12 | A watch line calls the battery model "a model's upper bound" | low | the battery audit's finding 6: it is not one | `wip/audit-analysis-12` | words: landing |
| 13 | Two dollar measures do not say their dollars are nominal; draft 20's nominal line | low | 2 of 34; draft 20's first year 28.8 to 34.2 at an assumed 2.5 percent a year | `wip/audit-analysis-13` | words: landing |

## 1. The five tests are not a test against chance

- **Where.** `warehouse/analysis/findings/hunt.py` lines 295 to 345 (`test_claim`); `deep/builder.py` lines 260 to 300 (`run`: every candidate over every region, the passing ones sorted, two kept a candidate, twelve a family's session). The note: `automated_analysis_findings.md`, "The weekly hunt" ("they do not test a cause") and session 316's two more tests.
- **What the tests are.** The last full year against the first; at least two later years on the claim's side of the first; the same sign with the window moved a year either way; a floor of observations; half the change left without the first year; the change at least one "typical yearly move" (1.4826 times the median absolute change between full years).
- **What they pass when nothing is there.** `hunt.test_claim` itself, on 4,000 simulated series of each kind with no trend (`a1`):

| Series with no trend | 6 years | 7 | 9 | 11 | 25 | 45 |
|---|---|---|---|---|---|---|
| independent years (a level with noise) | 15.6% | 14.0% | 12.8% | 15.2% | 11.5% | 12.1% |
| persistent years (AR(1), rho 0.7) | 37.8% | 39.6% | 42.2% | 40.6% | 43.2% | 41.7% |
| a random walk (a price, a stock of something) | 50.3% | 53.4% | 60.1% | 63.9% | 76.7% | 82.8% |

- **The strength counts years.** A straight line with no noise has strength (n - 1) / 1.4826: 3.37 at 6 years, 6.74 at 11, 29.68 at 45. The forty's strengths (1.46 to 66.05) say mostly how long and how smooth a series is, not how unlikely its change is by chance; the reading order (`rank.py`) gives 3 points at two typical moves.
- **How many were tried for each kept.** The deep hunt's modules hold 234 candidates (`a7`), each run over every region its table holds (a state, a hub, a balancing authority, a country): thousands of claims for 549 drafts. The count of claims tested is in each run's `runs/deep/<day>/<family>.json`, which this machine does not hold (data request 1). No draft and no note says it. The weekly hunt's drafts carry a Benjamini-Hochberg q over their own round (session 361); the deep drafts carry none (finding 6), and that q itself assumes independent years: on a random walk of 11 years the straight-line p is under 0.05 in 58 percent of series (`a1`, the fourth column).
- **The test.** `tests/test_audit_analysis_1.py` on `wip/audit-analysis-1`: random walks of 11 years pass all five tests more than 40 percent of the time, independent years more than 8 percent, and a noiseless line's strength is (n - 1) / 1.4826. Passes on main.
- **For Samuel's ruling.** Whether a draft says how many claims its hunt tested and how many passed, and whether a test against chance (a trend test with errors that allow persistent years, or a permutation over the region's own years) joins the five. Default: left as it is. Measured: no-trend series pass 12 to 83 percent.

## 2. Held and paused grids' figures in public files

- **What the rules say.** NYISO and SPP are held by the owner's ruling of 12 October 2026 (`daily_chart.HELD`); ISO-NE, MISO and NYISO are "license needed" from 21 October (`warehouse/metadata/license_status.csv`); MISO is paused (`paused_sources.csv`). The weekly hunt never drafts them "whoever published the rows" (`automated_analysis_findings.md`, line 186).
- **Where they reach a public file.**
  - The impact study's default card uses NYISO New York City as its control (`site/data/findings/catalogue.json`; `automated_analysis.md`, `impact_study_control`). The card prints "license needed" for the control's figures, but the difference it reports (USD 3,016.40) is computed from them, and its download `site/public/findings/erw_2026_impact_event_control.csv` holds all 56 of NYISO's daily values (`control_value`). `site/proxy.ts` leaves any address with an extension alone, so the file is served to anyone.
  - The gallery: `run.py` runs every public template over every parameter choice, the held and paused grids included. `docs/analysis/gallery/` holds 88 NYISO charts, 54 ISO-NE and 48 MISO (and 12 SPP), with their figures (for example `peak_premium_block/hub=CAPITL_iso=nyiso_window=7.json`: NYISO's Capital zone, 2026-10-29 to 2026-11-04, peak minus midday 9.83 USD/MWh), last written 8 November. `build-content.mjs` copies them to `public/analysis-files/`.
  - The weekly results: `watch_nyiso_reg` (`nyiso_as_prices`, license needed) and `watch_spp_regup` compete every week; `docs/analysis/2026-W43` to `W45/results.json` print their headline values and source lines (NYISO 19.46 USD/MW, week of 28 September), copied to the site the same way. In 2026-W41 NYISO's ranked fifth of 31.
  - The deep hunt drafts EIA's rows for New York (draft 8, Canada to New York) and New England (draft 9). `builder.run` asks `hunt.grid_of(region)`, which reads `rp_can_ny` and `rn_ne` as grids "rp" and "rn", never blocked. Chain 502 chose this and put it under "For Samuel's ruling" (`docs/reviews/findings-hunt-plan-2026-11-19.md`, line 86); the method note still says the opposite.
  - The scanner reads every table `coverage.csv` calls public and never `license_status.csv` (`findings_scanner.public_time_tables`, line 168): `nyiso_rtm_zone_prices` is public there and license needed here, and `scanner.yaml` pairs `iso_zone_prices_history`'s NYISO zones. Its drafts are internal until approved; the daily chart filters NYISO and SPP, not ISO-NE.
- **The test.** `tests/test_audit_analysis_2.py` on `wip/audit-analysis-2`: the impact download holds a control column from NYISO; the gallery holds files for `iso=nyiso`, `iso=isone`, `iso=miso`; a week's results hold `watch_nyiso_reg`; `run.py` and `watch.py` never read `license_status`; `grid_of` passes drafts 8 and 9's regions; the scanner's table list ignores the license file. Passes on main.
- **For Samuel's ruling.** Whether the held and paused grids leave the gallery, the weekly results and the impact study's default control (and the files already published are taken down). Default: left as it is. Measured: 56 NYISO daily values in one download, 190 gallery charts of held or paused grids, two held measures in every week's results, two drafts. This finding is a license matter: it is put first in the session's report.

## 3. The tightest hours are chosen by net load: draft 3 falls by construction

- **Where.** `warehouse/analysis/findings/deep/stress.py` (`tight_solar`, from `grid_stress_yearly`); the table's method `docs/methods/grid_stress.md` line 20: "The tightest hours: the 100 used hours of the year with the highest net load", net load "demand less wind less solar" (line 16).
- **Why it misleads.** The hours are picked by subtracting solar. As a grid adds solar, its highest net-load hours move to the hours with no sun, whatever the sun does. The draft says "Solar's output in ERCOT's tightest hours, as a share of its solar capacity, was 5.0 percent of solar capacity in 2025, against 71.1 percent of solar capacity in 2019": a reader takes it as solar failing when the grid is tight; it is mostly the definition.
- **How much, on the table's own definition.** A grid whose demand shape and solar shape never change, only solar's capacity (`tests/test_audit_analysis_3.py`): solar's output in the 100 hours of highest net load falls from 43.5 percent of capacity to 19.2, 6.3 and 3.2 as capacity grows from 5 to 20, 40 and 60 percent of the peak; in the 100 hours of highest demand it stays at 55.6 whatever the capacity. The measure moves with nothing but capacity.
- **What would measure the thing named.** The same share in the 100 hours of highest demand (not net of solar). ERCOT's hourly demand and solar (EIA-930) are not on this machine: data request 2.
- **Also.** Each year is one observation (`n` = 1), so test 3 ("sample large enough: 2019 holds 1 and 2025 holds 1 observations; the floor is 1") cannot fail; 83 of the 234 candidates have a floor of 1 or less (`a7`).
- **Draft 3 is listed as shown wrong** (its reading, not its arithmetic). State untouched.
- **For Samuel's ruling.** Whether `tight_solar`, `tight_wind` and `tight_gas` move to hours chosen by demand. Default: left as it is.

## 4. A plain mean of clock hours across midnight

- **Where.** `deep/prices_markets.py` lines 66 to 74 (`cheapest_hour`: `s["lhour"].mean()`). The draft's own limit says a year "split between night and midday averages to an hour in between"; the larger fault is the wrap at midnight, where 23:00 counts as 23 and 01:00 as 1.
- **How much.** HB_NORTH, from the hub history (`a3`):

| Year | Plain mean (the draft) | Circular mean | Median | Days cheapest 21:00 to 02:59 |
|---|---|---|---|---|
| 2015 | 6.04 | 2.54 | 3 | 39.7% |
| 2019 | 8.08 | 1.91 | 4 | 47.9% |
| 2025 | 10.67 | 10.59 | 10 | 17.3% |

- The draft's 2015 figure ("6.0") is an hour at which few days were cheapest; the move is +8.0 hours by the circular mean and +7 by the median, not +4.6. The direction holds.
- **The test.** `tests/test_audit_analysis_4.py`: the module's own `cheapest_hour`, fed days whose cheapest hour alternates 23:00 and 01:00, returns 12. Passes on main.
- **Draft 6 is listed as shown wrong** (its figures and the size of its move). State untouched.
- **For Samuel's ruling.** Whether the measure becomes the circular mean or the median. Default: left as it is. Measured: 2015 from 6.04 to 2.54.

## 5. The deep hunt has no method note (fixed in words)

- **Where.** `deep/builder.py` and its 44 family modules made 549 drafts, all forty of the sheet among them. `docs/methods/automated_analysis_findings.md` describes the weekly hunt (`hunt.py`) and its 20 patterns; neither it nor the other two notes names `deep/`, chain 164 or `scan-deep`. The method lives in `docs/reviews/findings-hunt-plan-2026-11-06.md` and `-11-19.md`, plans, not a method.
- **The fix, words only.** `wip/audit-analysis-5` adds a section "The deep hunt (chains 164 and 502)" to `automated_analysis_findings.md` that says what the code does: a candidate is a measure by region and year; every region is tested by `hunt.test_claim`; the passing are sorted by consequence then strength; two a candidate and twelve a family's session are kept; a region is held back only when `hunt.grid_of` reads a held grid (so EIA's rows for New York and New England pass); the drafts carry no `statistics` block (no trend p, no q, no step flag); the count of claims tested is in the run's file and in no draft. No figure moves.
- **The test.** `tests/test_audit_analysis_5.py`: the note names `deep/builder.py`, the two caps as the code holds them (`MAX_PER_CANDIDATE`, `MAX_DRAFTS`), and says the drafts carry no statistics block (fails on main, passes on the branch).

## 6. The forty carry no step-or-trend flag and no round

- **Where.** Session 361 gave the weekly hunt's drafts `statistics` (the trend p, Benjamini-Hochberg q over the round, `step_or_trend`); the page prints "A step, not a trend" when a step fits better (`FindingCard.tsx`). `deep/builder.py` builds its cards without any of them.
- **How much.** The engine's own `step_or_trend` on each of the forty's full years (`a8`): 12 of 37 fit a step better than a line, among them draft 5 (evening premium, break 2023), 9 (New England, 2024), 12 (data center construction, 2024), 16 (Henry Hub's daily move, 2020), 33 (cooling degree days in Texas: 8.81 before 2022, 9.95 from it) and 39 (reactors, 2022). Over the 37, two q-values exceed 0.05 (16 and 39), under the independence finding 1 shows does not hold.
- **The test.** `tests/test_audit_analysis_6.py`: `builder.py` never calls `step_or_trend` or `trend_p`, and the engine's own function finds draft 33 a step. Passes on main.
- **For Samuel's ruling.** Whether the deep drafts carry the session-361 block. Default: left as it is. Measured: 12 of 37 would be flagged.

## 7. A trend from four to seven years passes

- **Where.** `test_claim` needs four full years for test 2 and three for test 4, nothing more.
- **How much.** Four points rising by one a year pass all five (strength 2.02). Of the forty, 7 rest on seven full years (1, 3, 8, 9, 10, 11, 19) and 2 on six (33, 39); at six years a random walk passes half the time (finding 1).
- **The two weakest.** Draft 33, cooling degree days in Texas, 2019 to 2024: a weather measure, six years, three of five later years on its side, a step at 2022, and the region's weather table holds 2025 for 5,084 of 8,760 hours. Draft 39, the reactor fleet's capacity factor, 89.4 to 91.1 percent over six years: 55 percent of the change remains without the first year, the straight-line p is 0.08.
- **The test.** `tests/test_audit_analysis_7.py`: `test_claim` passes four rising points. Passes on main.
- **For Samuel's ruling.** A floor of full years (eight, say) for a drafted trend. Default: left as it is. Measured: 9 of the forty under eight.

## 8. The chart of the week is the largest of 21 to 31 scores

- **Where.** `run.py`: every measure's change gets a score, the share of its own last 104 (or 36) changes that were smaller; the highest score wins (`automated_analysis.md`, the rule's step 5). The caption: "Of the 104 week-to-week moves before it, 13 were as large."
- **What the caption leaves out.** It reads as one measure's rank. It is the top of 21 to 31 (`a4`: W41 31 competing, W43 25, W44 21, W45 21; chosen 96.9, 100, 87.5, 92.2). If no measure had moved more than usual, the largest of 21 scores would be at or above 87.5 with probability 1 - 0.875^21 = 0.94. A reader is told the chosen move is rare; it is rare for its measure, and the rule guarantees one such each week.
- **The test.** `tests/test_audit_analysis_8.py`: 21 random walks of 106 weeks through `run.change`: the largest score is at or above 87.5 in more than 85 percent of trials. Passes on main.
- **For Samuel's ruling.** Whether the caption says "the largest of N measures' moves this week". Default: left as it is. Measured: the probability above.

## 9. "The week before" when the week before is not held (fixed in words)

- **Where.** `run.change` pairs each held period with the previous held one (line 161); `run.finding` writes "the week before" for any weekly figure (line 190). A watch line drops a week with too few rows (`need`), so a gap is possible.
- **Shown.** A headline of 25 to 31 May with 18 to 24 May missing is compared with 11 to 17 May, and the caption says "up 10 from 10 the week before" (`a10`). No published week has hit it: every compared week in `docs/analysis/` ends the day before its headline begins.
- **The fix, words only.** `wip/audit-analysis-9`: when the compared week is not the one just before, the caption names it ("from 10 in the week of 2026-05-11 to 2026-05-17"). The score and every figure are unchanged.
- **The test.** `tests/test_audit_analysis_9.py` (fails on main, passes on the branch); the adjacent case keeps "the week before".

## 10. The scanner's flags by chance

- **Where.** `findings_scanner.py` lines 330 to 467, `scanner.yaml`. The first run scanned 6,797 series and raised 17 flags (`automated_analysis_scanner.md`).
- **What noise alone raises.** The engine's own `rule_record`, `rule_spike`, `rule_weekly` and `settled`, on 3,000 simulated daily series of each kind with nothing in them, one scan each (`a6`): independent lognormal days 0.07 percent of series (4.5 flags across 6,797), persistent days (log AR(1), rho 0.9) 0.43 percent (29.5), fat-tailed days (t, 3 degrees of freedom) 0.53 percent (36.3), before the cap of 12 drafts a day.
- **What the note says.** "A flag is a statement about the table ... not a statement about the world until a person has read the rows": right, and the review is the guard. It does not say how many flags chance gives, so a reviewer cannot weigh a day's twelve.
- **The test.** `tests/test_audit_analysis_10.py`: on persistent simulated series the three rules flag more than 0.1 percent per scan. Passes on main.
- **For Samuel's ruling.** Whether the note and the review list print the expected count by chance beside each day's flags. Default: left as it is.

## 11. What the regressions' errors assume

- **The impact study (28 days, a step dummy).** Newey-West at the rule's 3 lags gives p 0.0704 ("within 1.96 standard errors"). The days are strongly dependent (residual autocorrelation 0.76 at one day, after the date) and the verdict moves with the lag count: 0 lags p 0.0055, 1 lag 0.031, 2 to 7 lags 0.055 to 0.076, 10 lags 0.035, 13 lags 0.018 (`a5`). With 28 days no lag rule is reliable; the card states one verdict.
- **The hourly curtailment fit.** Clustered by Pacific day (2,807 clusters), error 0.0101. Weather and the fleet carry over days: by week (409) 0.0166 (x1.64), by month (94) 0.0268 (x2.64). The sign and p under 0.001 hold.
- **The five-grid lunch card.** NYISO's worst-interval multiple: HC1 p 0.039 (the card's), Newey-West p 0.108 (beside it); SPP's hours in the top 1 percent the other way (0.052 against 0.039). The subtitle follows HC1.
- **The hunt's trend p.** Ordinary least squares on years assumes independent years; finding 1 shows what that gives on persistent series.
- **The test.** `tests/test_audit_analysis_11.py`: from the public downloads, the impact study's p crosses 0.05 between 1 and 2 lags, and the hourly error clustered by week is more than 1.5 times the day's. Passes on main.
- **For Samuel's ruling.** Whether the impact study shows its p at several lags and the hourly card clusters by week. Default: left as it is.

## 12. A watch line calls the battery model "a model's upper bound" (fixed in words)

- **Where.** `warehouse/analysis/watch.py` line 72, `watch_battery_model_ercot`: "What a 2-hour battery could earn in Texas (a model's upper bound)". The battery audit (`docs/reviews/battery-model-audit-2026-11-20.md`, finding 6) shows the model's figure is not an upper bound: its empty start and hourly energy hold it 8.3 percent under a foreseeing battery's.
- **The fix, words only.** `wip/audit-analysis-12`: "(a model with perfect foresight, not an upper bound)". Land with or after `wip/audit-battery-6`, which fixes the battery page's own words.
- **The test.** `tests/test_audit_analysis_12.py` (fails on main, passes on the branch).

## 13. Dollars: two measures do not say nominal; draft 20's nominal line (fixed in words)

- **Where.** Of the 34 deep candidates in a dollar unit, 32 say "nominal" in their limits (`a7`); `hub_basis` and `spark_spread` (`deep/prices.py`) do not.
- **Draft 20.** Its line is USD 50 a MWh in every year, and its limit says so. Held at USD 50 of 2025 with an assumed 2.5 percent a year (the audit's assumption; no deflator is held in the warehouse), LZ_WEST's 2015 share is 34.2 percent, not 28.8; the change is 49.9 points, not 55.3 (`a3`).
- **The fix, words only.** `wip/audit-analysis-13`: the two limits gain "Nominal dollars, not adjusted for inflation". A draft already built keeps its words until rebuilt.
- **The test.** `tests/test_audit_analysis_13.py` (fails on main, passes on the branch).

## The attacks of the chain file, item 3, each answered

| Attack | Where answered |
|---|---|
| Many cuts tried, the striking kept: how many per kept, said or corrected | finding 1 (deep and weekly hunts), finding 8 (the rule), finding 10 (the scanner); corrected nowhere but the weekly hunt's q (session 361) |
| Two periods that differ in more than the thing named | finding 3 (tight hours move with solar); the sheet's own "one thing that would make it wrong" lines name it for drafts 1, 2 and 8 (a zone's bounds, a customer class, the ties between regions), read and not repeated |
| A trend from too few points | finding 7 |
| An average that hides a few extreme days | checked below: the price drafts hold on medians and with the dearest hour in a hundred left out; finding 4 (a mean of a clock) |
| A "since" chosen after looking | checked below: no |
| Correlation worded as cause | checked below: no draft or caption sentence says a cause |
| Units and the dollars' year | finding 13 |
| A held grid's data reaching a finding | finding 2 |
| Standard errors and neighbouring hours | finding 11 |

## What was checked and found right

- **Averages and extreme days.** Draft 4 (midday at LZ_WEST) with medians: 117.5 to 59.0; with the year's dearest 1 percent of hours left out: 118.6 to 51.9. Draft 5 (evening at HB_SOUTH): medians 114.7 to 157.0; trimmed 112.6 to 153.4. The years between swing with scarcity (in 2021, 61 percent of LZ_WEST's summed price fell in its dearest 1 percent of hours), but both claims' end years are calm and both hold (`a3`).
- **A "since" chosen after looking.** Every one of the forty starts at its table's first full year or at a first year the candidate states (`first_words`), and ERCOT's price tables begin in 2015, the drafts' first year. The lunch card's first year (2019, the lowest choice the page offers) does not matter: run at 2015, 2017 and 2019 the regression is the same 92 months (2019-01 to 2026-08), coefficient -10.7562 each time, because the load table begins in 2019 (`a9`). (The card on the page, computed 12 November, prints -10.8077; the tables have moved since, and the daily recompute follows them.)
- **Cause.** The deep sentence template (`builder.sentence`) states a figure, a place, two years and nothing else; the cards say "goes with" and "association"; the weekly caption states a move and its rank.
- **The weekly score.** `run.change` ranks by "smaller in size", the caption counts "as large": consistent; the known difference of 6 November (87.25 from the file against 87.5, 102 earlier changes in the file against 104 in the run) is already in the note.
- **The five tests' arithmetic.** As the note says, on every claim of the forty.

## Not covered, or left open

- The weekly hunt's 20 patterns and their drafts were not re-run (their tables are on the data machine).
- 28 of the forty's tables are not on this machine: their claims are re-done from their CSVs, their measures not from the tables.
- The scanner's real flags: no run's `flags.json` is here; the rules are measured on simulated series only.
- No Stata was run (none on this machine); no page was drawn (no build, by this machine's rule).

## The branches

Each from origin/main of 26 November 2026, pushed; the tests run with every test file that imports the changed module or reads the changed note.

| Branch | Kind | Test | What else was run |
|---|---|---|---|
| `wip/audit-analysis-1` | figure: shows the finding, not for landing | `tests/test_audit_analysis_1.py` | |
| `wip/audit-analysis-2` | figure: shows the finding, not for landing | `tests/test_audit_analysis_2.py` | |
| `wip/audit-analysis-3` | figure: shows the finding, not for landing | `tests/test_audit_analysis_3.py` | |
| `wip/audit-analysis-4` | figure: shows the finding, not for landing | `tests/test_audit_analysis_4.py` | |
| `wip/audit-analysis-5` | words: `docs/methods/automated_analysis_findings.md` gains the section on the deep hunt | `tests/test_audit_analysis_5.py` | the 13 test files that read the note |
| `wip/audit-analysis-6` | figure: shows the finding, not for landing | `tests/test_audit_analysis_6.py` | |
| `wip/audit-analysis-7` | figure: shows the finding, not for landing | `tests/test_audit_analysis_7.py` | |
| `wip/audit-analysis-8` | figure: shows the finding, not for landing | `tests/test_audit_analysis_8.py` | |
| `wip/audit-analysis-9` | words: `warehouse/analysis/run.py`, `finding()` names the week compared with when it is not the one just before | `tests/test_audit_analysis_9.py` | the 14 test files that import `run.py` or test its captions (344 passed, 2 skipped) |
| `wip/audit-analysis-10` | figure: shows the finding, not for landing | `tests/test_audit_analysis_10.py` | |
| `wip/audit-analysis-11` | figure: shows the finding, not for landing | `tests/test_audit_analysis_11.py` | |
| `wip/audit-analysis-12` | words: `warehouse/analysis/watch.py`, the battery line's title | `tests/test_audit_analysis_12.py` | the 4 test files that import `watch.py` (107 passed) |
| `wip/audit-analysis-13` | words: `warehouse/analysis/findings/deep/prices.py`, two limits say "Nominal dollars" | `tests/test_audit_analysis_13.py` | the 3 test files that import the deep prices module (15 passed) |

- The words branches fail their test on main and pass it on the branch; the figure branches pass on main.
- No site build and no snapshot here (this machine's rules: no build, no request to a live service). This file and its folder change no page; every page is in review. The words branches touch no page file; their landing is the desk's, with rule 8's snapshot there.

## Data requests (returned to the chain's desk, not written here)

1. From `runs/deep/<day>/<family>.json` of chains 164 and 502 (the desktop): for each family, `claims` and `passed`, and the drafts kept; so finding 1 can say how many claims were tested for each draft.
2. From `eia930_ba_supply_hourly` and `eia930_ba_demand_hourly`, ERCOT (ERCO), 2019 to 2025: solar's output as a percent of solar capacity in the 100 hours of highest demand (not net load) each year, beside the table's tight-hours figure; so finding 3 can say what draft 3 would read on hours chosen by demand.
