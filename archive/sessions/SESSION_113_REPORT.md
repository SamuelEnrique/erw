# Session 113 report: the battery page's refresh, mended; the deals tracker, version 2

**Both parts are done and on the live site.** The battery page's daily refresh works again: ERCOT's yearly reserve price file now comes as an Excel workbook, the connector reads both forms, and the page shows October with one more day. The deals tracker's second version is at `/deals/v2`, in review. One deploy (run 37251870016, merged as `3ac10a1`), with the snapshot of the live pages before and after.

## Read these first

1. **Two numbers on the home page moved, and this session moved them.** They are not the battery page's, so they are here at the top. "Rows" went from 13,849,370 to 13,849,610: the 240 new hours of ERCOT's reserve prices (the delivery days of 4 and 5 October, five services). "Last refresh" went from 2026-10-04 19:34 UTC to 2026-10-05 01:03 UTC: the time of the battery rebuild. Both follow from the steps you named (coverage and the live set), and the daily run moves both every day. I could not run the refresh without them.
2. **On the battery page only October 2026 moved. Nothing else did, and Texas's history did not.** The rebuilt table differs from the one the page read in 101 values of 10,542, all in the month of October 2026; 0 of the 10,380 rows before it differ, and 0 of Texas's 8,430. A full rebuild from the raw prices on this machine reproduces every earlier month exactly. The last twelve months did not move at all: October holds 3 or 4 of its 31 days, the page does not count a month under 90 percent of its days, so the twelve months still end in September. The table is below.
3. **The deals held are mostly not power contracts, and the page says so.** Of 404 deals, 11 state a size in MW and none states a price per MWh. 22 are power purchases and 21 offtakes; 106 are acquisitions and 234 are other things (equity raises, debt, fuel supply, joint ventures). No deal is a tolling agreement: the extraction has no such type. The storage view holds 3 deals, and two of them are about vehicle batteries (a battery plant, a battery-swap network). The page works; what it can show is thin until the extraction is aimed at power contracts.
4. **Three duplicate deals are shown once on the new page; the table itself is not rewritten.** Rewriting `energy_deals` would take 3 from the home page's row count and change the table `/deals` and the Roundup read, under the freeze. The pairs are in a register a later session can apply. Yours to say (For Samuel, 1).
5. **Whether ERCOT's change is permanent is not known.** I saw one file in the new form, the 2026 file published 4 October at 08:00 Central. The files of 2018 to 2025 and the daily documents are still CSV. The connector now reads either, so it no longer matters to the refresh.

## Part one: the battery page's daily refresh

### What ERCOT now posts

17 requests to ERCOT's public reports site, about 1 MB: 5 document lists and 12 documents (the 2026 file, the eight files of 2018 to 2025, three daily documents). Each is saved under `warehouse/raw/ercot_as_prices/` and was asked for once.

| | Before 4 October | The 2026 file of 4 October |
|---|---|---|
| Inside the zip | one CSV | one Excel workbook, `rpt.00013091.0000000000000000.20261004.080005.DAMASMCPC_2026.xlsx` |
| Layout | the header on line 1 | a logo, a title on row 6, the header on row 8 |
| Columns | Delivery Date, Hour Ending, Repeated Hour Flag, REGDN, REGUP, RRS, NSPIN, ECRS | the same, in the same order |
| A price | text, dollars and cents | a number; none stored with more than two decimals |
| Rows | | 6,623 hours, 1 January to 3 October 2026 |

The 2010 to 2025 files are listed as before; the eight this connector reads (2018 to 2025) each hold a CSV. The daily documents (NP4-188-CD) are CSV as before.

### The connector

`warehouse/connectors/ercot_as_prices.py`, `parse_year`: a zip with one CSV is read as before; a zip with one workbook is read by `year_workbook`, which finds the one header row, turns each cell to text as the CSV has it, and hands the result to the same checks. A price is written as the number the workbook stores (the shortest text that reads back to the same number): nothing is rounded. It refuses, with the reason, a zip with neither form or both, a workbook with more than one sheet, no header row or two, a price that is not a number, a date that is not text, a column it does not know, or no hours.

**Checked three ways before anything was written:**
- every one of the 33,115 prices of 2026 read from the workbook equals the price the table already held for that hour, read from the CSV form on 2 October (0 differ);
- a trial run into a scratch folder: all 336,092 hours held are unchanged, 240 are new;
- `tests/test_session113.py`: the real 2026 workbook and the real 2025 CSV, each saved as ERCOT served it (`tests/fixtures/session113/`, 328 kB). One test reads the workbook's own sheet without the library and compares all 33,115 prices; one writes the real 2025 CSV out as a workbook and requires the same rows from both.

### The run

| Step | Result |
|---|---|
| `ercot_as_prices` | 336,092 rows to 336,332, to 2026-10-06 04:00 UTC (delivery day 5 October); 0 days left out |
| `battery_stack_monthly` | 10,542 rows; ERCOT solved to 3 October (real-time) and 4 October (day-ahead), CAISO the same |
| `battery_stack_stress_daily` | 1,260 rows, no value changed |
| Validator | exit 0, the three tables pass with 0 warnings |
| Coverage | main's, with these three rows replaced (decision 1) |
| Archive | 33,456 rows new or changed (ERCOT's 2026 rows carry the new file's address; their prices are the same) |
| Redivis | draft only, row counts match; nothing released |
| Live set | `battery_stack_monthly` 101 rows written; `ercot_as_prices` matches at 336,332 (decision 3) |

Inputs: the energy prices on this machine are the ones the daily run of 4 October built (real-time to 3 October, day-ahead to 4 October). No price was pulled beyond ERCOT's reserve prices.

### On production: what moved on the battery page

The page shows no refresh date of its own; what moved is the newest month's row in "Every month", and the table's build stamp in coverage (2026-10-03 17:09 UTC to 2026-10-05 01:03 UTC). For the default 100 MW battery, October 2026, US dollars:

| Grid | Duration | Strategy | Days held | Energy | Ancillary | Total | Change in total |
|---|---|---|---|---|---|---|---|
| ERCOT | 2 h | foresight | 2 to 3 | 6,859 to 8,481 | 17,775 to 30,051 | 24,634 to 38,532 | +13,899 |
| ERCOT | 2 h | dayahead | 3 to 4 | 8,402 to 13,119 | 27,242 to 31,260 | 35,644 to 44,379 | +8,735 |
| ERCOT | 4 h | foresight | 2 to 3 | 11,541 to 14,527 | 18,619 to 30,946 | 30,160 to 45,473 | +15,313 |
| ERCOT | 4 h | dayahead | 3 to 4 | 17,389 to 27,321 | 29,168 to 33,165 | 46,557 to 60,486 | +13,929 |
| ERCOT | 8 h | foresight | 2 to 3 | 12,807 to 16,508 | 18,005 to 29,817 | 30,811 to 46,325 | +15,514 |
| ERCOT | 8 h | dayahead | 3 to 4 | 23,452 to 37,392 | 28,219 to 32,707 | 51,671 to 70,099 | +18,429 |
| CAISO | 2 h | foresight | 2 to 3 | 17,225 to 26,338 | 22,673 to 50,856 | 39,899 to 77,194 | +37,296 |
| CAISO | 2 h | dayahead | 3 to 4 | 20,441 to 24,912 | 52,067 to 84,836 | 72,508 to 109,748 | +37,240 |
| CAISO | 4 h | foresight | 2 to 3 | 31,816 to 50,597 | 18,726 to 40,687 | 50,541 to 91,284 | +40,743 |
| CAISO | 4 h | dayahead | 3 to 4 | 44,164 to 57,777 | 46,132 to 74,177 | 90,296 to 131,954 | +41,658 |
| CAISO | 8 h | foresight | 2 to 3 | 42,507 to 70,140 | 16,943 to 32,614 | 59,450 to 102,755 | +43,305 |
| CAISO | 8 h | dayahead | 3 to 4 | 80,651 to 113,852 | 32,367 to 45,666 | 113,017 to 159,518 | +46,501 |

Read on production after the deploy, in each of the 13 snapshots of the page (the default and the twelve above): 3 numbers moved, the October row's energy, ancillary and total, and each equals the rebuilt table's value. The summary sentence, the three headline numbers, every year, every other month, the debt coverage and the stress days: 0 moved. California's October moves more than Texas's because one day is a larger share of what it earned in three.

### Session 49's interchange test

`tests/test_session49.py::Interchange::test_interchange_ceiling` held the table to 150,000 rows. That number is the ceiling of one pull (`eia930_interchange.CEILING`, which counts what EIA reports before it pages). The daily run pulls three days and merges them into the table, which therefore grows by about 8,000 rows a day and passed 150,000 with the daily run of 3 October (151,632 rows; 159,144 after 4 October's), with nothing wrong in it. The test now asserts the connector's ceiling is still 150,000, and holds the table to what its days explain: no UTC day above 8,400 rows (350 pairs for 24 hours; EIA reported 341 on the fullest day held), no more than 8,400 for each day held, each pair's hour once. The reason is written in the test. A fixed larger number would have failed again in days.

## Part two: the deals tracker, version 2

### How the table is built, and what it holds

`warehouse/deals/extract.py` (session 15) sends the scored stories of nine sectors with significance 5 or more to a model, by cluster, and keeps each deal's type, parties, asset, technology, state, country, MW, MWh, dollars, price, term and status. A number is kept only if the words it was read from are in the story's title or summary and parse to the same value. The model is asked to mark a deal it has already extracted.

Read today (`energy_deals`, 407 rows; 404 deals once the three folded pairs are one):

| | Deals |
|---|---|
| Dated | January 2025 to October 2026; none in May to September 2025 (the stories of June to September 2025 are held but not scored) |
| By the page's types | power purchase 22, offtake 21, project finance 21, acquisition 106, tolling 0, other 234 |
| State a size in MW | 11, adding to 20,030 MW |
| State a price in USD per MWh | 0. One row carries "80 %" as a price figure (an equity raise for Lake Charles LNG); the page shows it as extracted and says it is not a price per MWh |
| State a value in US dollars | 218 |
| Tagged AI power | 171 |
| Name a US state | 29; 24 of them in a state one grid mostly serves |
| Technology not stated | 214 |
| A source link | all 407 rows; 371 open through Google News, where the ERW found the story |

### The page

`/deals/v2`, `review` in `site/lib/release.ts`; a visitor is shown the in-review page. In the battery page's layout: a fog beige panel on the left, the answer on the right.

- **Choices:** deal type (power purchase, offtake, project finance, acquisition, tolling, other), technology as the story states it, grid, counterparty (a name or part of one), year; "Storage only" and "AI power" as one-click choices beside "All deals". The choices live in the address and the form is a plain form, so the page works without JavaScript.
- **Answer:** one sentence written from the counts; three headline numbers (deals in the selection, disclosed megawatts with the count of deals behind the sum, how many state a price); deals by month; a table of every deal with date, type and asset, parties, technology, size, price, value in dollars and a link to each story.
- **"not stated"** in every cell a story gives no figure for. A sum is over the deals that state the figure, and the page says how many those are and that the rest are not zero.
- **It says what it is:** "These are deals reported in the news the ERW reads, not a complete record of the market", and, in a box under the sentence, "Of the 404 deals held, 11 state a size in MW and 0 state a price in US dollars per MWh".
- **Grid** is read from the state, for states one grid operator mostly serves; the page says so, and that Texas is counted as ERCOT. A state split between grids is not assigned.
- No model call, no request of its own: it reads `energy_deals` from the live set as `/deals` does. `/deals` is untouched.

### Duplicates and source links

**No deal lacks a source link.** Every row has its first story's address and every story's.

**Duplicates: six pairs found, three clear.** `warehouse/deals/duplicates.csv` holds them with the reason; `warehouse/deals/duplicates.py` checks the register against the table and writes the site's copy.

| Pair | Ruling | Why |
|---|---|---|
| Prysmian buying Atkore, 2 August 2026: `da2dcfbe` (Bloomberg, rumored) and `43f84d02` (Reuters, signed, USD 3.8 billion) | folded | same buyer, seller, asset and day |
| Amazon buying copper, 15 January 2026: `64f2494d` (WSJ, no seller named) and `808b5d20` (Reuters, Rio Tinto) | folded | same buyer, day and commodity |
| Blackstone's data center vehicle, May 2026: `2ac1277b` (aims to raise over USD 1.7 billion) and `82c92aa4` (after a USD 1.75 billion IPO, closed) | folded | one offering at two stages; the closed row is kept with its own figure |
| Lynas and the United States, March 2026: `35541de5` (Pentagon, USD 96 million) and `abf8fe8a` (US, signed) | doubtful, shown as two | probably one deal; no story held says the US buyer is the Pentagon |
| Anthropic's data centre financing, August 2026: `9fa7677c` (USD 200 billion) and `b3c43140` (USD 15 billion) | doubtful, shown as two | may be the whole and a part |
| Talks to invest in OpenAI, January 2026: `c0a548cc` (USD 40 billion, three investors) and `0ca69328` (Amazon, USD 50 billion) | doubtful, shown as two | different figures and parties |

A folded pair is one row on the page: the kept row exactly as extracted, with the story links of both. How I looked: every pair of deals within 45 days sharing a party, a figure or three words, then the titles of the stories behind each candidate. A duplicate whose two rows share no word would not have been found.

### Checks

- `tests/test_session113.py`, 26 tests. Part two runs `site/lib/deals2.ts` in Node on the table's rows and compares 18 selections with the same counts and sums computed from the CSV; the figures are computed, not written down, so tomorrow's new deals do not break it.
- The page as this machine's build served it, ten selections: every headline number, every row, the row order and every month's count against the table, 0 differences (`runs/113_page_check.out`).
- `site/scripts/check-deals-v2.mjs`, a real browser: 19 of 19 at a laptop's width and 19 of 19 at a phone's, on this machine's build and on production after the deploy. It checks the panel is beside the answer on a laptop and above it on a phone, the panel's colour, no sideways scroll, a source link on every row, the one-click choices, the form, a counterparty, and that tolling is empty and says why.
- Every session's tests on this machine: **864 passed, 16 skipped, none failed.** The interchange ceiling, failing since session 102, passes.

## Deploy and snapshots

Run 37251870016 passed (tests, site build, route check) and merged as `3ac10a1`; Vercel's deployment succeeded at 01:40 UTC. Three snapshots of the 25 live pages: `before-113` (00:52 UTC, before anything), `after-113-load` (01:33, after the live set, before the deploy), `after-113` (01:41, after the deploy).

`before-113` against `after-113`: **109 differences.**

| Page | Differences | What | Expected |
|---|---|---|---|
| the 13 battery pages | 65, 5 each | October 2026's energy, ancillary and total, and the row's text with its days held | yes: the refresh this session was for |
| `/` | 6 | two numbers, each counted as a number and two lines of text: "Rows" 13,849,370 to 13,849,610; "Last refresh" 2026-10-04 19:34 UTC to 2026-10-05 01:03 UTC | this session's, a consequence of the refresh (read first, 1) |
| `/` | 32 | the latest real-time prices of five hubs and their interval lines | yes: the 15-minute refresh |
| `/network` | 6 | "refreshed 00:05 UTC" became "01:05 UTC"; demand's newest hour 22:00 became 23:00 | yes: the hourly refresh |
| `/about`, `/storage`, the three seller pages, `/terms`, the four methods pages | 0 | | |

`after-113-load` against `after-113` (the deploy alone): 75 differences, 49 on ten battery pages whose hour-long cache had not yet turned at 01:33 and had by 01:41, and 26 on `/`, all latest prices. The deploy itself changed no live page. Between the two a second deploy happened that is not mine: the Sunday Roundup's commit (`cce5278`, 01:30 UTC).

## Errors and decisions

1. **Coverage was not rebuilt on this machine; three rows were replaced by hand.** `build_coverage.py` here rewrote every row from the local files, and about forty carried an older retrieval stamp than the daily run's (a table whose rows did not change keeps its older header on this machine), with one count off by two. I kept main's `coverage.csv` and `docs/coverage.md` and replaced the rows of the three tables this session rebuilt with the rows the build wrote for them (`runs/113_patch_coverage.py`). The daily run of 5 October rebuilds the file whole.
2. **`price_board_spreads` on this machine holds 2,180 rows; Redivis and coverage say 2,178.** Not this session's and not touched. It is the count that was off in decision 1.
3. **The first load failed on `ercot_as_prices` after writing it.** The database answered a read with a 500 ("JSON could not be generated") and the loader exited 1; `battery_stack_monthly` was already written. The second run, of that table alone, found 336,332 rows there and wrote 0. Both loads report "the older-than-live check could not run" for this table: a statement timeout on 336,000 rows.
4. **`lock.py run` starts the system's Python, not the virtual environment's,** when the command says `python`. It lacks `openpyxl` here, so the first try of the connector under the lock failed at its import and wrote nothing. The commands below name the environment's Python by its full path.
5. **Only this session's three rows were added to `run_status.csv`.** `run_status.py record` would also have written 35 rows of earlier sessions' local runs that were never recorded. They are true and not mine to add in passing.
6. **Grid from state is an attribution, and I made the rule:** the grid operator that serves most of a state, only where one does. 24 of 404 deals get a grid. It is on the page in words.
7. **The storage view is a match on words.** It cannot tell a grid battery from a vehicle battery, and the page says so.
8. **The method note's sentence on the workbook** (`docs/methods/capacity_and_ancillary.md`) is on this branch with the report, not on main: a push to main is a deploy.
9. **No model call. No pull beyond ERCOT's 17 requests. MISO was not requested. No force push. Model spend USD 0.00.**

## To finish

Nothing is owed for either part. For the record, the commands that ran, each with its exit code read:

```bash
PY="<the repository>/.venv/Scripts/python.exe"
python warehouse/lock.py run --task "ERCOT reserve prices" --minutes 20 -- "$PY" warehouse/connectors/ercot_as_prices.py        # exit 0
python warehouse/lock.py run --task "battery stack" --minutes 40 -- "$PY" warehouse/derived/battery_stack.py                   # exit 0
python warehouse/validate/erw_validate.py warehouse/output/ercot_as_prices.csv warehouse/output/battery_stack_monthly.csv warehouse/output/battery_stack_stress_daily.csv   # exit 0
python warehouse/lock.py run --task "archive" -- "$PY" warehouse/archive/archive.py --tables "^(ercot_as_prices|battery_stack_monthly|battery_stack_stress_daily)$" write   # exit 0
python warehouse/lock.py run --task "Redivis draft" -- "$PY" warehouse/redivis/upload.py --tables ercot_as_prices battery_stack_monthly battery_stack_stress_daily        # exit 0
python warehouse/lock.py run --task "live set" -- "$PY" warehouse/supabase/load.py --only '^(ercot_as_prices|battery_stack_monthly|battery_stack_stress_daily)$'         # exit 1, then 0 for ercot_as_prices alone
```

This report and the method note's sentence are on `wip/113-battery-deals`; they reach main with the next deploy.

## For Samuel

1. **The three duplicates in the table.** They are folded on `/deals/v2` only. To take them out of `energy_deals` the extraction needs a step that applies the register when it writes (the table's writer keeps every row it has ever held, so deleting three lines from the file does not last). It changes the home page's row count by 3, `/deals` and the Roundup's deal count. For after the freeze, if you want it.
2. **`/deals` shows no AI deal.** The older page tests the tag against "true" and the table holds "True" and "False" (and "false" in 3 rows), so its "Share tagged AI or datacenter power" reads 0 percent where 171 deals are tagged. I left the page untouched as told. It is one line.
3. **The daily run of 5 October, 14:00 UTC, is the first scheduled run with the mended connector.** Its `ercot_as_prices` and `battery_stack` rows in `run_status.csv` should read ok. It runs on GitHub with `requirements.txt`, which has `openpyxl`.
4. **What would make the deals page worth opening:** an extraction aimed at power contracts (a tolling type, a storage tag, the price per MWh and the term where a story gives them, the grid or the delivery point). That is a change to the prompt and a re-extraction, which costs model calls. The FERC contracts page already has prices as filed; the two could sit side by side.
5. **The Lynas pair** is probably one deal. If you know the US buyer is the Pentagon, change its ruling to `fold` in the register and run `python warehouse/deals/duplicates.py`.

Energy Research Warehouse (ERW), session 113, on the old laptop (`samueloldlaptop`, data role), 2026-10-05 from 00:50 UTC to about 01:55 UTC, unattended.
