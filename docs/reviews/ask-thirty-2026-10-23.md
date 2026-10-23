# Ask's thirty questions, asked again (23 October 2026)

Energy Research Warehouse (ERW), session 1113's asking, run by session 1126 (chain 076, the old laptop, unattended) on a local production build of chain 075's branch (`wip/1128-ask` merged with main, then `wip/1126-ask` with two fixes, below), through the site's `/api/ask` as an evaluation (the header `x-erw-ask-eval`, the ledger step `site_ask_eval`), each question as its page sends it. The keys of session 320's thirty (`questions_s320.yaml`) were computed again from the live set at 19:29 UTC (`eval_s1113_keys.json`; all equal to session 539's of 21 October within their tolerance). Asked from 19:29 to 19:41 UTC (b01 first, alone, as a probe of the route and the ledger); g08 and g10 again at 19:43 after the fixes. Cost USD 2.76 for the thirty as graded (USD 2.88 in the step's ledger today, the probe and the first g08 and g10 included). The answers, with every tool call and result: `warehouse/chat/eval/eval_s1113_run.json`; the grades: `eval_s1113_grades.json` (`python warehouse/chat/eval/eval_s1113.py --grade`).

## The result

| | Right |
|---|---|
| Session 320, 20 October 2026, on its keys | 17 of 30 |
| Session 539, the same answers graded under the license hold of 21 October | 14 of 30 |
| **This run, graded under the hold** (a held grid's question right when the answer says "license needed", names the grid and states no figure of it) | **19 of 30** |
| This run, on the figure keys alone (the four held questions counted wrong) | 15 of 30 |
| This run, if session 320's three open rulings went the answers' way (informative; nothing is ruled) | 30 of 30 |

## Question by question

| Id | 320 | 539, under the hold | Now, under the hold | Calls | Why wrong now |
|---|---|---|---|---|---|
| b01 to b06, b08 | wrong | wrong | wrong | 5 to 12 | Asked in USD per kW; the answer gives the table's USD per MW, the key times 1,000, and says it cannot convert (ruling 1; `ASK_PER_KW` is off) |
| b09 | wrong | wrong | wrong | 8 | as b01 |
| b07, b10 | right | right | right | 12, 3 | |
| g01, g02, g04, g05 | right | right | right | 4 to 12 | |
| g03, g06 | wrong | wrong | wrong | 12, 11 | "about 50,424" and "about 66,963" against an absolute tolerance of 0.01 (ruling 2) |
| g07 | right | wrong | **right** | 10 | ISO-NE held: the answer names the grid, says "license needed", gives no ISO-NE figure (session 1112) |
| g08 | wrong | wrong | **right** | 3 | NYISO held, said as g07; the first asking crashed (below, fix 1) |
| g09 | wrong | wrong | **right** | 7 | this asking wrote the figure to the cent |
| g10 | right | right | right | 9 | MISO: refused, "paused while terms are reviewed" (the first asking answered as a held grid: below, fix 2) |
| d01 to d04, d06, d08, d09 | right | right | right | 3 to 12 | |
| d05, d07 | right | wrong | **right** | 9, 2 | NYISO and ISO-NE held, said as g07 |
| d10 | wrong | wrong | wrong | 1 | PJM: a right refusal that cites no table; the key grades a refusal on a cited table (ruling 3) |

## What the run found, and fixed the same hour (session 1126)

1. **A compare naming a held grid crashed the loop** (g08, first asking: HTTP 502, "Cannot read properties of undefined (reading 'length')"). Session 1112's held-grid answer has no `result`; `compare` read the length of each side's. It now makes no difference or ratio with a held side and returns both sides (`site/lib/chat/tools.ts`, test `site/scripts/test-ask-1126.mjs`).
2. **MISO's scoped chat answered as a held grid** (g10, first asking: "held for a license", no figure, but not a refusal). MISO's pause says more than its license: a question of MISO's rows is now refused with the pause's words before the held-grid answer is reached.

## The loop, measured

- **Tool calls**: 1 to 12, median 7.5; six answers used all 12 (b05, b07, g03, g04, d04, d08). The limit of 12 (session 1111) was reached by six of thirty where 8 was by eleven; of the six, b05 and g03 are wrong, for their rulings, not for the limit.
- **Time**: 4 to 40 seconds, median 22.9.
- **Retries**: 7 (b01 to b06 and b08, the per-kW questions, each sent back once; none for a form name such as EIA-930, which session 320's run sent back four times).

## What would change the rest

The eleven still wrong are all session 320's open rulings (`docs/reviews/ask-board-rulings-2026-10-23.md`, items 1 to 3): eight wait on USD per kW (turning `ASK_PER_KW` on), two on the tolerance of large figures, one on how a refusal is graded. With them, 30 of 30.
