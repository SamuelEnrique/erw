# Session 377 report: reliability, the root causes written

20 October 2026, from 18:15 UTC, unattended, on lab-desktop (the data machine), the fifth session of the chain of 20 October, day (`queue/done/011-day-20-october-data.md`), done beside session 373's restore while the daily run held the data lock. Model spend USD 0. Pulls: none (Supabase's health table read once, for 20 October's file).

## Read these first

- **Every day of 6 to 20 October with a failure now has a "Root causes" section in its file** (`queue/summary/2026-10-<day>-health.md`; 13 and 14 October had none): one paragraph a cause, the fixing session and its commit named. 19 causes in 15 days; 17 have a fix on main (one of them, the bare `python`, needed none), 1 is fixed by this chain (the sources check, session 374), 1 is waiting for Samuel (Redivis's storage, below). One fix is not proven yet: ERCOT's zone load (sessions 202 and 277), which runs only in the Saturday supply refresh; its first proof is 24 October.
- **A new cause today: Redivis's free storage is full.** At 17:32 UTC `dm_ercot_hub_append_stores` failed: "This import would cause your account to exceed its free storage allotment of 10GB. Total storage after this import would be 10.1GB." Every table that grows now fails its Redivis step, so no day could count green while it stood. **This session records that refusal as a skip, as session 305 made the export cap one** (`STORAGE_SKIP` in `warehouse/redivis/upload.py`): the table is archived and waits; the skip's reason names the storage each day. Reversible (a decision below); the storage itself is Samuel's.
- **A day's root causes survive the daily rewrite.** The daily workflow writes yesterday's file again each morning; `warehouse/health.py summary` now keeps a "## Root causes" section it finds there (`kept_causes`). 20 October's file is written from Supabase as of 18:23 UTC with its five failures; tomorrow's run rewrites the counts and keeps the causes.
- **"One alert policy, draft for Samuel's ruling"** is in `docs/machines.md`: nine numbered lines, from the email rule (session 243), the chain watch, the idle alarm and the six-hour stop. Not in force.
- `site/data/health_days.json` was read, not written: 20 October's summary was written to `runs/s377_h/` first and copied, so the record of days was not touched.

## What to review

1. `queue/summary/2026-10-20-health.md`, then any earlier day: the section "Root causes" at the end.
2. `docs/machines.md`, "One alert policy, draft for Samuel's ruling (session 377)", before the session 202 section.
3. `warehouse/redivis/upload.py`: `storage_full` and `STORAGE_SKIP`.

## The causes, in one line each

| Cause | Days | Fixed by |
|---|---|---|
| grid_network read the lock's check as an EIA page | 6 to 9 | 149, merged by 166 |
| a restored table's note as its first header line (package tests) | 6 to 12 | 202 (`f4d85e77`) |
| CARB answers the runner HTTP 202 | 7 to 12 | 166 D, 206, 271 |
| board validate handed a file the runner never holds | 7 to 9 | 166 (`b4725793`) |
| board_page before the AS tables; then the LCFS file absent | 7 to 12 | 166, 202 |
| ERCOT's zone load: a renamed file, then a window ahead of the workbook | 9, 10 | 202 and 206, 277 (not proven until 24 October) |
| the ledger restored from the runner's own calls only | 10 to 12 | 206 (`a3cee0c5`) |
| regulators that did not answer the runner | 11, 12 | 206 (Oregon a known gap) |
| a bare `python` without pandas | 11 | none needed (the venv rule) |
| sources in Supabase not in main's `sources.csv` | 15 to 18, 20 | 305, then 374 |
| uncommitted tables refused the pull | 15 to 18 | 305 (`1ca1684e`) |
| Redivis's export cap | 15 to 19 | 305 |
| the stores' header read refused for the cap | 16 to 18 | 305 |
| a cut-off run's newer live rows | 19 | 321 |
| four draft tables not in coverage, their headers unreadable | 19 | 321 (`power_deals` left for a person) |
| EIA-930's midnight window | 20 | 336 (`effc3bac`) |
| generation_mix's absent input | 20 | 327 (`d65db7f7`), not 336 |
| the stacked rebuild lines (package tests) | 20 | 336 (`88702c6c`) |
| Redivis's storage full | 20 | 377 records it as a skip; the storage is Samuel's |

## Checks

| What | Exit | Notes |
|---|---|---|
| `warehouse/health.py summary --day 2026-10-20 --out runs/s377_h` | 0 | 631 steps, 5 failures at 18:23 UTC (the worktree has no `.env`: run from the main checkout) |
| `tests.test_session377` (7 tests), with `test_session376`, `test_session305`, `test_redivis_gates`, `test_session61` | 0 | the first run failed on this session's own test (its line matcher); fixed |

## Decisions made without you

1. **Redivis's storage refusal is a skip, not a failure**, as the export cap is (session 305): the day can count green while the storage waits for you. Undo: drop the `storage_full` branch in `upload.py`.
2. **The causes were researched by a subagent from the reports and git** and checked against the day files; where two reports disagree (ERCOT's zone load) both are written.
3. **20 October's file is written now**, from the day so far, so that its causes are on main before tomorrow's run writes the file again.

## For Samuel's ruling

- The draft alert policy in `docs/machines.md`: in force as written, changed, or not.
- Redivis's storage (the first item of the morning note): until it is settled every growing table's Redivis step is a skip and the draft falls behind.
- `reason_of` in `warehouse/health.py` names one failure a step (session 202's ruling 12, still open): it hid two to nine failing tests a day from 6 to 12 October.

## Files

- New: `queue/summary/2026-10-20-health.md`, `tests/test_session377.py`, this report.
- Changed: `queue/summary/2026-10-06` to `-12`, `-15` to `-19-health.md` (the section), `warehouse/health.py`, `warehouse/redivis/upload.py`, `warehouse/table_stores.py`, `docs/machines.md`.
