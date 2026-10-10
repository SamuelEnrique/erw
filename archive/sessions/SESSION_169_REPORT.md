# Session 169 agent report: Thesis Builder, the gate, the bug and the cheap redesign

Working copy `C:\Users\lossa\Documents\erw-144`, branch `wip/169-thesis`. Nothing pushed, nothing merged, no lock
taken, nothing written into the main copy's `warehouse/output` or `warehouse/metadata`. Built 06:34 to 07:35 UTC,
9 October 2026.

## Read these first

- **Three parts, four commits, all checks pass.** B `a7f85a0`; A `f783854` + `feecc9d`; C `a7551f7` (last).
  **A and B can land alone** (merge up to `feecc9d`): their checks passed at that commit (113 of 113 on the stand-in).
- **Migration 026 must be applied** (`026_thesis_gate.sql`: one nullable column `thesis_runs.gate`, one function
  `thesis_submit_forced`, the step `site_thesis_gate` admitted in `site_api_calls`; nothing of 024 or 025 replaced).
  Until it is, "Run anyway" answers "Run anyway is not switched on yet" and queues nothing (fails closed); every other
  path works.
- **Spend USD 0.70 of 4.00** (ledger 0.696 + one lost call of at most 0.0025). **Requests 21 of 100.** Two runs at
  USD 0.25 and 0.26, about two minutes each (the old run of the same niche: USD 1.00, 8.2 minutes).
- **Weak point, said plainly:** the trend charts. Only the EIA was reachable (BLS's robots.txt disallows everything;
  Census and FRED ask keys the `.env` lacks), so run 1 drew **0 of 5** trends and run 2 **1 of 5**. Every undrawn
  trend says "no real series: not drawn". Adding a FRED and a Census key would widen it (decision for you).
- **Two of my mistakes cost money and left rows:** one gate call (lost answer, ledger refused without the lock) and
  one research call of USD 0.18 (run `20261009T070917Z-3dee0e`, a signature bug, now tested). That run's row is on
  production as "failed" with usd 0; the ledger holds its real cost.

## What to review (after the landing and the migration)

Internal view first (`https://erw-flame.vercel.app/internal/unlock?token=...`, as always).

1. `https://erw-flame.vercel.app/thesis`: the form reads "Niche: one product or business, for one customer", the
   placeholder "For example: AI software that maps hidden geothermal resources", the help line, three example chips.
   Type `oil & gas demand`, press **Run**: the refusal "“oil & gas demand” is a sector or a market topic, not a
   niche..." with four chips (Methane leak detection for upstream operators, ...), nothing queued. Click a chip: it
   fills the box. Tick **Run anyway** only if you want a real run (it costs up to USD 1 and is marked "run anyway").
2. `https://erw-flame.vercel.app/thesis?run=20261009T071419Z-7c6826&tab=trends` (run 2, methane): trend 1 states
   its Fact and draws "U.S. Natural Gas Vented and Flared (MMcf)" (hover: year and value), the EIA source line under
   it, "The values" folds out; trends 2 to 5 read "no real series: not drawn" (reason on hover).
3. Same run, tabs **Timing** ("deploying", with evidence), **Capital**, **Policy** (4 actions from the policy
   monitor), **References** (31 sources), then **Company landscape**, **Deal funnel**, **Pipeline map**, **Success
   stories**, **Investors**: each greyed, "Connect PitchBook or Harmonic to fill this", with its columns.
4. `https://erw-flame.vercel.app/thesis?run=20261009T071056Z-e09496` (run 1, geothermal): Scope shows In scope and
   Sub-segments; Trends: five Facts, no chart (see above).
5. An old run, `https://erw-flame.vercel.app/thesis?run=20261008T101706Z-605e62&tab=landscape`: its company
   landscape, funnel (with its chart) and pipeline exactly as before; Timing says "This run was written before the
   Timing tab existed."; References lists its 127 sources.

## Part B: the short-word bug (`a7f85a0`)

- `run.words_of` and the policy words (`run.py` line 883, and `build.py` line 710 with the same bug) now keep oil,
  gas, ev, ai, lng, smr, ccs, dac, pv, h2, co2, each as a whole word ("oil" is not in "soil", "ev" not in
  "development"); every longer word reads exactly as before (tested against the old regex).
- Before the fix "oil and gas" had no word at all, so `warehouse_candidates` returned nothing.
- `tests/test_session169.py`: 13 tests for B.

## Part A: the gate on the niche (`f783854`, `feecc9d`)

- `site/lib/thesis/niche.ts`: the one module the form (`RunForm.tsx`) and the route (`api/thesis/run/route.ts`)
  read. Rules: refuse under two content words or all sector/market words; pass on something sold or a customer
  ("for <someone>", not a commodity). Curated table of 13 inputs (the owner's two lists word for word). Outside the
  table one Haiku 4.5 call (`nicheModel.ts`: no retry, 8 s, 40 an hour an instance, `THESIS_GATE_MODEL=0` switches it
  off; site ledger step `site_thesis_gate`); if it fails the rules decide (default chips). A chip offered never
  leads to a second refusal.
- Run anyway: stored on the run (migration 026), copied by the runner onto the report (`report.gate`), marked "run
  anyway" beside the niche with the reason on hover.
- Measured gate call: 452 in, 93 out, USD 0.000917.

## Part C: the cheap redesign (`a7551f7`)

- `run.COMPANY_SEARCH = False`: no company web search, no tie checks, no page fetch, no evidence store. The old
  `execute()` is kept whole (switching back also needs `RUN_USD` 2.00: its stages do not fit under 1.00).
- `run.execute_market`: research (Haiku, 8 searches) > two extractions (Haiku) > series pick (Haiku) > pulls in code
  (`warehouse/thesis/series.py`) > writing (Sonnet 5.5) with the literal-number check > policy pick (Haiku).
  RUN_USD 1.00; stage reserves sum to 0.91. A written Fact with a number no source holds is replaced by the cited
  claim (run 2: 3 of 5 were).
- Report version 2 keeps every version 1 key; the page draws v2 with the new tabs and v1 exactly as before.
- PitchBook paste: unchanged format and gate; a run naming no company asks PitchBook for up to 60 companies of its
  own; a pasted answer fills all five connector tabs, every row tagged PitchBook (tested on the stand-in).
- Harmonic answers are not mapped into the connector tabs (they show in the existing provider blocks only).
- The funnel's columns: **the MCJ workbook is not on this machine** (searched Documents, Downloads, Desktop); a
  stand-in set of 10 columns is used and named as such in the code.

## Test runs (cost from the ledger)

| Run | Run id | Cost | Time | Result |
|---|---|---|---|---|
| 3, "oil & gas demand" | none (refused) | 0 | 0.25 s | 422, the four oil and gas chips; no model, no row |
| 1 (failed attempt) | `20261009T070917Z-3dee0e` | 0.1793 | 1.1 min | my bug, answer lost; row "failed" |
| 1, "Geothermal mapping and sensing, US startups" | `20261009T071056Z-e09496` | 0.2538 | 2.2 min | 5 trends, 0 drawn; 11 capital rows, 6 incumbents, 5 risks, 1 policy, 33 sources; timing "deploying" |
| 2, "Methane leak detection for oil and gas operators" | `20261009T071419Z-7c6826` | 0.2620 | 2.0 min | 5 trends, 1 drawn (EIA vented and flared); 6 capital, 5 incumbents, 7 risks, 4 policy, 31 sources |

- **Run 1 beside the old run of the niche (`20261008T101706Z-605e62`, USD 1.00, 8.2 min):** better: a quarter of
  the cost and time, scope with in/out and sub-segments, 11 capital rows (3 before), 6 incumbents (3), a timing
  verdict, policy, no ranking of companies. Worse: no company names at all until a provider is pasted (4 on its
  landscape, 41 in its funnel before), 33 sources (127), and trends lean to EGS generally (the old ones were closer
  to mapping and sensing: AI prospecting, fiber sensing); no trend drawn (the old run drew one table chart).
- Run 2's fact quality: several Facts ran to two sentences or fell back to a claim with "(not confirmed: x)". After
  the runs I tightened the writer (numbers only from series or passages, ONE sentence) and drew annual series from
  their latest 30 years (run 2 drew 89 years from 1936). **These two changes are tested with stand-ins, not by a
  paid run.**

## Requests (ceiling 100): 21

- Robots and terms first: api.eia.gov (no robots file; answers its key error), api.bls.gov robots "Disallow: /",
  api.census.gov robots allow; www.eia.gov terms read (SHA-256 28ef6560399ba7c7..., 06:59:31 UTC); www.bls.gov 403
  (terms not read); www.census.gov terms read (12659f08763e185b..., 06:59:32 UTC). Saved in `runs/session169/terms/`.
- By host: api.eia.gov 10, api.census.gov 4, api.bls.gov 2, www.eia.gov 2, www.census.gov 2, www.bls.gov 1.
- One run makes at most 1 robots read + 5 series requests; `series.MAX_REQUESTS_RUN` = 20 holds a production run.
- EIA terms quoted in `docs/methods/thesis.md`; every EIA source line reads "Source: U.S. Energy Information
  Administration (<date>), <title>." as its terms ask.

## Checks (outputs in `runs/session169/`)

| Check | Exit |
|---|---|
| `tests/test_session169.py` (30) | 0 (`c_test169.out`) |
| thesis tests 135, 142, 147, 150, 158, 160, 169 (296) | 0 (`c_thesis_tests_4.out`) |
| whole Python suite, `unittest discover -s tests` (2,640, 212 skipped) | 0 (`c_full_suite.out`) |
| `test-thesis-niche.mjs` 16, `test-thesis-market.mjs` 7, `-pitchbook`, `-providers`, `-paste` | 0 each |
| `npx tsc --noEmit -p .` | 0 (`c_tsc.out`) |
| `npx eslint` on 14 thesis files | 0, one warning in an old line of `check-thesis-real.mjs` |
| `npm run build` under the mutex (07:20:45 to 07:21:16) | 0 (`c_build.out`) |
| `check-thesis.mjs` on the stand-in, port 3169 | 0, 129 of 129 |
| `check-thesis.mjs` on the real database | 0, 34 of 34 |
| `check-thesis-real.mjs` runs 1, 2 and the old run | 0, 0, 0 |
| Part A alone at `f783854`: stand-in check 113 of 113, build 0 | 0 |

- Tests changed on purpose: 142 (sets `COMPANY_SEARCH` and `RUN_USD` 2.0 for the old path), 158 and 160
  (`RUN_USD` 1.0; migration 026 listed; `where run_id` 4: the gate's select), `test-thesis-pitchbook.mjs` (the new
  tab list), `check-thesis.mjs` (the form's niche now names software, so no check can reach the model),
  `check-thesis-real.mjs` (a v2 funnel is a connector tab).
- No process left running (3169 and the stand-in stopped).

## Decisions made alone

- A sector-only input that names a customer after "for" passes ("storage for data centers"); "for data centers"
  alone or "AI for energy" does not.
- Business types (developers, installers, operators) are not "something sold": such inputs go to the model.
- The table's chips, the examples and the placeholder pass as curated niches.
- A ticked Run anyway asks nothing of the model; a niche the rules pass is an ordinary run whatever the box says.
- Run anyway without migration 026 fails closed rather than queue a run without its flag.
- The EIA API's key error on /robots.txt is read as "no robots file" (the ERW's daily connectors use the API).
- Monthly Energy Review series (geothermal, solar, wind consumption) added to the EIA list after run 1; titles come
  from EIA's answer where it gives one, and an answer naming another series is refused.
- No rerun of run 1 or 2 after the writer fix: the brief allows three runs.

## Hand-over commands (in order)

1. Land A and B (and C if you take it): merge `wip/169-thesis` (A+B alone: up to `feecc9d`). Site files changed:
   `site/app/thesis/page.tsx`, `site/app/api/thesis/run/route.ts`, `site/components/thesis/RunForm.tsx`,
   `Report.tsx`, `site/lib/thesis/{niche,nicheModel,server,types,view}.ts`; no shared file touched.
2. Migration (production): `cd C:/Users/lossa/Documents/erw` then
   `C:\Users\lossa\Documents\erw\.venv\Scripts\python.exe warehouse/supabase/apply.py --only 026`
3. Ledger rows, under the lock:
   `C:\Users\lossa\Documents\erw\.venv\Scripts\python.exe warehouse/lock.py run --task "session 169 ledger rows" -- C:\Users\lossa\Documents\erw\.venv\Scripts\python.exe runs/session169/ledger_merge.py`
   (dry run passed: 14 rows, USD 0.696).
4. Nothing else needs the lock. `thesis.yml` now passes `EIA_API_KEY` (the secret the daily run uses).

## Landing state (added by the chain's session 166 at 22:30 UTC on 9 October 2026)

- This report is the agent's report of the session, kept whole; this section is what happened after the hand-over.
- **Not landed.** The account's usage limit paused the chain from about 08:15 to 22:00 UTC, so the deploy cutoff (15:00 UTC)
  passed with nothing of this session on production. Nothing was pushed to `main` or to a `task/` branch after the cutoff.
- The branch is on GitHub: `wip/169-thesis` (`a7551f7`). Not merged into the landing branch (its own landing, after 166 to 168). To finish, from the main copy, outside 14:04 to 16:10 UTC:

```
cd C:/Users/lossa/Documents/erw
git fetch origin && git checkout wip/169-thesis && git merge origin/main      # after the 166 to 168 landing
'C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe' warehouse/supabase/apply.py --only 026      # 026_thesis_gate.sql
'C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe' runs/session169/ledger_merge.py --dry        # 14 rows, USD 0.696
'C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe' warehouse/lock.py run --task "session 169 ledger rows" -- 'C:/Users/lossa/Documents/erw/.venv/Scripts/python.exe' runs/session169/ledger_merge.py
cd site && npm run build; echo "exit=$?"; cd ..
node site/scripts/snapshot-live.mjs take 169_before
git push origin wip/169-thesis:task/169-thesis
python runs/gh_api.py wait task/169-thesis 15
node site/scripts/snapshot-live.mjs take 169_after && node site/scripts/snapshot-live.mjs compare 169_before 169_after
```
Spend: USD 0.70 of 4.00 (ledger 0.696).
- No em dash in this file (checked).

## Landing state (added by the chain's session 172 at 02:15 UTC on 10 October 2026)

- **Landed in full** (`a7551f7`, merged into `wip/172-land` with session 172's part D, pushed as `task/169-172-chain` at 02:02 UTC on 10 October 2026, checks run 38015478252 passed, merge `e9023b1`, production at 02:09:31 UTC). Migration `026_thesis_gate.sql` applied at about 02:05 UTC (`runs/session172/apply_026.out`); `thesis_submit_forced` answers 'not authorized' to a wrong token and `{ok: false, reason: input}` to a gate that is not forced, with no run queued (`runs/session172/forced_probe.out`). The 14 ledger rows (USD 0.696) were merged into the main ledger under the data lock. On production in the internal view the form reads as written above and `POST /api/thesis/run` with "oil & gas demand" answers 422 with the refusal and the four chips, no model call, nothing queued. Snapshots `172_before` and `172_after`: 0 differences on the 25 pages. Details: `archive/sessions/SESSION_172_REPORT.md`.
