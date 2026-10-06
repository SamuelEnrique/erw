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

## Limits

The tool has a spending ceiling for the day and for the month and a number of questions per visitor per day. When one is reached it answers with a plain message and your question is not sent to the model. They are described in [the limits note](/data/methods/ask_limits).

## What it cannot tell you

- **It answers from what is held.** A fact that is true and not in the tables or the page's text gets "not in the warehouse", not an answer from memory.
- **The page's text is short.** A question about an idea the text does not cover is not answered.
- **It can misread a question.** The sources under the answer show what was read; follow them.
