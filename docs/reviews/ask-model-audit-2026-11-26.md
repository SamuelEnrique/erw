# Ask the warehouse: the chat audited as a hostile expert would

Session 10234, 26 November 2026, chain 710 part D, on the old laptop. Platform tool 20: the general chat, the grids' chats and Ask ERCOT, read as an editor who must trust every number the chat prints, and as an engineer checking the spending guard. In the form of `docs/reviews/analysis-model-audit-2026-11-26.md`.

- Nothing changed on main but this file and its evidence folder. No table written, no lock taken, no default moved, no model called (model spend USD 0; every python run under `ERW_SPEND_CAP_USD=0`; no client of the provider built: every "model" below is a stub), no request to any live service, no build, no browser.
- Each finding's test is on its own branch, `wip/audit-ask-<n>`. Branches 3, 4, 5, 6 and 7 change words only and are returned for landing; branches 1, 2 and 8 hold a test that shows the finding, not for landing, and the fix is Samuel's ruling.
- Evidence: every script and its output in `docs/reviews/ask-model-audit-2026-11-26/` (`a2` to `a7`, `draw.mjs`, `drawn_words.txt`), run on this machine from the saved runs under `warehouse/chat/eval/` (the scripts were run from `runs/s10234/`; their paths are relative to that folder).

## In short

- **The number check does what its code does, and less than its note and the About page say (findings 1, 3, 4).** It sends back a figure no source holds (on the 1,327 stored answers, 1,447 of the 1,449 figures moved by 7.13 were stopped). But a figure passes when its magnitude, at the precision written, lies within half a unit of any number of any source: every tool result, every tool argument the model chose, the question. It never asks which row, grid, day or sign the number belongs to.
- **So these pass, each shown by a test with no model (finding 1):** a public grid's figure written as a held grid's (HB_HOUSTON's 64.27 as NYISO Zone J's); a whole number for the held grid ("64", "57"); the UTC stamp's day written as the local day; a difference in the wrong direction; a number the question supplied ("Did it average 200?"); a number the model put in its own threshold; "81,402.19 per kW" for a figure in USD per MW. A whole number from 1 to 100 passes against a stored answer's own sources 31 percent of the time; two decimals 1.1 percent.
- **No stored answer was found misled by these.** The trader's twenty and the held-out set, 45 answers re-scored by hand against their keys and their tool records, score as stored: 20 of 20; 16 right, 7 rightly refused, 1 wrong (h19, a wrong sum the tool returned and the check rightly passed), 1 ended in an error. Every date and figure in the trader's twenty traces to its own row.
- **A held grid's figure never reached a stored answer.** In all 48 stored held-grid questions no tool result held a value of a NYISO or ISO-NE row (`a6b`); 45 were headed "Answered from the warehouse" above a sentence that says the rows are held (finding 8).
- **The spending guards hold at their edges with stubbed clients, with three gaps (finding 2).** A session cap of 0 refuses before the call; a call that starts under the cap is sent whatever it costs (no reserve); with the ledger off the session cap never closes (USD 3.00 sent under a cap of USD 0.05). The evaluation runner counts a question that ended in an error at USD 0 (tr13 and tr14 of session 3280 were so). The site counts only the rows its ledger kept: a visitor's call whose row fails to write is not counted, while the note says "It fails closed" (finding 6, fixed in words).
- **Words fixed (findings 3 to 7):** the method note's rule, the About page (which also called 23 October the last asking; the set was asked to 14 November), the answer line that blamed every sent-back draft on an untraced number (3 of the 20 with a record were sent back for other reasons), the ceilings' note, and /terms and /privacy, which said the visitor's daily code "cannot be turned back into an address" (it can, with the server's secret).
- **No security weakness of high severity was found.** The open low finding T2 of `docs/security.md` (a visitor's own false earlier turn counts as given) is confirmed and not repeated.

## The ground: each file and what it does

| File | What it does |
|---|---|
| `site/app/ask/page.tsx` | `/ask` redirects to the Grid tool's Ask panel (the general chat, or a grid's chat with `?grid=`) |
| `site/app/ask/AskForm.tsx` | The general and the six grids' chats: the box, the conversation of three turns, the answer, its heading by status, its sources and reads, the line "N warehouse queries by <model>; ... model cost" |
| `site/app/ask/ercot/`, `site/components/ask/AskPanel.tsx`, `AnswerSources.tsx` | Ask ERCOT's page and panel; every chat's sources and reads line |
| `site/app/api/ask/route.ts` | `POST /api/ask`: the origin, user agent and type tests (`site/lib/guard.ts`), 10 questions an hour an address, the admission (`site/lib/chat/limits.ts`), the loop, one log line a question |
| `site/lib/chat/ask.ts` | The site's loop: at most 12 tool calls, the number check (`unverified`), the unit check (`unitMismatches`), the citations, one retry, the refusal; every model call into the ledger (`ledger.ts`) |
| `site/lib/chat/tools.ts`, `refused.ts`, `window.ts`, `heldrows.ts`, `history.ts` | The tools over the live set with the anon key; the held tables and held grids; a window's wholeness; a conversation's earlier turns |
| `site/lib/chat/limits.ts`, `limits.json`, migrations `023`, `028`, `035` | The ceilings: USD 3 a day, USD 30 a month, 15 questions a visitor a day, counted by the database (`site_ask_admit`); an evaluation's own step and day ceiling |
| `site/lib/chat/ledger.ts` | One row of `site_api_calls` a model call; a failed write is logged, and thrown only for an evaluation |
| `warehouse/chat/ask.py` | The Python loop (the CLI and the evaluation's own loop): the same rules, the number check, the unit check, the refusal checks; `--export-spec` writes `site/lib/chat/spec.json` |
| `warehouse/chat/tools.py` | The tools over the `erw` package: `list_tables`, `describe_table`, `query`, `compare` (the four), and `board_rank` and `grid_notes` |
| `warehouse/chat/license_hold.py`, `window.py`, `general_series.py`, `ercot.py` | The hold mirrored for the Python loop (`ASK_HOLD=on`, off by default); the window; the chart under an answer; Ask ERCOT's profile |
| `warehouse/llm.py` | The one client of the provider: the cost ledger, the session cap (`ERW_SPEND_CAP_USD`), the key's own limit |
| `warehouse/chat/eval/` | The questions and keys (`questions_*.yaml`, `keys_*.json`), the runners (`eval_s1113.py`, `eval_loop.py`, `eval_site.py`), the stored runs and grades (`*_run.json`, `*_grades.json`, named in `runs.json`), `replay.py`, `refusals.py`, `class_scores.py` |
| `docs/methods/ask.md`, `ask_limits.md`, `ask_ercot.md` | The notes; `/about`, `/terms` and `/privacy` make the public claims |

## The number check, exercised

`tests/test_audit_ask_1.py` on `wip/audit-ask-1` runs `ask.unverified` and `ask.unit_mismatches` (held equal to the site's by `tests/test_session1309.py`) on drafts written by hand against tool results stored by the evaluation: tr02's maximum (150 USD/MWh at 2026-11-04T03:00:00Z, which is 9 pm Central on 3 November) and tr19's held answer (NYISO named, the eleven public hubs' figures, no NYISO figure). And the Python loop end to end with a stub for the model and for the tools.

| Draft | Should | Does |
|---|---|---|
| 50.795417, 50.80, 50.8, 51 for a result of 50.795417 | pass | pass |
| 81,402.19 USD/MW; "10.26 below" for a difference of -10.264308 | pass | pass |
| "9 pm Central, 3 November 2026" for tr02's hour | pass | pass |
| The held answer as designed (hold's words, public figures) | pass | pass |
| 71.23 (in no result) | stop | stop |
| 50.79 (a truncation of 50.795417) | stop | stop |
| 99.61, a sum the model made | stop | stop |
| "18.7 percent", a percent the model made | stop | stop |
| 81.40 USD/kW from 81,402.19 USD/MW; 81,402.19 USD/kW; 50.80 USD/MW for a USD/MWh figure | stop | stop |
| 61.15 for NYISO (no public hub holds it) | stop | stop |
| **"NYISO's Zone J averaged 64.27 USD/MWh"** (HB_HOUSTON's figure) | stop | **pass** |
| **"NYISO's Zone J averaged 64" or "57"** (within half a unit of HB_HOUSTON's or HB_WEST's) | stop | **pass** |
| **"9 pm Central, 4 November"** and **"3 am Central, 4 November"** (the UTC stamp's day and hour) | stop | **pass** |
| **"SP15 was 10.26 above NP15"** for SP15 minus NP15 of -10.26 | stop | **pass** |
| **"HB_NORTH averaged 200"** when the question asked "Did it average 200?" | stop | **pass** |
| **"peaked at 512.33"** when 512.33 is only the model's own threshold argument | stop | **pass** |
| **"81,402.19 per kW"** or **"a kW"** (no money word, so the unit is not judged) | stop | **pass** |
| **"for 3 hours", "11 intervals", "12 days"** (counts no tool returned; 3, 11 and 12 stand in the result's local times) | stop | **pass** (7 hours is stopped) |
| The whole Python loop: a held grid's question, the tool's stored held result, a draft "NYISO's Zone J averaged 64 USD/MWh" | refused or sent back | **answered at the first draft, no retry** |

**How much of the number line passes** (`a2`, the same rule as `unverified`, checked against it on 30 answers with no disagreement): against each of the 1,327 stored answers' own sources (a median of 68 numbers, 114 when the answer listed the tables), a whole number from 1 to 100 passes 31 percent of the time (39 percent after a `list_tables`), one decimal 8.0 percent, two decimals 1.1 percent, a whole number from 1,000 to 100,000 0.02 percent. The check is strong for a price to the cent and for a large figure; it is weak for the small whole numbers an answer is full of: counts, hours, days, a percent written whole.

## 1. The number check traces magnitudes, not figures

- **Where.** `warehouse/chat/ask.py` lines 126 to 200 (`numbers`, `unverified`): the pool is every number of every source; a figure passes when `abs(abs(p) - abs(v)) <= 0.5 * 10**-d` for any `p`. The sources (line 741 and line 812): the question, every tool result and every tool argument, and in a conversation the earlier answers and their reads; the site's loop adds the day line (`site/lib/chat/ask.ts` line 356), the Python loop does not. The unit check (`unit_mismatches`, lines 264 to 292) judges a figure only when a money word or sign, percent or MW stands next to it, and only when every matching number is placed in another known unit.
- **What it means for a reader.** "Checked" means "these digits stand somewhere in what the tools returned, or in the question, or in the model's own arguments". It does not mean "this is the right hub's, day's or sign's figure", and the page and the About page say more (findings 4, 5).
- **Measured on the stored answers.** No stored answer was found to pin a public figure on a held grid (tr19, h23, h24 read whole); the 45 answers re-scored below hold no figure that is not their own row's. 80 of the 1,327 stored answers (6.0 percent) state a number found only in the question or a tool argument, nearly all the question's own terms (a 4-hour battery, 48 hours, a year asked about) (`a7`).
- **The test.** `tests/test_audit_ask_1.py` (19 tests). Passes on main.
- **For Samuel's ruling.** Whether the check binds each figure to the row it came from (its entity, its time and its sign) and stops counting the model's own tool arguments as sources. Default: left as it is. Measured: dropping the question and the arguments from the sources would send back 80 of the 1,327 stored answers, nearly all right ones that repeat the question's terms; a binding to rows is not written, so its effect on the saved answers is not measured.

## 2. The spending guards at their edges

Read, then tested with stubs only (`tests/test_audit_ask_2.py` on `wip/audit-ask-2`; each test clears `ERW_SPEND_CAP_USD` itself; the ledger file is never written or read from the repository).

| Guard | Edge | Result |
|---|---|---|
| `warehouse/llm.py` `check_cap` (every call of the warehouse's scripts) | cap 0 | refused before the call; the stub never called |
| | ledger at 0.99, cap 1.00, a call of USD 0.30 | sent; the session ends at 1.29: **no reserve**, a session can pass its cap by one call |
| | ledger at the cap exactly | refused (`>=`) |
| | `ERW_LEDGER=0`, cap 0.05, ten calls of USD 0.30 | **all ten sent**: the total is read from the ledger file alone, so with the ledger off the cap never closes |
| `llm.guarded` (the key's own limit) | the provider refuses with its usage-limit words | `KeyLimitReached`; the next call raises it again and is not sent; the return date kept ("2026-12-01 at 00:00 UTC") |
| `eval/eval_loop.py` `ask_all` (the Python-loop evaluation) | reserve USD 0.50 before ten questions, cap 0.49 / 0.70, USD 0.20 a question | 0 asked / 2 asked: strict at the edge, as the docstring says |
| | each question spends USD 0.25 and then ends in an error | **all ten asked, USD 2.50 under a cap of USD 1.00**: an errored question is recorded at USD 0 (`cost = rec.get("cost_usd") or 0`); stored: tr13 and tr14 of session 3280 (`a4`), whose cost the note already calls unrecorded |
| `site/lib/chat/limits.ts` `admit` (visitors) | no ceilings, no secret, no address, a database error, any answer but yes | refused (held by `tests/test_session128.py`) |
| `site/lib/chat/ledger.ts` `recordCall` | a visitor's row the ledger refuses | **logged, not thrown, not counted**: the ceilings sum the ledger, so they do not close for it; only an evaluation's write is strict (finding 6) |
| `site/lib/chat/limits.ts` `admitEvaluation` | the evaluation step's spend at its own ceiling | refused (`>=`); no reserve on the route, the runner keeps one (`eval_s1113.py`, 0.50 then 2.5 times the dearest) |

- **One question's bound.** At most 12 tool calls; with the draft, one retry and one cut-off, about 15 model calls of up to 16,000 output tokens each. A ceiling is checked before a question, never during one, as `ask_limits.md` says.
- **The site's model.** The loop takes the newest Sonnet-class model at run time; one with no price in `spec.json` writes a row with no price, and the next admission is then closed (fail closed, as the note says).
- **For Samuel's ruling.** Whether `eval_loop.py` counts an errored question at what its client spent (`LedgerClient.calls`), and whether `check_cap` keeps a reserve and refuses to run with a cap while the ledger is off. Default: left as it is. Measured: two stored questions recorded at USD 0; no saved answer changes (a guard, not the chat).

## 3. The method note's rule says more than the check does (fixed in words)

- **Where.** `docs/methods/ask.md`, "The rule": "Every figure in an answer must be a figure a tool returned in that turn". The section "The checks on every draft" names the question and the tool arguments; the rule above it does not, and neither says that a figure is matched to any number of any source.
- **The fix, words only.** `wip/audit-ask-3`: a paragraph "What the check proves, and what it does not" under the rule, naming the sources and the cases of finding 1, and h19 as the example of a figure traced and still wrong.
- **The test.** `tests/test_audit_ask_3.py` (fails on main, passes on the branch); `test_session5268_ask.py` and `test_session5276_ask.py`, which read the note, pass.

## 4. The About page says more than the check does, and calls 23 October the last asking (fixed in words)

- **Where.** `site/app/about/page.tsx` line 154: "states no number a query of the warehouse did not return: every figure of an answer is checked against what its tools read, in its unit", and "Its evaluation, last asked on 23 October 2026". The question's numbers and the model's arguments count (finding 1); a unit is judged only beside a money word, percent or MW; the sets were asked again to 14 November 2026 (`ask.md`, "The evaluations").
- **The fix, words only.** `wip/audit-ask-4`: "states no number it cannot trace: every figure of an answer must match, at the precision written, a number its queries returned or the question or its own queries named, a dollar figure is sent back when the tools gave it only in another unit ... The check traces a figure to a source; it does not prove that the figure is the right row, grid or day. Its evaluation of 23 October 2026 (later askings, to 14 November 2026, are in its method): ...". No score on the page moves.
- **Drawn: pass.** The page drawn with the site's own code (`site/scripts/tsx-register.mjs` and `font-stub-loader.mjs`, no build, no network), the new words read in the drawn text (`drawn_words.txt`).
- **The test.** `tests/test_audit_ask_4.py` (draws the page; fails on main, passes on the branch); the three page tests that read the About page pass.

## 5. The answer line blames every sent-back draft on an untraced number (fixed in words)

- **Where.** `site/app/ask/AskForm.tsx` line 112: "the first draft was sent back because a number could not be traced" whenever `retried`. The loop also sends a draft back for a unit, a citation, an empty answer, a refusal that states a figure, an answer cut short, an answer to a table the site cannot read. Of the 122 stored answers sent back once, 20 record why: 17 an untraced number, 1 a unit, 2 a refusal that stated a figure (`a5`).
- **The fix, words only.** `wip/audit-ask-5`: "the first draft did not pass the checks and was sent back once".
- **Drawn: pass.** The form drawn with its state handed in as an answer sent back once (React's `useState` stood in for before the form is imported; nothing of the form changed): "2 warehouse queries by claude-stand-in; the first draft did not pass the checks and was sent back once; model cost USD 0.0400."
- **The test.** `tests/test_audit_ask_5.py`; the eight test files that read `AskForm.tsx` pass, except `test_session137.py::test_the_panels_own_tests_pass`, which fails the same way on clean origin/main (the board's ERCOT rows, not this form).

## 6. "It fails closed" covers the admission, not the count (fixed in words)

- **Where.** `docs/methods/ask_limits.md`: "**It fails closed.** Anything that is not a plain yes from the database is a no." True of `admit`. The spend it compares is the ledger's rows, and a visitor's row that fails to write is logged and not counted (`ledger.ts` lines 25 to 46; `route.ts` line 107 sets `strictLedger` for an evaluation only). The note says so lower down ("A call that fails to reach the ledger is not counted") without drawing the consequence: a ledger that refused every row would leave the ceilings open.
- **The fix, words only.** `wip/audit-ask-6`: a paragraph "What it does not close for" under the rule. Whether a visitor's write should be strict too is the same ruling as finding 2.
- **The test.** `tests/test_audit_ask_6.py` (fails on main, passes); `test_session128.py`, `test_session5263_ask.py`, `test_session5151.py` pass.

## 7. /terms and /privacy: "cannot be turned back into an address" (fixed in words)

- **Where.** `site/app/terms/page.tsx` line 75 and `site/app/privacy/page.tsx` line 65. The code is HMAC-SHA256 of the UTC day and the address under `ASK_VISITOR_SALT` (`limits.ts` `visitorKey`). Without the secret it cannot be turned back; with it, an IPv4 address is one of about 4.3 billion and can be found by trying each. The code's own comment, the ceilings' note and `guard.ts` say "without the secret"; the two public pages did not.
- **The fix, words only.** `wip/audit-ask-7`: "without the server's secret" on both pages.
- **Drawn: pass**, both pages (`drawn_words.txt`).
- **The test.** `tests/test_audit_ask_7.py`; `test_session177.py` (which reads /terms) and `test_session241b.py` pass.

## 8. A held grid's question is headed "Answered from the warehouse"

- **Where.** The tools answer a held grid's rows with the hold's words, the public grids' figures and "Answer with not_in_warehouse false" (`site/lib/chat/tools.ts` line 509, `warehouse/chat/tools.py` line 724); the status is then "answered", which `AskForm.tsx` heads "Answered from the warehouse". The decision (session 1112) is to answer with the public grids' figures; the heading was not part of it.
- **Measured.** 45 of the 48 stored held-grid questions ended "answered" (`a6`); none states a held figure.
- **The test.** `tests/test_audit_ask_8.py` on `wip/audit-ask-8`. Passes on main.
- **For Samuel's ruling.** Whether a held grid's answer gets a status and a heading of its own ("Held for a license; the public grids' figures"). Default: left as it is. Measured: 45 stored answers would change heading; no answer's words.

## The saved evaluations re-scored by hand

| Set and run | Asked | Re-scored by hand | Stored grade | Notes |
|---|---|---|---|---|
| The trader's twenty, the site's loop (`eval_s5275_site_trader_run.json`, `keys_trader.json`) | 20 | 20 of 20 right: 18 figures, NYISO held, MISO paused | 20 of 20 | Every key found in its own row (`a3_trader_twenty.txt`). Every other fact checked against its tool result: tr02, tr04, tr06, tr09, tr10's hours converted from UTC by hand (CST from 1 November, CDT and PDT before); tr14's 0.77 and 0.30, tr15's first and last intervals, tr16's "only 31 October", tr17's 20 days (`a3_trader_traces.txt`). Form only: tr03 writes six decimals, tr11 and tr12 speak of "the compare tool" (asked before rule 12) |
| The held-out set, the site's loop (`eval_s6192_site_heldout_run.json`, `keys_heldout.json`) | 25 | 16 right, 7 rightly refused (two held grids, two held tables, MISO, two tables not loaded), 1 wrong (h19), 1 error (h30) | the same | h19: 419,388.74 MW where the rows sum to 419,636.335; the tool's read of three pages held a row twice (fixed in session 6192); the number check passed it rightly, since the tool returned it. h23's "New York local day" mislabels the public hubs' own operating days; the figures are their rows' |

45 answers re-scored; no grade changes.

## Each claim, set against the code

| The claim | Where | The code | Verdict |
|---|---|---|---|
| "states no number a query of the warehouse did not return" | `/about` | the question's numbers and the model's own arguments count | finding 4 |
| "Every figure ... a figure a tool returned in that turn" | `ask.md`, the rule | as above, and any source's number matches | finding 3 |
| "checked against what its tools read, in its unit" | `/about` | a unit judged only beside a money word, percent or MW | finding 4 |
| "the first draft was sent back because a number could not be traced" | the general form | sent back for seven reasons | finding 5 |
| "It fails closed" | `ask_limits.md` | the admission does; a visitor's lost ledger row is not counted | finding 6 |
| A visitor's answer carries no tool record | `ask.md`, session 1111 | `record` only for an evaluation admitted by its token (`route.ts` line 107; `ASK_RECORD_TOOLS` is a local server's) | holds |
| Logged without identity: the time, the question, the outcome | `/terms` | the log line also holds the question's number, its cost, its seconds, its tool calls, its grid and how many earlier turns came with it; never the address (`route.ts` lines 103, 114 to 116, 150, 153) | holds (the list is short of the cost and timings, none of which identifies) |
| The daily code "cannot be turned back into an address" | `/terms`, `/privacy` | not without the secret | finding 7 |
| A held grid's rows are never read for an answer | `ask.md`, session 1112 | refused in both loops' tools; no held figure in any of the 48 stored held answers | holds; the check would not stop a public figure written as the held grid's (finding 1) |
| A held grid's question gets the hold's words and the public grids' figures | `ask.md` | yes, as status "answered" | finding 8 (the heading) |
| The loops give a reader the same thing | `ask.md`, session 1300 | the site counts the day line as a source, the Python loop does not | low, noted: a day of the month the question did not name passes on the site only |
| A ceiling is checked before a question, not during | `ask_limits.md` | holds | holds |
| The evaluation's spend guard reads the whole ledger | `ask.md`, session 5263 | held by `test_session5263_ask.py` | holds; the Python runner's errored question is not (finding 2) |

## What was checked and found right

- The number check stops what it is built to stop: a figure in no source, a truncation, a sum, a percent or a unit change the model made (finding 1's second class), and the stored answers' figures moved by 7.13 (99.9 percent stopped, `a2`).
- Every one of the 45 answers re-scored by hand states its key's figure from its own row, at the cent; every hour converted from UTC is right.
- The held grids: no stored answer of 48 states a held figure; MISO's questions are refused in the pause's words.
- The key's limit: one refusal and no further request, in the client every warehouse script uses.
- The admission: fails closed on every input that is not a plain yes (`test_session128.py`).

## Not covered, or left open

- Nothing was asked of the model (spend USD 0; the key is at its limit until 1 December 2026): no fix is measured on new answers.
- The site's loop was read and tested through its Python twin and from its source; no node test of `ask.ts` was run beyond the drawings (the twin is held equal by `test_session1300.py` and `test_session1309.py`).
- Whether Vercel overwrites `x-forwarded-for`, on which the visitor's count and the hourly limit rest, was not checked (no web reads); the daily ceiling bounds the spend either way (`docs/security.md`, T3).
- The provider's console limit, the outer wall, was not read.

## The branches

Each from origin/main of 26 November 2026, pushed; the tests run with every test file that imports the changed module or reads the changed file.

| Branch | Kind | Test | What else was run |
|---|---|---|---|
| `wip/audit-ask-1` | behaviour: shows the finding, not for landing | `tests/test_audit_ask_1.py` | |
| `wip/audit-ask-2` | behaviour: shows the finding, not for landing | `tests/test_audit_ask_2.py` | |
| `wip/audit-ask-3` | words: `docs/methods/ask.md` | `tests/test_audit_ask_3.py` | `test_session5268_ask.py`, `test_session5276_ask.py` (25 passed) |
| `wip/audit-ask-4` | words: `site/app/about/page.tsx`, drawn | `tests/test_audit_ask_4.py` | `test_session115_page.py`, `116`, `120` (50 passed, 5 skipped) |
| `wip/audit-ask-5` | words: `site/app/ask/AskForm.tsx`, drawn | `tests/test_audit_ask_5.py` | the eight files that read the form (97 passed; `test_session137.py`'s panel test fails as on clean origin/main) |
| `wip/audit-ask-6` | words: `docs/methods/ask_limits.md` | `tests/test_audit_ask_6.py` | `test_session128.py`, `5263_ask`, `5151` (41 passed) |
| `wip/audit-ask-7` | words: `site/app/terms/page.tsx`, `site/app/privacy/page.tsx`, drawn | `tests/test_audit_ask_7.py` | `test_session177.py`, `241b` (54 passed) |
| `wip/audit-ask-8` | behaviour: shows the finding, not for landing | `tests/test_audit_ask_8.py` | |

- The words branches fail their test on main and pass it on the branch; the behaviour branches pass on main. The words branches touch different files and do not conflict.
- No site build and no snapshot here (this machine's rules). Every page is in review; the landing of the words branches that touch pages (4, 5, 7) is the desk's, with rule 8's snapshot there.
