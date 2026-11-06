# Sessions 3279 to 3282: Ask the warehouse, the trader's twenty and the investor's twenty

Energy Research Warehouse (ERW). The personal laptop's second window (portable-laptop), 6 November 2026, Opus 5.5, unattended. Prompt: `queue/done/199-day-6-november-portable-askeval.md` (pushed to main alone, `2865db0b8`, before any other work). Branch `wip/3279-askeval`, head `65f6d096c` (`origin/main` merged), pushed; row 12 of `docs/state/landing_request_portable.md`.

## Not as the rules ask

- **The queue file's push to main (`2865db0b8`) was made without rule 8's snapshots.** A push to main deploys. The report's push was snapshotted (below); no page a visitor sees changed in either, since every page is in review and neither push touched `site/`.

## Numbering

- **Sessions 3279 to 3282.** The first free number at or above 2340 on `origin/main` and every branch: 2399 is free alone (session 2385's report skipped it), 2834 to 2847 are an unpushed data branch named on main, 2848 to 2861 are chain 146's (parked), and the numbers up to 3274 are taken by reports, branches and queue files; the EV game chain in this laptop's first window took 3275 to 3278 minutes before (`fdc0fea6e`). So 3279.
- **Queue file 199.** 198 was taken by the EV game chain's prompt the same hour.

## Session 3279: what the questions read

- Read `scripts/ask_eval/lab_questions.py`, `questions_s2224.yaml`, `eval_loop.py`, `eval_s267.py`'s `RULES_2223`, `eval_s1113.py`'s `grade_set` and `docs/methods/ask.md`.
- **In the live set and read by the Python loop** (catalogue of 6 November 2026; `describe_table` through the chat's tools, Supabase backend, hold on): `iso_dam_hub_prices` (hourly, from 2 October 2026), `iso_rtm_hub_prices` (15-minute; SPP's real time not whole for the week, so SPP is asked day-ahead only), `iso_trader_daily`, `price_board_spreads` (spark spread at 7.0 against Henry Hub, the only gas hub held), `node_basis_summary` (review), `nyiso_dam_zone_prices` (held for NYISO), `energy_deals`, `datacenter_facilities`, `datacenter_projects` (held whole), `large_load_public`, the ERCOT, CAISO, SPP and NYISO queue tables, `lbnl_interconnection_queue`, `interconnection_durations_summary` (review).
- **Not in the live set:** `eia_nuclear_outages_daily`, `_facility_daily`, `_generator_daily`, `nuclear_fleet_status` (a reactor's outage days) and `generator_pipeline_by_grid`, `eia860m_planned_generators` (the EIA-860M slip by grid). On main and in coverage, not loaded. Their two questions are keyed "not in the warehouse" (see Decisions).

## The counts

| Set | First asking | After the fixes | Cost |
|---|---|---|---|
| The trader's twenty (`questions_trader.yaml`) | 17 of 20 (session 3280) | **19 of 20** (tr13, tr14 asked again in 3282) | USD 1.6027 + 0.3030 |
| The investor's twenty (`questions_investor.yaml`) | 14 of 17 asked (3281; stopped for memory before iv18) | **16 of 17 asked** (iv13 to iv15 asked again in 3282); iv18 to iv20 never asked | USD 1.1168 + 0.5689 |

## The faults, by class

- **A refusal where an answer exists**
  - tr13, tr14 (spark spreads): the Python loop raised `ValueError` on `latest` of `price_board_spreads.x_gas_date`, a text column blank in all 2,142 live rows, and the question ended with no answer. **Fixed:** `tools._num` reads text as no figure (None), as the site's loop reads it null. Both right on the second asking.
  - tr15 (15-minute intervals at ERCOT West above 100 USD/MWh in the week; the key is 23): `query` has no value filter, so the loop said it could not count and gave no estimate (honest). **Not fixed:** a threshold argument for `query` is a change to both loops' tools (`tools.py` and `tools.ts`), and the site's loop cannot be run on this machine. For Samuel's ruling.
- **Wrong table** (refused as "not in the warehouse")
  - iv13 to iv15 (months from request to operation by grid): the loop read the ISO's queue table, found no duration column and refused without listing the tables; `interconnection_durations_summary` holds the figures (iv16 listed the tables and found it). **Fixed in the shared prompt:** rule 3 now asks for `list_tables` before "not in the warehouse" and says a derived table often holds what a source table lacks (`ask.py`, `spec.json` exported). iv13 and iv15 right on the second asking.
  - iv14 is still wrong: it listed tables only with filters (`iso` CAISO, a sector) and stopped at the 12-call limit. A table that covers every grid is not listed under one grid's filter.
- **Wrong aggregation, period or unit; a held table answered; a number not fetched:** none. All held questions (iv01 to iv05, tr19) gave the hold's words and no figure; MISO's (tr20) the pause's.
- **A grading fault, found and fixed:** tr15 was first graded right on the "23" of "the 23:00 hour". A key marked `count: true` is not met by a clock time now; tr15 is graded wrong.

## What was built

- `scripts/ask_eval/trader_questions.py`, `investor_questions.py` (every key from the live set, `--check`), the two YAML sets and their keys files. Windows are local days (America/Chicago, America/Los_Angeles) checked whole before a key is written.
- `eval_s1113.py`: the `trader` and `investor` sets; a text key's parts joined by "|" (an hour written in UTC, local time or as the hour ending); `count: true`; `first: true` (the words in the answer's first sentence).
- `tests/test_session3282_ask.py`: scripted turns for the `latest` fault (fails on the old code), the rule in both loops' spec, and the grader's readings. Tests 1147 and 1304 extended for the four runs. `runs.json`, `ask-history.md`, `ask-replay.md` (none of the 40 new answers would now be sent back) and `ask-refusals.md` written again. `docs/methods/ask.md`: the section, the table rows, the decision.
- Tests: the 57 Ask test files with the new one, 429 passed, 79 skipped, 0 failed; after merging `origin/main`, 31 passed, 2 skipped on the eight closest. The site half of `test_session1300.py` skipped (no `node_modules`). Not built.

## Decisions made without you

- **Sessions numbered 3279**, not 2399 (a lone gap earlier chains skipped) nor 2834 or 2848 (an unpushed data branch and a parked chain).
- **Questions whose tables are not in the live set** (a reactor's outages, the 860M slip) are keyed "not in the warehouse" in the first sentence: the live set is what Ask reads. The script stops once either table reaches the live set, so a figure key is written then.
- **Held tables** (PPA prices, a counterparty's deals, the datacenter tracker) keyed as the lab set did: the hold's words, no figure. The public `large_load_public` added as the one public large-load question (iv06).
- **"Refused by name with no digit"** read as session 1112's held answer: NYISO named, "license needed", no figure (a date may carry digits), asked in NYISO's own chat.
- **Spark spread at the board's 7.0 MMBtu/MWh** against Henry Hub: a heat rate the board does not hold would need arithmetic the model is not allowed.
- **The investor run was not restarted** after Claude Code stopped it for low memory. The second asking was run in the foreground with memory checked first (1.6 to 1.8 GB free), because the prompt asks for the sets to run again.
- **The second asking covered only the questions a fix touched**, under the USD 4 cap (a full second asking of both sets costs about USD 2.7). iv17's check of the new rule was dropped for room. iv18 to iv20 were then stopped by the runner's USD 0.50 reserve: unasked.
- **The investor's first asking ran with the `_num` fix already in the worktree** (started while the trader run finished). No investor question used `latest` on a text column, so its counts are unaffected.
- **The fixes:** the prompt (shared) and `_num` (Python, made to match the site's null), not a new tool argument.
- **Python ran from the main checkout's `.venv`** (`..\erw\.venv\Scripts\python.exe`): the worktree has none.

## For Samuel's ruling

1. **A value threshold for `query`** in both loops (`above`/`below`), so "how many intervals above X" can be answered (tr15). Today the loop refuses honestly.
2. **Load `generator_pipeline_by_grid` and the nuclear outage tables into the live set**, so Ask can answer the slip and outage questions (the keys then turn to figures).
3. **`price_board_spreads.x_gas_date` is blank in every live row** though the method names it (Henry Hub's date behind a spark spread). Look at the load.
4. **`list_tables` with a grid filter hides tables that cover every grid** (iv14): list them under each grid, or say so in the rule.
5. **Ask iv18 to iv20 and the whole of both sets** in the next weekly run, now that the fixes are in (about USD 2.7).

## The cost

- Model `claude-sonnet-5-5` through the repository's client (`eval_loop.py`, ledger step `chat_eval`, ledger file not written). The runner keeps each question's cost, the sum of its model calls, from the responses' usage blocks; it does not keep one line per call.
- **Recorded: USD 3.5914 under the USD 4 cap.**
  - Session 3280: 1.6027. tr01 0.1293, tr02 0.0319, tr03 0.1021, tr04 0.1247, tr05 0.0461, tr06 0.0773, tr07 0.0582, tr08 0.1175, tr09 0.0931, tr10 0.1612, tr11 0.0684, tr12 0.0684, tr15 0.2566, tr16 0.0324, tr17 0.0871, tr18 0.0478, tr19 0.0621, tr20 0.0384.
  - Session 3281: 1.1168. iv01 0.0555, iv02 0.0386, iv03 0.0393, iv04 0.0524, iv05 0.0757, iv06 0.1652, iv07 0.0558, iv08 0.0301, iv09 0.0313, iv10 0.0321, iv11 0.0381, iv12 0.0392, iv13 0.0643, iv14 0.0816, iv15 0.0512, iv16 0.2091, iv17 0.0573.
  - Session 3282: tr13 0.1585, tr14 0.1445, iv13 0.2415, iv14 0.1604, iv15 0.1670.
- **Not recorded:** the model calls of tr13 and tr14's first asking (the exception lost the record, about 11 and 7 seconds of turns) and of iv18's interrupted first asking (stopped for memory). Each is a few cents at most. The chain's whole spend is estimated under USD 3.75.
