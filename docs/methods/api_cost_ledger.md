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
