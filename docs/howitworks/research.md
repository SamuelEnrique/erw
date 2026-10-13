# How it works: Research

- **Address:** `/research`, with a week's chart at `/research/<week>`, one card at `/research/card/<id>`, and the review list of drafts at `/internal/findings`.
- **Status:** in review, like every page of the site (`site/lib/release.ts`: "no page is live"). A visitor reads the in-review page; the tool shows only in the internal view.
- **Written from:** branch `origin/wip/238-research`, commit `f95bb129` (session 238, which renamed Automated Analysis to Research and rebuilt the page). That commit is not on `main` (head `de22f049`, the merge of session 247). Until it lands, production serves the same cards at `/analysis` in the earlier layout. The cards, their files and the engine are the same on both: the branch changes no file under `site/data/findings/` or `site/public/findings/`.
- **Date:** 2026-10-13.

## 1. What it is for, and for whom

Research is the library of findings that the ERW computes from its own tables. A finding is a question put to the warehouse and answered as a card: a title, the answer as a subtitle, one chart that compares, two or three before and after numbers, a paragraph, a method footnote, and three files to download (the data, the Python, a Stata do-file).

The page holds five things, in this order: a form to ask for an analysis, today's chart, this week's chart, the findings library, and an archive of every daily and weekly chart.

- **For researchers** (the audience `docs/tools.md` names): each card can be recomputed from its own download.
- **For investors and operators:** the cards state sizes with their errors, and say what the design cannot separate.
- **For the owner:** a review list where he approves or dismisses what the scanner and the weekly hunt raised.

What it holds today, counted on the branch:

| Thing | Count | Where |
|---|---|---|
| Analyses in the catalogue | 11 | `site/data/findings/catalogue.json` |
| Committed cards | 11 (5 econometric, 6 visual), all computed on 2026-10-10 | `site/data/findings/*.json` |
| Cards in the library | 9; the other 2 are earlier single-grid cards, linked under their five-grid successors | `site/lib/findings.ts`, `SUPERSEDED` |
| Download files | 33: 11 CSV, 11 Python, 11 Stata do-files; plus 22 pictures | `site/public/findings/` |
| Drafts waiting for a ruling | 16: 8 of the scanner, 8 of the weekly hunt | session 233's report |
| Drafts approved | 0 | sessions 231 and 233 |
| Daily charts held | 6, all proofs: no Digest has carried one | session 238's report |
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

1. **A question comes in by one of four doors.**
   - A session writes a finding as code, at the owner's request. The eleven analyses came this way.
   - A person asks on the page ("Ask for an analysis"): an analysis and its inputs are picked from lists. No free text is typed.
   - The daily scanner flags a value in a public table by one of five rules: a record, a first negative price, a spike, a weekly change outside its five-year range, a break between two series that move together.
   - The weekly hunt asks an existing finding's question of every region its code can compute, every Saturday at 12:00 local time on the data machine.
2. **A finding is specified as one Python module** in `warehouse/analysis/findings/`. It declares its id, title, kind (`visual` or `econometric`), its inputs with a default and a list of choices, and the tables it reads.
3. **The computation runs on the data machine,** the one machine that holds the full histories. A request is a row in a queue; a worker takes the oldest row, runs the module and writes the card back. A table that is not on the machine is said; nothing is filled in. The worker reads tables and writes no warehouse table.
4. **The statistics are fixed by the module.**
   - Visual findings are counts and shares by year (percent of hours, percent of days, percent of MW). They carry no standard error.
   - The monthly regressions are least squares of a spike measure on battery GW, load, the Henry Hub price and eleven month dummies, with HC1 standard errors (Stata's `vce(robust)`) and p from Student's t.
   - The hourly curtailment regression clusters its errors by Pacific day (2,779 clusters), because the hours of one day are not independent.
   - The impact study is a difference in differences with Newey-West errors (Bartlett kernel, lags by a stated formula), as Stata's `newey`.
5. **The words are written by code from the numbers.** The subtitle is chosen by the fit: one sentence when the estimate is negative with p below 0.05, another when positive with p below 0.05, a third when flat. No language model writes any word of a card, a scanner draft, a hunt draft or the daily chart.
6. **Every number on the card is checked against the code.** Each module has a function, `numbers_from_rows`, that recomputes every number of the card from the rows of its CSV download alone. A test reads the committed CSV back and compares each number with the card. The CSV's sha256 is pinned in the card.
7. **A person rules.** A scanner or hunt draft waits at `/internal/findings` with three buttons: Approve, Dismiss, Ask for a full card. Nothing reaches `/research` before Approve. Each ruling is kept with its time. The page itself is in review, and only the owner opens a page to visitors.
8. **The card is published with its files:** the data as CSV, the module as run, and a Stata do-file written to the owner's rules. A file the site does not hold reads "not held" and is never a link. Today all 33 are held.
9. **The page files each card** under grids and topics read from the card's own fields. A grid is a grid name found in the card's tables, inputs or chart; a topic is the kind of table the card read. The site computes no number of a card.
10. **A card can be chosen for the Sunday Roundup** with "Use in Roundup". With none chosen, the Roundup prints the weekly rule's own pick and says so.

**Where a language model is used:** in one place. The weekly chart of the week gets a two-sentence note drafted by a model (`warehouse/analysis/run.py`, step `analysis_note`). The note is kept only if every number in it appears in the template's own sentences as written; after two failed drafts the template's sentences are used. The rule picks the chart; code writes its caption. The model's own caption is stored and not published.

**Where it is not:** the findings engine, the scanner, the weekly hunt, the daily chart, the filing by grid and topic, and the review list.

## 3. Every assumption, its default and its source

"Inputs" means the lists under "Ask for an analysis". "Fixed" means a line of code or of `warehouse/config/scanner.yaml`, which a person edits.

| Assumption or rule | Default | Where it changes | Source |
|---|---|---|---|
| Hub of the ERCOT spike card | HB_HUBAVG | Inputs (6 hubs) | ERW's choice: the hub of the owner's thesis |
| First year of the price cards | 2019 | Inputs (3 choices; the five-grid spike card has 1) | ERW's choice |
| Spike measures | median, 99.9th percentile, their ratio, hours at or above USD 1,000 and USD 250, hours in the sample's top 1 percent | Fixed | ERW's choice; numpy's linear percentile, no cap or exclusion |
| Controls of the monthly regression | load in GW, Henry Hub in USD/MMBtu, eleven month dummies (15 parameters) | Fixed | ERW's choice; tables `ercot_zone_load_hourly`, `eia930_daily_demand`, `eia_fuel_spot_prices` |
| Standard errors, monthly and daily regressions | HC1 | Fixed | Statistical convention (Stata's `vce(robust)`) |
| Standard errors, hourly regression | clustered by Pacific day | Fixed | Statistical convention (Stata's `vce(cluster)`) |
| Standard errors, impact study | Newey-West, L = floor(4 * (n / 100)^(2/9)) lags, factor n / (n - 2) | Fixed | Statistical convention (Stata's `newey`) |
| Significance that picks a subtitle | p below 0.05 | Fixed | Statistical convention |
| "No difference beyond the error" | within 1.96 standard errors of zero | Fixed | Statistical convention |
| A regression printed as a description, not a test | 24 months against 15 parameters, 9 degrees of freedom | Fixed | ERW's choice, said on the card |
| A full year, spike cards | at least 90 percent of its intervals | Fixed | ERW's choice |
| A full year, peak-hour cards | at least 300 held days | Fixed | ERW's choice |
| A day counted, peak-hour cards | at least 20 held hours | Inputs (20 or 24) | ERW's choice |
| Evening and midday | 17:00 to 21:59 and 10:00 to 15:59, local | Fixed | ERW's choice |
| Heat rate of a gas plant | 7.0 MMBtu per MWh | Inputs (6.5, 7.0, 8.0) | ERW's choice; 6.5 and 8.0 shown beside it |
| Gas price | Henry Hub, the calendar month's mean | Fixed | `eia_fuel_spot_prices`; ISO-NE's share reads low on it, and the card says so |
| Negative price threshold | below 0 USD/MWh | Inputs (0, minus 10, minus 20) | ERW's choice |
| Queue cohort | queue years 2000 to 2020 | Inputs (3 choices each end) | `lbnl_interconnection_queue`, Berkeley Lab's 2026 edition |
| Smallest flow counted in a flip | 1,000 MWh a day | Inputs (0, 1,000, 5,000) | ERW's choice |
| Baseline of an event | the same calendar days 364 and 728 days earlier | Fixed | ERW's choice; `event_window_daily` gives the window |
| A day counted, daily curtailment card | 276 of 288 battery intervals and 23 solar hours | Fixed | ERW's choice |
| Charging ceiling | 90 percent of the largest hour of the prior 30 days, or of nameplate | Inputs (90 or 95) | ERW's choice; `storage_buildout_monthly` |
| Impact study window | 14 days before and after | Inputs (7, 14, 28, 56) | ERW's choice |
| Impact study defaults | ERCOT North Hub real-time, Winter Storm Uri, control NYISO New York City real-time | Inputs (23 series, 8 events or a date) | ERW's choice |
| Impact study refusal | fewer than 5 days held by both series on either side | Fixed | ERW's choice |
| Scanner: a record's margin | 0.5 robust standard deviations past the old record | `scanner.yaml` | ERW's choice: at 0.25, 22 of 31 records passed the old one by less than half a robust standard deviation (session 181) |
| Scanner: history before a record counts | 1,095 days, 156 weeks, 60 months, 10 years | `scanner.yaml` | ERW's choice |
| Scanner: how long the old record stood | 365 days, 52 weeks, 24 months, 5 years | `scanner.yaml` | ERW's choice: a climbing series must not flag monthly |
| Scanner: spike | more than 2.0 times the 99th percentile of the prior 3 years | `scanner.yaml` | ERW's choice |
| Scanner: first negative price | none below zero in the prior 365 days, 330 of them held | `scanner.yaml` | ERW's choice |
| Scanner: weekly change | outside the prior 5 years' range by 10 percent of its width; 3 years needed | `scanner.yaml` | ERW's choice |
| Scanner: pair break | fit over 365 days, R2 at least 0.60, 5.0 standard deviations | `scanner.yaml` | ERW's choice |
| Scanner: settling | a point is read 2 days after the scan's date; 7 for tables built from EIA-930 | `scanner.yaml` | ERW's choice: EIA revises |
| Scanner: volume | 12 drafts a day, 3 a table, 5 a rule, 1 a rule and entity | `scanner.yaml` | ERW's choice |
| Hunt: floor of the sample | 30,000 or 8,000 intervals, 8,000 hours, or 330 days, by pattern | Fixed (`hunt.py`) | ERW's choice |
| Hunt: the three tests | holds in at least two later full years; same direction with the window moved a year at each end; both end years above the floor | Fixed | The owner's ruling of 12 October 2026 |
| Hunt: volume | 12 drafts a hunt, 2 regions a pattern | Fixed | ERW's choice |
| Hunt and daily chart: licensed grids | ISO-NE, MISO, NYISO never drafted; NYISO and SPP held by ruling | A person edits `HELD`, or records a permission | `license_status.csv`; the ruling of 12 October 2026 |
| Chart of the week: ranking window | the last 104 weekly or 36 monthly changes, at least 8; period ended within 100 days | Fixed | ERW's choice (session 119) |
| Requests | at most 24 run requests a UTC day | Fixed (migration 027) | ERW's choice: a held-down button cannot queue without limit |
| Cost cap for scheduled model steps | USD 1.50 a UTC day, all scheduled steps together | `DAILY_MODEL_USD` in the workflows | The owner's ruling (session 206); it was 1.00 before |

## 4. The cross-checks

| What is checked | How | Result | Where it is written |
|---|---|---|---|
| Every number on a card against its CSV | `numbers_from_rows` recomputes each one from the download | Passes in the suite: 3,657 tests, OK, 224 skipped | `tests/test_session170.py`, `174`, `181`, `182`; session 238's report |
| Every callout number is a card number | Each number in a callout must be in the card's `numbers` | Passes | `tests/test_session170.py` |
| The download is the file that was checked | sha256 of the CSV against the card | Passes | `tests/test_session170.py`, `182` |
| The page shows the card's numbers | The built page is read and compared with each card's JSON | 279 of 279 | `site/scripts/check-analysis.mjs`; session 238's report |
| The request flow and the chart forms | A real browser redraws each card in every form and reads the numbers back | 229 of 229 | `site/scripts/check-analysis-flow.mjs` |
| The five-grid cards in a browser | Small multiples, the one-grid view, phone width | 163 of 163 | `site/scripts/check-findings-grids.mjs` |
| The full recomputation from the tables | The same test with `ERW_FINDINGS_FULL=1` and the tables present | Skipped in the ordinary suite; no session report records a run of it | `tests/test_session170.py` |
| The ERCOT spike card against the owner's thesis | 2025 median and 99.9th percentile at HB_HUBAVG | Equal to the cent: 25.68 and 311.80 USD/MWh | `tests/test_session170.py`; session 170's report |
| The queue card against the thesis | Withdrawn share of requested capacity | Thesis: 75 percent of 3,501 GW. Card: 75.2 percent of 3,509 GW. The difference is the edition | `docs/methods/automated_analysis_findings.md`, finding 3 |
| The five-grid cards against the cards they replace | ERCOT's and CAISO's numbers, row for row of the CSV | Equal | `tests/test_session182.py` |
| The Newey-West code | A case worked by hand (y = 1, 3, 2, 6; one lag) | Standard errors equal the square roots of 0.5 and 3.5 | `tests/test_session181.py` |
| Hourly curtailment against the table's own day totals | Hours summed by day | At most 0.001 MWh apart over 2,779 days | the hourly card's footnote |
| EIA's two reports of one flow | Each pair is reported by both sides; the card takes the mean | 7,870 pair-days hold both sides; in 1,459 they differ by more than a tenth | the "Who rescues whom" footnote |
| The scanner's first run against its raw rows | Each of the 17 flags was read in its table | 13 real, 1 artifact, 3 uncertain | sessions 181 and 191 |
| The scanner's rules | Built cases: one that must flag and one that must not, for each rule and guard | Pass | `tests/test_session181.py` |
| The weekly note's numbers | Every number must appear in the template's sentences as written | W39 and W40 passed on the first draft; W41's note is not the model's | `docs/analysis/<week>/chart_of_the_week.json`, `note_by` |
| Grids and topics of each card | Computed again in Python from the committed cards | Equal; the file holds 23 tests of the page | `tests/test_session238.py` |
| The Stata do-files | Their text is checked against the owner's rules | Pass as text. No report records a run of any of them in Stata; three sessions say their machine had none | sessions 178, 182 and 233 |
| A finding against a published paper | none | no number held | |

## 5. What it cannot see, ranked by how much it moves the answer

The order is the ERW's reading of the sizes below. Where no size is held, the place in the order is a judgment.

1. **Cause.** No card has an instrument or a randomized comparison. The sign itself can turn with the specification. In CAISO, by the hour, charging alone goes with plus 0.230 MW of curtailment per MW charged; with net load held fixed, minus 0.129; with the hour and the month too, minus 0.092; with curtailed MW added back to net load, minus 0.235. By the day, the controlled estimate is plus 1,081 MWh per GWh charged. For ERCOT's minus 10.76 per GW, the share that is batteries and not the 2021 storm, the offer cap, solar or gas: no number held.
2. **The grids not held.** PJM ("licensed source needed") and MISO ("paused while terms are reviewed") are never data on a card. CAISO, ISO-NE and SPP prices begin on 2024-09-01: 24 months, which leaves 9 degrees of freedom in the monthly regression. In the first weekly hunt, 16 of 36 claims were never drafted for a license or a hold, and 5 had no claim because CAISO has one full year. All 8 drafts were ERCOT's.
3. **Many tests, no correction.** The scanner's first run scanned 6,797 series and tested 105 pairs; it raised 17 flags, of which a reading of the rows found 1 artifact and 3 uncertain. The hunt asked 36 claims. Each econometric card reports several estimates (three measures, three specifications, or five grids). No adjustment for multiple comparisons is made anywhere, and no false-positive rate is held.
4. **Short samples and their errors.** The impact study's default case has 28 days: a difference of USD 3,016.40 per MWh with a standard error of USD 1,598.93. The daily curtailment card has 405 days in 15 months. The monthly regressions use HC1 errors, which do not allow for correlation between neighbouring months; the same regressions with errors that do: no number held.
5. **Hub and zone prices, not nodes.** Every price card reads a hub or a zone. NYISO's prices are hourly: an hour's mean hides a spike that quarter hours would show, so its level is not comparable with the 15-minute grids. The size of either effect: no number held.
6. **The gas price is one benchmark.** Henry Hub stands for every grid. New England's gas is dearer at Algonquin, so ISO-NE's share reads low. By how much: no number held. The heat rate moves ERCOT's 2025 share from 35.3 percent at 6.5 to 52.8 percent at 8.0, more than the years do (38.8 percent in 2019, 40.9 in 2025).
7. **Publication lags and revisions.** The fleet figures end with EIA-860M's inventory of August 2026, so the regressions end in 2026-08 while prices run to 2026-10-08. A monthly record is a record of what the publisher has released, and EIA revises its newest months. A flag depends on the day it is scanned.
8. **What the inventories leave out.** EIA-860M counts plants of 1 MW and more. Rooftop solar, most of New York's and New England's, is not in it: NYISO's counted 2,886 MW is not its solar. The missing part: no number held.
9. **A table's own artifacts.** The District of Columbia's industrial retail price is one customer's bill: 38.4 to 321.5 USD per MWh inside 26 months. The scanner flagged it as a record. A one-customer class is not guarded against.
10. **Replication in Stata is unproven.** No report records a run of any of the 11 do-files. Six of them read `varnames(1)` while their CSV begins with four comment lines; session 178 found that, as written, they would take a comment line for the column names.
11. **Freshness.** All 11 cards were computed on 2026-10-10 and are not recomputed on a clock. A new request needs the data machine awake.

## 6. The ten hardest questions

1. **How many findings are there, and how many has a person approved?**
   Eleven cards from eleven analyses; nine stand in the library. Sixteen drafts wait (8 of the scanner, 8 of the hunt); 0 are approved and 0 dismissed, as sessions 231 and 233 read the list on 13 October 2026. The eleven cards did not pass through the review list: sessions computed them and tests hold them. No file records the owner's sign-off on each. What the files do hold: the page is in review, and the only Roundup choice on record is the owner's, "The peak hour moved" for 2026-W41.

2. **How many tests did the scanner run, and how many did it keep?**
   First run, 10 October 2026: 117 tables, 36,852 series seen, 6,797 scanned, 105 pairs tested. It raised 17 flags (12 records, 3 spikes, 2 weekly changes), suppressed 20 under a known fault, and sent 8 drafts to the list. Read against their rows: 13 real, 1 artifact, 3 uncertain. The thresholds are not p-values and nothing is corrected for the number of series. The rate of false flags over time: the tool does not know. It would need the rulings on many weeks of drafts, and none has been ruled on.

3. **Did batteries shrink Texas price spikes?**
   The card says they go together and does not say cause. ERCOT's worst-interval multiple fell from 126.6x in 2019 to 12.1x in 2025 while the fleet went from 87 MW to 18,204 MW. With load, gas and the month held fixed, each added GW goes with a multiple 10.76 lower (standard error 2.32, p below 0.001, 92 months, R2 0.25). The same years brought the 2021 winter storm, a new offer cap, more solar and a gas price that doubled and fell back. The card names all four.

4. **Does it hold outside Texas?**
   Not in the data held. NYISO: plus 26.62 per GW (standard error 12.58, p = 0.038), on a fleet that never passed 0.27 GW and on hourly prices. CAISO, with 17,094 MW: 1.02 per GW with a standard error of 1.02 (p = 0.343), which the card calls flat, over 24 months. The years in which California's fleet was built are not in the warehouse.

5. **What does a finding that came out flat, or the wrong way, look like?**
   Flat: "Gas sets the price less often?" answers that in ERCOT the share barely moved, 38.8 percent of hours in 2019 and 40.9 in 2025. Flat with a large number: the Uri impact study, USD 3,016.40 with a standard error of USD 1,598.93 (p = 0.0704), reads "no difference beyond the error", because five days at the cap sit beside nine ordinary ones. The wrong way: "By how much do batteries cut curtailment" found more curtailment on days with more charging, 1,081 MWh per GWh (standard error 172), and its subtitle says so.

6. **How do I know a number on a card is the number the code computed?**
   The card's numbers are recomputed from its own CSV by the finding's own function, in a test, and the CSV's hash is pinned. The built page is then compared with the card: 279 of 279 checks. What this does not prove: that the method is the right one, or that the table is right. A full recomputation from the warehouse tables exists as a test and is skipped by default; no report records a run of it.

7. **Can a referee reproduce a card in Stata today?**
   The CSV, the Python and the do-file download with every card. The Python is the module as run. No session report records a run of a do-file in Stata, and sessions 178, 182 and 233 say their machine had none. Six of the eleven (the two earlier single-grid cards, the gas card, the queue card, the negative price card and the "Who rescues whom" card) read the column names from line 1, and line 1 of each CSV is a comment. The other five read names from line 5. What would settle it: one run of each in Stata.

8. **Where is a language model in this, and what does it cost?**
   Only in the weekly chart's two-sentence note. It cost USD 0.0040 in W39 and USD 0.0062 in W40; W41's note was the template's own sentence. The step sits under the daily cap of USD 1.50 shared by all scheduled model steps; at the cap the note is the template's sentences. Cards, drafts, the hunt and the daily chart call no model: session 233 built and ran the hunt at USD 0.

9. **What do licenses do to the findings on 21 October 2026?**
   From that day 40 of 197 tables read "license needed" on the site unless a permission is recorded; NYISO decides 29, ISO-NE 25, MISO 21. The hunt and the daily chart already draft nothing for ISO-NE, MISO, NYISO or SPP. For the committed cards the files say less. The license table lists `/analysis` among "the pages no license touches", because the page reads no table when it is drawn: its numbers come from committed card files. Four of the nine library cards are filed under NYISO and three under ISO-NE, and they read `iso_zone_prices_history`, `iso_hub_prices_history` and `nyiso_rtm_zone_prices`, which are held by grid. The branch's card code has no rule that replaces those grids' numbers. Whether those cards may show them after 21 October: the tool does not know. It needs a ruling or a recorded permission. The method note's own rule is that a card carries the most restrictive license of its inputs.

10. **If I ask for a new analysis now, what happens?**
    The request joins a queue, at most 24 a UTC day. The worker on the data machine takes it; the card arrives in 1 to 5 minutes when the machine is awake. On production a request queued at 02:55:07 UTC on 10 October 2026 was done at 02:55:21. When the machine is off the row stays queued with the time it was asked. A weekly chart template is different: it is shown at once from the last weekly run (2026-10-11) and nothing is queued. A request the design cannot answer is refused in words, for example a control that is the series itself.

## 7. A five-minute demo, click by click

The page is in review. On the machine you show it from, open the internal view first: `https://erw-flame.vercel.app/internal/open`, paste the token into the field "Token", press **Open the internal view**. Then open `https://erw-flame.vercel.app/research`.

This path was written from the code and the data on the branch, not clicked through. It holds once the branch has landed. Before that, the same cards are at `/analysis` without the library's filters and index.

**Minute 0 to 1: the page and one card.**

1. The title reads "Research". Under it are five links: **Ask for an analysis**, **Today's chart**, **This week's chart**, **Findings library**, **Chart archive**.
2. Click **Findings library**. The index reads "Card index, 9 of 9". The first card is "BATTERIES ATE THEIR OWN LUNCH? FIVE GRIDS".
3. Read its subtitle: "In Texas the spikes shrank as the fleet grew. No other grid shows it, CAISO with a fleet nearly as large included".
4. Read the three callouts: ERCOT worst-interval multiple, 126.6x in 2019 and 12.1x in 2025; NYISO, 8.8x and 20.9x; battery fleet in 2026-08, 18,204 MW in ERCOT and 269 MW in NYISO.
5. Under the chart, MISO reads "paused while terms are reviewed" and PJM "licensed source needed".

**Minute 1 to 2: one grid, and the table.**

1. In the card's row of buttons (**All grids**, **ERCOT**, **CAISO**, **NYISO**, **ISO-NE**, **SPP**), click **NYISO**. The callouts read 8.8x and 20.9x; 0 and 9 hours at or above USD 1,000; 8 MW and 269 MW. The sentence reads 26.62 higher per GW (standard error 12.58, p = 0.038). The caveat says the fleet never passed 0.27 GW.
2. Click **CAISO**. The sentence reads 1.02 per GW with a standard error of 1.02 (p = 0.343): flat.
3. Click **All grids**, then open the fold **Method, the table of estimates**. Five rows: ERCOT minus 10.76 (92 months), CAISO 1.02 (24), NYISO 26.62 (92), ISO-NE minus 4.02 (24), SPP 37.50 (24).

**Minute 2 to 3: the filters, and a finding that went the other way.**

1. In the row **By grid** click **CAISO** (its count is 5). The index reads "Card index, 5 of 9".
2. In the row **By topic** click **Curtailment** (its count is 2). The index reads "Card index, 2 of 9" and the address ends `?grid=caiso&topic=curtailment`.
3. The first card is "BY HOW MUCH DO BATTERIES CUT CURTAILMENT". Its subtitle: "Days with more charging see more curtailment, even with solar and the month held fixed". Callouts: 8,281 MWh a day at or below the median charging day, 19,401 above it; 699 and 1,081 MWh per GWh charged; standard error 172, R2 0.65.
4. The second card is the hourly one: net load alone predicts 925 MW in the charging hours of 2025, observed 812; r 0.39; 76 hours at the ceiling with curtailment on in 2021, 171 in 2025.
5. On either card, point at the row "Downloads": **data (CSV)**, **Python**, **Stata do-file**.

**Minute 3 to 4: the two charts on top.**

1. Click **All** in both rows, then the link **This week's chart**. The heading reads "This week's chart, 2026-W41", and under it "Chosen for the Roundup of 2026-W41".
2. The card is "THE PEAK HOUR MOVED": ERCOT median peak hour, hour 15 in 2019 and hour 19 in 2025; days peaking 17:00 to 21:59, 24.9% and 71.0%; solar fleet, 2,592 MW and 30,018 MW.
3. Open the fold **This week's results by the rule, 2026-W41**: the row marked "(picked)" is the rule's own pick, "Batteries discharging, Lower 48", 45,968 MWh a day. The Roundup carried the owner's chosen finding in its place.
4. Scroll up to **Today's chart**: "RECORD HIGH", 13 October 2026. Net generation from natural gas in Wyoming was 1,028,747 MWh in July 2026; the record until then was 765,381 MWh. The source line says the picture is a proof.

**Minute 4 to 5: asking, and the review list.**

1. Click **Ask for an analysis**. Under "Step 1: what to analyze", in the group "Findings", click **How often gas sets the price (Gas sets the price less often?)**. The inputs are "Heat rate (MMBtu per MWh)", default 7.0, and "First year", default 2019.
2. Under "Step 2: how to show it", the tile marked "Default for this analysis" is Paired bars. Press **Next** to see the same values as lines.
3. Press **Show the card computed 2026-10-10**. The card reads: ERCOT hours below gas fuel cost, 38.8% in 2019 and 40.9% in 2025; ISO-NE, 18.6% and 5.5%; ERCOT 2025 at heat rates 6.5 and 8.0, 35.3% and 52.8%.
4. **Ask the warehouse** queues a real request for the data machine. With the default inputs it is not needed: their card is already computed.
5. Open `https://erw-flame.vercel.app/internal/findings`. The heading is "Scanner drafts (internal)". "Waiting for a ruling" held 16 drafts on 13 October 2026. Each has **Approve**, **Dismiss** and **Ask for a full card**. A click is a real ruling, kept with its time. Back on `/research`, "Found by the scanner" reads "No draft of the scanner has been approved yet."

**If the page reads "in review":** the internal view is not open in this browser. Open `/internal/open` again.

## Where the numbers in this document come from

"Branch" is `origin/wip/238-research` at `f95bb129`. "Main" is the working tree of 13 October 2026.

| Number | Source file | Where in it |
|---|---|---|
| 11 analyses, 11 cards, 33 files, 22 pictures | `site/data/findings/`, `site/public/findings/` (branch) | the file lists |
| 9 library cards; 6 grid and 10 topic choices; filed counts (ERCOT 6, CAISO 5, SPP 5, NYISO 4, ISO-NE 3) | `archive/sessions/SESSION_238_REPORT.md` (branch; copy in `runs/session249/code_report_238.md`) | "What was built" 7; "Figures" |
| 279, 229 and 163 checks; 3,657 tests, 224 skipped; 23 new tests | the same report | "Checks, with exit codes" |
| 16 drafts waiting; 36 claims, 8 drafted, 16 never drafted, 5 no claim | `archive/sessions/SESSION_233_REPORT.md` (main) | "Read these first"; "Tonight's hunt" |
| 0 approved; the one Roundup choice | `archive/sessions/SESSION_231_REPORT.md` (main) | "Read these first"; the table of steps |
| 117 tables, 36,852 series, 6,797 scanned, 105 pairs, 17 flags, 20 suppressed, 8 drafts | `archive/sessions/SESSION_181_REPORT.md` (main); `docs/methods/automated_analysis_scanner.md` | "The first run"; "What is scanned" |
| 13 real, 1 artifact, 3 uncertain; 38.4 to 321.5 USD per MWh | `docs/methods/automated_analysis_scanner.md` (main) | "The review of the first run" |
| Every scanner threshold | `warehouse/config/scanner.yaml` (main) | each key |
| Hunt floors, caps and the three tests | `warehouse/analysis/findings/hunt.py` (main); `docs/methods/automated_analysis_findings.md` (branch) | `PATTERNS`, `MAX_DRAFTS`, `MAX_PER_PATTERN`; "The weekly hunt" |
| ERCOT: 126.6x, 12.1x, 87 MW, 18,204 MW, minus 10.76, 2.32, 92 months, R2 0.25 | `site/data/findings/batteries_lunch_grids.json` (branch) | `callouts`, `effect_table` |
| NYISO 26.62, 12.58, p 0.038; CAISO 1.02, 1.02, p 0.343; ISO-NE minus 4.02; SPP 37.50; 17,094 MW | the same file | `effect_table`, `why`, the NYISO panel |
| 8,281, 19,401, 699, 1,081, 172, R2 0.65, 405 days | `site/data/findings/batteries_curtailment.json` (branch) | `callouts`, `why` |
| 0.230, minus 0.129, minus 0.092, minus 0.235, 925, 812, 2,779 clusters, 0.001 MWh | `site/data/findings/batteries_curtailment_hourly.json` (branch) | `effect_table`, `why`, `footnote` |
| 3,016.40, 1,598.93, p 0.0704, 28 days | `site/data/findings/impact_study.json` (branch) | `callouts`, `footnote` |
| 38.8%, 40.9%, 18.6%, 5.5%, 35.3%, 52.8% | `site/data/findings/gas_sets_price.json` (branch) | `callouts` |
| Hour 15 and 19; 24.9% and 71.0%; 2,592 and 30,018 MW; 2,886 MW | `site/data/findings/peak_hour_moved.json`, `peak_hour_grids.json` (branch) | `callouts` |
| 7,870 pair-days, 1,459 apart | `site/data/findings/who_rescues_whom.json` (branch) | `footnote` |
| 25.68 and 311.80 USD/MWh; 3,501 and 3,509 GW | `tests/test_session170.py`; `docs/methods/automated_analysis_findings.md` | `test_batteries_lunch`; finding 3 |
| Six do-files read `varnames(1)`; four comment lines in each CSV | `site/public/findings/*.do`, `*.csv` (branch); `archive/sessions/SESSION_178_REPORT.md` | the import line of each; "At the top" |
| No Stata on the sessions' machines | `archive/sessions/SESSION_178_REPORT.md`, `SESSION_182_REPORT.md`, `SESSION_233_REPORT.md` (main) | "At the top"; line 121; "Read these first" |
| USD 0.0040 and USD 0.0062 | `docs/analysis/2026-W39/chart_of_the_week.json`, `2026-W40/` (branch) | `note_by` |
| 45,968 MWh a day, the rule's pick of W41 | `docs/analysis/2026-W41/results.json` (branch) | `picked`, its row's `headline` |
| 1,028,747 and 765,381 MWh | `docs/digest/charts/2026-10-13.json` (branch) | `fact` |
| USD 1.50 a day | `docs/methods/api_cost_ledger.md` (main) | "The daily cap for scheduled model steps" |
| 24 requests a day | `warehouse/supabase/migrations/027_analysis_requests.sql` (main) | `p_per_day` |
| 02:55:07 and 02:55:21 UTC | `archive/sessions/SESSION_170_REPORT.md` (main) | the last "Landing state" |
| 197 tables, 40 "license needed"; NYISO 29, ISO-NE 25, MISO 21; `/analysis` untouched | `docs/state/licenses_2026-10-21.md` (main) | "Read these first"; "The pages no license touches" |
| The weekly run of 2026-10-11 | `docs/analysis/gallery/index.json` (branch) | `computed_at` |
