# Session 176 report: the cost audit, and a daily cap for the scheduled model steps

Run on 10 October 2026 (UTC), from 07:57, unattended, first of the chain 176 to 180 (`CHAIN_OCT10_PROMPT.md`; the rules
of `CHAIN_OCT8_PROMPT.md` apply, deploys allowed). Built in the main copy on `wip/176-costs`. Outputs under
`runs/session176/`. Model spend: USD 0 (no model call was made).

## Read these first

- **USD 74.58 of the USD 75 is traced, call by call** (5,009 calls, 1 October to 10 October 01:58 UTC). The rest is
  about USD 0.30 of session 175's two calls that were paid before the ledger refused to write (estimated, in no ledger).
- **The schedule is not where the money went.** The steps that run on a clock cost USD 14.47 in nine days (19 percent;
  USD 1.37 to 3.31 a day). Sessions' test batches and tools cost USD 60.11 (81 percent): Ask ERCOT evaluation batches
  USD 31.03 (through the site USD 18.21, through the warehouse USD 12.82), the Thesis Builder USD 16.10, the policy
  audit USD 6.07, the deals rerun USD 4.27.
- **The cap is built: `DAILY_MODEL_USD`, default 1.00, asked before every scheduled model step.** At the cap a step is
  skipped with a row of `erw_health` and a line in the same-day email, and the digest and the Roundup are written
  without their model-written parts and still publish.
- **At today's costs the default bites every day.** News scoring alone costs about USD 1.10 a run, so once the key
  works again, every later model step of the day (policy, deals, datacenters, the fun fact, the digest's headlines and
  summary) is skipped until you raise the cap or rule on cut 1 below. With cut 1 the whole day costs about USD 0.73.
- **Nothing else was switched off.** The Anthropic key is still at its usage limit until 1 November (session 175), so
  no scheduled model step can spend today whatever the cap says.

## What to review

1. `https://erw-flame.vercel.app/internal/costs` (internal view): the page as before. It reads Supabase's copy of the
   ledger, which stops at 8 October 10:21 UTC (the loader failed from 5 to 9 October), so it shows USD 44.64 of the
   warehouse's USD 54.71 for October: about USD 10 of the daily run's own calls (6 to 9 October) are in the archive
   bucket and not yet on the page. The first good load carries them.
2. GitHub, the repository's Settings, "Secrets and variables", "Actions", the tab "Variables": to change the cap, click
   "New repository variable", name `DAILY_MODEL_USD`, value for example `1.50`. No variable means USD 1.00; `0` means
   no scheduled model step runs.
3. `runs/session176/digest_no_model_sample.md` on this machine: what a digest reads like at the cap (written from the
   real stories of 8 and 9 October with no model call). Its second line: "Today's headlines are the publishers' own
   titles, and the written summary of the numbers is left out: the day's model budget was reached."
4. `https://erw-flame.vercel.app/data/methods/api_cost_ledger` (internal view): the new last section, "The daily cap
   for scheduled model steps (session 176)".

## Where USD 74.58 went, by step

| What | USD | Calls | Share | Model | Who ran it |
|---|---|---|---|---|---|
| Ask ERCOT, through the site's route (`site_ask_ercot`) | 18.92 | 1,889 | 25.4% | Sonnet 5.5 (9 calls Haiku 4.5) | USD 18.21 in six batch hours of 149 to 756 calls (chains of 6 to 8 October); USD 0.71 outside them |
| Thesis Builder (`thesis`, `thesis_gate`) | 16.10 | 69 | 21.6% | Sonnet 5.5; Haiku 4.5 since session 169 | 18 runs, mean USD 0.89, largest 1.42 (sessions 135, 142, 147, 158, 169) |
| Chain test batches: Ask ERCOT evaluations in the warehouse (`chat_ercot_eval_*`) | 12.82 | 1,595 | 17.2% | Sonnet 5.5 | sessions 92, 114, 121 (4 and 5 October) |
| News scoring (`news_score`) | 8.57 | 127 | 11.5% | Sonnet 5.5 | the daily run, 9 runs |
| The policy audit (`policy_recheck_*`) | 5.30 | 273 | 7.1% | Sonnet 5.5 | session 157 (8 October) |
| Chain test batches: the deals rerun (`deals_extract_v3*`) | 4.27 | 539 | 5.7% | Sonnet 5.5 | session 130 (6 October) |
| Policy reads (`policy_reads`) | 2.13 | 144 | 2.9% | Sonnet 5.5 | the daily run; USD 1.83 of it on 8 October (129 calls) |
| Deals extraction (`deals_extract`) | 1.53 | 35 | 2.1% | Sonnet 5.5 | the daily run |
| News scoring, the Haiku shadow (`news_score_shadow`) | 1.34 | 46 | 1.8% | Haiku 4.5 | the daily run, 2 to 5 October, then its expiry |
| Chain test batches: Texas tariff reads | 0.97 | 17 | 1.3% | Sonnet 5.5 | sessions 138, 140 |
| The general chat, through the site (`site_ask`) | 0.95 | 83 | 1.3% | Sonnet 5.5 | USD 0.23 in one batch hour (4 October), the rest single questions |
| The policy audit: rule reads (`rule_reads`) | 0.77 | 141 | 1.0% | Sonnet 5.5 | session 154 |
| Datacenter extraction | 0.36 | 17 | 0.5% | Sonnet 5.5 | the daily run |
| Digest | 0.26 | 14 | 0.3% | Sonnet 5.5 | the daily run, weekdays |
| Policy scoring | 0.16 | 7 | 0.2% | Sonnet 5.5 | the daily run |
| Fun fact | 0.05 | 6 | 0.1% | Sonnet 5.5 | the daily run |
| Roundup | 0.04 | 4 | 0.1% | Sonnet 5.5 | Sunday 4 October (written twice, session 119's fault) |
| Roundup: the chart's note | 0.02 | 3 | 0.0% | Sonnet 5.5 | the same |
| **Total** | **74.58** | **5,009** | | Sonnet 5.5 USD 72.52, Haiku 4.5 USD 2.06 | |

## By day (USD)

| Day (UTC) | Scheduled steps | Ask ERCOT and chat on the site | Thesis Builder | Sessions' batches and audits | Total |
|---|---|---|---|---|---|
| 1 October | 0.64 | 0.11 | 0 | 0 | 0.74 |
| 2 October | 1.15 | 0 | 0 | 0 | 1.15 |
| 3 October | 1.73 | 0 | 0 | 0 | 1.73 |
| 4 October | 1.56 | 0.28 | 0 | 4.76 | 6.60 |
| 5 October | 1.74 | 0.42 | 0 | 8.06 | 10.22 |
| 6 October | 1.53 | 6.41 | 6.12 | 4.27 | 18.32 |
| 7 October | 1.37 | 2.90 | 6.20 | 0.97 | 11.45 |
| 8 October | 3.31 | 9.29 | 3.08 | 6.07 | 21.76 |
| 9 October | 1.44 | 0.31 | 0.70 | 0 | 2.45 |
| 10 October (to 01:58) | 0 | 0.16 | 0 | 0 | 0.16 |
| **Total** | **14.47** | **19.87** | **16.10** | **24.13** | **74.58** |

- The full table by step and day: `runs/session176/by_category_day.csv`; every call: `all_calls_october.csv`.

## Each scheduled step: its model and its cost per run

| Step (ledger name) | Model | Runs | Mean USD a run | Least | Most | Calls a run |
|---|---|---|---|---|---|---|
| News scoring (`news_score`) | Sonnet 5.5 | 9 | 0.95 (1.10 since 5 October) | 0.46 | 1.11 | 14 (16 since 5 October) |
| Policy reads (`policy_reads`) | Sonnet 5.5 | 6 | 0.36 (0.06 without 8 October) | 0.02 | 1.83 | 24 (3 without 8 October) |
| News scoring, the shadow (`news_score_shadow`) | Haiku 4.5 | 4 | 0.34 | 0.29 | 0.35 | 11.5 |
| Deals extraction (`deals_extract`) | Sonnet 5.5 | 8 | 0.19 | 0.16 | 0.22 | 4.4 |
| Digest (`digest`), weekdays | Sonnet 5.5 | 5 | 0.05 (0.04 since 6 October) | 0.04 | 0.07 | 2.8 |
| Datacenter extraction (`datacenters_extract`) | Sonnet 5.5 | 8 | 0.045 | 0.03 | 0.05 | 2.1 |
| Policy scoring (`policy_score`) | Sonnet 5.5 | 7 | 0.023 | 0.005 | 0.06 | 1 |
| Roundup (`roundup`), Sundays | Sonnet 5.5 | 2 | 0.022 | 0.022 | 0.022 | 2 |
| Fun fact (`funfact`), weekdays | Sonnet 5.5 | 3 | 0.017 | 0.017 | 0.017 | 2 |
| The chart's note (`analysis_note`), Sundays | Sonnet 5.5 | 2 | 0.006 | 0.006 | 0.006 | 1 |

- A run is one UTC day of the daily workflow (the Roundup: one Sunday). Every scheduled step picks the newest
  Sonnet-class model (`score.pick_model`); only the shadow scorer was set to Haiku.
- A weekday now costs about USD 1.45 (1.10 + 0.19 + 0.06 + 0.045 + 0.04 + 0.02 + 0.017): about USD 44 a month.
- Not on a clock: Ask ERCOT and the chat (Sonnet 5.5, about USD 0.01 a call in a warm batch, USD 0.16 for one cold
  question of two calls on 10 October); the Thesis Builder (Haiku 4.5 research and Sonnet 5.5 writing since session
  169, capped at USD 1.00 a run).

## The daily cap (what was built)

- `warehouse/health.py`: `budget --step <name>` (exit 0 under the cap, 75 at it), `model_cap()`, `model_spend()` (the
  day's rows of the ten scheduled steps, this machine's ledger joined by `event_id` with Supabase's copy),
  `SCHEDULED_MODEL_STEPS`; `alert_line()` now also tells of steps the cap skipped.
- `warehouse/run_daily.sh`: `model_step` asks the budget before each of its nine steps. At the cap: the step is not
  run and the status file says why; the digest (`news_brief`) runs with `--no-model` instead.
- `.github/workflows/roundup.yml`: the chart's note and the Roundup each ask the budget; at the cap they run with
  `--no-model`. Both workflows pass `DAILY_MODEL_USD` from the repository variable of that name.
- `warehouse/news/brief.py`, `roundup.py`: `--no-model` (the lead story's own title as the headline, no written
  summary of the numbers, one line under the title saying so; no client is built). `without_repeats()`: a policy
  action that repeats a story above it is dropped and logged instead of stopping the whole digest (found by the new
  test: with publishers' titles a Department of Energy release was both a story and a policy action).
- `docs/methods/api_cost_ledger.md`: the cap's section. `tests/test_session176.py`: 24 tests. `tests/test_session173.py`:
  one assertion brought to the new workflow line (same meaning: restore, analysis, Roundup, in that order).
- How loud a skip is: the job log (`::warning title=<step> skipped by the daily model cap`), a row of `erw_health`
  (status skipped, reason "daily model cap reached: USD x spent today ... of USD y (DAILY_MODEL_USD); <step> not run"),
  the next day's health summary ("Skips, by reason"), and the same-day email: subject "ERW: the daily model cap skipped
  N steps", line "The daily model cap reached: USD x spent today ... : N model steps not run (names)."

## Proposed cuts, for your ruling (each with its saving)

| # | Cut | Saving | What it costs |
|---|---|---|---|
| 1 | News scoring on Haiku 4.5 instead of Sonnet 5.5 | about USD 0.76 a day, USD 23 a month (Haiku scored the same stories for USD 0.34 a run against Sonnet's 1.10) | read the shadow comparison first (`warehouse/news/shadow.py`, 2 to 5 October): scores differ where they differ. With it the whole day is about USD 0.73, under the cap, and nothing is skipped |
| 2 | A ceiling on a chain's evaluation batch: at most 30 questions against the model, the rest against the recorded fixtures (`site/scripts/record-ask-fixture.mjs`) | six site batches and three warehouse batches cost USD 31.03 in five days; at 30 questions a batch about USD 3: USD 28 saved over the same work | less statistical power per evaluation; a full batch then needs your word in the prompt |
| 3 | The cap checked before every call, not only before a step (`warehouse/llm.py`, for the scheduled session) | bounds one runaway step: 8 October's policy reads ran 129 calls for USD 1.83 inside one step | a step can stop half way; each step must then leave its table whole (to be tested per step) |
| 4 | Policy reads: at most 10 reads a run, the backlog spread over days | USD 1.7 on a day like 8 October; nothing on a usual day (USD 0.06) | a backlog takes more days to read |
| 5 | Deals and datacenter extraction on Haiku 4.5 | about USD 0.15 a day, USD 4.50 a month, if Haiku costs them what it costs scoring (0.31 of Sonnet); not measured for these steps | extraction quality on Haiku is untested here: a shadow week first |
| 6 | Deals and datacenter extraction on Mondays and Thursdays only | about USD 0.17 a day, USD 5 a month | a deal reaches the tables up to three days later |
| 7 | Remove `SHADOW_MODEL: claude-haiku-4-5` from the two workflows | USD 0 now (the shadow expired on 5 October by `shadow.yaml`); it removes the chance of USD 0.34 a day returning with a new expiry date | none |
| 8 | A monthly ceiling for sessions' model work, enforced in `llm.py` for any `ERW_SESSION` (for example USD 30 a month, raised by you in a prompt) | sessions' batches, audits and tool runs were USD 60 of the 75 | a chain stops spending at the ceiling and reports |

- Already done by earlier sessions, counted in no cut: the Thesis Builder's redesign (about USD 0.26 to 0.35 a run
  since session 169 against a mean of 0.89 before); the Roundup no longer written twice (session 119).
- The policy audit (USD 6.07) was a one-time read; no recurring saving.

## Checks, each its own command, exit code read (outputs under `runs/session176/`)

| Check | Exit | File |
|---|---|---|
| `attribute.py`, `attribute2.py` (read-only) | 0, 0 | `attribute.out`, `attribute2.out` |
| `restore.py api_cost_ledger --from-bucket --out runs/session176/ledger_from_bucket.csv` (3,461 rows; a scratch file) | 0 | `restore_bucket.out` |
| `tests.test_session176` (24 tests) | 0 | `test_176.out` |
| tests 61, 119, 30, 166, 173, 170, 116 alerts, 91, 176 (183 tests, 1 skipped) | 0 | `test_neighbours.out` |
| `bash -n warehouse/run_daily.sh` | 0 | in the session's log |
| `health.py budget --step news_score` on this machine (USD 0.00 of 1.00, the step runs) | 0 | in the session's log |
| a whole digest with `--no-model` and a client that fails if built | 0 | `sample_digest.out`, `digest_no_model_sample.md` |

## Decisions made without you

1. **The cap is checked before each step, as the prompt says ("the remaining model steps are skipped"), not before each
   call.** A step that starts under the cap finishes; the day can end above the cap by that step's cost. Cut 3 is the
   stricter form.
2. **What counts toward the cap: the ten scheduled steps only**, for the run's own ledger session (`daily` on GitHub).
   Sessions' work, the Thesis Builder and the site's ledger are not counted: the site has its own daily ceiling
   (migration 023), and counting a Thesis Builder run would switch the schedule off, which the prompt forbids.
3. **A budget that cannot be read lets the step run** and records a failed row "model budget" (in the email). The
   other choice, skipping, would switch every model step off on a fault of the new check.
4. **At the cap the digest's headlines are the publishers' own titles** and one line under the title says so. The
   stories, their scored reasons, the numbers and the sources are unchanged. The fun fact is absent that day (its step
   is skipped, and the digest already omits the section when there is no item).
5. **The cap is a repository variable, not a secret**, so its value shows in the workflow's page and you can change it
   without a session.
6. **`without_repeats()` also applies on an ordinary day.** It only changes a digest that the hard check would have
   refused to write at all.
7. **No ledger write from this machine.** Its copy of the ledger lacks the daily run's 282 rows of 5 to 9 October
   (never synced) and holds 14 rows of session 169 the bucket lacks. Archiving from a copy that is behind could write
   those 282 rows as deletions, so nothing was archived; see "To finish".

## To finish

- Samuel: rule on the cuts above (1 and 2 are the two that matter), and raise the key's limit when you want the
  schedule to spend again (session 175).
- The 14 ledger rows of session 169 (USD 0.70) are on this machine only. To carry them: `python scripts/sync.py`
  (pulls the daily run's rows into this machine's tables, under the data lock), then the archive write and the load of
  `api_cost_ledger` as `roundup.yml` lines 255 to 259 do. Not done tonight: it is a locked write of about 15 minutes
  that no page needs.

## The landing

