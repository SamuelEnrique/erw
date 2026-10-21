# The morning note, 21 October 2026, after the night chain

Energy Research Warehouse (ERW), session 386, for Samuel. The data machine's chain of 20 to 21 October, night (sessions 384 to 386, `queue/done/013-night-20-october-data.md`), unattended on lab-desktop, from 21:16 UTC on 20 October to this note's push. Model spend USD 0 in every session. The day chain's note, before this one: [`docs/state/morning_2026-10-21_day.md`](morning_2026-10-21_day.md).

## Read these first

- **Why this machine's daily run of 20 October stopped, and the fix** (session 384, landed): its console window closed at 18:06 UTC (0xC000013A; the task runs "Interactive only", so it has a window). A closed window ends the process before `lock.py run` can release the lock, which is why the lock was held until it lapsed at 20:00 UTC. `lock.py` now releases the lock when the console closes, signs out or shuts down (`on_console_close()`, 5 tests). Running the task with no window is yours to rule.
- **Session 384's part (b) was not run**: it waited for the scheduled runs of 21 October, and at 05:15 UTC you asked for the wait to stop and this note to be written. It is the first session of the next chain (387).
- **Redivis's refusals for storage remove tables from the draft** (session 385): the uploader deletes a draft table before uploading its new copy, so the refusal of 17:32 UTC on 20 October left `ercot_all_hub_prices_history` out of the public draft (Redivis answers 404). Release v1 now holds it for storage beside `node_basis_daily`: **135 tables in v1, 41 held for a license, 2 for storage**; `release_v1.py --check` 0 differences. Any growing table refused the same way leaves the draft until the storage is settled.
- **The move under Ben's organization is prepared to the clicks** (session 385, [`docs/redivis/organization-move.md`](../redivis/organization-move.md)): where both datasets are (184 tables, 8.22 GB, and 39, 1.09 GB), the ERW's changes after the move as a diff not applied, the order against the release click, and the storage with what each choice frees. Redivis's own steps are not written there: its documentation host has no terms page, so the pages that describe the move were named, not read.
- **The next chain is written**: `queue/next/016-day-21-october-data.md`, sessions 387 to 389 (21 October's root causes and the green streak; the 20 tables whose license is not settled; the note), pushed to main on its own (`bfca6f1a`) with before and after snapshots.

## What each session landed

| Session | Landed |
|---|---|
| 384 | (a) the cause of 20 October's stop in `queue/summary/2026-10-20-health.md`, with its last two root causes; `lock.py`'s release on close with `tests/test_session384.py`. (b) not run (above). (c) the loader's guard comparing values when the stamps differ: a draft in its report, `load.py` unchanged |
| 385 | `docs/redivis/organization-move.md`; `ercot_all_hub_prices_history` held for storage in the release package (spliced, one row) and in its two documents |
| 386 | This note, session 384's report, and `queue/next/016-day-21-october-data.md` |

Session 384 (a) landed on `task/384-lock` (checks passed, run 39502028928; merged as `dfbe8e08`; deployed 21:52 UTC): snapshots `s384-land-before` and `-after`, **0 differences on 25 pages**, expected (every page in review). Session 385 on `task/385-redivis` (checks passed, run 39504428096; merged as `fcdff2d8`; deployed 22:07 UTC): `s385-land-before` and `-after`, 0 differences, expected. Session 386 lands this note and the reports of 384 and 386 on `task/386-morning`; the record of its checks is in session 389's note.

## Pulls against their ceilings

| Session | Pull | Used | Ceiling |
|---|---|---|---|
| 384 | none (Task Scheduler and the event logs read, on this machine) | 0 | 0 |
| 385 | Redivis's API, metadata only | 5 | 20 |
| 385 | docs.redivis.com (robots file, sitemap, pages' sitemap) | 3 | 4 |
| 386 | none (GitHub's public API for the deploys) | 0 | 0 |

Nothing was asked of a paused publisher. docs.redivis.com was a new host: its robots file was read first, and with no terms page found, none of its content pages was read.

## Decisions made without you (one line each; the reasons are in each report)

- 384: the lock released once, from the close handler or from `finally`, whichever comes first; the handler lets Windows end the process as before; part (b) carried to session 387.
- 385: `ercot_all_hub_prices_history` held for storage, not left in v1's list; table sizes from three list requests, the two missing tables asked for by name; the draft read as `version="next"`, never through `open_draft()` (which creates one); Redivis's move pages not read.
- 386: the next chain from items 5 and 6 only (item 9 waits on you and Ben); its session numbers 387 to 389, below the code machine's 401 to 415.

## Waiting for you, highest value first

1. **Redivis storage (10 GB, full)**, now more pressing: a refusal removes the table from the draft. The choices and what each frees are in `docs/redivis/organization-move.md` (the 41 license-held tables out of the draft: 0.94 GB; the private dataset elsewhere: 1.09 GB; a paid tier; the organization's storage after the move). With it, **the uploader's replace** (upload under a temporary name, swap once whole), so a refusal can no longer remove a table: proposed, not made.
2. **The move under Ben's organization**, and its order against the release click (the same document).
3. **The loader's guard** (session 384's report, part c): load a restored copy as unchanged when it equals the live one in value; `ferc_eqr_contracts`, 452 rows fewer here, still refused.
4. **The daily task with no console window** (session 384).
5. Still open from the day note: the four permission letters; `nyiso_load_queue` (coverage public, `sources.csv` internal); "One alert policy" in `docs/machines.md`; `restore_tables.py`'s note as a restored table's first header line.

## The other machines

- **The code machine's chains**: `queue/next/014-night-20-october-code.md` (sessions 381 to 383) and `015-day-20-october-code-pm.md` (401 to 415) are both still in `queue/next/`, while their sessions' branches are pushed: `wip/381-five-tools`, `wip/382-trader-path` and `wip/381-382-land`, and seven of `wip/403-s` to `wip/414-s` (403, 406, 407, 409, 410, 413, 414; the last, `wip/410-s`, at 05:04 UTC). `task/367-372` is pushed; its latest commit fixes `test_session166`, on which GitHub run 39524179379 failed.
- **A branch with session 420**, `wip/findings-oct20`, outside both machines' reserved numbers; this chain's 387 to 389 do not collide with it.
- **This machine** stays on `main` in its main checkout, with the daily run of 20 October's page files uncommitted as they were; its daily run of 21 October starts at 17:00 UTC.
