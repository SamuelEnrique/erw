# warehouse/chat: asking the warehouse questions (platform tool 20, v0)

A question-answering layer over the Energy Research Warehouse (ERW) that never states a number it did not fetch.

| File | Role |
|---|---|
| `tools.py` | The four tools the model may call: `list_tables`, `describe_table`, `query`, `compare`. Built on the `erw` package: local files by default, Supabase or Redivis with `ERW_BACKEND`. No free-form SQL. |
| `ask.py` | The loop: model choice, system prompt, at most 8 tool calls, the number post-check, one retry, refusal. CLI: `python warehouse/chat/ask.py "question"`. |
| `eval/expected.py` | Builds `eval/questions.yaml`: 30 questions whose answers are computed with pandas straight from the CSVs, independently of `tools.py`. |
| `eval/expected_s20.py` | Builds `eval/questions_s20.yaml` (session 20): the 30 recomputed, and 15 on curtailment, the energy mix, retail sales, the trader view, deals and datacenters. |
| `eval/eval.py` | Runs every question through `ask.py` and scores it; writes `eval/results/<run>.jsonl` and `.md`. |
| `../../site/lib/chat/` | The same loop for the public site's `/api/ask` route, in TypeScript, over the Supabase anon key. `spec.json` there is written by `ask.py --export-spec`. |

## The tools

- **`list_tables(sector, license, iso)`:** every table, with its sector, license, ISO, interval, first and last time, rows and source report.
- **`describe_table(table)`:** shape, columns, entities, nodes, variables, units, frequency, time span, source reports and license. For entities and events tables, it also gives the values of their text columns.
- **`query(table, aggregation, ...)`:** one aggregation from a fixed list: `latest`, `mean`, `median`, `min`, `max`, `percentile` (with a value), `count`, `sum`.
  - **Filters (optional):** `entity`, `variable`, `start`, `end`, and `where`, which takes exact-match filters on the table's own columns.
  - **`group_by` (optional):** `year`, `month`, `day` or `hour` of the row time in a time zone `tz`; `entity`; or one of the table's text columns.
  - **Result:** at most 60 rows. `min` and `max` also say when, and for which entity.
- **`compare(a, b)`:** two queries side by side, with the difference and the ratio when both are single values.

Every result carries `table`, `data_version` (backend, data commit, the table's last run), `source_report`, `license` and the `erw` citation.

`where`, `value_column`, `tz`, and grouping by a text column go beyond the four-tool outline in the session prompt. They are needed for entities questions ("operating gas generators in Texas") and for ISO operating days, which are local.

## The rules the model works under

The system prompt is `package/llms.txt` plus these rules:
1. **Answer only from tool results.** Compute nothing in its head.
2. **Cite every number** with its table, source report and data version.
3. **Say "not in the warehouse"** when the warehouse does not hold the answer, and give no numbers.
4. **Prefer public tables,** and label internal ones as internal.

The answer is JSON: `answer`, `citations`, `not_in_warehouse`.

**The post-check.** Every number in the answer must appear in a tool result, in the question, or in a tool argument (such as a percentile), at the precision the answer writes it. Every cited table must be one a tool read.
- If the check fails, the model gets one retry with the violations named.
- If the retry fails too, the answer is replaced by a refusal.
- The check is literal: a time of day or a "15-minute" in the prose counts as a number.

**Cost.** Token usage and cost are printed per question. Prices are in `PRICES` in `ask.py`; a model not listed there is reported as cost unknown.

## Ask ERCOT, the reference version (session 92)

`ercot.py` is a profile of the same loop, developed fully for one grid before any other. `ask.py` gained hooks whose
defaults are the general chat's own (schema, effort, tools, the first message, a mark on each tool result, further
reasons to send a draft back, what is added to the record), so the general chat and the grid pages' chats are as they
were: the spec exported for the site is byte for byte the one committed before, and a test holds it there.

What the profile adds:

1. **A scope.** The 26 ERCOT tables, and for each the rows that are ERCOT's (`SCOPE`: a market, an entity, a region, a
   delivery balancing authority). The tools read nothing else. One table is internal (`ferc_eqr_contracts`) and the
   answer must say so.
2. **A table guide in the system prompt** (`CARDS`): each table with its entities, variables, units and traps, and one
   line of facts from coverage. The model goes straight to a query. `python warehouse/chat/ercot.py --guide` prints it.
3. **Series.** Every query result carries a result id (`r3`; `r3a` and `r3b` in a compare). An answer that rests on
   values over time or one value per group names the results it rests on; the record then holds those rows as the
   tool returned them, with the table, its source report, tier and license (`record["series"]`). A page draws its chart
   and its table from them. If the model fetched a series and named none, the last grouped result of a table it cites
   is returned, and marked as chosen by default.
4. **Follow-ups.** Two or three questions the reader could ask next (`record["followups"]`), checked: a question,
   with no number in it that no tool returned (a year excepted).
5. **Context.** A view of the site may open the chat with its path, its name and its settings; they go into the first
   message as the defaults of the question, and their numbers count as given.

```bash
python warehouse/chat/ercot.py "How has the price of regulation up changed by year since 2018?"
python warehouse/chat/ercot.py --context '{"view": "/shoulder", "settings": {"month": "2025-01"}}' "How many hours did the shoulder ask for in this month?"
python warehouse/chat/ercot.py --export-spec site/lib/chat/spec_ercot.json     # after any change to the rules, the cards or the scope
python warehouse/chat/eval/ercot_expected.py                                    # rebuild the 44 questions from the tables
python warehouse/lock.py run --task "ask ercot eval" -- python warehouse/chat/eval/ercot_eval.py --arm after --cap 5
```

The evaluation writes the cost ledger (`warehouse/output/api_cost_ledger.csv`), so it runs under the data lock, and its
`--cap` is the session's spend cap: `llm.py` refuses a call once the ledger's total for the session has reached it.

On the site the profile is `site/lib/chat/ercot.ts`, the page `/ask/ercot` (in review), and the same checks; a test runs
the same tool results through both and compares what they return. The site reads the Supabase live set, which does not
hold every ERCOT table (the hub price history, the reserve prices, Berkeley Lab's queue, the owners, the internal
contracts): there the chat says the table is not in the site's live set.

## Ask ERCOT, to user-ready (session 121)

What the profile gained, in `ercot.py` and, the same, in `site/lib/chat/ercot.ts`:

1. **A conversation.** `ask(question, history=[earlier records])`. The first message carries, for each of the last
   three turns, the question, the answer and the queries run for it, so "and the year before?" is read as what it
   continues. The numbers of an earlier answer count as given (they were checked when it was written); every new
   number is still fetched and checked. Without a history the first message is byte for byte what it was.
2. **A refusal names the nearest thing held.** The answer schema has `nearest`: one to three tables of the guide,
   nearest first. A refusal that names none, or a table that is not in the guide, is sent back. What the reader is
   shown beside each table (`HOLDS`) is the guide's own sentence, written by code. The fixed refusal (an answer whose
   numbers could not be traced) lists the tables it read. A question plainly outside the tables is refused without a
   tool call.
3. **A premise.** The schema has `premise`: one sentence when the question takes for granted something the tables
   contradict (a level, a direction, a ranking, a date, an "always"). Its numbers are checked as the answer's are.
4. **A loose question is answered**, in the most natural reading the tables bear, which the answer states first.
5. **Time.** Every record has `seconds_first` (the model's first reply: the first thing a reader can be shown) beside
   `seconds`. `on_event` reports each table as its query starts; the site's route streams those as lines of JSON
   (`{"stream": true}`), then the answer, whole and checked. The site reads the queries of one model turn together and
   no longer waits on the cost ledger between model calls.
6. **A chart is the rows fetched.** Each series of a record carries `check`: the rows the tool returned, the rows of
   the series, whether they are the same key by key, and how many of them a line chart can place. A series that is
   not the tool's rows is not shown. `site/lib/chat/series.ts` is the one function the page draws from;
   `node site/scripts/check-series.mjs <records.jsonl>` sets every chart of a run against its rows.
7. **Cost.** Each record has `cost_usd`; the site's log line of a question has its cost, seconds and tool calls, and
   its rows in `site_api_calls` carry the step `site_ask_ercot`.

The second evaluation set: `eval/ercot_expected_s121.py` builds `eval/questions_ercot_s121.yaml`, 100 questions of
five kinds (join, vague, followup, premise, outside); `eval/ercot_eval_s121.py --arm before|after --cap USD` runs it,
`--rescore <jsonl>` scores saved answers again without a model call. `node site/scripts/time-ask-ercot.mjs <base>
<out.json>` times a few questions on the site itself (each is a model call).
