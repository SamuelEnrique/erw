# Progress of chain 701 (data machine, first window, 26 November 2026)

One line a landing, request, repair, source, table, file or view: its state and session. The chain file is `queue/done/701-night-26-november-desktop-repairs-equities-large-load.md`.

## The start (session 10000)

- start 1, main brought to origin/main: done, session 10000. Main was behind by one commit and ahead by none, so it fast-forwarded; nothing was pushed aside. Untracked files left where they are: `site/data/findings/queue_divorce__first_year-2010.json`, `site/public/findings/erw_2026_queue_outcomes_technology__first_year-2010.csv`, `site/public/findings/queue_divorce__first_year-2010.do`, `site/public/findings/queue_divorce__first_year-2010.py`, `warehouse/output/retired/` (and the ignored `runs/`, `warehouse/output/` and the like, untouched).
- start 2, precheck: done, session 10000 (exit 0, on duty until 2026-11-27 02:50 UTC). Drive C 30 GB free, memory 7.2 of 15.7 GB free (10:50 UTC). Chain file taken by `chain_queue.py next --file` (commit `1a0606f86`, pushed).
- start 3, resume file `queue/next/702-resume-chain-701.md`: done, session 10000 (commit `1b7814005`, pushed alone).
- start 4, this file: done, session 10000.

## Part A: the desk

- desk, session 10000 start (10:52 UTC): nothing requested. Every `landing_request_*.md` (desktop_w3, desktop_w4, oldlaptop, portable, window2) and every `data_requests_*.md` read by `runs/c701/desk.py`: 0 rows whose state is requested and not landed, stopped or waiting on a ruling. The files this run's windows will open (`landing_request_portable_w2.md`, `data_requests_predict.md`) do not exist yet.

## Part B: the equities contract

- B, `docs/state/page_files_equities.md` and six example files under `site/data/equities/` (every value null, `"example": true`): done, session 10000: on main at `f52d6872d` (10:54 UTC, within the chain's first hour), deployed 10:58 UTC; snapshots `c701-B-before` and `c701-B-after`: 0 differences on all 25 pages (expected: no page reads `site/data/equities/`). Note: the two pushes before it (the queue move `1a0606f86` and the resume file `1b7814005`) touched no site file and went without a snapshot.

## Part C: repairs

- C1, the load into Supabase: cause found, session 10000. The older-than-live guard refuses `datacenter_projects`, `energy_deals` and `news_index` (Supabase holds 2 projects, 7 deals and 400 stories loaded on 13 November that no copy in the repository holds; the three are model-extracted, rebuilt only with a model call); `sources` fails its count on one name in Supabase that `sources.csv` no longer has (`IEA` with an en dash), which only a person prunes. The guard is right and stands. Fix on `wip/c701-repairs` (`17e79196e`): those cases are held, the step ends as a skip whose reason begins `held:`, any other refusal still fails; test `tests/test_session10000_load_held.py`. State: waiting to land.
- C2, the battery files: cause found, session 10000. This machine's `battery_stack_monthly` is the build of 14 November (its October has 29 days held: 15 October had no energy hours then); the price tables have since filled 15 October, and the exports solve October again with 30 days. GitHub rebuilds the table daily (11,634 rows on 24 November), but `scripts/sync.py` compares only row counts and the newest timestamp with Redivis, so a table rewritten in value with the same rows and the same newest month is called current and never brought here. Fix: in progress.
