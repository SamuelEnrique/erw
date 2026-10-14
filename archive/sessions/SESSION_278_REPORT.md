# Session 278 report: the morning note

14 October 2026, 13:05 to 13:25 UTC, unattended, on lab-desktop (the data machine), the last session of the overnight chain of 14 October. Branch `task/278-morning-note`. Model spend USD 0: no model call. Pulls: none (three reads of Supabase with the anon key, to answer session 265's "0 rows").

## Read these first

- **`docs/state/morning_2026-10-14.md`:** what both machines landed, what failed, the five packs in reading order, and every open ruling in one list (18 from tonight, 58 carried from the note of 13 October, 13 ruled and done).
- **Every session of this chain landed, each with 0 differences on the 25 snapshot pages:** 271 to 277 between 09:51 and 13:13 UTC, before the 13:45 window; this note lands last.
- **Session 265's "0 rows" for `scarcity_hours_by_grid` was a cancelled read, not an empty table:** a read by the table's name alone passes the anon key's three seconds; with a date it answers in 0.2 seconds. The note says so for the code machine.

## The landings recorded here

- **Session 277:** before `s277-before` 12:18:51 UTC; pushed 12:18:57 (`task/277-stale-round-two`, `fbdc9dc5`); check run 38562874899 success 12:29:01; merged `be489151`; deployed 12:30:19; after `s277-after` 12:30:23; `compare`: 0 differences. Expected: a connector's message, two schedule steps, tests.
- **Session 273:** before `s273-before` 13:03:18; pushed 13:03:25 (`task/273-caiso-history`, `6305e079`); check run 38568649330 success 13:13:28; merged `896bbdaa`; deployed 13:14:48; after `s273-after` 13:14:51; `compare`: 0 differences. Expected: no page is live; the battery page's word for California's depth and its tables changed behind the in-review page. Its load into the live set (12:13) had its own snapshots, `s273-before-load` and `s273-after-load`: 0 differences.

## Checks

| What | Exit | Notes |
|---|---|---|
| `python scripts/precheck.py --what "session 278"` | 0 | six of six |
| the anon key's reads of `scarcity_hours_by_grid` and `large_load_public` | | by name alone: cancelled at 3 s; with a date: 221 ms; `large_load_public`: 341 rows |
| no em dash in the note and this report | | checked |

## Decisions made without you

1. **"The five packs" read as the five review packages of tonight:** the code machine's three (battery, generator, datacenter), Redivis v1 and the motion proofs. The Games review is named as a sixth, not landed.
2. **The carried rulings are the 13 October note's own lines,** by their numbers, with a few words where something moved; the thirteen ruled tonight are listed apart.
3. **The landing of this session is in no committed file:** a commit to record it would be one more landing. It is in the chain's closing message and in `runs/session278/landing.out`.

## For Samuel's ruling

- None of its own: the note's list is the list.

## Files

- New: `docs/state/morning_2026-10-14.md`, this report.
