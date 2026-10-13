# How it works: Research

- **Address:** `/research` (production: `https://erw-flame.vercel.app/research`), with a week's chart at `/research/<week>`, one card at `/research/card/<id>`, and the review list of drafts at `/internal/findings`.
- **Status:** in review, like every page of the site (`site/lib/release.ts`). A visitor sees the in-review page; a demo needs the internal view (section 7).
- **Written from:** `main` at commit `34b468fa`, on 2026-10-13 (session 260). The page landed that morning as `01161064` (session 238, which renamed Automated Analysis to Research; in one push with sessions 237, 239 and 240). `/analysis` and every address under it answer with a permanent redirect to the same place under `/research` (`site/next.config.ts`). This note replaces the one session 249 wrote from the branch before the landing.
- **What moved since the landing:** today's chart. The record of 13 October 2026 is the first that is not a proof: it was drawn from the scan of 13 October and the Digest of that day carries it.

## 1. What it is for, and for whom

- **The question.** What has the warehouse found in its own tables, how was each finding computed, and can a reader recompute it.
- **A finding** is a question put to the warehouse and answered as a card: a title, the answer as a subtitle, one chart that compares, two or three before and after numbers, a paragraph, a method footnote, and three files to download (the data, the Python, a Stata do-file).
- **The page, in order:** a form to ask for an analysis; today's chart; this week's chart; the findings library; an archive of every daily and weekly chart.
- **For whom.** Researchers: each card can be recomputed from its own download. Investors and operators: the cards state sizes with their errors, and say what the design cannot separate. The owner: a review list where he approves or dismisses what the scanner and the weekly hunt raised.
- **What it is not.** No card claims a cause. No card is a forecast. Nothing on a card, a draft or the daily chart is written by a language model.

What it holds on `main` today:

| Thing | Count | Where |
|---|---|---|
| Analyses in the catalogue | 11 | `site/data/findings/catalogue.json` |
| Committed cards | 11 (5 econometric, 6 visual), all computed on 2026-10-10 | `site/data/findings/` |
| Cards in the library | 9; the other 2 are earlier single-grid cards, linked under their five-grid successors | `SUPERSEDED`, `site/lib/findings.ts` line 78 |
| Download files | 33: 11 CSV, 11 Python, 11 Stata do-files; plus 22 pictures | `site/public/findings/` |
| Drafts waiting for a ruling | 16 at 10:49 UTC on 13 October 2026: 8 of the scanner, 8 of the weekly hunt. The scanner runs daily: read the count on the screen | `docs/reviews/findings-verified-2026-10-13.md` |
| Drafts approved or dismissed | 0 at that reading | the same |
| Daily charts held | 6: five proofs (6 to 12 October) and the chart of 13 October | `docs/digest/charts/` |
| Weekly charts held | 3 (2026-W39, W40, W41) | `docs/analysis/` |

The eleven analyses, by family:

- **Batteries and price spikes:** "Batteries ate their own lunch?" for one ERCOT hub, and for five grids (econometric).
- **Gas and the price:** "Gas sets the price less often?" (visual).
- **The queue:** "Till queue do us part" (visual).
- **The peak hour:** "The peak hour moved" for ERCOT and CAISO, and for five grids (visual).
- **Flows in an event:** "Who rescues whom" (visual).
- **Negative prices:** "Negative prices march west" (visual).
- **Batteries and curtailment in CAISO:** day by day, and hour by hour (econometric).
- **Impact of an event on a series:** a before and after against a control (econometric).

## 2. The model, in numbered steps

Here the model is the path from a question to a card on the page.

1. **A question comes in by one of four doors.** A session writes a finding as code, at the owner's request (the eleven analyses came this way). A person asks on the page, picking an analysis and its inputs from lists; no free text is typed. The daily scanner flags a value in a public table. The weekly hunt asks an existing finding's question of every region its code can compute.
2. **A finding is one Python module** in `warehouse/analysis/findings/`. It declares its id, title, kind (`visual` or `econometric`), its inputs with a default and a list of choices, and the tables it reads.
3. **The computation runs on the data machine,** the one machine that holds the full histories. A request is a row in a queue; `worker.py` takes the oldest row, `run_finding.py` runs the module and the card is written back. A table that is not on the machine is said; nothing is filled in. The worker writes no warehouse table.
4. **The scanner's five rules** (`findings_scanner.py`, thresholds in `warehouse/config/scanner.yaml`): a record, a first negative price, a spike, a weekly change outside its five-year range, a break between two series that move together.
5. **The hunt's three tests** (`hunt.py`): the claim holds in at least two later full years; it keeps its direction with the window moved a year at each end; both end years are above the floor of the sample.
6. **The statistics are fixed by the module.** Visual findings are counts and shares by year, with no standard error. The monthly regressions are least squares of a spike measure on battery GW, load, the Henry Hub price and eleven month dummies, with HC1 standard errors. The hourly curtailment regression clusters its errors by Pacific day (2,779 clusters). The impact study is a difference in differences with Newey-West errors.
7. **The words are written by code from the numbers.** The subtitle is chosen by the fit: one sentence when the estimate is negative with p below 0.05, another when positive with p below 0.05, a third when flat.
8. **Every number on the card is checked against the code.** Each module has a function, `numbers_from_rows`, that recomputes every number of the card from the rows of its CSV download alone. A test reads the committed CSV back and compares. The CSV's sha256 is pinned in the card.
9. **A person rules.** A scanner or hunt draft waits at `/internal/findings` with three buttons: Approve, Dismiss, Ask for a full card. Nothing reaches `/research` before Approve. Each ruling is kept with its time.
10. **The card is published with its files:** the data as CSV, the module as run, and a Stata do-file. A file the site does not hold reads "not held" and is never a link. Today all 33 are held.
11. **The page files each card** under grids and topics read from the card's own fields (`site/lib/researchrules.ts`). A grid is a grid name found in the card's tables, inputs or chart; a topic is the kind of table the card read. Neither is a judgment of the finding.
12. **Today's chart** is the newest record of `docs/digest/charts/`, drawn by `daily_chart.py` from the scanner's strongest flag of the day that no Digest has shown. A record marked `proof` is named a proof on the page.
13. **This week's chart** is the chart the newest Roundup carried: a finding's card when one was chosen for it with "Use in Roundup" (`roundup_pick.py`), else the weekly rule's own pick. The week's results by the rule are folded under it.
14. **The page computes nothing.** Every number on `/research` comes from a committed file (a card's JSON, a chart's record, a Roundup). No Supabase table is read when the page is drawn.

**Where a language model is used:** in one place. The weekly chart of the week gets a two-sentence note drafted by a model (`warehouse/analysis/run.py`). The note is kept only if every number in it appears in the template's own sentences as written; after two failed drafts the template's sentences are used.

**Where it is not:** the findings engine, the scanner, the weekly hunt, the daily chart, the filing by grid and topic, and the review list.

## 3. Every assumption, its default and its source

"Inputs" means the lists under "Ask for an analysis". "Fixed" means a line of code or of `warehouse/config/scanner.yaml`, which a person edits.

| Assumption or rule | Default | Where it changes | Source |
|---|---|---|---|
| Hub of the ERCOT spike card | HB_HUBAVG | Inputs (6 hubs) | ERW's choice: the hub of the owner's thesis |
| First year of the price cards | 2019 | Inputs | ERW's choice |
| Spike measures | median, 99.9th percentile, their ratio, hours at or above USD 1,000 and USD 250 | Fixed | ERW's choice; numpy's linear percentile, no cap or exclusion |
| Controls of the monthly regression | load in GW, Henry Hub in USD/MMBtu, eleven month dummies (15 parameters) | Fixed | ERW's choice; `ercot_zone_load_hourly`, `eia930_daily_demand`, `eia_fuel_spot_prices` |
| Standard errors | HC1 (monthly, daily); clustered by Pacific day (hourly); Newey-West (impact study) | Fixed | Statistical convention: Stata's `vce(robust)`, `vce(cluster)`, `newey` |
| Significance that picks a subtitle | p below 0.05 | Fixed | Statistical convention |
| A full year | spike cards: 90 percent of its intervals; peak-hour cards: 300 held days | Fixed | ERW's choice |
| Evening and midday | 17:00 to 21:59 and 10:00 to 15:59, local | Fixed | ERW's choice |
| Heat rate of a gas plant | 7.0 MMBtu per MWh | Inputs (6.5, 7.0, 8.0) | ERW's choice; 6.5 and 8.0 shown beside it |
| Gas price | Henry Hub, the calendar month's mean | Fixed | `eia_fuel_spot_prices`; ISO-NE's share reads low on it, and the card says so |
| Negative price threshold | below 0 USD/MWh | Inputs (0, minus 10, minus 20) | ERW's choice |
| Queue cohort | queue years 2000 to 2020 | Inputs | `lbnl_interconnection_queue`, Berkeley Lab's 2026 edition |
| Impact study | 14 days before and after; ERCOT North Hub real-time, Winter Storm Uri, control NYISO New York City | Inputs (7, 14, 28, 56 days; 23 series; 8 events or a date) | ERW's choice; refused under 5 days held on either side |
| Scanner: a record's margin | 0.5 robust standard deviations past the old record | `record_min_margin_sigmas`, `warehouse/config/scanner.yaml` line 81 | ERW's choice (session 181) |
| Scanner: how long the old record stood | 365 days, 52 weeks, 24 months, 5 years | `record_stood_points`, the same file, line 78 | ERW's choice: a climbing series must not flag monthly |
| Scanner: pair break | R2 at least 0.60; 5.0 standard deviations | `pair_min_r2`, `pair_break_sigmas`, lines 148 and 149 | ERW's choice |
| Scanner: settling | a point is read 2 days after the scan's date; more for tables whose publisher revises | `settle_days_default`, line 34 | ERW's choice: EIA revises |
| Scanner: volume | 12 drafts a day | `max_drafts_per_day`, line 158 | ERW's choice |
| Hunt: volume | 12 drafts a hunt, 2 regions a pattern | `MAX_DRAFTS`, `MAX_PER_PATTERN`, `warehouse/analysis/findings/hunt.py` lines 68 and 69 | ERW's choice |
| Hunt: the three tests | step 5 | Fixed | The owner's ruling of 12 October 2026 |
| Hunt and daily chart: licensed grids | ISO-NE, MISO, NYISO never drafted; NYISO and SPP held by ruling | A person edits `HELD` in `warehouse/analysis/findings/daily_chart.py`, or records a permission | `warehouse/metadata/license_status.csv`; the ruling of 12 October 2026 |
| Chart of the week: ranking window | the last 104 weekly or 36 monthly changes, at least 8; period ended within 100 days | Fixed | ERW's choice (session 119); the page prints the rule under the fold |
| Requests | at most 24 run requests a UTC day | Fixed | `p_per_day`, `warehouse/supabase/migrations/027_analysis_requests.sql` line 40 |
| Cost cap for scheduled model steps | USD 1.50 a UTC day, all scheduled steps together | `DAILY_MODEL_USD`, `.github/workflows/daily-prices.yml` line 213 | The owner's ruling (session 206); `docs/methods/api_cost_ledger.md` |
| Page cache | one hour | Fixed | `revalidate = 3600`, `site/app/research/page.tsx` line 18 |

## 4. The cross-checks

| What is checked | How | Result | Where it is written |
|---|---|---|---|
| Every number on a card against its CSV | `numbers_from_rows` recomputes each one from the download | Passes in the suite: 3,831 tests OK, 237 skipped, on a clean copy at the landing | `tests/test_session170.py`, `tests/test_session181.py`, `tests/test_session182.py`; `archive/sessions/SESSION_238_REPORT.md`, "The landing" |
| The download is the file that was checked | sha256 of the CSV against the card | Passes | `tests/test_session170.py` |
| The page shows the card's numbers | The built page is read and compared with each card's JSON | 279 of 279 at the landing | `site/scripts/check-analysis.mjs`; the same report |
| The request flow and the chart forms | A real browser redraws each card in every form and reads the numbers back | 229 of 229 on the branch's build; not rerun at the landing | `site/scripts/check-analysis-flow.mjs` |
| The five-grid cards in a browser | Small multiples, the one-grid view, phone width | 163 of 163 on the branch's build; not rerun at the landing | `site/scripts/check-findings-grids.mjs` |
| `check-values` on `/research` | Nothing to check: 0 keyed values, since no number is read from a table when the page is drawn | By design | `archive/sessions/SESSION_238_REPORT.md`, "Read these first" |
| The 16 waiting drafts, recomputed | Each hunt draft from its own CSV and again from the tables; each scanner draft from its table at its scan date | 16 of 16 reproduce exactly. Verdicts: 4 strong, 7 usable, 5 drop | `docs/reviews/findings-verified-2026-10-13.md` |
| The ERCOT spike card against the owner's thesis | 2025 median and 99.9th percentile at HB_HUBAVG | Equal to the cent: 25.68 and 311.80 USD/MWh | `tests/test_session170.py` |
| The queue card against the thesis | Withdrawn share of requested capacity | Thesis: 75 percent of 3,501 GW. Card: 75.2 percent of 3,509 GW. The difference is the edition | `docs/methods/automated_analysis_findings.md`, finding 3 |
| The five-grid cards against the cards they replace | ERCOT's and CAISO's numbers, row for row of the CSV | Equal | `tests/test_session182.py` |
| The Newey-West code | A case worked by hand (y = 1, 3, 2, 6; one lag) | Standard errors equal the square roots of 0.5 and 3.5 | `tests/test_session181.py` |
| The scanner's first run against its raw rows | Each of the 17 flags was read in its table | 13 real, 1 artifact, 3 uncertain | `docs/methods/automated_analysis_scanner.md` |
| Grids and topics of each card | Computed again in Python from the committed cards | Equal | `tests/test_session238.py` |
| The full recomputation from the tables | The same test with `ERW_FINDINGS_FULL=1` and the tables present | Skipped in the ordinary suite; no session report records a run of it for the 11 cards | `tests/test_session170.py` |
| The Stata do-files | Their text is checked against the owner's rules | Pass as text. No report records a run of any of them in Stata | sessions 178, 182, 233 and 252 |
| A finding against a published paper | none | no number held | none |

## 5. What it cannot see, ranked by how much it moves the answer

The order is the ERW's reading of the sizes below. Where no size is held, the place in the order is a judgment.

1. **Cause.** No card has an instrument or a randomized comparison. The sign itself can turn with the specification. In CAISO, by the hour, charging alone goes with plus 0.230 MW of curtailment per MW charged; with net load held fixed, minus 0.129; with the hour and the month too, minus 0.092. By the day, the controlled estimate is plus 1,081 MWh per GWh charged. For ERCOT's minus 10.76 per GW, the share that is batteries and not the 2021 storm, the offer cap, solar or gas: no number held.
2. **The grids not held.** PJM ("licensed source needed") and MISO ("paused while terms are reviewed") are never data on a card. CAISO, ISO-NE and SPP prices begin on 2024-09-01: 24 months, which leaves 9 degrees of freedom in the monthly regression. In the first weekly hunt, 16 of 36 claims were never drafted for a license or a hold. All 8 hunt drafts were ERCOT's.
3. **Many tests, no correction.** The scanner's first run scanned 6,797 series and tested 105 pairs; it raised 17 flags, of which a reading of the rows found 1 artifact and 3 uncertain. The hunt asked 36 claims. No adjustment for multiple comparisons is made anywhere, and no false-positive rate is held. Session 252 would drop 5 of the 16 waiting drafts, each of which reproduces to the last digit.
4. **Short samples and their errors.** The impact study's default case has 28 days: a difference of USD 3,016.40 per MWh with a standard error of USD 1,598.93. The monthly regressions use HC1 errors, which do not allow for correlation between neighbouring months; the same regressions with errors that do: no number held.
5. **Hub and zone prices, not nodes.** Every price card reads a hub or a zone. NYISO's prices are hourly, so its level is not comparable with the 15-minute grids. The size of either effect: no number held.
6. **The gas price is one benchmark.** Henry Hub stands for every grid. The heat rate moves ERCOT's 2025 share from 35.3 percent at 6.5 to 52.8 percent at 8.0, more than the years do (38.8 percent in 2019, 40.9 in 2025).
7. **A table's own artifacts.** The District of Columbia's industrial retail price is one customer's bill. The scanner flagged it as a record, and it was the daily chart of 8 October (a proof). A one-customer class is not guarded against.
8. **Replication in Stata is unproven.** No report records a run of any of the 11 do-files. Six of them read `varnames(1)` while their CSV begins with four comment lines.
9. **Freshness.** All 11 cards were computed on 2026-10-10 and are not recomputed on a clock. A new request needs the data machine awake.

## 6. The ten hardest questions

### 1. How many findings are there, and how many has a person approved?

Eleven cards from eleven analyses; nine stand in the library. Sixteen drafts waited at 10:49 UTC on 13 October 2026 (8 of the scanner, 8 of the hunt); none was approved or dismissed. The eleven cards did not pass through the review list: sessions computed them and tests hold them. No file records the owner's sign-off on each. What the files do hold: the page is in review, and the only Roundup choice on record is the owner's, "The peak hour moved" for 2026-W41.

### 2. How many tests did the scanner run, and how many did it keep?

First run, 10 October 2026: 6,797 series scanned and 105 pairs tested. It raised 17 flags and sent 8 drafts to the list. Read against their rows: 13 real, 1 artifact, 3 uncertain. The thresholds are not p-values and nothing is corrected for the number of series. The rate of false flags over time: the tool does not know. It would need the rulings on many weeks of drafts, and none has been ruled on.

### 3. Did batteries shrink Texas price spikes?

The card says they go together and does not say cause. ERCOT's worst-interval multiple fell from 126.6x in 2019 to 12.1x in 2025 while the fleet went from 87 MW to 18,204 MW. With load, gas and the month held fixed, each added GW goes with a multiple 10.76 lower (standard error 2.32, 92 months, R2 0.25). The same years brought the 2021 winter storm, a new offer cap, more solar and a gas price that doubled and fell back. The card names all four.

### 4. Does it hold outside Texas?

Not in the data held. NYISO: plus 26.62 per GW (standard error 12.58, p = 0.038), on a fleet that never passed 0.27 GW and on hourly prices. CAISO, with 17,094 MW: 1.02 per GW with a standard error of 1.02 (p = 0.343), which the card calls flat, over 24 months. The years in which California's fleet was built are not in the warehouse.

### 5. What does a finding that came out flat, or the wrong way, look like?

Flat: "Gas sets the price less often?" answers that in ERCOT the share barely moved, 38.8 percent of hours in 2019 and 40.9 in 2025. Flat with a large number: the Uri impact study, USD 3,016.40 with a standard error of USD 1,598.93 (p = 0.0704), reads "no difference beyond the error". The wrong way: "By how much do batteries cut curtailment" found more curtailment on days with more charging, 1,081 MWh per GWh (standard error 172), and its subtitle says so.

### 6. How do I know a number on a card is the number the code computed?

The card's numbers are recomputed from its own CSV by the finding's own function, in a test, and the CSV's hash is pinned. The built page is then compared with the card: 279 of 279 checks at the landing. What this does not prove: that the method is the right one, or that the table is right. A full recomputation of the 11 cards from the warehouse tables exists as a test and is skipped by default; no report records a run of it. The 16 drafts were recomputed from the tables on 13 October: 16 of 16 equal.

### 7. Can a referee reproduce a card in Stata today?

The CSV, the Python and the do-file download with every card. The Python is the module as run. No session report records a run of a do-file in Stata: sessions 178, 182, 233 and 252 say their machine had none. Six of the eleven read the column names from line 1, and line 1 of each CSV is a comment. What would settle it: one run of each in Stata.

### 8. Where is a language model in this, and what does it cost?

Only in the weekly chart's two-sentence note. It cost USD 0.0040 in W39 and USD 0.0062 in W40; W41's note was the template's own sentence. The step sits under the daily cap of USD 1.50 shared by all scheduled model steps. Cards, drafts, the hunt and the daily chart call no model.

### 9. What do licenses do to the findings on 21 October 2026?

From that day 40 of 197 tables read "license needed" on the site unless a permission is recorded; NYISO decides 29, ISO-NE 25, MISO 21. The hunt and the daily chart already draft nothing for ISO-NE, MISO, NYISO or SPP. For the committed cards the files say less. The page reads no table when it is drawn, so the license table lists it (under its old address) among the pages no license touches. Four of the nine library cards are filed under NYISO and three under ISO-NE, and the card code has no rule that replaces those grids' numbers. Whether those cards may show them after 21 October: the tool does not know. It needs a ruling or a recorded permission. One more, found by session 252: a hunt draft's source line names every table its finding read, so an ERCOT draft names tables that need a license for other grids' rows, though none of those rows is in the draft.

### 10. If I ask for a new analysis now, what happens?

The request joins a queue, at most 24 a UTC day. The worker on the data machine takes it; the card arrives in 1 to 5 minutes when the machine is awake. On production a request queued at 02:55:07 UTC on 10 October 2026 was done at 02:55:21. When the machine is off the row stays queued with the time it was asked. With the default inputs nothing is queued: the card is already computed and the button reads "Show the card computed 2026-10-10".

## 7. A five-minute demo, click by click

The page is in review. On the machine you will show it from, open the internal view first: `https://erw-flame.vercel.app/internal/open`, paste the token into the field "Token", press **Open the internal view**. Then open `https://erw-flame.vercel.app/research`.

This path was written from the page's code and the committed data on `main` on 2026-10-13. It was not clicked through in a browser.

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
4. Do not press **Ask the warehouse** in a demo unless you mean it: it queues a real request for the data machine.
5. Open `https://erw-flame.vercel.app/internal/findings`. The heading is "Scanner drafts (internal)". "Waiting for a ruling" held 16 drafts on the morning of 13 October 2026. Each has **Approve**, **Dismiss** and **Ask for a full card**. A click is a real ruling, kept with its time: do not click one in a demo. Back on `/research`, "Found by the scanner" reads "No draft of the scanner has been approved yet." until one is.

**With a sixth minute:** open `docs/reviews/findings-verified-2026-10-13.md` beside the review list. It gives each of the 16 drafts a verdict (4 strong, 7 usable, 5 drop) with its reason.

### If something goes wrong

- **"This tool is in review" in place of the page:** the internal view is not open in this browser. Open `/internal/open` again.
- **`/internal/findings` answers "not found":** the same cause; the list answers only the internal view.
- **A chart is blank for a moment:** the cards' charts are drawn in the browser. Wait, or reload.

## Where the numbers in this document come from

Every file is as it stands on `main` at `34b468fa`.

| Number | Source file | Where in it |
|---|---|---|
| 11 analyses, 11 cards, their kinds and dates; 33 files, 22 pictures | `site/data/findings/`, `site/public/findings/` | the file lists; each card's `kind` and `computed_at` |
| 9 library cards; the filed counts (CAISO 5; curtailment 2) | `archive/sessions/SESSION_238_REPORT.md` | "What was built" 7; "Figures" |
| 279, 229 and 163 checks; 3,831 tests, 237 skipped; 0 keyed values | the same report | "Checks, with exit codes"; "The landing"; "Read these first" |
| 16 drafts at 10:49 UTC, none ruled; 16 of 16 reproduce; 4 strong, 7 usable, 5 drop; the District's one customer; the source line of a hunt draft | `docs/reviews/findings-verified-2026-10-13.md`; `archive/sessions/SESSION_252_REPORT.md` | "Read these first" |
| 36 claims, 8 drafted, 16 never drafted | `archive/sessions/SESSION_233_REPORT.md` | "Tonight's hunt" |
| The one Roundup choice | `archive/sessions/SESSION_231_REPORT.md` | "Read these first" |
| 6,797 scanned, 105 pairs, 17 flags, 8 drafts; 13 real, 1 artifact, 3 uncertain | `docs/methods/automated_analysis_scanner.md`; `archive/sessions/SESSION_181_REPORT.md` | "The review of the first run"; "The first run" |
| Every scanner threshold | `warehouse/config/scanner.yaml` | each key, at the line given in section 3 |
| Hunt caps and the three tests | `warehouse/analysis/findings/hunt.py`; `docs/methods/automated_analysis_findings.md` | lines 68 and 69; "The weekly hunt" |
| ERCOT: 126.6x, 12.1x, 87 MW, 18,204 MW, minus 10.76, 2.32, 92 months, R2 0.25; NYISO 26.62, 12.58, 0.038, 269 MW; CAISO 1.02, 1.02, 0.343, 17,094 MW; ISO-NE minus 4.02; SPP 37.50 | `site/data/findings/batteries_lunch_grids.json` | `callouts`, `effect_table`, `why` |
| 8,281, 19,401, 1,081, 172 | `site/data/findings/batteries_curtailment.json` | `callouts`, `why` |
| 0.230, minus 0.129, minus 0.092, 2,779 clusters | `site/data/findings/batteries_curtailment_hourly.json` | `effect_table`, `footnote` |
| 3,016.40, 1,598.93, p 0.0704, 28 days | `site/data/findings/impact_study.json` | `callouts`, `footnote` |
| 38.8%, 40.9%, 35.3%, 52.8% | `site/data/findings/gas_sets_price.json` | `callouts` |
| Hour 15 and 19; 24.9% and 71.0%; 2,592 and 30,018 MW | `site/data/findings/peak_hour_moved.json` | `callouts` |
| 25.68 and 311.80 USD/MWh; 3,501 and 3,509 GW | `tests/test_session170.py`; `docs/methods/automated_analysis_findings.md` | `test_batteries_lunch`; finding 3 |
| Six do-files read `varnames(1)`; four comment lines in each CSV; no Stata on the sessions' machines | `archive/sessions/SESSION_178_REPORT.md`, `archive/sessions/SESSION_182_REPORT.md`, `archive/sessions/SESSION_233_REPORT.md`, `archive/sessions/SESSION_252_REPORT.md` | "At the top"; "Decisions made without you" |
| USD 0.0040 and USD 0.0062 | `docs/analysis/2026-W39/chart_of_the_week.json`, `docs/analysis/2026-W40/chart_of_the_week.json` | `note_by` |
| 45,968 MWh a day, the rule's pick of W41 | `docs/analysis/2026-W41/results.json` | `picked`, its row's `headline` |
| 1,028,747 and 765,381 MWh; the five proofs; the scan of 13 October | `docs/digest/charts/2026-10-13.json` and the five records beside it; `docs/digest/2026-10-13.md` | `fact`, `proof`, `candidates_from`; "ERW's Chart of the Day" |
| USD 1.50 a day | `docs/methods/api_cost_ledger.md`; `.github/workflows/daily-prices.yml` | "The daily cap for scheduled model steps"; line 213 |
| 24 requests a day | `warehouse/supabase/migrations/027_analysis_requests.sql` | `p_per_day`, line 40 |
| 02:55:07 and 02:55:21 UTC | `archive/sessions/SESSION_170_REPORT.md` | the last "Landing state" |
| 197 tables, 40 "license needed"; NYISO 29, ISO-NE 25, MISO 21; the pages no license touches | `docs/state/licenses_2026-10-21.md` | "Read these first"; "The pages no license touches" |
| The labels and addresses of section 7 | `site/app/research/page.tsx`, `site/components/research/Library.tsx`, `site/components/analysis/RequestFlow.tsx`, `site/components/analysis/ScannerFound.tsx`, `site/app/internal/findings/page.tsx` | the labels as written in the code |
