# Session 5251: the platform set keyed, wired and first asked; the live set's missing days

Energy Research Warehouse (ERW). portable-laptop, window P3, 13 November 2026 (18:47 to 19:19 UTC), Fable, unattended. Chain 238. Branch `wip/5200-ask` (worktree `erw-p3-5200`), `origin/main` merged at 18:47 UTC. Nothing built, nothing landed, no warehouse data written. Model spend USD 1.90.

## Read these first

- **The live set lacks whole days of its hourly tables**, and four monthly rows cover part of their month. Found by counting rows before any model call. The table is under "For Samuel's ruling": these are the data machine's.
- **The set is 134 questions and it runs**: twelve areas, seven kinds, every key computed from the live set with a visitor's key. Session 5202's builder had never run to its end: 21 of its 128 keys could not be computed.
- **Asked so far: 14. Right: 14.** Through the site's own loop with no build. `docs/reviews/ask-eval-2026-11-13.md` holds the set, the findings and the scores.
- **A question costs USD 0.14 on average through the site's loop** (USD 0.04 to 0.23). The set is about USD 18 once. So it is asked in two halves: the first now, the second after the fixes, as the held-out measure.
- **The second asking ended USD 0.015 over its written estimate** (USD 1.6148 against USD 1.60) and under its cap (USD 1.70). From session 5252 the estimate written before an asking is its cap.

## What session 5202 left, and what became of it

- `scripts/ask_eval/platform_questions.py`: kept, run, corrected. Committed.
- `site/scripts/eval-ask-site-loop.mjs`, `eval-loader.mjs`, `eval-register.mjs`, `eval-tool.mjs`: kept. The runner asks through `site/lib/chat/ask.ts` with no build; its dry run listed 140 tables with the anon key. Committed with a Node test.
- `warehouse/chat/eval/eval_site.py`, which the runner named and session 5202 had not written: written.

## The 21 keys that could not be computed

| Keys | Why | What was done |
|---|---|---|
| pw01, pw02, pw03, pw10, pr02, pr03, ga07, nu01, nu02, re03, tx05 | the day (5 November) and the week (2 to 8 November) are not held whole | the day is now 10 November, the week 19 to 25 October, both held whole by every series asked |
| po01 to po04 | `policy_actions` is held whole for a license | po01 and po02 are `hold` keys; po04 to po06 are new figures from public tables (Flex Alert hours, ERCOT's conservation appeals, CAISO's Stage 3 notices) |
| oi06, po05, po06 | `impact_tax_rules` is held whole | oi06 and po03 are `hold` keys |
| tx01, tx02 | a balancing authority's rows have no `net_import_mwh`; they have three other measures | each question names its measure; tx01 asks CAISO's August (31 days held), not ERCOT's (27 of 31) |
| tx07 | ERCOT's 2019 entry year has no `mw_withdrawn` | it asks `mw_operating` |

- Two keys that computed were wrong to ask as figures: pr05 and tx04 sit on October rows that cover 48 of 744 hours and 20 of 31 days. They are `partial` keys now. The chat's own first answer to pr05 said so before the key did.

## New in the set

- **`gap` (3 questions):** a day the series lacks. Right: "not in the warehouse", the day named.
- **`partial` (5 questions):** a week or a month held in part. Right: the answer says so.
- The builder stops when a gap has been filled or a window has become whole, and names the question to turn into a figure.

## The grader

- **`partial_grade`** (`eval_s1113.py`): a `partial` key is met by an answer that says the window is not whole.
- **`hold_public_grids`** (`eval_s267.py`, `RULES_5251`): pr11 (NYISO's Zone J) was answered as the loop is built to (the owner's ruling of 12 October): the hold's words, no NYISO figure, each public grid's figure. The grader counted any figure as the held grid's. Under the rule a hold key is met when every figure stated is among the public grids' figures of a held answer in the answer's own record.
- Stored gradings keep their rules. `eval_site.py` grades under `RULES_5251`; `eval_loop.py` is unchanged.

## The asking

- `eval_site.py --session N --set platform --slice a --cap 2`: the questions, the runner, the grades, the run named in `runs.json`, and `ask-history.md`, `ask-replay.md` and `ask-refusals.md` written again.
- A session's asking is its own run file (about 60 KB a question: the catalogue it listed is in its record).
- An error stops the run: an errored call may be paid for and unrecorded.
- Every model call is a row of `site_api_calls` under `site_ask_eval`. After two questions the ledger held USD 0.287473 in 10 rows; the run file USD 0.2875.

## What the 14 answers showed

- 14 of 14 under `RULES_5251` (13 of 14 under the rules of session 5201: pr11).
- **Tool calls:** 2, 3, 3, 4, 4, 5, 5, 6, 7, 11, 12, 12, 12, 12. Four used the whole limit. pw09 had its count of 11 on the third call and asked nine more. pw12 was told the table is not in the live set and asked it three more times. Both right; both cost over USD 0.20.
- **Seconds:** 7 to 35.
- Two drafts sent back once (pw03, pr03), right the second time.
- `replay.py --check` exit 0: the Python loop's checks would send none of the 14 back.

## Checks run

- `tests/test_session5251_ask.py`: 38 passed. `node --test site/scripts/test-eval-ask-site-loop.test.mjs`: 7 of 7.
- The 44 test files that read the Ask evaluation, its grader or its run list: 389 passed, 65 skipped, exit 0.
- `check_spec.py`, `replay.py --check`, `history.py --check`, `refusals.py --check`: each exit 0.
- `platform_questions.py --check`: exit 0.
- Precheck (from the main checkout): exit 0.

## Model spend

| Asking | Estimate before | Actual |
|---|---|---|
| The probe | 3 questions at about USD 0.10: USD 0.30; cap USD 0.50 | 2 questions, USD 0.2875 |
| Slice a | about 13 questions at about USD 0.125: USD 1.60; cap USD 1.70 | 12 questions, USD 1.6148 |

- Session: USD 1.9023 of USD 2. Chain 238: USD 1.90 of USD 20.

## Decisions made without you

- **The set is asked through the site's loop, not the Python loop.** The Python loop lists 184 tables under this machine's key; a visitor's chat lists 140. The set measures the visitor's.
- **The evaluation's spend is written to the site's cost ledger**, as the route writes an evaluation's (step `site_ask_eval`, no public ceiling counts it). `--no-ledger` leaves it out.
- **Two halves, the second held out.** The whole set twice does not fit USD 20.
- **Two test pins loosened**: `test_session1147` and `test_session1304` count the other sets' runs and refusals; this set's, which grow a session at a time, are held by `test_session5251_ask.py`.
- **The signed Flex Alert reduction is not keyed** (the table holds it negative; "reduced by" is not one of the grader's words of direction). po04 asks the alert hours.
- **The questions on missing days are all in the first half**: a later load may fill them.

## For Samuel's ruling

- **The live set's missing days** (read 13 November, 18:50 to 19:10 UTC, a visitor's key). Default: this window changes nothing; the data machine fills them, and the builder then stops and names the questions to re-key. The table is the section after this one.

- **Should a query say when its window is short?** The tool returns the rows matched, not the steps the window should hold. Default: wait for the eight questions on these days; if the chat states a short window's figure as the whole window's, the tool gains a count of steps expected (sessions 5257 on).
- **A visitor's question costs about USD 0.14** and the public ceiling is USD 3 a day: about 21 questions. Default: no change; said for the ceiling's owner.
- **The Python loop and the site's loop list different tables** on a machine that holds the service key (184 and 140). Default: the weekly run stays as it is; this set is the visitor's measure.

## The live set's missing days (the table of the first ruling above)

| Table | Series | Missing |
|---|---|---|
| `eia930_all_demand` | ERCOT, the Lower 48 | 5 to 8 November |
| `eia930_all_demand` | PJM, CAISO | 30 October to 8 November |
| `eia930_all_generation` | PJM coal and nuclear | 2 and 5 to 8 November |
| `eia930_all_generation` | ERCOT gas, the Lower 48 nuclear | 5 to 8 November |
| `iso_dam_hub_prices` | ERCOT, CAISO, SPP hubs | 7 and 8 November (local days) |
| `iso_rtm_hub_prices` | CAISO SP15, ERCOT hub average | 5 to 8 November (local days) |
| `ercot_wind_solar_hsl_daily` | ERCOT wind | 15 October, 30 October to 1 November, 5 to 8 November |
| `cost_of_power_monthly` | October 2026, both hubs | 48 of 744 hours |
| `merchant_revenue_monthly` | October 2026, ERCOT hub average | 336 of 744 hours |
| `node_basis_summary` | October 2026, ERCOT | 20 of 31 days |
