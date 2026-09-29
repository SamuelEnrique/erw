# Session 12 report

Energy Research Warehouse (ERW), session 12, run 2026-09-26 (UTC). Platform tool 20, v0: a question-answering layer that never states a number it did not fetch.

- **Evaluation: 27 of 30 correct (90%).** The set covers power, gas, oil, products, capacity, news, entities and refusals.
- **Cost:** USD 1.30 for the whole run, USD 0.043 per question on average.
- **Tool calls:** 2.93 per question on average.
- **Code after the results:** no code was changed in response to them. No outright bug was found in the harness.
- **Nothing pushed, no key printed or committed.** `ANTHROPIC_API_KEY` is read from `.env` (Python) or the server environment (site). It was added to `site/.env.local` for the local run, and that file is ignored by git.

## What was built

| Task | Result | Commit |
|---|---|---|
| 1 | `warehouse/chat/tools.py`: `list_tables`, `describe_table`, `query`, `compare` over the `erw` package. The backend is local by default, or Supabase or Redivis with `ERW_BACKEND` | `135017f` |
| 2 | `warehouse/chat/ask.py`: model choice, system prompt from `package/llms.txt`, at most 8 tool calls, JSON answer with citations, the number post-check, one retry, refusal, token usage and cost per question | `a4c7ff1` |
| 3 | `warehouse/chat/eval/`: `expected.py` (pandas answers), `questions.yaml` (30 questions), `eval.py` (scoring), and the run's records and summary in `results/` | `43ac886` |
| 4 | `site/app/api/ask/route.ts` (server-side, rate-limited), the `/ask` page, and `site/lib/chat/` (the same loop in TypeScript over the Supabase anon key) | `625d06f` |
| 5 | This report | final commit |

## Task 1: the tools

**What each tool does:**

| Tool | Returns |
|---|---|
| `list_tables(sector, license, iso)` | Every table with its sector, license, ISO, interval, first and last time, rows and source report |
| `describe_table(table)` | Shape, columns, entities, nodes, variables, units, frequency, time span, source reports, license and header notes. Entities and events tables also get the values (with counts) of their text columns |
| `query(table, aggregation, ...)` | One aggregation over a filtered, optionally grouped table (details below) |
| `compare(a, b)` | Two queries side by side, plus the difference and ratio when both give one value |

**`query` in detail:**
- **Aggregations**, a fixed list: `latest`, `mean`, `median`, `min`, `max`, `percentile` (numpy linear, with a value), `count`, `sum`.
- **Groupings:** `year`, `month`, `day` or `hour` of the row time in a time zone `tz`, `entity`, or one of the table's text columns.
- **Result:** at most 60 rows. `min` and `max` also say when, and for which entity.
- **No free-form SQL.**

**Every result carries its provenance:** `table`, `data_version`, `source_report`, `license`, and the `erw.cite()` citation. `data_version` is the backend, the data commit for local files, and the table's last run.

**Beyond the prompt's outline** (decision 1 explains why):
- `where` (exact-match filters on a table's own columns);
- `value_column`;
- `tz`;
- grouping by a text column.

## Task 2: the loop

- **Model:** the newest model whose id contains "sonnet", by `created_at` in the API's models list. It was `claude-sonnet-5`; the list also held `claude-sonnet-4-6` and `claude-sonnet-4-5-20250929`.
- **Settings:** effort `high`, adaptive thinking (the model's default), `max_tokens` 16,000.
- **System prompt:** the rules, then `package/llms.txt` in full. It is cached, and the evaluation read 1,179,764 tokens from the cache against 395,930 uncached.
- **Rules:**
  1. Answer only from tool results.
  2. Compute nothing in its head: use `compare` for differences and ratios.
  3. Cite every number with its table, source report and data version.
  4. Say "not in the warehouse" and give no numbers when the warehouse lacks the answer.
  5. Prefer public tables and label internal ones.
- **Answer format:** JSON through structured outputs (`answer`, `citations`, `not_in_warehouse`). A one-call probe confirmed that the API accepts a JSON output format together with tools on this model.
- **Tool budget:** at most 8 tool calls. After the 8th, the request is sent with `tool_choice` `none`.

**The post-check:**
- **Numbers:** every number in the answer must appear in a tool result, in the question, or in a tool argument (such as a percentile of 99.9), at the precision the answer writes it. 25.1834 may be written 25.18, but not 25.19. A sign may be stated in words.
- **What counts as a number:** digits glued to a letter, underscore or dot are not read as numbers (`eia930_ciso`, `P99.9`). List markers at the start of a line are ignored.
- **Citations:** every cited table must be one a tool read, and an answer with numbers must have a citation.
- **On failure:** one retry with the violations named. If the retry fails too, the answer becomes a fixed refusal.

**The CLI** prints token usage and cost for every question, from `PRICES` (the claude-api skill's table: Sonnet 5 at USD 2 and 10 per million input and output tokens). Example:

```
$ python warehouse/chat/ask.py "What was the most recent Henry Hub natural gas spot price in the warehouse, and on what date?"
The most recent Henry Hub natural gas spot price in the warehouse is 2.90 USD/MMBtu, dated 2026-09-22 (interval start, UTC), from the eia_fuel_spot_prices table.
  [eia_fuel_spot_prices] source eia:natural-gas/pri/fut;eia:petroleum/pri/spt; local backend, data commit 6eb0326ecc27; table last run 2026-09-25T23:57:29Z

status answered; model claude-sonnet-5; tool calls 2; requests 3; tokens in 2266 out 376 cache write 9998 cache read 19996; cost USD 0.0373; 9.8 s
```

## Task 3: the evaluation

**How the expected answers were computed.**
- **Independent of the tools:** `expected.py` reads each CSV itself (provenance lines skipped by count) and computes the answer with pandas. It shares no code with `tools.py` or the `erw` package.
- **Peak premium from raw data:** the ERCOT peak-premium answers are recomputed from the raw 15-minute yearly tables. They reproduce the method document's thesis values exactly: HB_HUBAVG peak IQR 7.64 (2015) and 34.12 (2025), and P99.9 311.80 (2025). That is an independent check of `ercot_peak_premium_annual`.
- **Fixed date:** the set is fixed to today = 2026-09-26, and `eval.py` passes that date to the model.

**Scoring.** A question is correct when every check that applies passes:
- **number:** every expected number is in the answer, within the question's tolerance: 0.01 for prices, 0.5 for MW, counts and kbbl.
- **text:** required words are present (the winning ISO in q02, the year in q18).
- **citation:** a cited table is one of the acceptable ones, every citation has a source report and a data version, and an internal table is labeled internal.
- **refusal:** "not in the warehouse" exactly when expected.

**Results** (run `20260926T085749Z`; records in `warehouse/chat/eval/results/20260926T085749Z.jsonl`, summary in `.md`):

| Measure | Result |
|---|---|
| Correct | **27 of 30 (90%)** |
| number | 25 of 28 |
| text | 28 of 28 |
| citation | 25 of 28 |
| refusal | 27 of 30 (both "not in the warehouse" questions correct; 3 answerable questions wrongly not answered) |
| Retried after the number check | 7 (6 then passed, 1 refused) |
| Total cost | USD 1.2996 |
| Cost per question | mean USD 0.0433, median 0.0269, min 0.0103, max 0.1527 |
| Tool calls per question | mean 2.93 (min 1, max 8) |
| Time per question | median 11.4 s, max 43.4 s |
| Tokens (all 30) | 395,930 input, 27,179 output, 1,179,764 cache read, 118 requests |

| Id | Sector, shape | Question (short) | Expected | Correct | Status | Calls | Cost (USD) |
|---|---|---|---|---|---|---|---|
| q01 | power, series | ERCOT HB_NORTH DA average, yesterday (local day) | 33.3904 | yes | answered | 2 | 0.0275 |
| q02 | power, series | ISO with the highest RT price, 2026-09-18 to 24 | ERCOT, 337.72 | yes | answered | 8 | 0.1527 |
| q03 | power, derived | HB_HUBAVG peak-block IQR, 2015 and 2025 | 7.64, 34.12 | **no** | refused_unverified | 4 | 0.0718 |
| q04 | power, series | CAISO SP15 DA max, 2026-09-01 to 24 | 200.3339 | yes | answered | 1 | 0.0103 |
| q05 | power, series | NYISO N.Y.C. RT mean, 2026-09-20 local | 40.6518 | yes | answered | 3 | 0.0375 |
| q06 | power, series | ERCOT HB_WEST RT median, 2026-09-01 to 24 | 32.185 | yes | answered | 1 | 0.0106 |
| q07 | power, series | HB_WEST intervals at or below 0, 2025 | 2724 | **no** | not_in_warehouse | 2 | 0.0265 |
| q08 | power, derived | HB_HUBAVG RT P99.9, 2025 | 311.8005 | **no** | not_in_warehouse | 3 | 0.0261 |
| q09 | power, series | ISO-NE hub DA average, 2026-09-24 local | 33.6487 | yes | answered | 4 | 0.0623 |
| q10 | power, series | MISO Indiana hub RT hourly max, 2026-09-23 EST | 57.87 | yes | answered | 4 | 0.0622 |
| q11 | power, series | SPP North hub DA min, 2026-09-15 to 24 | 3.6304 | yes | answered | 3 | 0.0227 |
| q12 | power, derived | HB_HUBAVG peak-block median, August 2023 | 131.75 | yes | answered | 4 | 0.0779 |
| q13 | power, series | US48 peak hourly demand, 2026-09-01 to 24 | 735095 | yes | answered | 3 | 0.0212 |
| q14 | power, series | ERCOT solar, sum of 24 hourly values, 2026-09-20 | 261586 | yes | answered | 3 | 0.0677 |
| q15 | power, series | CAISO average hourly demand, 2026-09-15 | 30210.875 | yes | answered | 3 | 0.0252 |
| q16 | gas, series | Henry Hub on 2026-09-15 | 2.97 | yes | answered | 2 | 0.0144 |
| q17 | oil, series | Brent (EIA) average, August 2026 | 91.076 | yes | answered | 3 | 0.0266 |
| q18 | gas, series | Highest Henry Hub price and its date | 30.72 (2026-01-23) | yes | answered | 2 | 0.0144 |
| q19 | products, series | Latest NY Harbor conventional regular gasoline | 3.551 | yes | answered | 3 | 0.0240 |
| q20 | oil, series | US commercial crude stocks, latest week | 426398 | yes | answered | 3 | 0.0273 |
| q21 | power, series | Texas residential retail price, July 2026 | 158.8 | yes | answered | 3 | 0.1480 |
| q22 | oil, series | US crude imports from Canada, June 2026 | 4112 | yes | answered | 3 | 0.0468 |
| q23 | oil, series | WTI minimum, 2026-09-01 to 24 | 91.48 | yes | answered | 3 | 0.0274 |
| q24 | power, entities | Operating gas generators in Texas: count, nameplate MW | 1293, 84133.4 | yes | answered | 4 | 0.0821 |
| q25 | power, entities | Planned solar nameplate MW | 122381.4 | yes | answered | 3 | 0.0809 |
| q26 | power, entities | ERCOT queue: active projects, total MW | 1198, 301059.16 | yes | answered | 3 | 0.0443 |
| q27 | news, events | News stories dated 2026-09-25 | 559 | yes | answered | 2 | 0.0125 |
| q28 | capacity, series (internal) | PJM RTO capacity price, 2025/2026 | 269.92, "internal" | yes | answered | 3 | 0.0222 |
| q29 | none | PJM Western Hub RT LMP | not in the warehouse | yes | not_in_warehouse | 1 | 0.0124 |
| q30 | none | Lithium carbonate spot price | not in the warehouse | yes | not_in_warehouse | 2 | 0.0140 |

### Failure cases, verbatim

**q03** (refused by the post-check; the model's numbers were right).

Question: "What was the ERCOT HB_HUBAVG peak-block (16:00 to 21:00) interquartile range of real-time prices in 2015, and in 2025?" Expected 7.64 and 34.12.

The model's calls:
1. `list_tables {"iso": "ERCOT"}`
2. `describe_table {"table": "ercot_peak_premium_annual"}`
3. `query {"table": "ercot_peak_premium_annual", "aggregation": "latest", "entity": "ercot:HB_HUBAVG", "variable": "peak_iqr", "start": "2015-01-01", "end": "2016-01-01"}`
4. The same query for 2025.

First draft, rejected for the numbers 20, 59 and 15:
> For ERCOT hub HB_HUBAVG, the peak-block (local hours 16:00–20:59, i.e. interval starts 16:00 to 21:00) real-time price interquartile range (Q3–Q1) was 7.64 USD/MWh in 2015 and 34.12 USD/MWh in 2025 (ercot_peak_premium_annual, a derived table built from ERCOT's 15-minute real-time settlement point prices).

Second draft, rejected for the number 15:
> For ERCOT hub HB_HUBAVG, the peak-block real-time price interquartile range (Q3−Q1, defined as local hour of interval start 16 to 21) was 7.64 USD/MWh in 2015 and 34.12 USD/MWh in 2025 (ercot_peak_premium_annual, a derived table built from ERCOT's 15-minute real-time settlement point prices).

Final answer:
> I cannot give an answer I can verify: the numbers in my draft could not all be traced to a warehouse query. Try asking for one value, one table and one period at a time.

**q07** (wrongly "not in the warehouse").

Question: "How many 15-minute real-time intervals at ERCOT HB_WEST had a price at or below zero in 2025 (ERCOT operating year)?" Expected 2724.

The model's calls:
1. `describe_table {"table": "ercot_rtm_hub_prices"}`
2. `query {"table": "ercot_rtm_hub_prices", "aggregation": "count", "entity": "ercot:HB_WEST", "start": "2025-01-01", "end": "2026-01-01"}`

Answer:
> Not in the warehouse: the ercot_rtm_hub_prices table (ERCOT real-time settlement point prices, HB_WEST included) only covers 2026-08-26 through 2026-09-25 UTC, with zero rows for calendar/operating year 2025, so the count of non-positive 15-minute intervals for 2025 cannot be computed from ERW data.

**q08** (wrongly "not in the warehouse").

Question: "What was the 99.9th percentile of ERCOT HB_HUBAVG real-time prices in 2025?" Expected 311.8005.

The model's calls:
1. `query {"table": "ercot_rtm_hub_prices", "aggregation": "percentile", "entity": "HB_HUBAVG", "percentile": 99.9, "start": "2025-01-01", "end": "2026-01-01"}`
2. `describe_table {"table": "ercot_rtm_hub_prices"}`
3. `query {"table": "ercot_rtm_hub_prices", "aggregation": "count", "entity": "HB_HUBAVG"}`

Answer:
> Not in the warehouse: the ercot_rtm_hub_prices table (which holds ERCOT HB_HUBAVG real-time settlement point prices) only spans 2026-08-26 to 2026-09-25 UTC, so it contains no data for 2025 and the requested percentile cannot be computed.

**What the failures show:**
- **q07 and q08 are model errors.** Both answers are wrong: the 2025 history is in `ercot_rtm_hub_prices_2025`, and in `ercot_peak_premium_annual` (`n_negative`, `all_p999`).
  - Neither run called `list_tables`, so the model never saw the yearly history tables.
  - `package/llms.txt`, the model's briefing, recommends `ercot_rtm_hub_prices` and does not mention the yearly tables or the derived tables. The briefing is out of date on this point (open question 1).
  - The refusals are at least honest: no number was invented.
- **q03 is the post-check working as specified, at a cost.** The two numbers asked for were correct and cited. The model added its own numbers ("20:59", "15-minute") that no tool result holds, and the check does not tell a descriptive number from a data value.
- **The other 6 retries passed on the second draft.** What the check caught:
  - q21: a cents/kWh conversion the model computed itself;
  - q09 and q10: UTC offsets it worked out;
  - q02 and q14: "15-minute" and "23" in descriptions;
  - q29: "EIA-930", a form name, read as the number 930.
- **Some flags are real catches and some are false positives:** q21, q09 and q10 were real catches of numbers not fetched; q02, q14 and q29 were false positives on descriptive text.

**Bugs fixed after seeing results: none.** One change was made after the run, and it is not a scoring change: `ask.py` and the site route now replace em dashes in model text with " - " (as `warehouse/news/score.py` does), because the repository allows no em dashes. The run's records hold model text as JSON escape sequences (backslash, u, 2014), not em dash characters, so they were left as written.

## Task 4: `/ask` on the site

**The route.** `site/app/api/ask/route.ts` takes `POST {"question": "..."}`. It is read-only and runs on the server only (`runtime` nodejs, `maxDuration` 120). It calls `lib/chat/ask.ts`, reads `ANTHROPIC_API_KEY` from the environment, and gets its data through the Supabase anon key, so public rows only.
- **Input checks:** questions over 500 characters are rejected.
- **Rate limit:** 10 questions per IP per hour.

**The same loop in TypeScript.** The Python loop cannot run in a Vercel Next.js route, so the loop is ported:
- **Shared definition:** `lib/chat/spec.json` holds the system prompt, tool schemas, answer schema, limits, retry message and prices. `python warehouse/chat/ask.py --export-spec site/lib/chat/spec.json` writes it, so the prompt and tools have one source.
- **The port:** `lib/chat/ask.ts` ports the loop and the number check line for line.
- **The tools:** `lib/chat/tools.ts` implements the four tools over PostgREST with the same aggregations. It filters on the server, including on `extra->>column` for entities.
- **Differences from Python:**
  - the site sees the live set only (public tables; the last 90 days of power prices and demand);
  - `describe_table` lists text-column values from a 2,000-row sample, without counts;
  - the data version reads "Supabase live set (public site); table last run ...".

**The page.** `/ask` is a question box, the answer, and the citations (table linked to `/data`, source report, data version), in the site's design. "Ask" is in the nav.

**Checked locally,** against the production build:

| Question (through `/api/ask`) | Answer | Pandas expected | Calls | Cost (USD) |
|---|---|---|---|---|
| Henry Hub on 2026-09-15 | 2.97 USD/MMBtu, cites `eia_fuel_spot_prices` | 2.97 | 3 | 0.0194 |
| Operating gas generators in Texas | 1,293 and 84,133.4 MW, cites `eia860m_operating_generators` | 1293, 84133.4 | 4 | 0.0680 |
| PJM Western Hub real-time LMP | not in the warehouse | refusal | 1 | 0.0123 |
| HB_WEST median, 2026-09-01 to 24 (from the page, screenshot) | 32.18 USD/MWh, cites `ercot_rtm_hub_prices` | 32.185 | 1 | 0.0164 |

**Rate limit.** Ten requests from one IP were accepted. The eleventh got `HTTP 429` with `Retry-After: 3590`, and another IP was unaffected.

**Screenshots:** `site/screenshots/ask-desktop.png`, `ask-mobile.png` and `ask-answer-desktop.png` (after a real question). The session 11 screenshots were taken before "Ask" was added to the nav.

## Decisions

1. **Tool arguments beyond the prompt's outline.** The outline's `query` has no way to filter an entities table by column: the eval's own example, "operating gas generators in Texas", needs one. It also groups by day only in UTC, which splits ISO operating days. So I added:
   - `where` (exact match on the table's own columns only);
   - `value_column`;
   - `tz`;
   - grouping by a text column.
   None of them is free-form.
2. **Numbers allowed from the question and from tool arguments.** "The 99.9th percentile", or a date the user gave, is not a fetched fact, and refusing it would refuse every restatement of the question.
3. **Signs may be stated in words.** A result of -3.2 may be written "fell by 3.2".
4. **The site's loop is a TypeScript port with a shared definition,** not a call into Python (see Task 4).
5. **The rate limit is kept in memory, per server instance.** A durable limit needs a store the anon key can write, and the route was to be read-only. On Vercel the limit is therefore per instance, which `site/README.md` says.
6. **The evaluation date is fixed** (2026-09-26), so relative questions ("yesterday") have one right answer as the tables grow.

## Errors hit

1. **A reader crash, not a harness error.** My ad hoc reader of the eval records crashed on a Unicode minus sign under the Windows code page, and was rerun with UTF-8 output.
2. **A literal em dash in source.** Writing the `nodash` helper through a heredoc put a literal em dash into `ask.py`. It now uses `chr(0x2014)`, and a search finds no em dash in any new file.

## Rerun

```bash
python warehouse/chat/ask.py "What was the Henry Hub spot price on 2026-09-15?"
python warehouse/chat/eval/expected.py        # rebuild questions.yaml from the CSVs
python warehouse/chat/eval/eval.py            # about USD 1.30 for all 30
python warehouse/chat/ask.py --export-spec site/lib/chat/spec.json
cd site && npm run build && npm start         # then POST /api/ask, or open /ask
```

## Open questions for the human

1. **`package/llms.txt` is out of date,** and it is the model's briefing. It says the ERW holds six ISOs' prices, EIA-930 and three fuel prices. It does not mention:
   - the ERCOT history from 2015 or the peak-premium tables (q07 and q08 failed on this);
   - the EIA-860M and queue entities;
   - the monthly EIA series.
   Updating it is a documentation fix, not tuning on the eval. I left it for a human decision so that this run's results stay a clean baseline.
2. **Should the post-check ignore descriptive numbers?** It cost one correct answer (q03) and 3 other needless retries (q02, q14, q29). Candidates are time-of-day ranges, "15-minute", and form names like "EIA-930". A narrower check, applied only to numbers followed by a unit or in the result position, would be a v1 design change. It should be evaluated on a new question set, not this one.
3. **Vercel:** add `ANTHROPIC_API_KEY` as a third environment variable for `/ask` (see `site/README.md`). Consider a key with a spending limit: the route is public and in-memory rate limiting is per instance.
4. **Carried over from session 11:**
   - `VACUUM FULL` on Supabase (the database is still 339 MB, over the loader's 300 MB guard);
   - the first Redivis release;
   - the CAISO `lmp_rtm_5min` label.
