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
