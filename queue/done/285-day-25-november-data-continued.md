# Chain of 25 November 2026: sessions 3993 to 3999 and 4016 to 4024, data machine (lab-desktop), unattended: chain 279's unfinished steps, the landing desk, the runs of the week, the data requests and the records

machine: data

Written by session 3977 of chain 279 (`queue/done/279-day-24-november-data-continued.md`) on 14 November 2026, as that chain's rules ask; session 3992 updates it with what chain 279 did not finish. It takes sessions 3993 to 3999 and 4016 to 4024, the first sixteen free numbers after 3992 (4000 to 4015 are taken by desktop window 2's chains; each checked free on origin's main and on every branch by session 3977; its first session checks again, skips a taken one upward and says so). Model: Opus 5.5, high effort. One Claude Code session on the desktop: the data chain and the landing desk together.

## Why this chain

Chain 279 reads the runs of 15 and 16 November, the first with chain 278's four fixes, keeps landing the laptops' rows and takes the data requests still open. What it does not finish comes first here; then the week's runs, the requests and the records.

## Rules for every session

The rules of `queue/done/279-day-24-november-data-continued.md` hold word for word (and through it those of chains 278, 272, 267, 241, 227, 226, 223, 221, 218, 216, 215, 212, 147 and 157). Also:

- **Session 3993 writes the next file first** (`queue/next/<first free number at or above 286>-day-26-november-data-continued.md`, `machine: data`, at least fourteen sessions, carrying the owner's rules of 14 November below word for word), commits it alone and pushes it with snapshots; session 4024 updates it.
- **The build lock has no queue** (every waiter polls every 20 seconds): launch a gate early, and commit to its branch only before `lock=` appears in its `gate*_held.out`.
- **Before removing a worktree that is not this chain's,** list its ignored files (`git -C <wt> status --ignored --short`).
- **Commit at least every 25 minutes,** waits included (an empty commit on the chain's branch will do): the chain worker closes a session that shows no commit for 30 minutes.
- **A push that may be refused as a force is never forced:** merge, then push plainly (a `--force-with-lease` was denied on 14 November).

## The owner's rules of 14 November 2026 (they win over anything older in this file or the files it names)

From 14 November the desktop runs one Claude Code session, 24 hours a day: this data chain and the landing desk together (the windows B, 3 and 4 closed; files 250 and 265 retired). Every successor data file carries these two rules word for word, under this heading, and requires its own successor to carry them.

- **No waiting.** Never stop to ask: a reversible choice goes under "Decisions made without you", the rest under "For Samuel's ruling" with a default. Never end a turn idle: poll any wait yourself and keep working in between. Never wait on Samuel. Never wait for the daily run (14:00 UTC) or any time of day: a step that needs the next daily run, or a later date, is written as waiting in the report and skipped; meanwhile take the landing desk, the data requests and every other step that can be done now, and come back to the skipped step once the run or the date has come. This replaces the 20-minute rule and every "not before" of the older files. The weekly limit is the only stop. Reports in short bullets, no em or en dash.
- **The landing desk.** At the start of every session: `git fetch`, then read every `docs/state/landing_request_*.md` (`oldlaptop`, `portable`, `desktop_w3`, `desktop_w4`, and any new one) for rows marked requested. Land each requested row in order of request (several from one stack may land as one) through `scripts/land_check.py`, exactly as desk window B did (its rules in `queue/done/228-day-13-november-desktop-window2-landings.md` and its sessions' reports): the work in a worktree beside the main checkout, `origin/main` merged into the branch first; every command the lander prints run as its own command with its exit read; never between 14:00 and 16:15 UTC; the snapshots before and after, every difference listed; a failing gate fixed on the requesting stack only when the fix is small and plainly correct, otherwise the failure written in the row and the desk moves on. Mark each row landed with its commit and push. A landing outranks the session's other steps.

Read first: chain 279's note `docs/state/note_<its day>_data_c279.md`, chain 278's note `docs/state/note_2026-11-14_data_c278.md`, `docs/state/rulings_2026-11-06.md` and any newer rulings file, every `docs/state/data_requests_*.md`, `CLAUDE.md`.

## Session 3993: the next file, the ground, the landing desk, chain 279's first unfinished step

Long end 1:00. The next file. Memory and disk; `git worktree list`, landed worktrees removed; `scripts/precheck.py` from the main checkout, `scripts/freeze.py status`; main green or not (a gate's suite, or `scripts/suite_gate.py --ref origin/main`), the first line of the report. The landing desk. Then chain 279's first unfinished step, from its note's "What waits" (session 3992 writes them here).

## Sessions 3994 to 3998: chain 279's other unfinished steps

Long end 1:30 each. Written by chain 279's session 3992 on 15 November 2026 at about 19:15 UTC from its note (`docs/state/note_2026-11-15_data_c279.md`). The daily run and the data machine's run of 15 November both committed (the first since 12 November); chain 279's gate h (its last reports, the rename of test 3999 to 3979, the citations) was running at its close: land it first if session 3992's report does not say it landed. Left, in this order; a run not yet in is waiting and skipped:

- **Gate h's landing** (`wip/c279-land-h`, task `3992-landing`, port 3992), if not yet landed: the lander's commands, snapshots before and after.
- **The Energy Roundup of 15 November** (Sunday evening; last week's started 23:00 UTC) and **the Digest of 16 November** with check-values on `/digest`: the owner's API key is at its limit until 1 December, so their model parts may be refused; say what was published and what was not, at the top of the report.
- **The daily run of 16 November** (14:00 UTC): its commit through the guard, `package tests` (the rollups' `Source:` line, gate g), the health summary; `supabase_load` will still refuse `datacenter_projects`, `energy_deals` and `news_index` (older than the live copy) and `sources` (the stale IEA row) until the rulings of chain 279's note.
- **The data machine's run of 16 November** (17:00 UTC): `dm_commit` lands with the replication group put back while test 5502 holds the signature pack's figures.
- **The CAISO's FERC compliance filing** (due 16 November) for the siting gaps.
- **Ask request row 6** settles only with `energy_deals`' rebuild (coverage 527, the archive 532).
- **The Ask weekly run** (USD 4) on or after 19 November, and only once the key answers.

## Session 3999: the runs of the days since chain 279's last reading

Long end 1:30. Each daily run, board, Digest (weekdays), Roundup (Sundays) and data machine run since chain 279's last reading: each job's row in `erw_health` over `SUPABASE_DB_URL`, each failed step opened with its first error line, a fault of this repository's code fixed with its test on the chain's branch. A run not yet in is waiting, and skipped.

## Sessions 4016 to 4019: the data requests still open

Long end 2:00 each. Every row still requested in `docs/state/data_requests_*.md`, in order of request, one or two rows a session: done with its commit, or what stops it under "For Samuel's ruling" with the default taken. Robots and terms before any new host; every write under the data lock; every new table validated, archived, in coverage and registered.

## Session 4020: the siting gaps and the tab

Long end 1:30. From the newest dated state section of `docs/reviews/siting-gaps.md`, any row a public US document can now fill; the All grids tab's cells wired; a new dated state section.

## Session 4021: the findings, the Ask weekly run and the records

Long end 1:30. The drafts checked (`check.py --tables` with an absolute path, `check_cards.py` from the main checkout, `check_do.py`), the count by family before and after; nothing approved. The Ask weekly run (USD 4) when its seven days have passed since the last, and only if the owner's API key answers. `package/tools/build_tables.py --check`, the tests of sessions 1001, 1008 and 1009, `scripts/build_llms.py` after the last coverage row; this chain's new public tables on the Redivis draft, nothing released.

## Session 4022: the week's daily runs

Long end 1:00. Pulls: GitHub's API, at most 30 requests. Each scheduled job's last seven days, each failed step with its first error line; the guard's verdict on every bot push; `runs/data_machine_status.txt` and the `dm_` rows of `erw_health`; the health summary's "Stale on main" line quoted.

## Session 4023: the note

Long end 1:00. `docs/state/note_<the day>_data_c285.md` in chain 147's note's form.

## Session 4024: the next file, the landing, the queue

Long end 1:00. The next file (written by session 3993) updated with what this chain did not finish, carrying the owner's rules of 14 November word for word, and pushed alone; this chain's branch landed through the gate (never between 14:00 and 16:15 UTC); `python scripts/chain_queue.py next`, and run the file it prints the same way. If the queue step exits 3, write the next data file (`machine: data`, carrying both rules) and continue.
