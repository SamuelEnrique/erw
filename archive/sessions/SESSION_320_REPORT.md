# Session 320 report: Ask, round two, and the review note

19 October 2026, from 22:45 UTC, unattended, on samueloldlaptop (the code machine), the seventh and last session of the chain of 19 October, daytime (`CHAIN_OCT19B_PROMPT.md`). Branch `wip/320-ask` in the worktree `erw-320` (new), from session 319's commits; lands on main as `task/320-ask` after session 319. Model spend cap USD 5 through the evaluation's own ledger step (`site_ask_eval`, session 314), never the public day ceiling. SPEND. No pull, no warehouse data written (the live set was read with the anon key for the expected numbers).

## Read these first

- **Thirty hard questions on the three economics pages, written and keyed before any model call** (`warehouse/chat/eval/questions_s320.yaml`, committed at `cf7a5105` before the first question was sent): ten on the battery page (`battery_stack_monthly`: the last twelve months' revenue per kW for the default battery, 81.40, its energy and ancillary parts, a 2-hour day-ahead battery, 2021 and 2025, the best month of 2025, CAISO's 4-hour battery, an 8-hour battery's discharge), ten on the generator page (`merchant_revenue_monthly`: capture prices and rates by month, a year's peaker margin and solar output per MW, SPP's wind, ISO-NE's and NYISO's hubs, the generator rule's battery, and MISO, which must refuse), ten on the datacenter page (`cost_of_power_monthly`: load-weighted and simple means, shape premiums, hours, the dearest month of 2025, ERCOT against CAISO, and PJM, which must refuse). Every expected number was computed from the tables as the site reads them by `runs/chain_oct19/s320_expect.py` (not in git); the battery page's own figure (USD 81.40 per kW) is reproduced to the cent by the first question's key, which says the aggregation mirrors the page's.
- RESULTS
- **The review note** for your evening hour: `docs/state/review_2026-10-19_code_pm.md`.
- **Then the queue step** (rule 12): QUEUE

## What to review

1. `docs/state/review_2026-10-19_code_pm.md`.
2. `warehouse/chat/eval/questions_s320.yaml` and `eval_s320_fixtures.json`.

## What was done

- `warehouse/chat/eval/questions_s320.yaml` (30 questions), `eval_s320_fixtures.json` (FIXTURES), `warehouse/chat/README.md` (one row).
- `tests/test_session320.py`.
- `docs/state/review_2026-10-19_code_pm.md`.
- Not in git: `runs/chain_oct19/s320_expect.py` (the keys' computation), `s320_ask.py` (the runner: the pages' request bodies, the evaluation's header, the cap read from the step's own ledger rows before each question, the grader of session 267).

## Checks

| Check | Exit | Result |
|---|---|---|
| `s320_expect.py` | 0 | 30 keys from the three tables; b01 equals the battery page's USD 81.40 per kW |
| The probe (one question through the evaluation's step) | PROBE | |
| The thirty questions | ASKED | |
| `tests.test_session320` | TESTS | |
| Suite, clean copy, the commit pushed | SUITE | |
| `scripts/freeze.py status` | FREEZE | |

## Landing of session 319 (recorded here: session 319's report is in that landing's own commit)

LANDING319

## Landing

LANDING

## Decisions made without you

- **The local site that asks carries `ASK_EVAL_TOKEN`, `ASK_EVAL_DAILY_USD=5` and the write key in `site/.env.local`** (an ignored file; the token was drawn at random on this machine and is nowhere else): the route then treats the runner's requests as the evaluation's and writes their calls under `site_ask_eval`.
- **Questions of a whole year ask for "the twelve months summed" or "the average of the twelve monthly figures"** so that the aggregation is the reader's words, not the tool's guess; a monthly figure is asked for its month.
- DECISIONS

## For Samuel's ruling

- RULINGS

## Files

- New: `warehouse/chat/eval/questions_s320.yaml`, `warehouse/chat/eval/eval_s320_fixtures.json`, `tests/test_session320.py`, `docs/state/review_2026-10-19_code_pm.md`, this report.
- Changed: `warehouse/chat/README.md`.
