# Session 137 report: Ask ERCOT as the answer panel

## Three things to know before anything else

1. **On production Ask ERCOT answers no one yet.** `ASK_VISITOR_SALT` is still not set in Vercel (session 128's step 1), so the tool is closed. I sent one question to production after the deploy: HTTP 503, "This tool is not answering questions right now. Your question was not sent to the model.", and no row in the cost ledger. Everything below was measured on a local build of the same code, through the site's own route.
2. **My evaluation used USD 6.28 of October's USD 30 ceiling, and all of today's.** The 228 test answers went through the site's own cost ledger (762 model calls, step `site_ask_ercot`), which is the ledger production's ceilings count. The month now stands at USD 7.21. Today's total is USD 6.41 against the daily ceiling of USD 3, so even with the salt set, production would have refused questions until 00:00 UTC. The local test server ran with a test ceiling of its own (USD 7.50 a day); production's configuration is unchanged (3 a day, 30 a month, 15 questions a visitor a day, and a test holds it).
3. **Answers about numbers got slower, not faster.** A question about an idea now takes 3.3 seconds (it took 14.3). A question about numbers takes about 17 seconds (it took about 9.5), because it now answers where it used to refuse quickly, and reads more before it answers. Details under "Time".

## Verdict: not ready to open, and close. What is left, exactly

1. **Set `ASK_VISITOR_SALT` in Vercel**, and the two items session 128 left with it: a spending limit in the model provider's console, and the words on `/terms` about the one-day visitor count.
2. **Seventeen seconds for a number is too long for a box on a page.** The reader sees "reading <table>" after about 3 seconds and the answer whole at about 17. Two ways down, neither built: let one query return a row and its series together (number questions now make 3.2 tool calls where they made 2.3), and send the words of an answer as soon as its numbers have passed the check.
3. **One of the 100 questions still fails, and it is the data, not the tool:** "What is ERCOT's highest hourly demand so far in 2026?" The site's live set holds hourly demand for the newest weeks only, so the tool says "not in the warehouse", which is true. A table of daily demand peaks exists (`eia930_daily_demand`) and is held out of the live set. I did not load it: a load during the freeze, into tables the network page may read, is not mine to make.
4. **73 of the 99 passing answers were not asked again after the last fixes.** The fixes changed the instructions every answer is written under. I asked the 15 failures again and a sample of 12 that had passed (three of each kind): all 12 passed. A full second run did not fit the cap with margin.
5. **The Python reference loop does not know the panel.** `warehouse/chat/ercot.py` is the loop the site's was copied from, and it exports the site's instructions. The answer's form, the page tool and the refusal rules are the site's additions (`site/lib/chat/panel.ts`). The exported file is untouched and the two earlier tests that hold the loops together still pass, because an answer that names no form is treated exactly as before. Someone should bring the Python loop along, or rule that the site is now the reference.

## What was asked for, and what was built

| Asked | Built |
|---|---|
| Answers right below its box | The box, then the newest answer directly under it, earlier answers below, newest first |
| The form the question calls for | The answer names its form: **words** (an idea), **sentence** (one figure), **chart** (how something moved), **table** (a breakdown). The page draws by it |
| Never a chart for its own sake | A series is shown only under form chart or table. The earlier rule "if the answer names no series, show the last one it fetched" is gone for these answers. An answer in words or a sentence that names a series is sent back |
| Every chart checked against the rows it fetched | Session 121's check, kept and extended to the new source: each series is set against the tool's rows key by key and value by value, and the chart's points against the series; one that differs is not shown. 25 charts in the final answers, 0 that differed |
| Learns the tables landed today | The price board and Supply and trade are files of the site built from tables held out of the live set, so a new tool, `page_figures`, reads their rows: ERCOT's and those of no grid, never another grid's. The energy mix's three tables are in the live set and are read with the ordinary query |
| Uses the ERCOT page's written content, citing it | The page's five sections (who runs the grid, how its market sets prices, what makes it different, the short history, the glossary) are carried in the instructions, so an idea is answered in one model call. The answer cites `docs/grids/ercot.md`, shown as "Written page" with a link. Its years and dates count as given for the number check |
| Session 128's ceilings and per-visitor limit stay | Untouched. A question is admitted by the database before any model call, as before |
| One component, the grid a parameter | `site/components/ask/AskPanel.tsx`: `<AskPanel grid="ercot" />`. A grid with a profile of its own (today: ERCOT) is asked as that profile; any other grid is asked of the general chat for that grid, in the same box |
| Used on `/grid/ercot` and `/ask/ercot`; nothing else on `/grid/ercot` changes | Both use it. On `/grid/ercot` it stands where the box that opened `/ask` stood, between "Who runs this grid" and "Right now: demand". Compared with production before the deploy: the same 14 headings in the same order, no block of text gone, one added: the link "Method note". The six other grids' pages keep their box (CAISO compared: the same headings and no block of text differs) |
| 100 new test questions, 25 of each kind | `warehouse/chat/eval_ercot_panel.json`, with the rule that judges each kind |
| Fix every failure at its cause | Seven fixes, below. One failure is the data's and stands |
| Log cost per question | Each answer's cost is in the site's ledger under its question number, and in `warehouse/chat/eval_ercot_panel_results.csv`, one row a question, before and after |

**Page-face rules.** The panel's face holds the box, the answer, its sources, and the chart or table. What it said about how answers are made (the number check, the rows drawn, the queries and cost, the ten an hour) is in a new Method note, `docs/methods/ask_ercot.md`, linked under the box. `/ask/ercot`'s two paragraphs about method moved there too. The chart answers the mouse; a row with no value reads "not held" with its reason on hover.

## Pass rates by kind, before and after

One rule a kind, the same before and after (`site/scripts/eval-judge.mjs`):

- **conceptual:** answered; at least 15 words; no chart or table; cites the ERCOT page's text.
- **chart:** answered; at least one series, each equal to the rows fetched; at most 120 words.
- **sentence:** answered; no chart or table; a number in it; at most 70 words; a table cited.
- **refuse:** not answered; no chart; the answer names what was asked about.

| Kind | Before (the tool as it stood) | After, first full run | After the fixes (each question's newest answer) |
|---|---|---|---|
| Conceptual | 18 of 25 | 24 | **25** |
| Numbers needing a chart | 12 of 25 | 19 | **25** |
| Numbers needing a sentence | 12 of 25 | 18 | **24** |
| Refused or redirected | 25 of 25 | 24 | **25** |
| **All** | **67** | **85** | **99** |

- **The 10 questions that need today's tables:** 0 passed before, 10 after (Henry Hub, the spark spread, gas in storage, ERCOT's fuel burn, its day-ahead cleared energy, the mix by hour, the carbon-free share, the lowest net load).
- **A chart where none was called for:** before, a series was shown under 21 answers, 5 of them to a question about an idea or one figure ("What is a hub?" came with a chart). After: under the 25 chart questions and no other.
- **Before, the 7 conceptual failures** were a chart shown (3), the page's text not cited (3) and "an interconnection queue is a general concept, not a data series" refused (1).

## Every failure, and its cause

| # | What failed | Cause | Fix |
|---|---|---|---|
| 1 | Six questions on generation by fuel, the carbon-free share and net load: "the table returned no rows" | The ERCOT scope filtered the three energy-mix tables on their market column, which they leave empty. Their rows are a grid's by entity | The scope names the entity (`iso:ercot`) for those tables; the instructions name their real variables |
| 2 | "What happened on the ERCOT grid during Winter Storm Uri?" came with a chart of prices | Nothing said that a question about what happened is a question about an idea | A question that asks what, why or how and asks for no figure is answered in words, even when tables hold numbers on its subject |
| 3 | Three one-figure answers ran to 71 to 79 words | The note of how the question was read ("I read last month as...") was not counted in the length | It is counted: 50 words in all |
| 4 | Two questions on yesterday's hourly demand refused with no query at all | The exported guide prints each table's last date as of the day it was written; the tool believed it | It must query before saying a recent day is not held, and answer for the newest whole day held |
| 5 | A refusal about ISO-NE's fuel mix was itself refused, twice | It named an energy-mix table as the nearest thing held, and the check on "nearest" knew only the exported guide's tables | The check and the list shown know the three mix tables, each with what it holds |
| 6 | Could not see why a draft was sent back | The check's reasons went nowhere | They go to the server's log, never to the reader (`erw_ask_check`): the untraced numbers, the uncited tables, the problems |
| 7 | (found while looking, not a test failure) An answer that names today's date after no tool call would be refused as unverified | The date the loop gives the model was not among the texts whose numbers count as given | It is. No test question showed this; I did not prove it on one |

- **Not fixed at a cause: "daily peak demand over the last two weeks"** failed the number check on the first run and passed when asked again. The log of a later draft shows the check doing its job (a first draft sent back for two rounded figures, 78000 and 82000, a second that passed). The same question can fail again.
- **Stands: the year's highest hourly demand** (above, item 3 of the verdict).
- **Three regressions in the first run**, all fixed: two sentence answers over the length (fix 3) and the ISO-NE refusal (fix 5).

## Cost per question

| Kind | Before, USD a question | After, USD a question |
|---|---|---|
| Conceptual | 0.0385 | 0.0113 |
| Numbers needing a chart | 0.0288 | 0.0517 |
| Numbers needing a sentence | 0.0225 | 0.0472 |
| Refused or redirected | 0.0057 | 0.0069 |
| **Mean of the 100** | **0.0239** | **0.0293** |

A question costs 23 percent more on average: ideas cost less than a third of what they did, numbers nearly twice as much (they are answered now, with more reading, where half were refused in one or two calls). The costliest answers after: the average day's wind by hour, USD 0.12; how batteries charge across the day, USD 0.11.

## Time

Seconds from the question to what a reader sees, medians:

| Kind | To the first sign, after | To the whole answer, before | To the whole answer, after |
|---|---|---|---|
| Conceptual | 3.2 | 14.3 | **3.3** |
| Numbers needing a chart | 2.2 | 9.8 | 17.3 |
| Numbers needing a sentence | 3.2 | 9.2 | 17.1 |
| Refused or redirected | 3.0 | 3.0 | 3.0 |

- **Time to first word.** The answer is not sent in pieces: it is checked whole first, as session 121 ruled, so its first word arrives with its last. For an idea that is 3.3 seconds. For a number the reader sees "reading <table>" at 2 to 3 seconds and the first word at about 17.
- **Like for like,** the 22 number questions that passed both before and after took 13.0 seconds on average before and 12.7 after, with 2.3 tool calls before and 3.2 after. The medians above rose because 17 number questions that used to be refused in a few seconds are now answered, most of them with several queries.
- The slowest answer after: the spark spread, 46.6 seconds.

## Every pull against its ceiling

**No data pull.** No MISO request. **Model spend: USD 6.2839 of the USD 8.00 cap**, every cent of it in the site's ledger (762 calls for 228 answers; the answers' own counts sum to the same figure).

| Run | Answers | USD |
|---|---|---|
| Before: the tool as it stood, the 100 questions | 100 | 2.3904 |
| After: the changed tool, the 100 questions | 100 | 2.8808 |
| The 15 failures asked again after fixes 1 to 4, 6 and 7 | 15 | 0.7106 |
| The last failure and 12 that had passed, after fix 5 | 13 | 0.3022 |
| **Total** | **228** | **6.2840** |

The runner stops before a question when the spend so far plus a reserve for one more would pass its budget, so a budget is never passed by starting a question (session 135's lesson). The local server's daily ceiling, counted by the database, was the second stop. Neither was reached.

## The deploy

One deploy, with the snapshot before and after: **6 differences, all on `/network`, all its hourly refresh at 21:05 UTC** (the refresh stamp, the newest demand hour, the source line's build stamp); no checked number moved (3,357 compared). Checks passed (run 37536688654), merged as `f06211b`. **Vercel built it**: "Deployment has completed" at 21:59 UTC, production's build id is `zL4v2BePC5YY5sySX_qcc`. On production, in the internal view, `/ask/ercot`, `/grid/ercot` and the new Method note answer 200; a visitor sees the in-review page for each. The panel's browser check passes against production, 13 of 13, with recorded answers and no model call. Both pages stay `review`.

## Checks

| Check | Result |
|---|---|
| `tests/test_session137.py` | 16 tests: the 100 questions and their rule, the one component and where it stands, the form and the chart rule, the sources, the ceilings as they were |
| `site/scripts/test-ask-panel.mjs` | 8 tests, no request: the page tool returns ERCOT's rows and no other grid's, a series is the page's own points date for date, another grid's row cannot be asked for by its id |
| `site/scripts/check-ask-panel.mjs`, a real browser, recorded answers | 13 of 13, locally and on production: words and a sentence show no chart and no table; a chart answers the mouse and shows every row; the newest answer comes first under the box |
| `site/scripts/check-ask-ercot.mjs` (session 92's) | 23 pass. **It had been failing since session 121 made the route stream**: its recorded answer has no type, and the page dropped it. The panel now takes a whole answer that arrives without a type |
| The earlier Ask tests (sessions 91, 92, 114, 121, 128) and the menu test | pass. One line of session 121's test now reads the component's new file |
| The whole suite and the site's checks on GitHub | passed (run 37536688654) |

## The five most interesting things the tool now does

1. **"What is a hub?" in three seconds, in words, with the page's own text as its source.** Before: 34 seconds, six model calls and a chart.
2. **It reads the pages landed today.** Henry Hub, the spark spread, gas in storage, what ERCOT burned and what its day-ahead market cleared: ten questions it refused this afternoon and answers tonight, each citing the page it read.
3. **It tells an idea from a figure from a movement.** The same subject gets words, a sentence or a chart depending on what was asked, and the chart appears only for the third.
4. **A refusal is a signpost.** Another grid's question names that grid's own page; a licensed price names the spot price that is held; a company's earnings are declined by name.
5. **It can be measured for a few dollars.** One hundred questions, one rule a kind, the cost and seconds of every answer in a file, and a runner that stops before its budget. The next change to Ask ERCOT can be judged the same way.

## Decisions I made without you

1. **Evaluated through the site's own route on a local build**, with each question sent from its own made-up address so the per-address and per-visitor limits saw 100 visitors, and a local daily ceiling of USD 7.50. The alternative, calling the loop directly, would not have tested the route, the limits or the ledger.
2. **The board and Supply and trade are read as the pages hold them:** each row's newest value, its changes, and its recent points (30 for the board, 52 weeks for Supply and trade). A longer history of a board row is not reachable from the panel yet.
3. **"The seven grids together" is not ERCOT's row** and the panel does not return it.
4. **Winter Storm Uri is now answered from the page's text alone** unless the question asks for a figure. The prices of that week are still there for "what did prices do during Uri?".
5. **The answer's footer is gone from the face** (the number of queries, the model, the seconds, the cost). The seconds are an attribute of the answer for the checks; the cost is in the ledger and at `/internal/ask`.
6. **Other grids' pages keep their old box.** The component would work there through the general chat; I did not place or test it, as you asked for ERCOT only.

## For Samuel

1. Set `ASK_VISITOR_SALT`; then ask "Teach me how ERCOT sets prices" and "What was the Hub Average price yesterday?" on `/grid/ercot` in the internal view.
2. Say whether 17 seconds for a number is acceptable for now, or the two speed-ups come first.
3. Rule on the Python reference loop.
4. Rule on loading `eia930_daily_demand` so the year's peak can be answered.
