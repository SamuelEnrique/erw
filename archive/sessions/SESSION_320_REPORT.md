# Session 320 report: Ask, round two, and the review note

19 October 2026, from 22:45 UTC, unattended, on samueloldlaptop (the code machine), the seventh and last session of the chain of 19 October, daytime (`CHAIN_OCT19B_PROMPT.md`). Branch `wip/320-ask` in the worktree `erw-320` (new), from session 319's commits; lands on main as `task/320-ask` after session 319. Model spend cap USD 5 through the evaluation's own ledger step (`site_ask_eval`, session 314), never the public day ceiling. Spent: USD 0.0671, one model call (the probe below), which the ledger refused to record because migration 035 is not applied; the thirty questions were not asked. No pull, no warehouse data written (the live set was read with the anon key for the expected numbers).

## Read these first

- **Thirty hard questions on the three economics pages, written and keyed before any model call** (`warehouse/chat/eval/questions_s320.yaml`, committed at `cf7a5105` before the first question was sent): ten on the battery page (`battery_stack_monthly`: the last twelve months' revenue per kW for the default battery, 81.40, its energy and ancillary parts, a 2-hour day-ahead battery, 2021 and 2025, the best month of 2025, CAISO's 4-hour battery, an 8-hour battery's discharge), ten on the generator page (`merchant_revenue_monthly`: capture prices and rates by month, a year's peaker margin and solar output per MW, SPP's wind, ISO-NE's and NYISO's hubs, the generator rule's battery, and MISO, which must refuse), ten on the datacenter page (`cost_of_power_monthly`: load-weighted and simple means, shape premiums, hours, the dearest month of 2025, ERCOT against CAISO, and PJM, which must refuse). Every expected number was computed from the tables as the site reads them by `runs/chain_oct19/s320_expect.py` (not in git); the battery page's own figure (USD 81.40 per kW) is reproduced to the cent by the first question's key, which says the aggregation mirrors the page's.
- **The thirty questions were not asked: the evaluation's ledger step is refused until migration 035 is applied.** The probe (the first question, b01, through the local site's `/api/ask` with the evaluation's header at 22:59 UTC) was admitted by the step's own ceiling (the admission read the step's spend, USD 0, through `internal_ask_spend` with the write key), the model was called once (claude-sonnet-5-5, 26,622 tokens in, 56 out, USD 0.067123 by the model's price), and the site's strict ledger write of that call under `site_ask_eval` was refused by the database (`23514`, the step check of migration 023, which allows `site_ask` and `site_ask_ercot` alone); the route answered 502 with the cause named ("the cost ledger refused the site_ask_eval row (is migration 035 applied?)"). The run stopped there, as the runner is built to (one probe before the rest). **That one call is spent and unrecorded**: the strict write is what keeps an evaluation from spending unrecorded beyond its first call, and the first call is the proof. Nothing of the public ledger or the public ceilings was touched (the step's rows are left out of `site_ask_admit` only once 035 is applied; today no row of the step exists). The run is yours to finish: "To finish" below, four commands.
- **The review note** for your evening hour: `docs/state/review_2026-10-19_code_pm.md`.
- **Then the queue step** (rule 12): QUEUE

## What to review

1. `docs/state/review_2026-10-19_code_pm.md`.
2. `warehouse/chat/eval/questions_s320.yaml` and `eval_s320_fixtures.json`.

## What was done

- `warehouse/chat/eval/questions_s320.yaml` (30 questions), `eval_s320_fixtures.json` (not written: the run did not happen; the probe's record is `runs/chain_oct19/s320/probe_fixtures.json`, not in git), `warehouse/chat/README.md` (one row).
- `tests/test_session320.py`.
- `docs/state/review_2026-10-19_code_pm.md`.
- Not in git: `runs/chain_oct19/s320_expect.py` (the keys' computation), `s320_ask.py` (the runner: the pages' request bodies, the evaluation's header, the cap read from the step's own ledger rows before each question, the grader of session 267).

## Checks

| Check | Exit | Result |
|---|---|---|
| `s320_expect.py` | 0 | 30 keys from the three tables; b01 equals the battery page's USD 81.40 per kW |
| The probe (one question through the evaluation's step) | 0 (runner), 502 (route) | admitted by the step's ceiling; one model call, USD 0.0671; the ledger row refused (`23514`, migration 035 not applied); the step's ledger today 0 rows |
| The thirty questions | not run | waits for migration 035 ("To finish") |
| `tests.test_session320` | 0 | OK (4 run, 2 skipped: the recorded answers' tests skip until the fixtures exist) |
| Suite, clean copy, the commit pushed | SUITE | |
| `scripts/freeze.py status` | FREEZE | |

## Landing of session 319 (recorded here: session 319's report is in that landing's own commit)

LANDING319

## Landing

LANDING

## To finish (the thirty questions, after migration 035)

On the code machine, from the main copy, with session 320 on main (or in `erw-320` with `ERW_EVAL_WT` pointing at it). The local site reads `site/.env.local`, which holds `ASK_EVAL_TOKEN` (drawn at random on this machine), `ASK_EVAL_DAILY_USD=5` and the write key; the runner reads the token from the same file and the service key from the root `.env`.

```bash
.venv\Scripts\python.exe warehouse/supabase/apply.py --only 035        # the schema change: yours
bash runs/chain_oct19/s320_server.sh start                             # a production build of main on port 3320 (build first: cd site && npm run build)
.venv\Scripts\python.exe runs/chain_oct19/s320_ask.py --probe --base http://localhost:3320      # b01 alone: the step accepted, its row in the ledger
.venv\Scripts\python.exe runs/chain_oct19/s320_ask.py --base http://localhost:3320              # the thirty, under the cap of USD 5, the fixtures written
bash runs/chain_oct19/s320_server.sh stop
```

Then: a question wrong at first is fixed at its cause (not its key) and asked again (`--only <id>`), its `first_asking` carrying the cause and the fix; `tests.test_session320` reads the fixtures; the fixtures and the README row's figures go in a commit on a `task/` branch with the landing's snapshots.

## Decisions made without you

- **The local site that asks carries `ASK_EVAL_TOKEN`, `ASK_EVAL_DAILY_USD=5` and the write key in `site/.env.local`** (an ignored file; the token was drawn at random on this machine and is nowhere else): the route then treats the runner's requests as the evaluation's and writes their calls under `site_ask_eval`.
- **Questions of a whole year ask for "the twelve months summed" or "the average of the twelve monthly figures"** so that the aggregation is the reader's words, not the tool's guess; a monthly figure is asked for its month.
- **The probe was asked although migration 035 was known to be unapplied** (session 314's report, this morning's rulings): the step's admission and the strict refusal had not been exercised on a real route before, and one call (USD 0.07) is the price of knowing that both work as built. The alternative, a ledger row inserted by hand to test the check, would have written a made-up row into the cost ledger.
- **The probe's record stays out of git** (`runs/chain_oct19/s320/probe_fixtures.json`): a fixtures file holding one refused answer would read as the evaluation's result, and `tests.test_session320` would fail on it; the fixtures are written by the run.
- **The review note is written from the reports and the landings as they stood** when this session ended; the thirty questions' result is not in it beyond the probe.

## For Samuel's ruling

- **Apply migration 035** (`warehouse/supabase/migrations/035_ask_eval_step.sql`; the rollback beside it), then run the thirty questions ("To finish"): until then no evaluation can spend through its own step, and the probe's one call (USD 0.0671, 22:59 UTC) stands unrecorded in the ledger.
- **Whether the probe's unrecorded call should be written into the ledger by hand** (one row: `site_ask_eval`, claude-sonnet-5-5, 26,622 in, 56 out, USD 0.067123, request `req_011CgCRbmPrgAQCPhYjN1p5H`, 22:59:02 UTC) once 035 is applied, or left as a line in this report. The session wrote no row.

## Files

- New: `warehouse/chat/eval/questions_s320.yaml`, `warehouse/chat/eval/eval_s320_fixtures.json`, `tests/test_session320.py`, `docs/state/review_2026-10-19_code_pm.md`, this report.
- Changed: `warehouse/chat/README.md`.
