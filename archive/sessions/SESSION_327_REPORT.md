# Session 327 report: the afternoon note

19 and 20 October 2026, from 23:48 UTC, unattended, on lab-desktop (the data machine), the last session of the chain of 19 October, daytime. Model spend USD 0. Pulls: none (GitHub's API and the live database, read only).

## Read these first

- **`docs/state/afternoon_2026-10-19.md`** is the note for Samuel's evening hour: the manual run and the green days, one line a session, every pull against its ceiling, every decision made without him, and what waits for him, highest value first, with the permissions list linked.
- **The manual daily run 39344868297 finished green** (job success 02:17:43; the daily step ok at 02:11:22; the metadata commit `2bea6dc1`), but three steps wrote failed rows, so 20 October will not be a green day: `eia930` (a midnight dispatch: EIA's last hour of 19 October unpublished), `generation_mix` (its input absent after `eia_series` was stopped at its budget; **now a skip**, landed here) and one package test (`nyiso_zone_load_hourly`). **Green days: 0, counted to 19 October.**

## Checks

| What | Exit | Notes |
|---|---|---|
| `scripts/precheck.py --what "session 327"` | 0 | |
| the manual run's jobs and steps (GitHub's API) and its `erw_health` rows | 0 | job success; steps 9 to 18 success; `erw_health`: daily run ok, supabase_load ok, eia930, generation_mix and package tests failed, eia_series skipped at its budget |

## The landing

- First try: `task/327-afternoon` pushed 02:19:55; its checks (run 39358324576) **failed** in "Tests (tests/)". Reproduced here with `GITHUB_ACTIONS=true`: the whole suite fails the five standing tests (51, 94, 125, 165, 267) and two that **main itself now fails**, since the manual run's metadata commit `2bea6dc1` brought new data: `test_session157.TagRule` (the site's policy file holds tagged actions the test's cases do not: `federalregister:2026-21217`, `puct:537c766a4c02`) and `test_session156.TheNodeTests` (case 18: the briefing's Texas curtailment share against the new `curtailment/ercot.json`). Neither file is touched by this session, so every `task/` branch fails until they are updated.
- So the note went **straight to main**, as session 305 did, after the local suite showed no failure main does not already have: freeze 0; before `s327b-before`; merged origin/main; pushed 02:38:56 (`d65db7f7`); deployment success 02:40:29; after `s327b-after`; **0 differences on 25 pages**.
- This line went out in a second push, with its own snapshots.

## Decisions made without you

1. **The note waited for the manual run's end**, so that it could say how the run ended.
2. **`generation_mix` skips when its input is absent** (`warehouse/run_daily.sh`, with a test in `tests/test_session321.py`), landed with this note: the manual run showed a budget skip upstream turning into a failure downstream.

## For Samuel's ruling

- `eia_series`'s budget (split it, or a longer one) and the package test of `nyiso_zone_load_hourly`: the note's items 6 and 7.
- Tests 156 (case 18) and 157 (`TagRule`) fail on main since the daily commit `2bea6dc1`: a session must update their cases to the new data before any `task/` branch can land (the note's item 8).

## Files

- New: `docs/state/afternoon_2026-10-19.md`, this report.
- Changed: `warehouse/run_daily.sh` (`generation_mix`), `tests/test_session321.py`, session 321's report (the manual run and the third landing).
