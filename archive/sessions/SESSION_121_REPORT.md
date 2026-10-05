# Session 121 report: Ask ERCOT, to user-ready

**Done and deployed (review page).** One hundred new questions of five kinds: 76 correct before, 100 after. The first thing a reader sees now arrives in 3.5 seconds at the median (it was the whole answer, at 12.5). Model spend: USD 7.15 of the USD 8 cap. No live page changed (snapshot below).

**Verdict: ready to open, on one condition that is yours.** The chat answers, corrects, refuses and follows up as a reader would expect, and every number is still checked. What it cannot yet do is protect your money: there is no daily ceiling on what visitors can spend. That, and three smaller things, are under "What is left".

## Read these first

1. **Pass rates, before and after, on the same 100 questions.**

   | Kind | What it tests | Before | After |
   |---|---|---|---|
   | Joins across two tables | both tables cited, both numbers right | 19 of 20 | 20 of 20 |
   | A newcomer's vague question | answered, never refused or sent back | 20 of 20 | 20 of 20 |
   | Follow-ups ("And the year before?") | the answer that only the previous turn makes possible | 3 of 20 | 20 of 20 |
   | Wrong premise | says what the tables show, does not go along | 19 of 20 | 20 of 20 |
   | Outside what is held | refuses, and names the nearest table held | 15 of 20 | 20 of 20 |
   | **All** | | **76 of 100** | **100 of 100** |

2. **The follow-ups were the real failure.** The page kept nothing of the previous answer. Asked "And a four-hour one?" on its own, the chat did not refuse: it guessed a question and answered that. Of the 17 that failed, 15 were answers to a question nobody asked and 2 were refusals because their numbers could not be traced. The page now keeps the conversation and sends the last three turns with each question.
3. **Two faults were in the chat's own guide, not in the model.** Both about `ba_supply_monthly`:
   - The guide called `demand_mwh` "demand". It is demand over the days the supply figures hold: 318 of 2025's 365. Summed, it makes 2025 look 6 percent smaller than 2024 (431,326,248 MWh against 461,064,137). Over all days 2025 was larger (484,301,530 against 463,615,518). The guide now sends a month's or a year's demand to `demand_all_days_mwh`.
   - The guide gave ERCOT's row two variables it does not have (`net_import_mwh`, `net_import_share_pct`); those belong to the tie rows. It now names the three measures the row does have.
4. **A refusal now names what is held.** Before, a refusal described the nearest thing in words ("hub prices"). Now it must name one to three tables of the guide, and the page shows each with the guide's own sentence of what it holds. A refusal that names none is sent back. A question plainly outside (the weather, another grid) is refused without a single query: 18 of 20 refusals made no query, against 13 before, and the weather question, which had taken 8 queries and 22.3 seconds, takes none and 3.3.
5. **Time.** On the 100 questions, on this machine:

   | | Before | After |
   |---|---|---|
   | To the first thing shown, median | 12.5 s (the whole answer: nothing was shown before it) | 3.5 s (the table being read) |
   | To the first thing shown, 90th percentile | 23.9 s | 5.4 s |
   | To the full answer, median | 12.5 s | 9.8 s |
   | To the full answer, 90th percentile | 23.9 s | 21.5 s |
   | Answers over 20 seconds | 26 | 13 |
   | Model requests per question | 3.94 | 3.04 |

   On the site itself, six questions before and the same six after: median 10.1 s to the answer before, with nothing shown until then; after, 3.4 s to the first thing shown and 7.2 s to the answer. The slowest of the six took 39 s before and 26.9 s after.
6. **Every chart is checked against the rows fetched, twice.** In the loop: each series is set against the tool's rows, key by key and value by value, and one that differs is not shown. On the page: the chart's points come from one function, and the line under each chart says how many of the fetched rows it shows and names any it cannot draw. Over the after run: 28 series, 282 rows, 21 line charts with 226 points, 56 rows named as not drawn (rows of bar series and rows with no value), 0 mismatches.
7. **Cost per question is logged.** Mean USD 0.0254 after (0.0311 before); the dearest question USD 0.094. Each record of a run holds its cost; the site's log line for each question now holds cost, seconds and queries, and its ledger rows are marked `site_ask_ercot`.
8. **One miss on the older set, and it is rounding.** A sample of 22 of the first set's 54 questions: 21 correct. The miss answered "about 3.6 hours" where the table says 3.6085 and the scorer wants two decimals.

## What changed

| What | Before | Now |
|---|---|---|
| A follow-up | asked alone; the chat guessed what it continued | the last three turns go with the question: each earlier question, its answer and the queries run for it. "And in 2022?" is read as what it continues. A new number is still fetched and checked; a number repeated from an earlier answer is allowed because that answer was checked |
| A refusal | one sentence; the nearest thing in words, sometimes | `nearest`: one to three tables of the guide, required, checked by code; shown with what each holds. The fixed refusal (numbers that could not be traced) lists the tables it read |
| A wrong premise | usually corrected in the text | `premise`: one sentence saying what the question assumed and what the tables show, shown above the answer; its numbers are checked like the answer's |
| A loose question | answered, at length (8 queries for "what's a normal price?") | the rules say: take the most natural reading, say which, answer it |
| What a reader sees while waiting | "this can take up to a minute" | the table being read, as each query starts; then the answer, whole, after its check. The answer is never shown in pieces: an unchecked number must not reach the page |
| The site's queries | one after another | the queries of one model turn are read together |
| The site's cost ledger | awaited between model calls | written beside the loop, awaited once at the end |
| A chart | drawn from the series | drawn from the series by one tested function; checked against the tool's rows; says how many rows it shows |
| The page | one answer at a time | the answers stay, oldest first; "New conversation" clears them |

The same in both loops (`warehouse/chat/ercot.py` and `site/lib/chat/ercot.ts`), with a test that the site writes the conversation exactly as Python does. The general chat (`/ask`) and the grid pages' chats are untouched: their route is called argument for argument as before, and a test holds it.

## The questions

`warehouse/chat/eval/ercot_expected_s121.py` builds them. Every expected number is computed from the tables with pandas, apart from the chat's tools. Every wrong premise is checked against the tables when the file is built: the build stopped three times because a premise I had written turned out to be true (solar did capture the flat price's level in the month I named; summed over held days, demand did "fall" in 2025), and reading its output I found a fourth that passed for the wrong reason (solar's capture rate is a percent, not a ratio). Each became a better question.

- **How a question is scored.** Status (an answer where one is due, a refusal for the outside kind); every expected number within its own tolerance (half a percent; a count to the unit); the required words; the cited tables (for a join, one from each of two groups); for a refusal, a table of the guide named.
- **A weakness of the first set's scorer, not repeated.** It had one tolerance for a whole question, so a rate of 0.6 could pass beside a count of 4,000. Here each number has its own.
- **What the vague kind does not measure.** It passes when the question is answered from a table that can bear it. Whether the reading chosen was the best one is a judgment the scorer does not make. All 20 passed before and after; what changed is how long they took (median 17.9 s to 12.7 s).

## Money

| | USD |
|---|---|
| Before run, 100 questions | 3.11 |
| Pilot of the changed code, 11 questions | 0.29 |
| After run, 100 questions and the 20 first questions of the follow-ups | 2.90 |
| A sample of the first set, 22 questions | 0.41 |
| On the site: timing before and after, a local check, the browser check | 0.44 |
| **Total** | **7.15 of 8.00** |

The Python runs are rows of the cost ledger under session 121 (USD 6.71). The site's calls are rows of `site_api_calls`; their sum is from each answer's own cost, with the three browser-check questions estimated at USD 0.02 each because that script does not record cost.

**The ledger is whole again.** Session 119 left this to me: 6 rows of the two Roundup runs of 4 and 5 October (USD 0.0568) were in the archive only, and 1 trial row (USD 0.0073) in a folder. All 7 are merged in by their id; coverage, archive, the live set and the Redivis draft now hold 2,154 rows.

## The live pages

One deploy: `task/121-ask-ercot`, run 37304131476, merged to main as `28587f4`. One load: the cost ledger (internal, read by no page). No freeze was in force (`scripts/freeze.py status`: exit 0).

Snapshots `before-121` (11:31 UTC) and `after-121` (11:47 UTC, production serving the new chat): 25 pages, 4,098 checked numbers each, 0 failed reads.

**32 differences, all of them the clock. None is this session's.**

| Page | Differences | What | Expected |
|---|---|---|---|
| `/` | 26 | the price board's newest real-time interval of the hubs, with their lines of text | yes: the 15-minute price job |
| `/network` | 6 | the hourly refresh stamp, the newest demand hour, the build stamp in the source line | yes: the hourly network refresh |
| the other 23 pages and views, `/terms` and the four methods pages among them | 0 | | |

`/ask/ercot` is in review; a visitor asking for it still gets the in-review page (the route check: 16 live pages, 99 in review, 0 failed).

## Decisions made without you

- **The answer is never streamed word by word.** Time to first word was asked for. An answer's numbers are checked only when it is whole, so showing words as they come would show unchecked numbers. What is streamed is what the chat is reading. I report "the first thing shown".
- **A reader's own earlier answers count as given.** The page sends them back with the next question, and their numbers pass the check as the question's own numbers do. A reader could edit what the page sends and make the chat repeat an invented number as "said earlier". It is the same trust the question already has; the answer says where the number is from.
- **Three turns of history, 1,500 characters of each answer.** Enough for a follow-up; small enough to keep cost flat (a follow-up costs USD 0.018 on average, less than a first question).
- **I did not add tables to the chat's scope** (the storage awards, the large loads). The question set would have had to change under it.
- **The "before" follow-ups were asked bare**, as the page did. That is why "before" is 3 of 20 and not 0: three bare follow-ups happened to mean what the chat guessed.

## Errors, and what caught them

| What | Caught by | Now |
|---|---|---|
| Four premises that were true | the question builder's own checks | reworded from the data |
| The scorer could not read the record's `nearest` (objects, not names) | a unit test before the after run | fixed; no run was scored wrong |
| My test file switched the cost ledger off for every test after it | session 30's test, in the full run | removed |
| The general chat's call in the route reworded | session 92's test | as it was |
| A table's rows did not fit on a Windows command line in a test | the test | the script goes on standard input |

## Tests

`tests/test_session121.py`, 34 tests, no model call: the conversation (and that without one the first message is byte for byte what it was); refusals; the premise; time; the chart check; the guide's two faults against the table; the question set and its scorer; the site against Python. Earlier tests changed: session 92's stand-in answers gained the two new fields.

`site/scripts/check-ask-conversation.mjs`, in a real browser, three real questions: a table was named while the answer was prepared; the chart said "49 of 49 rows"; "And a year earlier than the first of those?" was answered with 2019, which only the conversation could tell it; a household's bill was refused with two tables and the guide's sentence beside each. All 9 checks passed.

Full suite: 1,208 tests; the one failure outside this session's files was mine and is fixed (above). Site build exit 0. Route check exit 0.

## What is left

1. **A spending ceiling for visitors (yours to set).** The route allows 10 questions an hour from one address, per server instance. Nothing caps a day. At USD 0.025 a question that is small until someone scripts it. Before opening: a daily cap in the route, counted in the database, with the page saying so when it is reached. Half a day of work; I did not build it because the amount is your decision.
2. **Precision.** The chat sometimes rounds to one decimal ("about 3.6"). A rule to keep the table's two decimals would fix the one miss on the older set. It changes every answer, so it needs a full run of both sets (about USD 4) and I had USD 0.85 left.
3. **The site's tables.** The runs were on this machine's full tables. The site holds hub prices by day and the newest weeks by interval; a question that needs one interval of 2021 is answered from the day's figures there. Session 114 said so; it is still so.
4. **The vague kind needs a human read.** Twenty answers to loose questions, each reasonable by the scorer. Ten minutes of your reading would tell more than the score.
