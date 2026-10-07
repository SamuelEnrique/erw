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

## Limits

The tool has a spending ceiling for the day and for the month and a number of questions per visitor per day. When one is reached it answers with a plain message and your question is not sent to the model. They are described in [the limits note](/data/methods/ask_limits).

## What it cannot tell you

- **It answers from what is held.** A fact that is true and not in the tables or the page's text gets "not in the warehouse", not an answer from memory.
- **The page's text is short.** A question about an idea the text does not cover is not answered.
- **It can misread a question.** The sources under the answer show what was read; follow them.
