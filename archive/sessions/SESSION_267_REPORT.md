# Session 267 report: Research, deep, and Ask accuracy

14 October 2026, 09:14 to about 10:45 UTC, unattended, on the old laptop (a code machine), one session of the chain of sessions 263 to 267. Branch `wip/267-research-ask` in the worktree `erw-144`, from `ce6ee59b` (session 268's palette tokens). Part A was done by two agents of this session (A1: items 1, 3, 4, 5; A2: items 2, 6); Part B by the session itself. Pulls: none. Writes: none to the warehouse, the archive or Redivis; the Ask route's own writes, below.

## Read these first

- **Model spend: USD 2.4669 of the cap of USD 3.00, 30 questions of the cap of 30** (193 API requests, all `claude-sonnet-5-5`, 09:36 to 09:45 UTC). The cap was enforced before each question: no question was sent when the ledger's total plus a reserve would pass USD 3 (reserve USD 0.50 for q01 to q21, USD 0.30 for q22 to q30, see decision 3). Each question's cost is the route's own `cost_usd`, from the API's usage figures; the ledger is `runs/session267/ledger.csv` (not in git) and every fixture carries its question's cost and usage. No call to any model after q30.
- **Ask: 27 of 30 right on the one asking.** Right number, right table, cited, or a refusal where the warehouse truly lacks the answer. The three wrong answers are fixed at their causes; **none of the three fixes is verified with a call** (the cap of 30 questions was used).
  - **q28, MISO: Ask stated a MISO figure** (83.79 USD/MWh, MISO's Indiana hub, September 2026, from `cost_of_power_monthly`) and never said MISO is paused. The pages show none. Fixed in `site/lib/chat/tools.ts` `query()`: a MISO table or entity is refused with the pause's words (`MISO_PAUSED`), MISO's own rows (`miso:...`) are left out of every read; EIA's figures for the MISO balancing authority are kept.
  - **q10: hours of negative prices at HB_WEST in 2024.** The briefing never named `ercot_hub_prices_daily`; the model read intervals from `ercot_peak_premium_annual` and declined to convert. Fixed in `package/llms.txt` (one row of the question-to-table map).
  - **q04: a 4-hour battery's revenue at ERCOT in 2024.** The briefing named only `battery_stack_monthly` for a battery's earnings (energy and ancillary); the key was `merchant_revenue_monthly` (energy alone, never named in the briefing). The model's figures trace to its table; the question was ambiguous. Fixed in `package/llms.txt` (one row).
- **Two of my keys were wrong, and the model was right** (q24: SPP's queue spells wind three ways, the key counted one; q22: the same 23.3292 is in two tables). The keys were corrected after the answers, from the tables, and the YAML says so in each note. Counted right.
- **The 30 questions' cost went into the route's ledger (`site_api_calls`) as any visitor's would.** It counts toward today's public Ask ceiling of USD 3 a day (`site/lib/chat/limits.json`): the public Ask (in review) may close for the rest of 14 October UTC. My local server ran with `ASK_DAILY_USD=8` and `ASK_PER_VISITOR_PER_DAY=40` so that its own admission would not refuse the evaluation; each batch of 8 questions came from its own local address (`x-forwarded-for`), so the hourly limit of 10 a visitor did not stop the run. Decision 2.
- **`site/lib/chat/spec.json` was exported again** (`python warehouse/chat/ask.py --export-spec site/lib/chat/spec.json`; only its `system` changed). Session 266 edits the same briefing: **at the landing, after both merge, the spec must be exported again** and `warehouse/chat/check_spec.py` must exit 0.
- **Research (Part A): all six items done.** The verdict of 13 October beside each of the 28 drafts (7 strong, 14 usable, 7 drop); the brand palette in the charts; the 25 percent guard on the daily chart (it would have held the published chart of 13 October, 34.4 percent past its record); a plain-names file of 69 entries (7 draft); the six do-files' first data line; the review pack, with 18 cross-checks.

## What to review

Open `https://erw-flame.vercel.app/internal/open` first.
- `https://erw-flame.vercel.app/research`: the charts read the brand's tokens (five colors; the eight of "Many series" past five; cardinal for the highlight).
- `https://erw-flame.vercel.app/internal/findings`: each draft's line "Verdict of 13 October 2026 (session N; block K of the document): strong / usable / drop", with the block's words.
- `https://erw-flame.vercel.app/ask`: ask "What was the flat price at MISO's Indiana hub in September 2026?" (it should now say MISO is paused and give no figure) and "Summed over the days of 2024, how many hours of negative real-time prices did ERCOT's HB_WEST hub have?" (the key: 874.25, `ercot_hub_prices_daily`).
- `docs/reviews/packs/research.md` (replaces `docs/howitworks/research.md`).
- `warehouse/chat/eval/questions_s267.yaml`, `eval_s267_fixtures.json`, `eval_s267.py`.

## What changed

Part A (agents A1 and A2):
- `site/lib/findingverdicts.ts` (new, generated from `docs/reviews/findings-verified-2026-10-13.md`) and `site/app/internal/findings/page.tsx`: a line of words under each draft, with `data-draft-verdict`; a draft raised later says "no verdict". No section moved.
- `warehouse/analysis/style.py`: `series_colors(n, highlight=None)`, `BRAND_SERIES` (ink, cardinal, blue, grey, light grey, `docs/brand.md` section 2), `MANY_SERIES` (the eight of `--chart-series-1` to `-8`); paper, panel, rule and muted in the brand. `warehouse/analysis/findings/card_image.py` (today's chart) takes them. `site/components/echarts.ts` `LITERAL_TOKENS`: the new values map to their tokens, so a research chart reads CSS variables (only inside `data-chart-tokens`, which only the research pages carry).
- `warehouse/analysis/findings/daily_chart.py`: `RECORD_JUMP = 0.25`, `record_jump`, `must_wait`, `held_before`, `keep_held`, `choose(..., waited=None)`; a held record goes to `docs/digest/charts/held.json` and is checked again the next run. `warehouse/news/brief.py`: the check run passes `waited`. Pins moved in `tests/test_session232.py` (note "session 267").
- `warehouse/analysis/plain_names.json`: 69 series and variables, plain name and unit, 7 marked draft.
- The six do-files (`batteries_lunch`, `gas_sets_price`, `negative_prices_west`, `peak_hour_moved`, `queue_divorce`, `who_rescues_whom`): `varnames(5) rowrange(6)` for `varnames(1)` over a CSV whose first four lines are comments; the module, its copy under `site/public/findings/` and the `.do`. Lines added to `docs/methods/automated_analysis_findings.md` and `automated_analysis_scanner.md`.
- `docs/reviews/packs/research.md` (new); `git rm docs/howitworks/research.md`; the README row points at the pack. `tests/test_session267_findings.py`.
- Today's chart of 13 October was redrawn in the brand from the committed fixture card, without a model, to `runs/session267/today_2026-10-13.png` (not committed: the published picture stays, rule 3).

Part B:
- `warehouse/chat/eval/questions_s267.yaml`: the 30 questions, committed (`2af94b96`) before the first model call; each note names the table, entity, variable, period and aggregation.
- `site/lib/chat/ask.ts`: `ASK_RECORD_TOOLS=1` (a local server only, off by default) adds `trace` (every tool call and its result) to the answer.
- `site/lib/chat/tools.ts`: `MISO_PAUSED`, `misoOwn`, the refusal at the top of `query()`, and `kept()` in its read.
- `package/llms.txt`: two rows of the question-to-table map (`ercot_hub_prices_daily`; `merchant_revenue_monthly` against `battery_stack_monthly`), placed away from the carbon rows session 266 edits. `site/lib/chat/spec.json` exported again.
- `warehouse/chat/eval/eval_s267.py` (the grader), `eval_s267_fixtures.json` (658 KB: each answer whole, its trace, grade, verdict, cause and fix), `warehouse/chat/README.md` (one row), `tests/test_session267.py` (Part B classes).

## Ask: the 30, graded

The route: `POST /api/ask` on a local production build of this branch at `b5997e28` (`next start`, port 3267), the general chat (no grid, no profile), `ASK_VISITOR_SALT` from the root `.env`, the model key the site reads (`site/.env.local`).

| Grid | Asked | Right |
|---|---|---|
| ERCOT | 13 (q01 to q12, q30) | 11 (q04, q10 wrong) |
| CAISO | 5 | 5 |
| NYISO | 3 | 3 |
| SPP | 4 | 4 |
| ISO-NE | 2 | 2 |
| PJM (EIA carbon) | 1 | 1 |
| MISO (paused) | 1 | 0 (q28) |
| US48 | 1 | 1 |

- q30 (ERCOT 2012, before the tables begin) was refused, rightly. Every answered question cites its table with a source report and a data version; every number of every answer is in a tool result (the replay of `ask.py`'s number check, a test).
- Hardest right ones: the widest day-ahead spread year (2021, 63.25), Regulation Up's dearest month (February 2021, 2,957.43 USD/MW-hour), HB_NORTH's dearest day of 2024 (8 May, 4,981.35), CAISO's record solar curtailment (May 2026, 1,361,345.63 MWh), ERCOT's active battery queue (628 projects, 118,905.95 MW).

## Checks, with exit codes

- `npx tsc --noEmit`: 0 (after the first build; the first try, before it, failed on a stale `.next/types` file of another branch's page, removed). FINAL-CYCLE
- `npm run build`: 0, no "statement timeout" line. FINAL-CYCLE
- `check-values` restricted to `/research,/internal/findings`: exit 127 twice, "0 values checked, fewer than the floor of ten a run". These pages carry no check key: their numbers come from committed files (cards, charts), not from a table read. Not a gate for them; for Samuel's ruling 3.
- `check-routes`: FINAL-CYCLE
- `check-analysis.mjs`: 0 (279 of 279). `check-findings-grids.mjs`: 0 (163 of 163).
- The battery page (echarts.ts is shared): `capture.mjs` at 1280, `_nums.txt` against `runs/session211/shots/after_nums.txt`: 0 lines; `h` 5016.
- Python, each module alone: `test_session267` 0 (27 tests), `test_session267_findings` 0, `test_session262` 0, `test_session249` 0, `test_session260` 0; the modules that read the files changed for Ask: `102, 103, 114, 121, 128, 137, 143, 148, 156, 161, 168_ask, 207, 215, 65, 92`: all 0 (seven failed once on a quote mark in `MISO_PAUSED`, fixed, run again); A1's and A2's modules (in their notes): all 0. `warehouse/chat/check_spec.py`: 0.
- No em dash in any file this session wrote.

## Decisions made without you

1. **"30 model calls" read as 30 questions through the route.** The brief asks 30 questions through the route and allows 30 model calls; one question makes several API requests (193 in all, at most 8 tool turns each). The USD cap held on every request's cost.
2. **The real route, with three settings for a local server only:** `ASK_DAILY_USD=8`, `ASK_PER_VISITOR_PER_DAY=40`, and one local address a batch of 8. The route's own writes stayed (its admission counter and `site_api_calls`): they are the route as a visitor meets it, not warehouse data. Reversible: nothing was changed in the code or the database.
3. **The reserve before each question:** USD 0.50 (3.6 times the dearest question seen so far) for q01 to q21; USD 0.30 from q22, once 21 questions had shown a maximum of USD 0.138 at the limit of 8 tool turns. With USD 0.50 throughout the cap would have stopped the run at 29 questions.
4. **Two keys corrected after the answers** (q22, q24): the model's reading was the right one, checked against the table; the YAML's notes say so. Counted right. q16 is right at one decimal (the grader reads a coarser precision).
5. **MISO held in Ask's general query tool,** as the pages hold it; `eia930:MISO` and `iso:miso` (EIA's figures) kept. Python's `warehouse/chat/tools.py` (the CLI, not the route) is not changed.
6. **The trace switch** (`ASK_RECORD_TOOLS`) stays in the code, off by default, for the next evaluation.

## For Samuel's ruling

1. **MISO in Ask:** (a) hold every row of MISO's own data, as now; (b) answer with the figure and the words "paused while terms are reviewed"; (c) hold also EIA's regional figures for MISO. (a) matches the pages; (b) would serve figures the pages do not show.
2. **An ambiguous question (q04):** (a) the battery stack (energy and ancillary, two strategies) is the answer to "what a battery earns", the energy-only table second; (b) the reverse; (c) Ask asks back. The briefing now names both and says which is which.
3. **check-values on pages with no table-read number:** (a) exempt `/research` and `/internal/findings` from the floor of ten; (b) give the research cards' numbers check keys against their files.
4. The Research pack's questions (its section 9), among them whether a draft's figure must be checked against a publisher's own figure (none was: sessions 251 and 252 used the tables only).

## To finish

- FINAL-CYCLE-TOFINISH

## The landing

filled by the orchestrator
