# Ask the warehouse: method

`warehouse/chat/` (the loop and its tools in Python, `ask.py`, `tools.py`), `site/lib/chat/` (the same in TypeScript for the site's `/api/ask`), the Ask panel `site/components/ask/AskPanel.tsx`. The account of how it was built, session by session, is `warehouse/chat/README.md`; Ask ERCOT's own rules are [`ask_ercot.md`](ask_ercot.md) and the spending ceilings [`ask_limits.md`](ask_limits.md). This note states the rules an answer is held to as they stand after the chain of 23 October 2026 (sessions 1108 to 1125), each dated.

## The rule

The AI layer never states a number it did not fetch. Every figure in an answer must be a figure a tool returned in that turn, at the precision the answer writes it or a coarser one (a result of 25.1834 may be written 25.18 or 25.2); every cited table must be one a tool read. A draft that fails is sent back once with what failed named; a second failure is refused.

## The tools

| Tool | What it returns |
|---|---|
| `list_tables` | every table with its sector, license, grid, interval, first and last time, rows and source report |
| `describe_table` | a table's shape, columns, entities, variables, units, span, source reports and license |
| `query` | one aggregation (`latest`, `mean`, `median`, `min`, `max`, `percentile`, `count`, `sum`) of a table's rows, filtered by entity, variable, window and the table's own columns, grouped by time, entity or a text column |
| `compare` | two queries side by side, with the difference and the ratio |
| `board_rank` (23 October 2026, session 1122) | every hub's newest value of one of the price board's measures (`price_board_latest`, `price_board_spreads`), ranked highest, lowest or by the size of the move, each value with its own date; it is `query` (latest by entity) and a sort, so it agrees with the board's tables |

A grid's scoped chat reads the tables the rule of session 314 finds for the grid (`docs/grids/grid_tables.json`) and the grid's rows only.

## The checks on every draft (23 October 2026)

- **Numbers** (session 20 on): every number of the answer is in a tool result, the question or a tool argument, at the answer's precision. Digits after a letter and a hyphen are a name, not a figure: EIA-930, EIA-860M, COVID-19 (session 1110; session 320's run sent four right drafts back for the 930 of EIA-930).
- **Money units** (session 1110): a figure written with a money unit (USD per MWh, per MW, per kW, per kWh, with USD, US dollars, dollars or a dollar sign) must match a returned figure in that unit. A tool number's unit is its own key's (`..._usd_per_mw`, `value_usd_per_kw`), else the nearest `unit` or single `units` above it. A draft is sent back only when every returned number it matches is in another unit (81,402.19 written as USD per kW when the tool gave USD/MW). A number no result places in a unit, a result over mixed units, a unit with no money and a compound unit (MWh per MW, USD per MW-month) are not judged by this check.
- **Citations**: every cited table was read; an empty or uncited answer is sent back ("not in the warehouse" needs no citation).

## The refusal (23 October 2026)

After the second failure the answer is: "The warehouse does not hold that figure: the numbers in my draft could not all be traced to a warehouse query. Try asking for one value, one table and one period at a time." (session 1110), and one sentence saying why with no figure in it, for example "Why: the draft was checked twice and a figure in it was in no tool result." (session 1111). The untraced figure is never shown to the reader. The panel heads such an answer "The warehouse does not hold that figure" (session 1115).

## The limits (23 October 2026)

- **At most 12 tool calls** a question (8 until session 1111: 11 of session 320's thirty used all 8). The route's time limit is 120 seconds.
- **The tool calls and their results are recorded** in every answer of an evaluation (a request admitted by its header and the server's `ASK_EVAL_TOKEN`, session 314), and in none of a visitor's (session 1111). `warehouse/chat/eval/eval.py` asks with the record on.

## A held grid (23 October 2026, session 1112)

The rows of ISO-NE, NYISO and MISO in the tables the status file holds by grid (`site/data/license_status.json`; the owner's ruling of 12 October 2026) are never read for an answer. A query that asks for a held grid's rows, by its entity or, with none, by the chat's own grid, returns no figure of it: the grid named, "its rows are held for a license: license needed", the hold's words, and the same query's figure for each public grid of the table (one read by entity), so the answer can say what the warehouse does hold in the same sentence: "NYISO's rows are held for a license (license needed). For the public grids, the flat price in July 2026: ERCOT 29.17 USD/MWh, CAISO 39.43 USD/MWh, SPP 53.79 USD/MWh (merchant_revenue_monthly)." The hold itself is unchanged by this. MISO's rows are also paused (its own message stands first).

## What an answer shows (23 October 2026, session 1115)

Under the answer and its sources, one line for each query or compare it read: the table, the entity, the variable, the window (the end not included) and the aggregation, never a figure; and how long it took, with how many reads of the warehouse.

## Prepared and off

- **USD per kW** (session 1109, for session 320's open ruling 1): with `ASK_PER_KW=on` a query of `battery_stack_monthly` whose rows are all USD/MW carries each value divided by 1,000 as `value_usd_per_kw`, the method note's own conversion (`battery_stack.md`), so the number check traces a per-kW figure. Off by default: every result is what it was.

## The evaluations

| Set | Questions | Keys | Runs |
|---|---|---|---|
| `questions_s320.yaml` | 30 on the three economics pages | computed from the live set before any model call; again by `eval_s1113.py --keys` the hour of an asking | 17 of 30 (20 October 2026), 14 of 30 under the hold (session 539); session 1113, below |
| `questions_s1114.yaml` | 30 a trading, an infrastructure-finance and a policy lead would ask, ERCOT, CAISO, SPP and national series only | `expected_s1114.py`, from the live set the hour of the asking | session 1114, below |
| `questions_s1122.yaml` | 5 on the price board | `expected_s1122.py`, from recorded rows of the board's tables | not yet asked |

`python warehouse/chat/eval/eval_s1113.py --keys`, then `--ask --base <a local server> --cap <USD>` (with `--set s1114` for the second set), then `--grade`: the asking runs through the site's route as an evaluation, under its own ledger step, the spend checked before each question.

All of it as one command (23 October 2026, session 1128): `python warehouse/chat/eval/run_eval.py --set s320 --cap 6` (or `--set s1114`, `--only t01,t02`), whose steps are, in order: the database probe, at least 3 GB of memory free, the build lock (waited for at most 20 minutes), a production build with the reads timed, the build served with the visitor salt and the evaluation's ceiling raised by the cap for that server only, the keys from the live set, the asking, the grading, the server stopped by its process id and the lock released whatever happened. `--dry-run` prints them and starts nothing.

## Decisions

Each dated, with the session that made it; the reports in `archive/sessions/` carry the reasons.

- 23 October 2026, session 1110: the unit check judges money units only, and only when every matching number is placed in another unit.
- 23 October 2026, session 1111: 12 tool calls, not a measured number (the stored run cannot say what a question needs past 8).
- 23 October 2026, session 1112: a held grid's question is answered with the public grids' figures, not refused.
- 23 October 2026, session 1122: the board's questions are answered from the board's derived tables, the tables the live set holds.
