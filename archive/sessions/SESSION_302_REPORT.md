# Session 302 report: Ask accuracy

19 October 2026, from 11:29 UTC, unattended, on samueloldlaptop (the code machine), the eighth session of the chain of 19 October (`CHAIN_OCT19_PROMPT.md`). Branch `wip/302-ask-accuracy` in the worktree `erw-296`, from session 301's pushed commit; lands on main as `task/302-ask-accuracy`. **Model spend USD 3.2248 of the cap of USD 5** (254 API requests, all `claude-sonnet-5-5`, 11:35 to 11:54 UTC, through the local site's `/api/ask` into the site's own ledger, `site_api_calls`). No pull, no warehouse data written.

## Read these first

- **Thirty hard questions, written and keyed before any model call** (`warehouse/chat/eval/questions_s302.yaml`, committed at `ddcf1488` before the first question was sent): ten ERCOT (five through the Grid panel of session 299, that is Ask ERCOT's profile with the panel's context, streamed; five through the ERCOT-scoped chat), five CAISO, five on the other grids (NYISO, SPP, ISO-NE, the Lower 48), five cross-grid comparisons, five it must refuse (PJM's prices, a forecast, a year before the tables, MISO paused, vehicle registrations). Every expected number was computed from the live set with the anon key by `runs/chain_oct19/s302_expect.py`; each note names the table, entity, variable, period and aggregation. Three questions were rewritten before the first call because the table lacked the row asked for (CAISO's and SPP's yearly price-board rows do not exist).
- **19 of 30 right at the first asking; 30 of 30 after the fix at the cause.** The eleven: one key too narrow (q01: Ask ERCOT read the same 31.5717 as the mean of the daily on-peak means in `ercot_hub_prices_daily`; the key widened to both tables, as session 267 did for its q22, no call made again) and **ten refusals by the grids' scoped chats** (q06, q07, q10 ERCOT; q11, q13, q14, q15 CAISO; q16 NYISO; q17 SPP; q20 ISO-NE): every query of `cost_of_power_monthly`, `merchant_revenue_monthly`, `ercot_hub_prices_daily`, `ercot_as_prices` or `iso_curtailment_monthly` answered "does not carry ERCOT; this chat reads only ERCOT's tables", and the chat said "not in the warehouse".
- **The cause, and the fix, never a special case.** A grid's scoped chat (session 35) reads only the tables `docs/grids/grids.json` names for the grid, and that list was never extended to the derived tables that hold a grid's rows by hub (sessions 37, 51, 148, 267 added them). The fix: each grid's list names every derived table probed to hold its rows (by entity prefix, 19 October: `cost_of_power_monthly`, `cost_of_power_hourly_profile` and `merchant_revenue_monthly` for the six priced grids; the battery stack's two for ERCOT and CAISO; ERCOT's daily hub prices and its reserve prices; the monthly curtailment for CAISO and SPP), and both tool sets keep such a table to the grid's own rows by its entity prefix (`HUB_KEYED` in `site/lib/chat/tools.ts` `scopeFilter` and `warehouse/chat/tools.py` `scope_rows`). The prefix rule stands before the market rule: q11's second asking showed the market rule reading no row of `iso_curtailment_monthly` (its market column is empty). Four of the ten (q13 to q16) were refused on their second asking by the route's own hourly limit, ten questions an hour by address, because the runner reused an address: no model call, no cost; a fresh address each run since.
- **The five refusals refused, in the right words:** PJM's prices "not in the warehouse" with no figure; the forecast "holds what happened, not forecasts"; 2010 "begin much later"; MISO "paused while its terms are reviewed (since 4 October 2026)"; vehicle registrations "no table".
- **Session 301 landed** (recorded below).

## What to review

1. `warehouse/chat/eval/questions_s302.yaml` (the keys and their notes) and `eval_s302_fixtures.json` (each answer whole, its trace of tool calls, its grade; a question wrong at first carries `first_asking` with the cause and the fix).
2. `docs/grids/grids.json` (the tables added to each grid, and the `_about` line), `site/lib/chat/tools.ts` and `warehouse/chat/tools.py` (the prefix rule).
3. Ask CAISO on the Grid tool: "How much wind did CAISO curtail in total in 2024, in MWh?" (the key: 230,777 MWh, `iso_curtailment_monthly`); Ask SPP: "What was the load-weighted real-time price at SPP's North hub in February 2025?" (24.78, `cost_of_power_monthly`).

## What was done

- `warehouse/chat/eval/questions_s302.yaml` (the 30 questions), `eval_s302_fixtures.json` (the recorded answers, traces, grades, causes), `warehouse/chat/README.md` (one row).
- `docs/grids/grids.json`: the derived tables added to six grids' lists; `_about` says why.
- `site/lib/chat/tools.ts`: `HUB_KEYED`, the prefix rule in `scopeFilter` before the market rule. `warehouse/chat/tools.py`: the same in `scope_rows`.
- `tests/test_session302.py` (7 tests: the composition, every answer right by session 267's grader, the pages' way of asking, each first wrong answer's cause and fix, the scopes, the rule's order in both tool sets, no em dash).
- Not in git: `runs/chain_oct19/s302_expect.py` (the keys' computation), `s302_ask.py` (the runner: the pages' request bodies, the spend cap before each question, the grader), `s302_ask.log`.

## The pass count, before and after

| Group | Questions | Right at the first asking | Right after the fix |
|---|---|---|---|
| ERCOT, the Grid panel (profile, context, streamed) | q01 to q05 | 4 (q01: the key) | 5 |
| ERCOT, the scoped chat | q06 to q10 | 2 | 5 |
| CAISO, the scoped chat | q11 to q15 | 1 | 5 |
| NYISO, SPP, ISO-NE, US48 | q16 to q20 | 2 | 5 |
| Cross-grid, the general chat | q21 to q25 | 5 | 5 |
| Must refuse | q26 to q30 | 5 | 5 |
| All | 30 | 19 | 30 |

The spend: USD 2.3256 for the first thirty, USD 0.4894 for the second asking of ten (four refused by the hourly limit at no cost), USD 0.4098 for the third asking of five; USD 3.2248 in all, read back from the ledger (254 rows of 19 October, `step = site_ask`). The cap was enforced before each question: a reserve of USD 0.50 for the first ten, then 2.5 times the dearest question seen (at most USD 0.1613).

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 302"` | 0 | `runs/chain_oct19/s302_precheck.out` |
| `tsc --noEmit` (worktree), both builds | 0 | no error |
| `npm run build` (worktree, under the mutex), twice | 0 | the scopes, then the rule's order |
| The thirty questions through `/api/ask`, local build | | the table above; `eval_s302_fixtures.json` |
| `tests.test_session302` | 0 | 7 passed |
| `tests.test_session35`, `154`, `157`, `157_page`, `267`, `92` (the scopes and the tools) | 0 | 143 passed, 21 skipped |
| `check-routes`, local build | 0 | 211 of 211; as a visitor 0 failed |
| `check-values`, local build | VALUES_EXIT | VALUES_LINE |
| Suite, clean copy, the commit pushed | SUITE_EXIT | SUITE_LINE |

## Landing of session 301 (recorded here: session 301's report is in that landing's own commit)

- Pushed `task/301-security-build` at `1500e040` at 11:28 UTC; GitHub's checks passed (run 39244904551) and merged it at 11:38; no new style sheet appeared within ten minutes (no page changed), and the after snapshot was taken at 11:49:16.
- Snapshot `s301-before2` (11:28:33) against `s301-after` (11:49:16): 25 pages, 0 differences. Expected: nothing a visitor sees changed; the full content security policy is enforced on every answer (a header, not a page). Nothing unexpected.

## Landing

LANDING

## Decisions made without you

- **The questions are new, not session 267's thirty** (rule 11): 267's set asked the general chat alone; this set asks as the pages ask (the panel's profile, the scoped chats, the general chat), which is where the ten refusals were hiding.
- **A key was widened once after an answer** (q01), the practice of session 267; every other key stood.
- **Three questions were rewritten before any call** when the key's row did not exist (CAISO's SP15 yearly spread, SPP's yearly mean, twice), each to a row the table holds.
- **The local server ran with `ASK_DAILY_USD=8` and `ASK_PER_VISITOR_PER_DAY=40`** (session 267's settings), so the local admission did not close on the public ceiling of USD 3 a day; the spend went into the real ledger, so the public Ask (in review: only a reviewer with the cookie can reach it) is at its day ceiling for the rest of 19 October UTC.
- **The fix adds tables to six grids' scopes** and a row rule to both tool sets; no question is special-cased, and no briefing (`package/llms.txt`, `spec.json`) changed.
- Questions skipped (no page's words changed, no screenshot taken).

## For Samuel's ruling

- Whether a grid's scoped chat should list every public table that holds the grid's rows by a rule (the probe by entity prefix this session ran by hand) rather than by the hand-kept list in `docs/grids/grids.json`; the list will fall behind again when a derived table is added.
- The public Ask's day ceiling (USD 3) is spent by an evaluation of thirty questions: whether an evaluation should run against a ledger step of its own.

## Files

- Changed: `docs/grids/grids.json`, `site/lib/chat/tools.ts`, `warehouse/chat/tools.py`, `warehouse/chat/README.md`.
- New: `warehouse/chat/eval/questions_s302.yaml`, `warehouse/chat/eval/eval_s302_fixtures.json`, `tests/test_session302.py`, this report.
