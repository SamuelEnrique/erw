# Review pack: Research

- Address: `/research` (production `https://erw-flame.vercel.app/research`), with a week's chart at `/research/<week>`, one card at `/research/card/<id>`, and the review list of drafts at `/internal/findings` (internal view only).
- Status: in review, like every page (`site/lib/release.ts`: no page is live since session 166). A visitor sees the in-review page; the review needs the internal view (`https://erw-flame.vercel.app/internal/open`).
- Written from: the branch `wip/267-research-ask` at `412eeef9` (base `ce6ee59b`, session 268's palette), on 2026-10-14, session 267.
- Replaces: the how-it-works note on Research (session 260, from `main` at `34b468fa`); all of its content is folded in below, its demo kept as the appendix.
- The page landed as `01161064` (session 238, which renamed Automated Analysis to Research). `/analysis` and every address under it answer with a permanent redirect to the same place under `/research` (`site/next.config.ts`).
- Since session 260's note: session 251 took the weekly hunt from 7 patterns to 20 and raised 12 drafts (the list holds 28); session 258 made a draft's source line name only the tables whose rows it uses; session 267 put the verdict of 13 October beside each draft, the brand palette in the charts, a guard on the daily chart, a plain-names file and the do-files' first lines.

### Session 315: the page as built (19 October 2026)

The owner's rulings of 19 October on section 9 and of 13 October on the layout, built by session 315 (`archive/sessions/SESSION_315_REPORT.md`):

- The page, in order: **the request form** (the reader's own question, the tables to read, an email for the answer; it writes `analysis_requests` through the server route and a person answers), with the finding flow under it; **today's chart** with its sentence and its record's figures; **this week's chart** (the Roundup's) with its callouts; **the findings library** (the approved cards, each with its chart, its sentence, its tables and its downloads); **the archive** last. Every figure on a card is a Num with its card's JSON (`finding|...` keys), today's record's figures too (`digest_chart|...`).
- Section 9's outcomes: **1b** nothing changes at `/internal/findings` (no card reaches the page without approval). **2a** the hunt's floor and fourth test: session 316. **3a** the 25 percent guard stays. **4b** a record of EIA's newest month carries the publisher's figure: session 316. **5b** the plain names follow the methods notes (six of the seven drafts rewritten, listed in the methods note; the retail sales draft stays, no note names it). **6a** the NYISO and ISO-NE figures on the cards read "license needed" from 21 October by the tools' rule; the cards stay.
- Counts on the branch: the eleven analyses, the eleven committed cards and the nine in the library are as the table below says; the drafts on the review list and the verdicts are session 304's (`site/lib/findingverdicts.ts`, each dated).

## Against roadmap item 2 (session 381)

Roadmap item 2 (`docs/roadmap.md`, "Five tools sellable") is done for a tool when it has a method note signed by Samuel, a replication a reader can run, a cross-check table against published figures and a decisions block. Read on 21 October 2026 by session 381 from `wip/381-five-tools` (cut from `main` at `dc4d5ba6`); every exit code below is of a run that day, its output under `runs/chain_oct21/s381/` on the code machine. The checks that read the built site were not run: the local production build stopped twice on Supabase statement timeouts (the home page's required read), and each cell says so. No method note is signed: none of the five has a signature in any file. No page and no default figure was changed by this session. The parts below this section are the pack as written on 14 October and amended since; where a figure here differs, this section is the newer.

| Roadmap item 2 asks | What the tool has | Where | Today | What it lacks |
|---|---|---|---|---|
| A method note signed by Samuel | `automated_analysis_findings.md` (every card: data, method, the hunt, the page, session 361's statistics) and `automated_analysis.md` (the weekly engine); no note in the decision tools' algorithm form | `docs/methods/automated_analysis_findings.md`, linked from every card (`method`) | not signed: no sign-off block, no signature in any file | Samuel's signature, and a block to sign in |
| A replication a reader can run | Each card downloads its CSV, its do-file and its generator's Python. New in session 381: one Python mirror of the nine library cards' do-files, from their CSVs alone (standard library and numpy) | `site/public/findings/`: `<card>.do`, `<card>.py`, the CSVs; `erw_2026_research_replication.py` (session 381) | The new mirror: exit 0 from its folder; with `--json site/data/findings`, 304 figures compared, 0 different (exit 0). The cards' own `.py` downloads: exit 1 when run from the folder, 11 of 11 (`ModuleNotFoundError: findings_common`: each is the generator and reads the warehouse's tables). The do-files: not run | A link to the new mirror from `/research` (a page change). The cards' `.py` downloads do not run for a reader: whether to ship `findings_common.py` beside them or to say on the card that the do-file and the mirror are the replication is for Samuel |
| A cross-check table against published figures | New in session 381: a "Cross-checks" section in the decision tools' form, 4 rows (ERCOT's 2025 median and 99.9th percentile and the queue's withdrawn share against the owner's thesis, the CDC's two rates); part 4 below keeps 18 rows of reproductions against the ERW's own tables | `docs/methods/automated_analysis_findings.md#cross-checks`; part 4 below | `tests/test_session381.py` holds the form; no page line counts the rows | Publishers' figures not held, listed there: CAISO's annual curtailment totals, a market monitor's share of hours gas set the price, Berkeley Lab's report's own summary. Three of the four rows are against the thesis, not a publisher; whether that counts is for Samuel |
| A decisions block | None on the page. The rulings of 19 October on part 9 (1b, 2a, 3a, 4b, 5b, 6a) are in this pack and in the method note (session 315) | `site/app/research/page.tsx`: no block | none to check | A block that says the rulings on the page, as the Grid tool's does (session 299): a page change, listed for Samuel's ruling |
| Automated Analysis in its final form | Session 315's form, from the rulings of 19 October and the layout of 13 October: the request form, today's chart, this week's chart, the findings library (nine cards, one a screen), the archive; `/analysis` redirects to `/research` | `site/app/research/page.tsx`, `view.tsx`, `site/next.config.ts` | `check-analysis.mjs` (every card drawn with its JSON's numbers, the downloads, the visitor's page): not run on 21 October (no local build) | Samuel's word that this form is the final one |

**On a built site (session 422, 21 October 2026).** A build at 15:22 UTC of `wip/422-tool-checks`, which is main with chain 019's branches not yet landed (`wip/461-combined`), served on localhost; outputs in `runs/chain_021/s422/` (git ignores `runs/`). `check-analysis.mjs` as main holds it, exit 1: 269 of 279; the 10 failures are callouts that the cards now draw as "license needed" (the holds of 21 October), which session 474's version of the check (on `wip/474-checks`, not in this build) reads as held, 279 of 279 on production. `erw_2026_research_replication.py --json ../../data/findings` exit 0: 304 figures compared with the cards' JSON, 0 different.

## 1. What it is for, and for whom

- The question: what has the warehouse found in its own tables, how was each finding computed, and can a reader recompute it.
- A finding is a question put to the warehouse and answered as a card: a title, the answer as a subtitle, one chart that compares, two or three before and after numbers, a paragraph, a method footnote, and three files to download (the data, the Python, a Stata do-file).
- The page, in order: a form to ask for an analysis (the reader's own question since session 315, with the finding flow under it); today's chart; this week's chart; the findings library; an archive of every daily and weekly chart.
- Researchers: each card can be recomputed from its own download.
- Investors and operators: the cards state sizes with their errors, and say what the design cannot separate.
- The owner: a review list (`/internal/findings`) where he approves or dismisses what the scanner and the weekly hunt raised, now with the verdict of 13 October beside each draft.
- What it is not: no card claims a cause; no card is a forecast; nothing on a card, a draft or the daily chart is written by a language model.

What it holds on the branch today:

| Thing | Count | Where |
|---|---|---|
| Analyses in the catalogue | 11 | `site/data/findings/catalogue.json` |
| Committed cards | 11 (5 econometric, 6 visual), all computed on 2026-10-10 | `site/data/findings/` |
| Cards in the library | 9; the other 2 are earlier single-grid cards, linked under their five-grid successors | `SUPERSEDED`, `site/lib/findings.ts` |
| Download files | 33: 11 CSV, 11 Python, 11 Stata do-files; plus 22 pictures | `site/public/findings/` |
| Drafts on the review list | 28 at 18:19 UTC on 13 October 2026: 8 of the scanner, 20 of the weekly hunt, all in state draft | `archive/sessions/SESSION_251_REPORT.md`, "Checks" |
| Verdicts of the 28 | 7 strong, 14 usable, 7 drop (16 by session 252: 4, 7, 5; 12 by session 251: 3, 7, 2) | `docs/reviews/findings-verified-2026-10-13.md` |
| Drafts approved or dismissed | 0 at that reading | the same |
| Hunt patterns | 20 (7 of session 233, 13 families of session 251) | `warehouse/analysis/findings/hunt.py`, `hunt_measures.py` |
| Daily charts held | 6: five proofs (6 to 12 October) and the chart of 13 October | `docs/digest/charts/` |
| Weekly charts held | 3 (2026-W39, W40, W41) | `docs/analysis/` |

The eleven analyses, by family:

- Batteries and price spikes: "Batteries ate their own lunch?" for one ERCOT hub, and for five grids (econometric).
- Gas and the price: "Gas sets the price less often?" (visual).
- The queue: "Till queue do us part" (visual).
- The peak hour: "The peak hour moved" for ERCOT and CAISO, and for five grids (visual).
- Flows in an event: "Who rescues whom" (visual).
- Negative prices: "Negative prices march west" (visual).
- Batteries and curtailment in CAISO: day by day, and hour by hour (econometric).
- Impact of an event on a series: a before and after against a control (econometric).

## 2. The model, step by step

Here the model is the path from a question to a card on the page.

1. A question comes in by one of four doors: a session writes a finding as code (`warehouse/analysis/findings/<id>.py`); a person asks on the page, picking an analysis and its inputs from lists, no free text (`RequestFlow` in `site/components/analysis/RequestFlow.tsx`); the daily scanner flags a value (`scan()` in `warehouse/analysis/findings/findings_scanner.py`); the weekly hunt asks a finding's question of every region (`hunt()` in `warehouse/analysis/findings/hunt.py`).
2. A finding is one Python module that declares its id, title, kind (`visual` or `econometric`), its inputs with a default and a list of choices, and the tables it reads; `compute()` returns its rows and `card()` builds the card (`warehouse/analysis/findings/<id>.py`, loaded by `load()` in `warehouse/analysis/findings/run_finding.py`).
3. The computation runs on the data machine, which holds the full histories: a request is a row in a queue, `turn()` and `run_one()` in `warehouse/analysis/findings/worker.py` take the oldest row and `run()` in `warehouse/analysis/findings/run_finding.py` writes the card back. A table not on the machine is said; nothing is filled in; the worker writes no warehouse table.
4. The scanner's five rules: a record (`rule_record()`), a first negative price (`rule_negative()`), a spike (`rule_spike()`), a weekly change outside its five-year range (`rule_weekly()`), a break between two series that move together (`rule_pair()`), all in `warehouse/analysis/findings/findings_scanner.py`, thresholds in `warehouse/config/scanner.yaml`.
5. The hunt's three tests, `test_claim()` in `warehouse/analysis/findings/hunt.py`: the claim holds in at least two later full years; it keeps its direction with the window moved a year at each end; both end years are above the pattern's floor of observations. Session 251's 13 families are measures by region and year in `warehouse/analysis/findings/hunt_measures.py`; the two spike patterns are computed and never drafted (`one_interval`).
6. A draft's source line names only the tables whose rows it uses: `tables_used()` and `source_line_of()` in `warehouse/analysis/findings/hunt.py` (session 258); the eight older drafts keep the old line until the data machine runs `hunt.py --fix-source-lines`.
7. The statistics are fixed by the module: visual findings are counts and shares by year with no standard error; the monthly regressions are least squares of a spike measure on battery GW, load, the Henry Hub price and eleven month dummies with HC1 errors (`batteries_lunch_grids.py`); the hourly curtailment regression clusters by Pacific day, 2,779 clusters (`batteries_curtailment_hourly.py`); the impact study is a difference in differences with Newey-West errors (`impact_study.py`).
8. The words are written by code from the numbers: the subtitle is chosen by the fit, one sentence when the estimate is negative with p below 0.05, another when positive with p below 0.05, a third when flat (each module's `card()`, `warehouse/analysis/findings/`).
9. Every number on the card is checked against the code: `numbers_from_rows()` in each module recomputes every number from the rows of its CSV download alone; a test reads the committed CSV back and compares (`tests/test_session170.py`); the CSV's sha256 is pinned in the card.
10. A person rules: a draft waits at `/internal/findings` (`listDrafts()` in `site/lib/scanner.ts`, drawn by `site/app/internal/findings/page.tsx`) with three buttons, Approve, Dismiss, Ask for a full card (`site/components/analysis/DraftReview.tsx`); since session 267 each draft carries the verdict of 13 October (`VERDICTS` in `site/lib/findingverdicts.ts`, `VerdictLine` in the page). Nothing reaches `/research` before Approve; each ruling is kept with its time.
11. The card is published with its files: the data as CSV, the module as run, and a Stata do-file (`filesHeld()` in `site/lib/research.ts`); a file the site does not hold reads "not held" and is never a link. All 33 are held.
12. The page files each card under grids and topics read from the card's own fields (`gridsOf()` and `topicsOf()` in `site/lib/researchrules.ts`): a grid is a grid name found in the card's tables, inputs or chart; a topic is the kind of table the card read. Neither is a judgment of the finding.
13. Today's chart is the newest record of `docs/digest/charts/`, chosen by `choose()` in `warehouse/analysis/findings/daily_chart.py` from the scanner's strongest flag of the day that no Digest has shown, written by `fact_from_flag()` and drawn by `warehouse/analysis/findings/card_image.py`; a record marked `proof` is named a proof on the page.
14. The daily chart's guard (session 267): a scanner record more than 25 percent past the old one (`RECORD_JUMP = 0.25`, measured by `record_jump()`) waits a day: `must_wait()` keeps it off that run, `keep_held()` writes it to `docs/digest/charts/held.json`, and `held_before()` lets it be shown on a later day's run if the scan raises it again (`warehouse/analysis/findings/daily_chart.py`).
15. The chart colors are the brand's (session 267): up to five series in ink, cardinal, blue, grey and light grey, more than five in the eight `--chart-series-1` to `-8` (`series_colors()` in `warehouse/analysis/style.py`, read by `warehouse/analysis/findings/card_image.py`); on the site each color is read from its CSS variable (`LITERAL_TOKENS` in `site/components/echarts.ts`).
16. This week's chart is the chart the newest Roundup carried: a finding's card when one was chosen with "Use in Roundup" (`chosen_card_id()` in `warehouse/analysis/findings/roundup_pick.py`), else the weekly rule's pick (`change()` in `warehouse/analysis/run.py`); the week's results by the rule are folded under it (`roundupChart()` in `site/lib/research.ts`).
17. The page computes nothing: every number on `/research` comes from a committed file (a card's JSON, a chart's record, a Roundup) read at build by `loadCards()` in `site/lib/findings.ts`; no Supabase table is read when the page is drawn (`revalidate = 3600` in `site/app/research/page.tsx`).

Where a language model is used: in one place. The weekly chart of the week gets a two-sentence note drafted by a model (`warehouse/analysis/run.py`). The note is kept only if every number in it appears in the template's own sentences as written; after two failed drafts the template's sentences are used.

Where it is not: the findings engine, the scanner, the weekly hunt, the daily chart, the filing by grid and topic, and the review list.

## 3. Every assumption

"Inputs" means the lists under "Ask for an analysis". "Fixed" means a line of code or of `warehouse/config/scanner.yaml`, which a person edits.

| Assumption | Default | Source | Ruling of 12 October |
|---|---|---|---|
| Hub of the ERCOT spike card | HB_HUBAVG; inputs: 6 hubs | ERW's choice: the hub of the owner's thesis (`docs/methods/ercot_peak_premium.md`) | none |
| First year of the price cards | 2019; an input | ERW's choice | none |
| Spike measures | median, 99.9th percentile, their ratio, hours at or above USD 1,000 and USD 250; fixed | ERW's choice; numpy's linear percentile, no cap or exclusion | none |
| Controls of the monthly regression | load in GW, Henry Hub in USD/MMBtu, eleven month dummies (15 parameters); fixed | ERW's choice; `ercot_zone_load_hourly`, `eia930_daily_demand`, `eia_fuel_spot_prices` | none |
| Standard errors | HC1 (monthly, daily); clustered by Pacific day (hourly); Newey-West (impact study); fixed | Statistical convention: Stata's `vce(robust)`, `vce(cluster)`, `newey` | none |
| Significance that picks a subtitle | p below 0.05; fixed | Statistical convention | none |
| A full year | spike cards: 90 percent of its intervals; peak-hour cards: 300 held days; fixed | ERW's choice | none |
| Evening and midday | 17:00 to 21:59 and 10:00 to 15:59, local; fixed | ERW's choice | none |
| Heat rate of a gas plant | 7.0 MMBtu per MWh; inputs 6.5, 7.0, 8.0 | ERW's choice; 6.5 and 8.0 shown beside it | none |
| Gas price | Henry Hub, the calendar month's mean; fixed | `eia_fuel_spot_prices`; ISO-NE's share reads low on it, and the card says so | none |
| Negative price threshold | below 0 USD/MWh; inputs 0, minus 10, minus 20 | ERW's choice | none |
| Queue cohort | queue years 2000 to 2020; an input | `lbnl_interconnection_queue`, Berkeley Lab's 2026 edition | none |
| Impact study | 14 days before and after; ERCOT North Hub real-time, Winter Storm Uri, control NYISO New York City; inputs 7, 14, 28, 56 days, 23 series, 8 events or a date | ERW's choice; refused under 5 days held on either side | none |
| Scanner: a record's margin | 0.5 robust standard deviations past the old record | `record_min_margin_sigmas`, `warehouse/config/scanner.yaml`; ERW's choice (session 181) | none |
| Scanner: how long the old record stood | 365 days, 52 weeks, 24 months, 5 years | `record_stood_points`, the same file; ERW's choice: a climbing series must not flag monthly | none |
| Scanner: pair break | R2 at least 0.60; 5.0 standard deviations | `pair_min_r2`, `pair_break_sigmas`, the same file; ERW's choice | none |
| Scanner: settling | a point is read 2 days after the scan's date; more for tables whose publisher revises | `settle_days_default`, the same file; ERW's choice: EIA revises | none |
| Scanner: volume | 12 drafts a day | `max_drafts_per_day`, the same file; ERW's choice | none |
| Hunt: volume | 12 drafts a hunt, 2 regions a pattern | `MAX_DRAFTS`, `MAX_PER_PATTERN`, `warehouse/analysis/findings/hunt.py`; session 251 kept the cap | none |
| Hunt: the three tests | step 5 | `warehouse/analysis/findings/hunt.py`; `docs/methods/automated_analysis_findings.md`, "The weekly hunt" | "deeper findings are hunted automatically and published only after he approves them at `/internal/findings` (he runs the Stata first)" |
| Hunt: what is posted | nothing; the tool prepares the image and the caption | `docs/methods/automated_analysis_findings.md`, "The weekly hunt" | "Nothing posts to LinkedIn: the tool prepares the image and the caption for him" |
| Hunt and daily chart: licensed grids | ISO-NE, MISO, NYISO never drafted; NYISO and SPP held | `HELD` in `warehouse/analysis/findings/daily_chart.py`; `warehouse/metadata/license_status.csv` | NYISO and SPP: the ruling "holds until their licenses are answered" (`docs/methods/automated_analysis_scanner.md`) |
| Daily chart: no approval | the day's strongest unseen flag, drawn by code | `docs/methods/automated_analysis_scanner.md`, "The daily chart in the Digest" | "every weekday Digest carries one chart, a fact and its picture, chosen and drawn by code with no model and no approval" |
| Daily chart: a monthly record stays fresh | 130 days (`fresh_days`) | `docs/methods/automated_analysis_scanner.md` | none |
| Daily chart: a record far past the old one | more than 25 percent past the old record waits a day (`RECORD_JUMP`) | `warehouse/analysis/findings/daily_chart.py` (session 267's brief) | none |
| Chart colors | the brand's ink, cardinal as the highlight, blue, grey, light grey; for more than five series the eight `--chart-series-1` to `-8` | `docs/brand.md` section 2; `site/app/tokens.css` (session 268) | none |
| Chart of the week: ranking window | the last 104 weekly or 36 monthly changes, at least 8; period ended within 100 days | `WINDOW` in `warehouse/analysis/run.py`; ERW's choice (session 119) | none |
| Verdict of a draft | strong, usable or drop, by session 252's rule | `docs/reviews/findings-verified-2026-10-13.md`, "How each was checked" | none |
| Requests | at most 24 run requests a UTC day | `p_per_day`, `warehouse/supabase/migrations/027_analysis_requests.sql` | none |
| Cost cap for scheduled model steps | USD 1.50 a UTC day, all scheduled steps together | `DAILY_MODEL_USD`, `.github/workflows/daily-prices.yml`; `docs/methods/api_cost_ledger.md` (session 206) | none |
| The page's name and address | Research, at `/research`; `/analysis` redirects | `site/next.config.ts`; `docs/methods/automated_analysis_findings.md` | "The owner's task of 12 October 2026: Automated Analysis is Research" |
| Page cache | one hour | `revalidate = 3600`, `site/app/research/page.tsx` | none |

## 4. The cross-checks

Theirs is the figure the finding was verified against: for a draft, the same figure recomputed by session 252 (or session 251 by its rule) from the draft's own CSV and again from the warehouse's tables; for a card, the owner's thesis or the publisher's edition the method note names. No figure was compared with a publisher's own site: none is held (section 9, question 4).

| What is compared | Ours | Theirs | Gap | Reason |
|---|---|---|---|---|
| ERCOT, days whose dearest hour fell in the evening, 2019 and 2025 (draft `scan-hunt-e5fe5b80e074`) | 24.9 and 71.0 percent of days | 24.9 and 71.0, rebuilt from `ercot_all_hub_prices_history` by `peak_hour_grids` | 0 (45 values, 0 differ) | reproduces exactly; verdict strong |
| ERCOT, days whose dearest hour fell at midday, 2019 and 2025 (`scan-hunt-bbb2fe2a3844`) | 32.9 and 3.8 percent | 32.9 and 3.8 | 0 (45 values) | reproduces exactly; strong, one finding with the evening draft |
| ERCOT North, hours below zero, 2019 and 2025 (`scan-hunt-9868ad33205b`) | 0.57 and 2.56 percent of hours | 0.57 and 2.56, rebuilt by `negative_prices_west` | 0 (45 values) | reproduces exactly; strong |
| NYMEX natural gas, managed-money long, week to 2026-09-29 (`scan-weekly-4be2976922ee`) | minus 46,041 contracts | minus 46,041, the table cut after 2026-09-29 | 0 (34 values) | the table gained a week after the scan; strong |
| Wyoming, gas generation, July 2026 (`scan-record-483f592bf064`) | 1,028,747.26 MWh; old record 765,381.40 | the same, from `eia_state_generation_monthly` | 0 (30 values) | unrevised; usable: one first-estimate month |
| CAISO, export non-spinning reserve, day-ahead, 2026-10-06 (`scan-spike-4c52d4239fe9`) | USD 20.65 per MW-hour | 20.65, from `caiso_as_prices` | 0 (29 values) | usable: third dearest day of 767 |
| District of Columbia, industrial retail price, July 2026 (`scan-record-6e1d1cff0ae4`) | a record | reproduces; the customers count is 1 in every month of the last year | 0 | drop: the sector is one customer |
| ERCOT, the median day's steepest evening rise of net load, 2019 and 2025 (`scan-hunt-5ed296972954`) | 1,123 and 6,871 MW per hour | 1,123 and 6,871, rebuilt by the measure | 0 (45 values) | strong (session 251) |
| CAISO, the same measure (`scan-hunt-eb88fc07112e`) | 4,473 and 7,122 MW per hour | 4,473 and 7,122 | 0 (45 values) | strong (session 251) |
| CAISO, curtailed share of wind and solar, 2015 and 2025 (`scan-hunt-64af52af05e4`) | 0.67 and 4.53 percent of output | 0.67 and 4.53 | 0 (47 values) | strong (session 251) |
| ERCOT LZ_WEST, hours below zero, 2015 and 2025 (`scan-hunt-ab16dcb071fb`) | 1.38 and 5.42 percent of hours | 1.38 and 5.42 | 0 (45 values) | usable: a hump, peak 9.95 in 2022 |
| ERCOT spike card, HB_HUBAVG, 2025 median and 99.9th percentile (`batteries_lunch`) | 25.68 and 311.80 USD/MWh | the owner's thesis, as `docs/methods/ercot_peak_premium.md` reproduces it: 25.68 and 311.80 | 0, to the cent | the same prices, the same percentile |
| Queue card, withdrawn share of requested capacity, 2000 to 2020 (`queue_divorce`) | 75.2 percent of 3,509 GW | the thesis: 75 percent of 3,501 GW | 0.2 points; 8 GW | Berkeley Lab's 2026 edition against the thesis's edition |
| Every number on the 11 cards against the card's CSV | every number of 11 cards, by `numbers_from_rows()` | the 11 cards' JSON | 0 | `tests/test_session170.py`, `test_session181.py`, `test_session182.py` |
| The built page against each card's JSON | 279 values read on the built page | the same 279 in the cards' JSON | 0 (279 of 279 at the landing) | `site/scripts/check-analysis.mjs`; `archive/sessions/SESSION_238_REPORT.md` |
| The Newey-West code against a case worked by hand (y = 1, 3, 2, 6; one lag) | the module | square roots of 0.5 and 3.5 | 0 | `tests/test_session181.py` |
| The five-grid cards against the cards they replace, ERCOT and CAISO | the 2 grids' rows of the 2 five-grid CSVs | the 2 single-grid cards' rows | 0 | `tests/test_session182.py` |
| The scanner's first run against its raw rows | 17 flags | 13 real, 1 artifact, 3 uncertain | 1 artifact | `docs/methods/automated_analysis_scanner.md` |

## 5. The edge cases tested

Tested on a local production build of the branch at `b5997e28` (port 3267, 14 October 2026, 09:30 UTC), in the internal view unless the row says otherwise; the addresses read with curl, the cards and the redirects by the page's own checks.

| Case | What was typed (the address) | What the page does |
|---|---|---|
| The page itself | `/research` | 200, the h1 "Research" and the card index of 9 (`data-library-index="9"`); a visitor gets the in-review page (200) |
| The old address | `/analysis` | 308 to `/research`; `/analysis/<week>` and `/analysis/card/<id>` likewise, the query kept (`check-analysis.mjs`, 279 of 279) |
| A week held | `/research/2026-W41` | 200, the h1 "ERW's Chart of the Week" with the week's chart |
| A week not held | `/research/2026-W99` | 404, "No page at this address" (`notFound()` in `site/app/research/[week]/page.tsx`) |
| A card held | `/research/card/batteries_lunch_grids` | 200; its five grids open large and the address keeps the grid (`?lunch_grid=caiso`), `check-findings-grids.mjs`, 163 of 163 |
| A card not held | `/research/card/no_such_card` | 404 |
| A filter of both kinds | `/research?grid=caiso&topic=curtailment` | "Card index, 2 of 9", the address kept (in a browser, at `2961d3e0`) |
| A grid that is not one | `/research?grid=nowhere` | the filter is ignored: "Card index, 9 of 9" (in a browser, at `2961d3e0`); so is a topic that is not one (`?topic=nothing`) |
| The review list without the internal view | `/internal/findings` in a fresh browser | 404 |
| The review list in the internal view | `/internal/findings` | 200, 28 drafts, each with its verdict: 7 strong, 14 usable, 7 drop (`data-draft-verdict`), none "no verdict" |

## 6. What the model cannot see, ranked

The order is the ERW's reading of the sizes below. Where no size is held, the place in the order is a judgment.

1. Cause. No card has an instrument or a randomized comparison, and the sign itself can turn with the specification. In CAISO, by the hour, charging alone goes with plus 0.230 MW of curtailment per MW charged; with net load held fixed, minus 0.129; with the hour and the month too, minus 0.092. By the day, the controlled estimate is plus 1,081 MWh per GWh charged. For ERCOT's minus 10.76 per GW, the share that is batteries and not the 2021 storm, the offer cap, solar or gas: no number held.
2. Many tests, now counted, not corrected. The scanner's first run scanned 6,797 series and tested 105 pairs; it raised 17 flags, of which 1 was an artifact and 3 uncertain. The hunt of 13 October asked 143 claims; 50 passed the three tests. Since session 361 every card carries the line of its round (`statistics.round`, `docs/methods/automated_analysis_findings.md`): the library's eleven cards hold 26 tested claims, 15 of them under p 0.05, and each claim's Benjamini-Hochberg q-value over the 26 (ERCOT's battery-spike multiple 0.00004; the same card's hours at USD 1,000 0.061, against its p of 0.031); the hunt (version 1.3.0) writes the same for its round, each claim's trend p-value and q-value (a dry run of 20 October: 88 claims tested, 25 passing, 70 with a trend p-value), and a draft's footnote states it. Since session 355 the card shows the line in its fold, under the table of estimates. A caveat, not a gate: nothing is dropped by a q-value, and no false-positive rate of the scanner's rules is held. Of the 28 drafts, 7 are drop and 14 usable only with a limit, though every one reproduces to the last digit.
3. The grids not held. PJM ("licensed source needed") and MISO ("paused while terms are reviewed") are never data on a card. CAISO, ISO-NE and SPP prices begin on 2024-09-01: 24 months, 9 degrees of freedom in the monthly regression. In the hunt of 13 October, 44 of 143 claims were regions of a grid that needs a license or is held.
4. Steps read as trends, now flagged. Five of the seven usable drafts of session 251 are one step or a hump ("up from 2015" where the share peaked in 2022). Since session 361 the hunt fits a draft's full years with one step and with a straight line and flags "a step, not a trend" when the step fits better (the Bayesian information criterion), with the break year and the two levels, in the draft's `statistics.shape` and its footnote. Rerun on session 251's seven usable drafts it flags exactly the five (break years 2024, 2020, 2021, 2023, 2021) and not the two trends; a hump is flagged as a step to its higher level, so a page should still show the years. The library's cards are not fitted: their claims are regressions and figures, not end years. Since session 355 a draft that carries the flag shows it on its card, above its errors.
5. Short samples and their errors. The impact study's default case has 28 days: USD 3,016.40 per MWh with a standard error of USD 1,598.93 (Newey-West). Since session 361 the monthly regressions report Newey-West errors beside HC1 (`statistics.newey_west`; 3 lags on 92 months, 2 on 24): ERCOT's battery-spike multiple, minus 10.76 per GW, has HC1 2.32 (p 0.00001) and Newey-West 2.69 (p 0.0001); CAISO's, plus 1.02, HC1 1.02 (p 0.34) and Newey-West 0.65 (p 0.15); the daily curtailment card's charging coefficient, 699 MWh per GWh, HC1 73.5 and Newey-West 115.9 (5 lags on 405 days). HC1 stays the figure the card states; no verdict changes with the second error. Since session 355 the card's fold shows both, a table under the table of estimates (SE and p by HC1 and by Newey-West, the lags). The 24-month grids remain short: 9 degrees of freedom.
6. Hub and zone prices, not nodes. Every price card reads a hub or a zone. NYISO's prices are hourly, so its level is not comparable with the 15-minute grids. The size: no number held.
7. The gas price is one benchmark. Henry Hub stands for every grid. The heat rate moves ERCOT's 2025 share from 35.3 percent at 6.5 to 52.8 percent at 8.0, more than the years do (38.8 percent in 2019, 40.9 in 2025).
8. A table's own artifacts. The District of Columbia's industrial retail price is one customer's bill; the scanner flagged it as a record and it was the daily chart of 8 October (a proof). A one-customer class is not guarded against. A first-estimate month far past its record (Wyoming's gas, 34.4 percent past it) is what the daily chart's new guard holds for a day.
9. Replication in Stata is unproven. No report records a run of any of the 11 do-files in Stata (sessions 178, 182, 233, 252 and 258 had none). Until session 267 six of them read the column names from a comment line.
10. Freshness. All 11 cards were computed on 2026-10-10 and are not recomputed on a clock; a new request needs the data machine awake.

## 7. The ten hardest questions

### 1. How many findings are there, and how many has a person approved?

Eleven cards from eleven analyses; nine stand in the library.
The review list held 28 drafts at 18:19 UTC on 13 October 2026 (8 of the scanner, 20 of the hunt); none approved or dismissed.
The eleven cards did not pass through the review list: sessions computed them and tests hold them.
The only Roundup choice on record is the owner's, "The peak hour moved" for 2026-W41.

### 2. Which of the 28 drafts would you approve tomorrow?

The seven strong: ERCOT's evening and midday peak hour (one finding told twice), ERCOT North's negative hours, the NYMEX managed-money fall, the evening ramp in ERCOT and in CAISO, CAISO's curtailed share.
Each now shows its verdict on `/internal/findings`; the reasons are in `docs/reviews/findings-verified-2026-10-13.md`.

### 3. How many tests did the scanner and the hunt run, and how many did they keep?

Scanner, first run on 10 October 2026: 6,797 series, 105 pairs, 17 flags, 8 drafts; read against their rows, 13 real, 1 artifact, 3 uncertain.
Hunt, 13 October: 143 claims, 50 pass, 12 drafted, 26 wait beyond the cap.
The thresholds are not p-values and nothing is corrected for the number of series. The rate of false flags over time: not held.

### 4. Did batteries shrink Texas price spikes?

The card says they go together and does not say cause.
ERCOT's worst-interval multiple fell from 126.6x in 2019 to 12.1x in 2025 while the fleet went from 87 MW to 18,204 MW.
With load, gas and the month held fixed, each added GW goes with a multiple 10.76 lower (standard error 2.32, 92 months, R2 0.25).
The same years brought the 2021 winter storm, a new offer cap, more solar and a gas price that doubled and fell back; the card names all four.

### 5. Does it hold outside Texas?

Not in the data held.
NYISO: plus 26.62 per GW (standard error 12.58, p = 0.038), on a fleet that never passed 0.27 GW and on hourly prices.
CAISO, with 17,094 MW: 1.02 per GW with a standard error of 1.02 (p = 0.343), which the card calls flat, over 24 months.

### 6. What does a finding that came out flat, or the wrong way, look like?

Flat: in ERCOT gas set the price about as often, 38.8 percent of hours in 2019 and 40.9 in 2025.
Flat with a large number: the Uri impact study, USD 3,016.40 with a standard error of USD 1,598.93 (p = 0.0704).
The wrong way: more curtailment on days with more charging, 1,081 MWh per GWh (standard error 172), and the subtitle says so.

### 7. How do I know a number on a card is the number the code computed?

The card's numbers are recomputed from its own CSV by the finding's own function, in a test, and the CSV's hash is pinned; the built page matched the cards 279 of 279 at the landing.
The 28 drafts were recomputed from their own files and from the tables on 13 October: 28 of 28 equal.
What this does not prove: that the method is right, or that the table is.

### 8. Can a referee reproduce a card in Stata today?

The CSV, the Python and the do-file download with every card; no session report records a run in Stata.
Six do-files read the column names from line 1 (`varnames(1)`) while line 1 of each CSV is a comment; session 267 made them read `varnames(5) rowrange(6)`, as the other five do.
What would settle it: one run of each in Stata (section 8).

### 9. Why did the daily chart of 13 October show Wyoming's gas, and would it today?

It was the flag the rule chose from the scan of 13 October: 1,028,747 MWh in July 2026 against a record of 765,381 MWh, 34.4 percent past it, one first-estimate month.
Under the guard of session 267 it would have waited a day (34.4 percent is past 25) and been checked again on the next run; 7 October's proof was 103 percent past its old record.

### 10. What do licenses do to the findings on 21 October 2026?

From that day 40 of 197 tables read "license needed" unless a permission is recorded; NYISO decides 29, ISO-NE 25, MISO 21.
The hunt and the daily chart already draft nothing for ISO-NE, MISO, NYISO or SPP.
Four of the nine library cards are filed under NYISO and three under ISO-NE, and the card code has no rule that replaces those grids' numbers: it needs a ruling or a recorded permission.

## 8. What Samuel's Stata run must reproduce

Research has no single replication do-file (no `erw_2026_research_replication.do` is held): each card carries its own, in `site/public/findings/`, beside its CSV. The values below are the cards' as the page shows them.

| Name | Value the page shows | The do-file's display line |
|---|---|---|
| ERCOT, battery GW against the worst-interval multiple | minus 10.76 (SE 2.32, 92 months, R2 0.25) | `batteries_lunch_grids.do`: `regress ... if grid == "ERCOT", vce(robust)` |
| NYISO, the same | 26.62 (SE 12.58, p 0.038) | the same line, NYISO |
| CAISO, the same | 1.02 (SE 1.02, p 0.343, 24 months) | the same line, CAISO |
| ISO-NE and SPP, the same | minus 4.02 and 37.50 (24 months each) | the same line, ISO-NE and SPP |
| CAISO, MWh curtailed per GWh charged, charging alone | 699 (SE 73.5, 405 days) | `batteries_curtailment.do`: `regress curtailed_mwh charging_gwh, vce(robust)` |
| The same, solar and month held fixed | 1,081 (SE 172) | `batteries_curtailment.do`: `regress curtailed_mwh charging_gwh solar_gwh i.month_id, vce(robust)` |
| Uri impact study, the difference in differences | 3,016.40 USD/MWh (SE 1,598.93, p 0.0704, 28 days) | `impact_study.do`: `newey diff after, lag(...)` |
| ERCOT hours below gas fuel cost, 2019 and 2025 | 38.8 and 40.9 percent | `gas_sets_price.do`: `list grid year n_hours share_below_hr7` |
| ERCOT days peaking 17:00 to 21:59, 2019 and 2025 | 24.9 and 71.0 percent | `peak_hour_moved.do`: `list grid year median_peak_hour share_evening_pct ...` |
| Requested capacity withdrawn, 2000 to 2020 | 75.2 percent of 3,509 GW | `queue_divorce.do`: `list technology requested_gw withdrawn_pct ...` |

```stata
cd "C:\Users\lossa\Documents\erw\site\public\findings"
do batteries_lunch_grids.do
do batteries_curtailment.do
do impact_study.do
do gas_sets_price.do
do peak_hour_moved.do
do queue_divorce.do
```

A hunt draft's own do-file (one of six files a draft carries) downloads from `/internal/findings/file` in the internal view and runs the same way from its own folder; the ruling of 12 October asks that it be run before the draft is approved.

## 9. Questions only Samuel can answer

1. The 28 drafts, with a verdict each: approve the seven strong and dismiss the seven to drop?
   - (a) as the verdicts say: 7 cards reach `/research`, 7 leave the list for good, 14 wait.
   - (b) approve only after your Stata run of each: nothing reaches the page until then.
   - (c) dismiss the usable ones too: the list empties, and the page shows the seven.
2. A floor on the hunt's strength of one typical yearly move, and a fourth test (half the change remains without the first year)?
   - (a) both: the four spike drafts and ERCOT's night wind would not have been drafted.
   - (b) the floor alone.
   - (c) neither: the verdicts do the work by hand.
3. The daily chart's new guard: a record more than 25 percent past the old one waits a day.
   - (a) keep it at 25 percent: Wyoming's 34.4 percent record would have waited.
   - (b) a different share.
   - (c) no guard: the chart is shown the day it is flagged, as before 14 October.
4. The cross-checks compare each draft with its own recomputation, not with a publisher's figure, which is not held. Should a draft carry a publisher's figure before approval?
   - (a) yes, for every draft: a session reads the publisher's report and records the figure.
   - (b) only for records of EIA's newest month.
   - (c) no: the tables are the evidence.
5. The plain-names file (`warehouse/analysis/`) has entries marked "draft": who rules on the names?
   - (a) you, entry by entry.
   - (b) the methods notes win and the file follows them.
   - (c) leave them as drafts until a page shows one.
6. The cards filed under NYISO (four) and ISO-NE (three) after 21 October 2026.
   - (a) withdraw those grids' numbers from the cards.
   - (b) keep them until the publisher answers.
   - (c) record a permission first.

## Appendix: the five-minute demo

The page is in review. On the machine you will show it from, open the internal view first: `https://erw-flame.vercel.app/internal/open`, paste the token into the field "Token", press **Open the internal view**. Then open `https://erw-flame.vercel.app/research`.

This path was written by session 260 from the page's code and the committed data on `main` on 2026-10-13. It was not clicked through in a browser.

**Say this first:** every card is a question, one chart, the numbers before and after, and the files to recompute it. Code wrote every word; a person approves what the scanner raises.

### Minute 0 to 1: the page and one card

1. The title reads "Research". Under it are five links: **Ask for an analysis**, **Today's chart**, **This week's chart**, **Findings library**, **Chart archive**.
2. Click **Findings library**. The index reads "Card index, 9 of 9". The first card is "BATTERIES ATE THEIR OWN LUNCH? FIVE GRIDS".
3. Read its subtitle: "In Texas the spikes shrank as the fleet grew. No other grid shows it, CAISO with a fleet nearly as large included".
4. Read the callouts: ERCOT worst-interval multiple, 126.6x in 2019 and 12.1x in 2025; battery fleet in 2026-08, 18,204 MW in ERCOT and 269 MW in NYISO.
5. Under the chart, MISO reads "paused while terms are reviewed" and PJM "licensed source needed".

### Minute 1 to 2: one grid, and the table

1. In the card's row of buttons click **NYISO**. The sentence reads 26.62 higher per GW (standard error 12.58, p = 0.038). The caveat says the fleet never passed 0.27 GW.
2. Click **CAISO**. The sentence reads 1.02 per GW with a standard error of 1.02 (p = 0.343): flat.
3. Click **All grids**, then open the fold under the card. The table of estimates has five rows: ERCOT minus 10.76 (92 months), CAISO 1.02 (24), NYISO 26.62 (92), ISO-NE minus 4.02 (24), SPP 37.50 (24).

### Minute 2 to 3: the filters, and a finding that went the other way

1. In the filter by grid click **CAISO** (its count is 5), then in the filter by topic click **Curtailment** (its count is 2). The index reads "Card index, 2 of 9" and the address is `/research?grid=caiso&topic=curtailment`.
2. The first card is "BY HOW MUCH DO BATTERIES CUT CURTAILMENT". Its subtitle: "Days with more charging see more curtailment, even with solar and the month held fixed". Callouts: 8,281 MWh a day at or below the median charging day, 19,401 above it; 1,081 MWh per GWh charged, standard error 172.
3. Say: this is the answer the question did not expect, and the card prints it.
4. On the card, point at the downloads: the data (CSV), the Python file, the Stata do-file.

### Minute 3 to 4: the two charts on top

1. Click **All** in both rows, then the link **This week's chart**. The heading reads "This week's chart, 2026-W41", and under it "Chosen for the Roundup of 2026-W41".
2. The card is "THE PEAK HOUR MOVED": ERCOT median peak hour, hour 15 in 2019 and hour 19 in 2025; days peaking 17:00 to 21:59, 24.9% and 71.0%; solar fleet, 2,592 MW and 30,018 MW.
3. Open the fold **This week's results by the rule, 2026-W41**: the row marked "(picked)" is the rule's own pick, Lower 48 battery discharge, 45,968 MWh a day. The Roundup carried the owner's chosen finding in its place.
4. Scroll up to **Today's chart**: "RECORD HIGH", 13 October 2026. Net generation from natural gas in Wyoming was 1,028,747 MWh in July 2026; the record until then was 765,381 MWh, in July 2024. The source line links the Digest of 13 October 2026. If a newer day's chart stands there, read the screen.

### Minute 4 to 5: asking, and the review list

1. Click **Ask for an analysis**. Under "Step 1: what to analyze" choose the gas finding ("Gas sets the price less often?"). Its inputs are the heat rate, default 7.0, and the first year, default 2019.
2. Under "Step 2: how to show it", one tile is marked "Default for this analysis".
3. Press **Show the card computed 2026-10-10**. The card reads: ERCOT hours below gas fuel cost, 38.8% in 2019 and 40.9% in 2025; ERCOT 2025 at heat rates 6.5 and 8.0, 35.3% and 52.8%.
4. Do not press **Ask the warehouse** in a demo unless you mean it: it queues a real request for the data machine. The request joins a queue, at most 24 a UTC day; the card arrives in 1 to 5 minutes when the machine is awake (on production a request queued at 02:55:07 UTC on 10 October 2026 was done at 02:55:21).
5. Open `https://erw-flame.vercel.app/internal/findings`. The heading is "Scanner drafts (internal)". "Waiting for a ruling" held 28 drafts on the evening of 13 October 2026, each with its verdict of 13 October above its card. Each has **Approve**, **Dismiss** and **Ask for a full card**. A click is a real ruling, kept with its time: do not click one in a demo. Back on `/research`, "Found by the scanner" reads "No draft of the scanner has been approved yet." until one is.

**With a sixth minute:** open `docs/reviews/findings-verified-2026-10-13.md` beside the review list. It gives each of the 28 drafts its verdict with the reason.

### If something goes wrong

- **"This tool is in review" in place of the page:** the internal view is not open in this browser. Open `/internal/open` again.
- **`/internal/findings` answers "not found":** the same cause; the list answers only the internal view.
- **A chart is blank for a moment:** the cards' charts are drawn in the browser. Wait, or reload.
- **A hunt draft's source line names other grids' tables:** the builder is corrected (session 258) and the eight older drafts carry the old line until the data machine runs `hunt.py --fix-source-lines` (`archive/sessions/SESSION_258_REPORT.md`, "To finish"). No row of those tables is in a draft: all eight are ERCOT's, from `ercot_all_hub_prices_history`.
- **The model's note of the chart of the week** cost USD 0.0040 in W39 and USD 0.0062 in W40; W41's was the template's own sentence. Cards, drafts, the hunt and the daily chart call no model.

## Where every number comes from

Every file is as it stands on the branch at `412eeef9`.

| Number | File | Section |
|---|---|---|
| 11 analyses, 11 cards, their kinds and dates; 33 files, 22 pictures | `site/data/findings/`, `site/public/findings/` | the file lists; each card's `kind` and `computed_at` |
| 9 library cards; the filed counts (CAISO 5; curtailment 2) | `archive/sessions/SESSION_238_REPORT.md` | "What was built" 7; "Figures" |
| 279, 229 and 163 checks; 0 keyed values | the same report | "Checks, with exit codes"; "Read these first" |
| 28 drafts at 18:19 UTC; 143 claims, 50 pass, 12 drafted, 26 beyond the cap, 44 of a held grid; 20 patterns | `archive/sessions/SESSION_251_REPORT.md` | "Read these first"; "The 13 families"; "Checks" |
| The 28 verdicts and every draft figure of section 4 (24.9, 71.0, 32.9, 3.8, 0.57, 2.56, minus 46,041, 1,028,747.26, 765,381.40, 20.65, 1,123, 6,871, 4,473, 7,122, 0.67, 4.53, 1.38, 5.42, 9.95, 34.4 percent) | `docs/reviews/findings-verified-2026-10-13.md` | blocks 1 to 28; "Read these first" of each part |
| The verdict beside each draft on the page | `site/lib/findingverdicts.ts` | `VERDICTS`, generated from the document above |
| 6,797 scanned, 105 pairs, 17 flags, 8 drafts; 13 real, 1 artifact, 3 uncertain | `docs/methods/automated_analysis_scanner.md`; `archive/sessions/SESSION_181_REPORT.md` | "The review of the first run"; "The first run" |
| Every scanner threshold; 130 days fresh | `warehouse/config/scanner.yaml`; `docs/methods/automated_analysis_scanner.md` | each key; "The daily chart in the Digest" |
| Hunt caps and the three tests | `warehouse/analysis/findings/hunt.py`; `docs/methods/automated_analysis_findings.md` | `MAX_DRAFTS`, `MAX_PER_PATTERN`, `test_claim()`; "The weekly hunt" |
| ERCOT: 126.6x, 12.1x, 87 MW, 18,204 MW, minus 10.76, 2.32, 92 months, R2 0.25; NYISO 26.62, 12.58, 0.038, 269 MW; CAISO 1.02, 1.02, 0.343, 17,094 MW; ISO-NE minus 4.02; SPP 37.50 | `site/data/findings/batteries_lunch_grids.json` | `callouts`, `effect_table`, `why` |
| 8,281, 19,401, 699, 73.5, 1,081, 172, 405 days | `site/data/findings/batteries_curtailment.json` | `callouts`, `effect_table`, `why` |
| 0.230, minus 0.129, minus 0.092, 2,779 clusters | `site/data/findings/batteries_curtailment_hourly.json` | `effect_table`, `footnote` |
| 3,016.40, 1,598.93, p 0.0704, 28 days | `site/data/findings/impact_study.json` | `callouts`, `effect_table` |
| 38.8%, 40.9%, 35.3%, 52.8% | `site/data/findings/gas_sets_price.json` | `callouts` |
| Hour 15 and 19; 24.9% and 71.0%; 2,592 and 30,018 MW | `site/data/findings/peak_hour_moved.json` | `callouts` |
| 25.68 and 311.80 USD/MWh | `tests/test_session170.py`; `docs/methods/ercot_peak_premium.md` | `test_batteries_lunch`; "Thesis reproduction (HB_HUBAVG)" |
| 75.2 percent of 3,509 GW; 75 percent of 3,501 GW | `site/data/findings/queue_divorce.json`; `docs/methods/automated_analysis_findings.md` | `why`; finding 3, "Data" |
| No Stata on the sessions' machines | `archive/sessions/SESSION_178_REPORT.md`, `SESSION_182_REPORT.md`, `SESSION_233_REPORT.md`, `SESSION_252_REPORT.md` | "Decisions made without you" |
| USD 0.0040 and USD 0.0062 | `docs/analysis/2026-W39/chart_of_the_week.json`, `docs/analysis/2026-W40/chart_of_the_week.json` | `note_by` |
| 45,968 MWh a day, the rule's pick of W41 | `docs/analysis/2026-W41/results.json` | `picked`, its row's `headline` |
| 1,028,747 and 765,381 MWh; the five proofs | `docs/digest/charts/2026-10-13.json` and the five records beside it | `fact`, `proof` |
| 103 percent past its old record, the proof of 7 October (223.0 against 110.0) | `docs/digest/charts/2026-10-07.json` | `flag.value`, `flag.compared.old_record` |
| The guard's 25 percent and its file | `warehouse/analysis/findings/daily_chart.py` | `RECORD_JUMP`, `HELD_FILE` |
| USD 1.50 a day | `docs/methods/api_cost_ledger.md`; `.github/workflows/daily-prices.yml` | "The daily cap for scheduled model steps" |
| 24 requests a day | `warehouse/supabase/migrations/027_analysis_requests.sql` | `p_per_day` |
| 02:55:07 and 02:55:21 UTC | `archive/sessions/SESSION_170_REPORT.md` | the last "Landing state" |
| 197 tables, 40 "license needed"; NYISO 29, ISO-NE 25, MISO 21 | `docs/state/licenses_2026-10-21.md` | "Read these first" |
| The labels and addresses of the appendix | `site/app/research/page.tsx`, `site/components/research/Library.tsx`, `site/components/analysis/RequestFlow.tsx`, `site/components/analysis/ScannerFound.tsx`, `site/app/internal/findings/page.tsx` | the labels as written in the code |
