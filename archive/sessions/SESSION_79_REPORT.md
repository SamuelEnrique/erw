# Session 79 report: reserves that are called

**The answer is not the one session 74 expected.** Built on ERCOT's own published record of when it released its reserves, a battery that is called earns almost exactly what the price-taker earns: within 0.1 percent in 2018, 2019 and 2020, 0.6 to 1.9 percent less in 2021, and 1 to 10 percent **more** from 2022. Being called is rare, so it is not why the model's early years are high. Nothing live changed; no number on `/cost-of-power/battery` moved.

Energy Research Warehouse (ERW), session 79, third of the chain of 3 October, on the old laptop, 2026-10-03 from about 20:18 to 20:35 UTC, unattended. **Model spend: USD 0.00.** No source pull, no model call, no force push. Two web searches to find a document's address; the document was then downloaded and read locally. Branch `wip/079-called` (it holds 077 and 078). The data lock was never taken.

## To finish

```bash
# 1. After wip/077-housekeeping and wip/078-california have merged, this one. It changes no live number. It does change
#    the text of one live page: /data/methods/battery_stack gains a section, "Reserves that are called (session 79, for
#    review)". The snapshot script does not read methods pages; look at that page after the deploy.
git checkout wip/079-called && git fetch origin && git merge origin/main
git push origin wip/079-called:task/079-called

# 2. Nothing to load or upload. The results are local analysis files (warehouse/output/analysis_internal/ is not in git):
#      battery_called_ercot_daily.csv, battery_called_ercot_yearly.csv, ercot_as_release_events.csv
#    To rebuild them on another machine: the events file must be transcribed again from the document (its address and
#    sha256 are in this report), then
python warehouse/analysis/battery_called.py; echo "exit=$?"
```

## In plain words

### Where the calls come from

- **No table held carries ERCOT's deployments.** `ercot_as_prices` holds day-ahead capacity prices and `ercot_as_quantities` the planned quantities of the last month.
- **So the calls are ERCOT's own lists of events, from one cited document:** ERCOT, "ERCOT Ancillary Services Study", Final White Paper, September 2024, Appendix 2, "Historical Use of AS" (`https://www.ercot.com/files/docs/2024/10/07/ERCOT-Ancillary-Services-Study-Final-White-Paper.pdf`, 57 pages, sha256 `ef2b8fec5613adc5...`). It lists, each with a start, an end and the most MW involved:
  - every event in which **Responsive Reserve** was released, 2018-01-01 to 2024-07-31: 184 events, 45.7 hours in all;
  - every event in which **ECRS** was released, 2023-06-10 to 2024-07-31: 53 events, 59.4 hours;
  - every event in which **off-line Non-Spin** was deployed, 2018-01-01 to 2024-07-31: 93 events, 443.2 hours.
- This is a record of events, better than the "stated share" the prompt allowed for. It is transcribed, 330 rows, in `warehouse/output/analysis_internal/ercot_as_release_events.csv`, with the printed page of every row. It is an analysis input, not a warehouse table: not in coverage, not uploaded.
- **One flaw in the document, handled:** its duration column prints hours, minutes and seconds only. For the Non-Spin event of 14 to 19 February 2021 (Winter Storm Uri) it prints 10:51:53 for a span of four days and almost eleven hours. The model uses each event's start and end, never that column; the other 329 durations agree with their start and end to the minute.

### What is assumed, and it is an assumption each time

1. **During an event the battery's whole award is called.** ERCOT's list gives the most MW released, not the share of what was procured, so the share is not scaled down. This is the most a battery is called.
2. **The event times are Central.** The document does not say; ERCOT's operating reports are.
3. **Regulation is never called.** ERCOT deploys regulation every four seconds, and the document gives no figure for how much. I did not invent one. For Regulation Up and Down, `called` is still the price-taker.
4. **Non-Spin follows the off-line events.** A battery provides on-line Non-Spin, which ERCOT releases to the real-time dispatch continuously behind a USD 75 offer floor (the same document, section 8), so it is called more often than these events. The document gives no start date for that rule, and it is not modelled.
5. **The calls are known in advance,** as the real-time prices are under perfect foresight. So `called` is still an upper bound.

### The model

`warehouse/analysis/battery_called.py`. The page's program for one day, with four changes when a product is called for a share of an hour:

- the state of charge falls by the energy delivered, as a discharge does;
- that energy is paid the hour's real-time price, on top of the award's capacity price;
- the energy stored behind an award covers the longer of the product's required duration and the call, and after the hour only what is still owed;
- the one cycle a day counts the calls, and the battery does not charge in the called part of an hour in which it holds a called award.

With no call it is the page's program: the same constraint matrix row for row, and the same optimum on every toy day. `warehouse/derived/battery_stack.py` is not touched.

### Results: ERCOT, all strategies on the same days

2,404 Central days, 2018-01-01 to 2024-07-31 (the events' window), none left out. USD per kW of rated power. `foresight` and `dayahead` are the page's strategies, solved here on the same days; 2024 is January to July, so it is below the page's full year.

| Year | Foresight 2h | Day-ahead 2h | **Called 2h** | Foresight 4h | Day-ahead 4h | **Called 4h** | Foresight 8h | Day-ahead 8h | **Called 8h** |
|---|---|---|---|---|---|---|---|---|---|
| 2018 | 233.1 | 208.8 | **233.1** | 243.7 | 209.4 | **243.7** | 246.8 | 209.5 | **246.9** |
| 2019 | 374.5 | 323.0 | **374.9** | 402.2 | 323.4 | **402.6** | 408.8 | 323.4 | **409.2** |
| 2020 | 178.4 | 162.7 | **178.4** | 187.5 | 163.1 | **187.5** | 190.2 | 163.1 | **190.2** |
| 2021 | 3,404.0 | 3,384.5 | **3,338.1** | 3,430.6 | 3,390.1 | **3,400.8** | 3,441.0 | 3,390.3 | **3,419.4** |
| 2022 | 352.5 | 301.3 | **356.6** | 393.1 | 314.9 | **401.8** | 413.9 | 323.2 | **426.5** |
| 2023 | 451.5 | 416.9 | **455.6** | 530.1 | 459.6 | **562.3** | 551.6 | 467.5 | **607.3** |
| 2024 (to July) | 85.0 | 76.9 | **86.7** | 102.7 | 91.2 | **106.4** | 109.3 | 96.1 | **113.1** |

**How far `called` falls from the price-taker (perfect foresight), each year:**

| Year | 2h, USD per kW | 2h, percent | 4h, USD per kW | 4h, percent | 8h, USD per kW | 8h, percent | Hours RRS was released | Hours ECRS | Hours off-line Non-Spin |
|---|---|---|---|---|---|---|---|---|---|
| 2018 | -0.01 | -0.01 | +0.03 | +0.01 | +0.04 | +0.02 | 1.47 | none bought | 66.18 |
| 2019 | +0.32 | +0.09 | +0.37 | +0.09 | +0.37 | +0.09 | 1.58 | none bought | 4.80 |
| 2020 | -0.01 | -0.01 | +0.01 | 0.00 | +0.01 | +0.01 | 3.90 | none bought | 5.05 |
| 2021 | -65.85 | -1.93 | -29.73 | -0.87 | -21.56 | -0.63 | 31.18 | none bought | 146.20 |
| 2022 | +4.05 | +1.15 | +8.67 | +2.21 | +12.63 | +3.05 | 3.62 | none bought | 175.22 |
| 2023 | +4.12 | +0.91 | +32.16 | +6.07 | +55.72 | +10.10 | 3.97 | 53.67 | 45.75 |
| 2024 (to July) | +1.78 | +2.09 | +3.72 | +3.62 | +3.72 | +3.41 | 0.00 | 5.70 | 0.00 |

**By stream, 4 hours** (2 and 8 hours are in `battery_called_ercot_yearly.csv`). "Called energy" is the real-time price paid for energy delivered on call.

| Year | Strategy | Energy | Called energy | Regulation Up | Regulation Down | Responsive Reserve | ECRS | Non-Spin | Total |
|---|---|---|---|---|---|---|---|---|---|
| 2018 | foresight | 45.16 | 0.00 | 7.33 | 35.13 | 135.71 | | 20.36 | 243.69 |
| 2018 | day-ahead | 8.62 | 0.00 | 7.47 | 35.99 | 136.93 | | 20.36 | 209.38 |
| 2018 | called | 44.94 | 0.23 | 7.50 | 35.12 | 135.52 | | 20.40 | 243.72 |
| 2019 | foresight | 110.74 | 0.00 | 17.11 | 65.69 | 198.31 | | 10.34 | 402.18 |
| 2019 | day-ahead | 2.44 | 0.00 | 17.62 | 67.06 | 225.43 | | 10.88 | 323.43 |
| 2019 | called | 109.21 | 1.51 | 17.34 | 65.69 | 198.11 | | 10.70 | 402.56 |
| 2020 | foresight | 34.10 | 0.00 | 27.66 | 59.08 | 65.68 | | 0.96 | 187.48 |
| 2020 | day-ahead | 3.93 | 0.00 | 30.18 | 60.36 | 67.63 | | 1.01 | 163.09 |
| 2020 | called | 34.06 | 0.05 | 28.21 | 59.08 | 65.13 | | 0.96 | 187.49 |
| 2021 | foresight | 23.02 | 0.00 | 106.61 | 808.77 | 2,463.54 | | 28.62 | 3,430.56 |
| 2021 | day-ahead | -37.74 | 0.00 | 108.06 | 811.34 | 2,479.12 | | 29.36 | 3,390.13 |
| 2021 | called | -51.39 | 78.73 | 426.57 | 806.50 | 2,110.63 | | 29.79 | 3,400.82 |
| 2022 | foresight | 126.12 | 0.00 | 58.88 | 68.39 | 48.30 | | 91.42 | 393.10 |
| 2022 | day-ahead | 58.87 | 0.00 | 59.07 | 70.00 | 44.81 | | 82.10 | 314.85 |
| 2022 | called | 75.45 | 52.36 | 60.62 | 68.27 | 43.27 | | 101.81 | 401.78 |
| 2023 | foresight | 152.00 | 0.00 | 49.88 | 114.27 | 18.13 | 185.81 | 10.05 | 530.14 |
| 2023 | day-ahead | 100.44 | 0.00 | 44.72 | 116.53 | 21.61 | 166.26 | 10.07 | 459.63 |
| 2023 | called | 76.13 | 83.20 | 51.63 | 112.45 | 22.17 | 203.35 | 13.37 | 562.30 |
| 2024 (to July) | foresight | 35.90 | 0.00 | 6.34 | 20.25 | 7.01 | 30.18 | 2.98 | 102.67 |
| 2024 (to July) | day-ahead | 26.26 | 0.00 | 7.57 | 20.55 | 6.50 | 26.36 | 3.97 | 91.21 |
| 2024 (to July) | called | 28.61 | 6.13 | 7.40 | 20.24 | 6.65 | 34.40 | 2.96 | 106.39 |

### What the numbers say

- **Being called is rare.** Responsive Reserve was released for 1.5 to 4 hours a year outside 2021, mostly in events of three minutes. Only 290 of the 2,404 days hold any call. A reserve held all year and called for two hours loses almost nothing.
- **The early years are high for another reason: the capacity prices themselves.** In 2018 Responsive Reserve alone pays USD 135.71 of the 243.69 per kW at 4 hours, and in 2019 USD 198.31 of 402.18: a battery selling its full power as that reserve every hour at the clearing price. The fleet was then about 100 MW against some 2,300 MW of Responsive Reserve bought (session 74), so one battery's share is not the limit either. Those two years may simply be what an upper bound looks like when reserve prices were high and batteries few.
- **2021 falls, by less than the storm suggests.** On 15 and 16 February 2021 the called battery earns USD 16,541 and 17,326 per MW less than the price-taker at 4 hours, out of 318,711 and 526,361. Responsive Reserve was released for eight and six hours on end and a 4-hour battery cannot hold a megawatt of it through that. But the battery moves to Regulation Up, which this model never calls: its Regulation Up income for 2021 rises from USD 106.61 to 426.57 per kW while Responsive Reserve falls from 2,463.54 to 2,110.63. **That refuge is assumption 3, not a finding about the market.** In the storm regulation was surely used to its limit.
- **From 2022 the called battery earns more.** When ECRS or Non-Spin is called in a tight hour, the battery is paid the real-time price for the energy on top of the capacity price, and knows it in advance. In 2023 at 8 hours that is USD 55.72 per kW more (10.1 percent). On the day-ahead schedule, without knowing the calls, it would not capture all of that.

### Recommendation, not applied

1. **Do not put `called` on the page.** It would not change the years it was meant to fix, and from 2022 it raises the figure, on an assumption (foreknowledge of the calls) no operator has. The page's sentence under the chart stays true as it is: an upper bound, a battery never called.
2. **Change the method note's explanation, not the model:** the early years are high because reserve prices were high and the model sells full power into them every hour, not because reserves are never called. The note's new section says what this session found; the sentence session 74 added, that the years before 2024 need a model of being called, should be read against it.
3. **If the early years still need a second figure, the two candidates left are regulation and February 2021.** For regulation, ERCOT's data product of deployed regulation by interval would settle how much energy a regulation award moves; it is a pull, yours to approve. For 2021, the page could show the year with and without February, as the method note already does for the average.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session79.py` | 14 tests, OK. Session 67's tests on the new program: the optimum equals an exhaustive search on toy days with calls; two days by hand (150, and 95 against 150 never called); no double counting in an hour and no charging while called; every constraint every hour; a longer battery never earns less. And the two asked for: **with no call it reproduces the existing strategy** (the same matrix row for row, the same optimum on 30 toy day-durations, and it passes the page's own check), and **the state of charge never goes negative** (60 toy day-durations with calls). Also: a six-hour call pays a 2-hour battery only for what it can deliver; the hour shares; the transcribed events (counts, window, Uri's hours); the yearly file is the daily file's sum; a day with no event is the price-taker's day exactly |
| On the real days | every one of the 21,636 day-solutions passed its constraint check in the run (the run stops on the first that does not) |
| `tests/test_session67.py`, `tests/test_session74.py` | 25 tests OK: the page's program is untouched |
| `python -m unittest discover -s tests` | 428 tests, 1 failure, 12 skipped, exit 1: the failure is session 77's finding (`eia930_all_interchange` over its ceiling) |
| `npm run build` | exit 0 (the method note is bundled into the site) |

Not run: the validator, coverage, the archive, the uploader, the loader (no warehouse table was written), `check-routes` and `check-values` (no page code changed).

## Errors and decisions

- **Decision: ERCOT's event lists, not a share.** The prompt allowed a stated share from a cited ERCOT document if no deployment table was held. The document I found holds the events themselves, which is closer to the truth than any share. Reading a published report and transcribing its tables is not a source pull as the ERW uses the word, but it is new data on this machine; it stays an internal analysis file.
- **Decision: the web search.** Two searches, to find the document's address and to look for a published figure of regulation deployment (none found). The page-summarising fetch tool was not used; the PDF was downloaded and read with `pdfplumber`.
- **Decision: regulation is not called,** rather than called at a share I would have had to make up.
- **Decision: a separate analysis module.** The page's builder and its table are not touched, so nothing live can change by merging this.
- **Decision: all three strategies are solved again on the events' days,** so the comparison is like for like. The foresight and day-ahead columns equal session 74's table for 2018 to 2023, which came from the live table.
- **Decision: the method note gains a section.** It is the note of a live tool, so its page changes at merge ("To finish", step 1).
- **Error, mine:** my first hand-worked day gave 90 where the program found 95; the program was right (it charges in the cheaper hour). The test states the corrected arithmetic.
- **Error, mine:** the new matrix first listed the same rows as the page's in another order; reordered so the test can compare them as they stand.

## For Samuel

1. **Session 74's explanation of the early years does not hold** on ERCOT's own record of calls. Say whether the page's wording about those years should change.
2. **Approve or decline a pull of ERCOT's deployed-regulation data,** the one assumption here that could still move the numbers.
3. **The on-line Non-Spin rule** (released behind a USD 75 floor) would call Non-Spin far more often than the off-line events. If you know when that rule began, the model can apply it from the held prices with no pull.
