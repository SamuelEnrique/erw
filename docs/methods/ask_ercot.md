# Ask ERCOT: how an answer is made

Ask ERCOT is the question box on the ERCOT page and at `/ask/ercot`. You type a question about the Texas grid and the answer appears right below the box. This note says where answers come from, what form they take, what is checked before you see one, and what the tool will not answer.

## Where an answer comes from

| Source | What it holds |
|---|---|
| The ERCOT tables of the warehouse | Prices at the hubs and for reserves, demand, generation by source, the batteries and what they could earn, the evening shoulder, storms and heat waves, the interconnection queue, the cost of power, carbon intensity |
| The ERCOT page's own text | Who runs the grid, how its market sets prices, what makes it different, a short history, a glossary |
| The price board | ERCOT's hub prices with their moves over a day, a week, a month and a year, the spark spread, and prices that belong to no grid: natural gas, oil, Treasury yields |
| Supply and trade | Natural gas in storage, oil stocks and trade, the fuel burned for power in ERCOT, the energy ERCOT's day-ahead market cleared |
| The energy mix | Each source's output by hour of the day, the carbon-free share, the hardest hours of each year |
| What a datacenter pays, curtailment, the capture price and the map of resources (since 8 October 2026) | What a flat load paid at a hub or zone, the share of wind and solar output curtailed, where power was priced near nothing, what curtailed energy was worth, the capture price of solar and wind, and the natural resource layers. See "Four pages more" below |

Every source an answer used is listed under it, with a link.

## The form of an answer

The answer takes the form the question calls for.

| The question | The answer |
|---|---|
| About an idea: "how does ERCOT set prices?", "what is a hub?" | Words alone, from the ERCOT page's text, which it cites. No chart |
| For one figure: "what was the Hub Average price yesterday?" | A sentence or two with the figure, its unit and its date. No chart |
| How something moved: "how has the price moved over the last 30 days?" | A short answer and a chart of the series it fetched, with the rows in a table under it |
| A breakdown: "generation by fuel this week" | A short answer and the rows as a table |

A chart is drawn only when the question asked how something moved. It is never added for its own sake.

## What is checked before you see an answer

- **Every number comes from a query.** A number in an answer must appear in a result the tool fetched for that question, or in the page's text for a year or a date. An answer with a number that cannot be traced is not shown: you see "No answer: its numbers could not all be traced to a query" instead.
- **The tool does no arithmetic of its own.** Averages, differences and shares are computed by the query, not written by the model.
- **Every chart is set against the rows fetched.** The series under an answer is the rows the query returned, key by key and value by value, and the chart's points are those rows. A series that differs is not shown. Under each chart is the number of rows drawn, and the table holds every row.
- **A source is cited only if it was read.**
- **A premise the tables contradict is said first.** If a question takes for granted something the tables do not show, the answer says so before answering.

## What it does not answer

Ask ERCOT speaks for ERCOT only. It says so plainly, and says where to look, for:

- **Another grid.** PJM, CAISO, MISO, NYISO, ISO-NE and SPP each have their own page on this site.
- **Licensed data.** Futures and forward prices, and the price assessments of S&P Global, ICE and CME, are not held. It names the nearest thing that is: a spot or day-ahead price.
- **What a named company earned, bid or owns.** The warehouse holds markets, not company accounts.
- **Forecasts and advice.** The warehouse holds what happened.

When a question cannot be answered it names up to three tables that come nearest, and what each holds.

## A conversation

The last three answers go with the next question, so "and the year before?" is read as what it continues. "New conversation" starts again.

## What the tables on this site hold

The site reads the live set of the warehouse, a part of it. Hub prices are held by day since 2015 (each day's mean, its peak and off-peak means, its lowest and highest price, and its hours below zero and above 200 USD/MWh), and interval by interval for the newest weeks only. A question that needs the single intervals of an older day is answered from the day's figures, and the answer says what they cannot give. The price board and Supply and trade are read as the pages hold them: the newest value of each row, its changes, and its recent points (the last 30 for the board, the last 52 weeks for Supply and trade).

## How long an answer takes

An answer is made in stages. The site records how long each took for every answer, in its own log and in the record of its test questions; none of it is shown on the page.

| Stage | What happens in it |
|---|---|
| Planning | The model reads the question and names what to read: which tables, which rows, which sums |
| Fetching | Those reads are run, all of one turn together |
| Writing | The model writes the answer from what was read, and its numbers are checked |
| Drawing | The series under a chart or table is built and set against the rows fetched |
| Other | The check of the spending ceilings before anything is sent to the model, and the cost record |

The five sum to the whole wait, to the millisecond.

Measured on 7 October 2026 on 78 of the 100 test questions (the spending cap of the session stopped the run before the other 22; they are listed in the session's record and none is counted here). Seconds from the question to what a reader sees, median, with the 90th percentile in brackets. "Before" is the same 78 questions in the record of 6 October.

| The question | Before: the whole answer | Now: the answer's words | Now: the whole answer |
|---|---|---|---|
| About an idea (20 questions) | 3.4 (5.4) | 2.3 (3.1) | 3.3 (4.3) |
| For one figure (19) | 17.1 (24.6) | 6.5 (15.0) | 7.2 (15.1) |
| How something moved, with a chart (20) | 13.4 (24.8) | 6.3 (21.5) | 7.7 (21.5) |
| Not answered, with where to look (19) | 3.0 (5.2) | 2.1 (3.6) | 3.1 (4.2) |

77 of the 78 answers passed the rule of their kind, as 77 of the same 78 did before: one that failed before passes now (the year's highest hourly demand, now read from the table of each year's hardest hours) and one that passed before failed (how the batteries charge and discharge across the hours of a day: it answered with daily figures and no chart).

The aims were 5 seconds to the words for a question about numbers and 2 for a question about an idea. Neither is met at the median: 6.4 seconds for numbers (11 of 39 under 5) and 2.3 for ideas (2 of 20 under 2).

What shortened the wait:

- **One reading turn, then one writing turn.** The model names everything it needs at once and the reads run together. It then writes from the results in a turn in which no tool can be called. Before, a question about numbers took six or seven model calls, most of them the same query asked again; now it takes two or three.
- **No query twice.** A call already made for a question, with the same arguments, is not made again: the model is told its result is above.
- **A series comes with its own summary.** A result grouped by day, month, year or category carries its lowest and highest row, its first and last, the change between them and its mean, computed by the query. An answer about a movement no longer runs one query a figure.
- **The tables' dates are held ready.** Each table's first and last date, and for the energy mix's tables their variable names, are read from the warehouse's catalogue and kept for ten minutes, so no question spends a model call finding them. The list says where to look and nothing more: a recent day is still queried before it is called not held, and every number of an answer still comes from a query.
- **The words first.** The answer's words are shown as soon as they are whole and their numbers, their form and their premise have passed the check: about a second before the sources, the chart or table and the questions to ask next. Nothing is shown in pieces and nothing unchecked is shown. If the whole answer then failed a check the words would be taken back; that did not happen in the 78.
- **A suggested next question that fails its own check is left out.** The answer stands; before, the whole answer was written again.

What was tried and not kept:

- **A smaller model for the reading turn.** On seven questions it took 2.9 seconds at the median for its turn against 2.8 for the model that writes, so it saved nothing; and it called a tool for a question about an idea, and wrote a refusal without the nearest tables, so those two answers were made twice. The model is the one it was.
- **The model's lowest setting of thought.** One of seven answers that passed with the usual setting failed with it, and the reading turn was no shorter. The setting is the one it was.

Where the rest of the time goes, for a question about numbers that is read once and written once (29 of the 39): about 2.7 seconds for the reading turn, a fifth of a second for the reads, and 2.2 seconds of the writing turn until the words are whole. The slowest answers are those the first reading did not settle (10 of the 39, from 8 to 44 seconds) and those that read a whole year of hourly rows a thousand at a time (the reserve prices of a year: 13 seconds for one read).

### The last seconds (session 148, 7 October 2026)

Four changes, written and tested with no question asked. What each did to the 100 test questions is measured after them and written here when it is known; until then two of the four are off.

- **Reserve prices by day and by month.** The slowest answer of the 78 read a year of hourly reserve prices: 8,760 rows, nine requests one after another, 13.3 seconds. Two derived tables now hold those prices added up by ERCOT's local operating day and by month, `ercot_as_prices_daily` and `ercot_as_prices_monthly` ([method](/data/methods/ercot_as_prices_rollup)). A question about more than 35 days of reserve prices is read from them: a year by month is twelve rows. The hourly table is still the one read for an hour, a day or a few weeks. The rule is the query's own, not only the model's guide: while the two tables are on the site, a query of the hourly table that gives no start, or spans more than 35 days, is refused before any row is read, with a message that names the two tables. A day or a month with fewer hours than it has is never filled: it carries its count of hours, and the answer says that it is partial. What the two tables cannot give over a long span (a count of hours above a price, a median or a percentile of hourly prices) is no longer answered here: the answer gives the nearest thing held and says what it cannot give.
- **The pages of one large read are asked for together.** The site's database answers 1,000 rows a request. A read of several thousand rows was that many requests in a row. Now the first page is asked for alone, exactly as before, and the pages after it four at a time. The rows, their order and a failure are the ones the old reader gave: this is tested on a recorded read of three pages, and `site/scripts/compare-paged-reads.mjs` read every table the three open pages read both ways and compared every row (on 7 October 2026: 44 reads, 40,647 rows, none different; the 16 reads of more than one page took 7.1 seconds one after another and 3.0 seconds together). While the site is built the reader is the one it was, one page after another.
- **A plan made by rule (off until measured).** For three shapes of question the read is the same every time, and code writes it, with no reading turn by the model: a price at a named hub in a named market over a named period; the electricity generated from a named source over a named period; the price of a named reserve product over a named period. The rule must account for every word of the question. One word it does not know (an hour of the day, "now", "last week", another grid, a second hub), a hub, a market or a period that is not named, a period that has not begun, or a question that continues a conversation, and the question goes to the model as before. It plans 16 of the 100 test questions (8, 7 and 1 by shape) and none of the 50 about an idea or to be refused. The model still writes the answer, under every check above; when it cannot write it from what the rule read, the model reads for itself.
- **Lower effort on the reading turn (off until measured).** The first model call, the one that decides what to read, can be given a lower effort setting by the server; the writing turn is not changed. A question that is answered without reading (an idea, a refusal) has only that first call, so with the switch on its words are written at the lower setting too.

**What the 100 questions said (8 October 2026).** Before: the tool as session 143 left it, 77 answers from that session's record and 23 asked again on 8 October (the 22 it had not asked and the one that had failed): 100 of 100 pass. After: all 100 asked once with the four changes on. The record is `warehouse/chat/eval_ercot_speed_results_148.csv`.

| Kind | Pass, before then after | Seconds to the words, median, before then after | Under the target, before then after |
|---|---|---|---|
| A question about numbers (50; target 5 seconds) | 50, 48 | 6.2, 4.8 | 15, 27 |
| An idea (25; target 2 seconds) | 25, 25 | 2.3, 2.1 | 2, 7 |
| A refusal (25) | 25, 25 | 2.1, 2.0 | 3, 11 under 2 seconds |

- **The year of reserve prices by month** went from 43.9 seconds and eight model calls to 2.5 seconds and one: twelve rows of the monthly table, and a chart equal to them.
- **The 16 questions the rule planned all pass**, in one model call each: 5.5 seconds to the words at the median before, 3.0 after; 13 of the 16 are under 5 seconds, where 6 were.
- **The other 34 questions about numbers**, read by the model at the lower effort: 6.7 seconds before, 5.3 after. The reading turn itself took 3.0 seconds at the median before and 2.0 after.
- **Two charts were lost in that run, and neither loss is laid to a change.** One (battery capacity in the queue by the year it plans to come online) failed again with the lower effort off, and again with the tool's guide as session 143 left it: the query cannot group a date column by year, and the answer depends on the model finding a way round. The other (wind across the hours of an average day) failed again with the lower effort off and passed with the two reserve tables not offered; it had passed before. Four askings do not say why. Both are questions the tool cannot answer with one query.
- **So the two switches stay off in the code.** The rule was that a change is switched on only if all 100 pass with it, and 98 did. The rule lost none of the 16 questions it touches and changes nothing for the others; the lower effort lost no question that passed again without it. Both can be set on the server (`ASK_RULE_PLAN=on`, `ASK_READER_EFFORT=low`); the figures above are with both set.
- **What is slow now.** The five slowest answers (18 to 28 seconds) are all questions the first reading did not settle, so the model read again and again, up to the limit of eight calls: the average day by hour, yesterday's demand by hour when yesterday is not yet held, a date column by year. And a read of thirty rows of the hub prices by day sometimes takes 5 to 13 seconds (twice in the 100): the query asks for "this entity or this node", which the database answers about five times slower than "this entity" (0.4 seconds against 0.09 when it is warm), and when it is not warm the statement is cancelled for time and tried again.

## Four pages more (session 153, 8 October 2026)

Ask ERCOT reads what stands behind four pages built in the week of 5 October 2026: [What a datacenter pays](/cost-of-power), [Curtailment](/curtailment) with "Where free energy is", [What a generator earns](/cost-of-power/seller) for the capture price, and [Where the resources are](/resources). No table was loaded for it and no page changed.

**Where each figure is read from.** Everything those pages show comes from one of four kinds of source, and each kind is read in its own way.

| Kind of source | How Ask reads it | Which |
|---|---|---|
| A public table already on the site | With the query that reads every other table | `iso_curtailment_monthly`, `caiso_curtailment_daily`, `spp_curtailment_daily`, `ercot_wind_solar_hsl_daily`, `caiso_curtailment_profile`, `eia930_demand_growth`, `interconnection_queue_summary`, `ercot_large_load_status`, `cost_of_power_hourly_profile`, `cost_of_power_carbon` |
| A public table that is not on the site | It would have to be loaded first | None was needed |
| A file the page reads that no table holds | With a tool, `page_file`, that reads the same file the page reads, through the page's own functions | The hourly prices behind what a flat load paid, and the hours a grid was tight; the capture prices; the shares of curtailment; Texas's days; where free energy is; what curtailed energy was worth; the resource layers |
| A table held internally | Never. The answer says "held, not shown" and why | Listed below |

A figure from `page_file` is the page's figure: there is no second copy that could drift from the page. The source under such an answer is the file's name (for example `site/data/seller/capture.json`) and links to the page.

**Other grids, for these pages only.** The four pages are tools for every grid, so for what they show Ask answers for CAISO, NYISO, ISO-NE and SPP as well as ERCOT. Everything else about another grid is still not answered here: its price on a day, its demand, its fuel mix, its batteries. MISO reads "paused while terms are reviewed" and PJM "licensed source needed": no figure of either is given.

**What each is, and what it is not.** Each sentence is from the page's own Method note.

- **What a flat load paid** ([method](/data/methods/datacenter_cost)). The mean of the hourly prices at a hub or zone: the last twelve complete months, a bad month, power per GPU-hour at the page's two stated defaults, and each year or month. It is not a bill: wholesale energy only, with no delivery, transmission, demand or retail charge. A hub or zone is an average over many points, not a site. A flexible load is computed on the page from the reader's own inputs and is not read by Ask. The hours a grid was tight are the hours within 5 percent of that year's own highest hour of demand: a count near the year's peak, not a measure of scarcity or of an emergency.
- **The capture price** ([method](/data/methods/cost_of_power)). The price of each hour weighed by the grid's solar or wind generation of that hour, against the flat average of the same hours. It is the fleet's shape, not a site's: one plant's resource, curtailment, congestion and node price are not in it, and it is not what a plant with a contract earns. The page's hybrid figure "Combined" is two revenues added, each priced as if it stood alone; Ask does not read it and never adds the two.
- **The share of output curtailed** ([method](/data/methods/curtailment)). Curtailed energy over curtailed plus output. The grids' figures do not mean the same thing and are never added up. CAISO's and SPP's are the operators' own. ERCOT publishes no curtailment figure: Texas's is the ERW's estimate, output below the limit the plants reported, held for whole days from 28 September 2026 and never for a month. CAISO's shares of 2026 rest on its Today's Outlook output, which shows more output than its Daily Renewable Report, so a share on the report's output would be higher. The data does not say where a curtailment happened.
- **Where free energy is.** For each hub and zone, the hours priced below zero and the hours priced under USD 5 per MWh, over the last month and the last twelve. It is a count of hours at a wholesale price, not energy that can be had for nothing, and a hub or zone is not a site.
- **What curtailed energy was worth.** Each hour's curtailed energy times the hub's price of that hour. It is what the energy would have fetched at the hub, not a loss anyone booked, and it is negative when the energy was curtailed in hours priced below zero.
- **A resource layer** ([method](/data/methods/resources)). The publisher's estimate of a resource over an area: its unit, publisher, vintage and range; the value of a cell at a longitude and latitude; a basin, play, county or lease area by name. It is not a siting study and says nothing of land use, access to transmission, permits or cost, so a question that asks where to build is not answered. The wind capacity factor layer is not a gross capacity factor and is not called one. No place name is looked up: a place is a longitude and a latitude.

**Held, not shown.** These tables are held internally under their publishers' terms. No tool reads them: a query that names one is refused before anything is read, and the answer says "held, not shown" with the reason and the nearest thing that is shown.

| Table | What it is |
|---|---|
| `isone_zone_prices_history` | ISO-NE's load zone prices, 2019 to August 2026 |
| `isone_ddg_undelivered_monthly` | ISO-NE's monthly undelivered energy of its dispatchable wind and solar plants |
| `isone_zone_load_hourly` | ISO-NE's hourly demand by zone |
| `nyiso_load_queue` | New York's load in line |
| `texas_transmission_matrix` | The Texas Commission's transmission charge matrices |
| `texas_delivery_charges` | The four large Texas wires utilities' delivery and transmission charges |

The two Texas tables are a case of their own. The page prints their figures as public regulatory filings, each with its document and page, and says that the 2026 matrices are filed, not approved. Ask reads neither table and gives no figure of them: it says where on the page they stand.

**The 20 test questions** are in `warehouse/chat/eval_ercot_pages.json`: at least four a page, sentences and charts, and two that must be refused (ISO-NE's monthly curtailment, held and not shown; a MISO figure, paused). Every expected number is computed by `warehouse/chat/eval/ercot_pages_expected.py` from the file or table the question is answered from, and the site's tool is set against those numbers with no model (`site/scripts/test-ask-tables.mjs`). The judge is still a rule in code. For these questions it also checks that an expected number is in the answer, that the source is the one the question names, and that a chart holds the expected row.

**What the 120 questions said (8 October 2026).** All 120 were asked once, on the tool as the code stands (the two switches of session 148 off), the 20 new ones first. The record is `warehouse/chat/eval_ercot_pages_results_153.csv`.

| Questions | Pass | Seconds to the words, median | USD a question |
|---|---|---|---|
| The 20 of the four pages | 19 of 20 | 5.0 | 0.0281 |
| What a datacenter pays (4) | 4 of 4 | 4.7 | 0.0480 |
| The capture price (5, one a refusal) | 5 of 5 | 5.1 | 0.0174 |
| Curtailment and free energy (7, one a refusal) | 6 of 7 | 5.0 | 0.0262 |
| The resource layers (4) | 4 of 4 | 5.0 | 0.0247 |
| The 100 of before | 98 of 100 | 4.1 | 0.0202 |

- **The one new question that failed** asked what percent of the reported limit Texas wind and solar output was below, over the days held. The page's file holds that figure (4.57 percent over nine whole days from 28 September 2026). The tool read the daily table instead, which starts nine days earlier and holds no share, and answered with two ratios, one for wind and one for solar, over another span of days. Asked a second time it read the page's file and passed. Two sources hold the same thing over different days, and the guide does not yet say which to read for a share.
- **The two refusals were given in the expected words**: ISO-NE's monthly curtailment "held, not shown", with the reason; a MISO capture price "paused while terms are reviewed". Neither gave a figure.
- **The ten older refusals about another grid all held**, though the tool now answers for other grids on these four pages.
- **Two of the 100 failed, both charts the tool cannot fetch with one query**, and neither read a new table or the new tool: the batteries across the hours of a day, and the queue by the year a plant plans to come online. Both passed in session 148's record of the tool with the switches off; the second failed in that session's three other askings. One asking each does not say whether the longer guide played a part.
- **The first question of the run cost USD 0.14**: it wrote the longer guide to the model's cache. Without it the new questions cost USD 0.0223 each. The 100 cost USD 0.0202 each against 0.0186 before: the guide is about 4,700 tokens longer, and every model call reads it.
- One of the 100 was answered from a page's file: the year's highest hourly demand, 91,134 MW from the operator's own hourly demand as the datacenter page holds it. Session 143's answer to the same question was 91,075 MW, from EIA's hourly demand: two sources, two figures, each said with its source.

`ASK_PAGES=off` on the server leaves the tool as it was before this session.

## Limits

The tool has a spending ceiling for the day and for the month and a number of questions per visitor per day. When one is reached it answers with a plain message and your question is not sent to the model. They are described in [the limits note](/data/methods/ask_limits).

## What it cannot tell you

- **It answers from what is held.** A fact that is true and not in the tables or the page's text gets "not in the warehouse", not an answer from memory.
- **The page's text is short.** A question about an idea the text does not cover is not answered.
- **It can misread a question.** The sources under the answer show what was read; follow them.
