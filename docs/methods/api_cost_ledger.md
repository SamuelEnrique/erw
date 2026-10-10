# API cost ledger: method

Built in session 30 (Part B1). The table `api_cost_ledger` records every call the ERW's code makes to the Anthropic Messages API: one row per call, written at the time of the call. It is **internal**: never on the public site, never in the public Redivis dataset.

## How a call is recorded

- Every script that calls a Claude model builds its client with `llm.client(step)` (`warehouse/llm.py`). That is the only construction of the Anthropic client in the warehouse's code; `grep` finds no other.
- The wrapper passes each `messages.create` call to the Anthropic SDK unchanged, then appends one row with the response's `usage` block.
- The site's `/ask` cannot write the table (it holds the anon key only). Its calls go to the Supabase table `site_api_calls` instead (migration 010, `site/lib/chat/ledger.ts`). The internal page reads both.

## Columns

Events shape (`docs/datastandard.md`), `event_type` `api_call`, `source` `anthropic:messages-usage`, then:

| Column | Meaning |
|---|---|
| `run_id` | The run (`ERW_RUN_ID`, else the process start, `YYYYMMDDTHHMMSSZ`) |
| `session` | The Claude Code session number (`ERW_SESSION`), else `daily` on GitHub and `local` elsewhere |
| `step` | What made the call: `news_score`, `news_score_shadow`, `digest`, `roundup`, `deals_extract`, `datacenters_extract`, `policy_score`, `policy_reads`, `funfact`, `analysis_note`, `chat`, `thesis`, and so on |
| `model` | The model that answered, as the response names it |
| `input_tokens` | Uncached input tokens |
| `cached_input_tokens` | Input tokens read from the prompt cache |
| `cache_write_tokens` | Input tokens written to the prompt cache |
| `output_tokens` | Output tokens |
| `web_searches` | Web search tool uses (the Thesis Builder) |
| `usd` | The cost, computed as below; empty when the model has no configured price |
| `ts_utc` | When the call returned |
| `prices_as_of` | The date of the price table used |
| `request_id` | Anthropic's request id |

## The cost

`usd = (input x input price + output x output price + cache reads x cache read price + cache writes x cache write price) / 1,000,000 + web searches x (USD 10 / 1,000)`.

- Prices per million tokens are in `warehouse/config/model_prices.yaml`, the one place they live, with their date.
- A 5-minute cache write costs 1.25 times the input price, a 1-hour write 2 times; a cache read costs 0.1 times (0.05 on Claude Opus 5.5, 0.025 on Claude Fable 5.1).
- The token counts are Anthropic's own, per call. The dollars are the ERW's arithmetic on them at list prices, which is why the table's tier is `derived`: a check against Anthropic's invoice, not a copy of it.

## The spend cap

With `ERW_SPEND_CAP_USD` and `ERW_SESSION` set, the wrapper sums the ledger's `usd` for that session before every call and refuses the call once the sum reaches the cap. A session's model work therefore stops at its cap, whatever script it runs.

## Where it goes

- `warehouse/output/api_cost_ledger.csv`, merged by `event_id` (the request id).
- The archive, Redivis (internal dataset) and Supabase (license internal), like every internal table.
- `/internal/costs` on the site: spend per day, per step and per model over the last 30 days, and the projected monthly bill (the mean daily spend of the last 7 days times 30). No link reaches it; it answers 404 without the token `INTERNAL_COSTS_TOKEN`, and the database function behind it (`internal_costs`) answers nothing without the same token.

## The daily cap for scheduled model steps (session 176)

`DAILY_MODEL_USD`, default 1.00, is one cap for all the model steps that run on a clock, together: news scoring, the Haiku shadow scorer, policy scoring and reads, deals and datacenter extraction, the fun fact, the digest, the Roundup and its chart's note (`SCHEDULED_MODEL_STEPS` in `warehouse/health.py`). It is a repository variable on GitHub (Settings, Variables, `DAILY_MODEL_USD`); unset or empty means 1.00, and 0 means no scheduled model step runs.

- **Where it is enforced.** `python warehouse/health.py budget --step <name>` is asked before each model step: by `model_step` in `warehouse/run_daily.sh`, and by the Roundup's workflow before the chart's note and before the Roundup.
- **What is counted.** The day's (UTC) `usd` of the ledger's rows whose `step` is one of the scheduled steps and whose `session` is this run's (`daily` on GitHub). The ledger on the machine and Supabase's copy of it (`events`, `table_name` `api_cost_ledger`) are joined by `event_id`, so the Roundup's runner counts what the daily run spent the same day once the loader has carried it. A session's work, the Thesis Builder and the site's own ledger are not counted and not capped here (the site has its own daily ceiling, migration 023).
- **At the cap.** The step is not run. A row of `erw_health` says so (status `skipped`, the reason beginning "daily model cap reached: USD x spent today ... of USD y (DAILY_MODEL_USD)"), the job log carries a warning, the next day's health summary lists it under "Skips, by reason", and the same-day email (`health.py alert`) says "The daily model cap reached: ... N model steps not run (names)".
- **The digest and the Roundup still publish.** At the cap they are written with `--no-model`: each headline is the lead story's own title as its publisher wrote it, the model-written summary of the numbers is left out, the chart's note is the template's own sentences, and one line under the title says so. Everything computed from the warehouse (the numbers, the tables, the policy lines, the sources) is as on any day.
- **The check is before a step, not before a call.** A step that starts under the cap runs to its end, so a day can end above the cap by that step's cost (news scoring alone costs about USD 1.10 a run at October 2026 volumes).
- **A budget that cannot be read never switches a step off.** The step runs, and a failed row of `erw_health` ("model budget") says the budget could not be read, which the same-day email carries.
