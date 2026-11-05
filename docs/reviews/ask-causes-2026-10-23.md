# Ask's thirteen wrong answers, sorted by where the fix lives (23 October 2026)

Energy Research Warehouse (ERW), session 1108 (chain 075, the old laptop, unattended). No model call, no database read: this note reads session 320's stored run (`warehouse/chat/eval/eval_s320_first_run.json`), session 539's regrade (`warehouse/chat/eval/eval_s539_regrade.json`, `docs/reviews/ask-thirty-2026-10-21.md`) and the local server's log of the run (`runs/chain_oct19/s320/server.out`, not in git: the number check's twelve findings on first drafts).

Each cause goes in one of three places:

- **code:** a tool returns the wrong rows, the number check lets a wrong figure through or stops a right one, the loop stops early, a unit or a window is misread. Fixed by this chain.
- **hold:** the license rule refuses, correctly (Samuel's ruling of 12 October; held rows since 21 October). The answer's wording is this chain's (session 1112); the rule is not.
- **ruling:** one of session 320's three open items (`archive/sessions/SESSION_320_REPORT.md`, "For Samuel's ruling"). This chain may prepare the change behind a switch that is off, so a ruling is one line; it does not turn it on.

## The result in one line

Of the thirteen wrong answers, **none has its cause in the code alone**: 8 wait for ruling 1 (USD per kW), 3 for ruling 2 (the keys' tolerance), 2 for ruling 3 (the keys' tables). Four more questions (g07, g08, d05, d07) are held. What the code does hold are four faults the stored run shows on the way to its answers, none of which made a final answer wrong: a form name read as a figure (4 first drafts sent back), the eight-call limit reached (11 answers), the tool calls not recorded (30 answers), and the loop's cost on a one-figure question (b01: 8 calls and a retry for one sum).

## The thirteen, and the four held

| Id | Asked | Wrong because | Place | Where a fix would live | The fixture that proves it |
|---|---|---|---|---|---|
| b01 | ERCOT 4h foresight, total, 2025-10 to 2026-09, USD per kW | The tables hold USD per MW; the answer gives 81,402.19 USD per MW and refuses the conversion, as its rule says | ruling 1 | `site/lib/chat/tools.ts` `query` (a per-kW column beside the per-MW one where `docs/methods/battery_stack.md` names the conversion), or `unverified()` in `site/lib/chat/ask.ts` and `warehouse/chat/ask.py` (a figure that is a returned one divided by 1,000) | the stored answer and key 81.4022 (`eval_s320_first_run.json`, b01) |
| b02 | the same, energy part | as b01 (54,598.58 USD per MW) | ruling 1 | as b01 | b02, key 54.5986 |
| b03 | the same, ancillary part | as b01 (26,803.61) | ruling 1 | as b01 | b03, key 26.8036 |
| b04 | ERCOT 2h day-ahead, total | as b01 (51,067.14) | ruling 1 | as b01 | b04, key 51.0671 |
| b05 | ERCOT 4h foresight, 2021 | as b01 (3,430,556.56) | ruling 1 | as b01 | b05, key 3,430.5566 |
| b06 | ERCOT 4h foresight, 2025 | as b01 (87,439.61) | ruling 1 | as b01 | b06, key 87.4396 |
| b08 | CAISO SP15 4h foresight, 2025-10 to 2026-09 | as b01 (79,308.31); the key of 19 October was also stale (79.046 then, 79.3083 now) | ruling 1 | as b01; the keys computed the same hour as the asking (session 1113) | b08, key now 79.3083 (`eval_s539_keys.json`) |
| b09 | CAISO SP15 4h day-ahead, energy, 2025 | as b08 (42,503.77, 3 days left out, which is the table's) | ruling 1 | as b08 | b09, key now 42.5038 |
| g03 | ERCOT peaker margin, 2025 | "about 50,424 USD/MW" against 50,424.0741 with an absolute tolerance of 0.01 | ruling 2 | `warehouse/chat/eval/eval_s267.py` `matches()` (a relative tolerance, or a whole-number answer accepted for a key of 1,000 or more) | g03's stored answer |
| g06 | SPP North wind revenue, 2025 | as g03 ("about 66,963") | ruling 2 | as g03 | g06 |
| g09 | ERCOT generator-rule battery, energy | as g03 ("about 58,534") | ruling 2 | as g03 | g09 |
| g08 | NYISO N.Y.C. flat real-time price, July 2026 | right figure (73.87) cited from `cost_of_power_monthly`; the key accepts `merchant_revenue_monthly` only; held since 21 October | ruling 3, and hold | `questions_s320.yaml` g08 `tables`; `eval_s267.py` `grade()` | g08 |
| d10 | PJM Western hub, August 2026 (must refuse) | right refusal that cites no table; the key grades a refusal on a cited table | ruling 3 | `eval_s267.py` `grade()` (a refusal graded on the refusal and the absence of a figure) | d10 |
| g07 | ISO-NE solar capture price, August 2026 | right on 20 October; the rows are held since 21 October, so asked today the right answer is "license needed" | hold | the answer's wording only (session 1112): `site/lib/chat/tools.ts` (the held grid's result), `ask.ts` | g07's question with the held rows left out |
| d05 | NYISO N.Y.C. load-weighted real-time, January 2026 | as g07 | hold | as g07 | d05 |
| d07 | ISO-NE day-ahead shape premium, June 2026 | as g07 | hold | as g07 | d07 |

## What the code does hold: four faults on the way, in order of how many questions each touches

| # | Fault | Questions | Where it lives | The fixture that proves the fix | Session |
|---|---|---|---|---|---|
| 1 | The tool calls are not recorded in an evaluation (`trace` is null on all 30: `ASK_RECORD_TOOLS` was not set), so no regrade can read what a tool returned | 30 | `site/lib/chat/ask.ts` (the `tracing` switch), `warehouse/chat/eval/eval.py` | an evaluation run's records carry `trace`; the site's default stays off (a test of both) | 1111 |
| 2 | The eight-call limit reached: the loop answered on its last call or was told "tool call limit (8) reached; answer now" | 11: b01, b07, b08, g03, g04, g08, g09, g10, d03, d04, d10 | `MAX_TOOL_CALLS` in `warehouse/chat/ask.py`, `max_tool_calls` in `site/lib/chat/spec.json` (exported), the loop in `ask.ts` | the stored counts: the limit set from them, and a fixture loop that needs nine calls answers | 1111 |
| 3 | A form name read as a figure: "EIA-930" gives the number 930, which no tool returned, so the first draft is sent back | 4 first drafts: d01, d02, d05, d08 (the log's four `930`) | `numbers()` in `warehouse/chat/ask.py` and `site/lib/chat/ask.ts` (the hyphen after a letter is not a minus and the code after it is a name) | "EIA-930", "Form 860", "EIA-923" give no number; "fell -3.2", "(-3.2)" still do; both languages on the same strings | 1110 |
| 4 | One figure, eight calls: b01 is one sum over twelve months of one variable, and took 8 calls and a retry (USD 0.17, 32 seconds; half the thirty took 5 calls or fewer) | b01 (and b08: 8 calls, retried) | the tools' description of `query` with `aggregation: sum` and a window, in `warehouse/chat/tools.py` and `site/lib/chat/tools.ts`; no trace says which calls were spent | a tool test: one `query` call on saved `battery_stack_monthly` rows returns the twelve-month sum and its months; the call count is read in session 1113's run, which records the trace | 1109 |

The `1000` of the eight per-kW first drafts is not a fault: the number check stopped a conversion no tool returned, which is the rule. It stays until ruling 1.

## What sessions 1109 to 1112 take

- **1109, the tools:** fault 4, and every tool result of the thirty checked for the wrong table, the window off by a day or a timezone, a unit mixed and an entity that does not resolve, on saved rows, no model; ruling 1's change prepared in the tool behind a switch that is off (`ASK_PER_KW`, default off), so the eight become right in the grader's offline replay only when the switch is on.
- **1110, the number check:** fault 3; the check made exact on units (a figure and its unit must match a returned figure and unit), retried once with the mismatch named, then refused with "the warehouse does not hold that figure"; six fixtures.
- **1111, the loop:** faults 1 and 2; a refusal that says why in one sentence.
- **1112, the held grids:** g07, g08, d05, d07: the grid named, its rows held for a license, the public grids' figure in the same shape.

Rulings 2 and 3 are the evaluation's keys, not the loop: they go to `docs/reviews/ask-board-rulings-2026-10-23.md` (session 1124) with a recommendation, and session 1113 grades its run both ways, as session 539 did.
